"""Draw the proteus card's structure with proteus itself: `proteus view --html` writes the
WebGL page, headless Chromium renders it, and the canvas is keyed off the ground colour and
cropped to the ribbon.

    proteus view 1pgb.pdb --html 1pgb.html
    uv run --with playwright --with pillow --with numpy python scripts/capture_ribbon.py 1pgb.html ribbon-1pgb.png

The PNG is RGBA at the canvas's full resolution; build_static.py scales it into the card.
"""

import argparse
import base64
import io
import math
from pathlib import Path

import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright


def capture(html, yaw, pitch, width, height):
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--enable-unsafe-swiftshader", "--use-angle=swiftshader"])
        page = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=2,
                                color_scheme="dark")
        page.goto(Path(html).resolve().as_uri())
        page.wait_for_function("window.ProteusViewer !== undefined")
        url = page.evaluate(
            """([yaw, pitch]) => {
                const v = window.ProteusViewer;
                Object.assign(v.state, { yaw, pitch, spin: false });
                v.render();
                return document.getElementById('view').toDataURL('image/png');
            }""",
            [math.radians(yaw), math.radians(pitch)],
        )
        browser.close()
    return Image.open(io.BytesIO(base64.b64decode(url.split(",", 1)[1]))).convert("RGBA")


def key(img):
    """Ground pixels become transparent and the image is cropped to what is left. The post pass
    writes the exact ground colour wherever depth is empty (no antialiasing), so the corner
    pixel is the key."""
    a = np.asarray(img).copy()
    ground = a[0, 0, :3].copy()
    a[(a[..., :3] == ground).all(axis=-1)] = 0
    out = Image.fromarray(a, "RGBA")
    return out.crop(out.getbbox()), tuple(int(c) for c in ground)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html")
    ap.add_argument("out")
    ap.add_argument("--yaw", type=float, default=0.0, help="degrees from proteus's principal-axis view")
    ap.add_argument("--pitch", type=float, default=0.0, help="degrees")
    ap.add_argument("--viewport", default="1600x950", help="CSS pixels, drawn at 2x")
    args = ap.parse_args()
    w, h = (int(v) for v in args.viewport.split("x"))
    img, rgb = key(capture(args.html, args.yaw, args.pitch, w, h))
    img.save(args.out)
    print(f"{args.out}: {img.width}x{img.height}, ground rgb{rgb} keyed out")


if __name__ == "__main__":
    main()
