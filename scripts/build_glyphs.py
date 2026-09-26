"""Extract Geist Mono outlines into scripts/glyphs.json, so the daily deck job
needs only the Python standard library.

    uv run --with fonttools python scripts/build_glyphs.py ~/dev/s1re/fonts

Geist Mono is Copyright 2024 The Geist Project Authors and licensed under the
SIL Open Font License 1.1 (https://openfontlicense.org).
"""

import json
import sys
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

CHARS = "".join(chr(c) for c in range(32, 127)) + "·…→←─│×–—●○"
FACES = {"regular": "GeistMono-Regular.otf", "medium": "GeistMono-Medium.otf"}


def main(fonts):
    out = {
        "font": "Geist Mono",
        "license": "SIL Open Font License 1.1, Copyright 2024 The Geist Project Authors",
        "upem": 1000,
        "advance": 600,
        "faces": {},
    }
    for face, file in FACES.items():
        tt = TTFont(Path(fonts) / file)
        cmap, glyphs = tt.getBestCmap(), tt.getGlyphSet()
        assert tt["head"].unitsPerEm == 1000
        paths = {}
        for ch in CHARS:
            name = cmap.get(ord(ch))
            if name is None:
                continue
            assert tt["hmtx"][name][0] == 600, ch
            pen = SVGPathPen(glyphs, ntos=lambda v: str(round(v)))
            glyphs[name].draw(pen)
            paths[ch] = pen.getCommands()
        out["faces"][face] = paths
    dest = Path(__file__).with_name("glyphs.json")
    dest.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")))
    print(f"{dest}: {dest.stat().st_size:,} bytes")


if __name__ == "__main__":
    main(sys.argv[1])
