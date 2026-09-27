"""Build the profile's static SVGs: the nf-audit and proteus cards and the two
contact cards. Run on a machine with the brand fonts:

    uv run --with fonttools --with brotli --with uharfbuzz --with pillow python scripts/build_static.py \\
        --fonts ~/dev/s1re/brand/fonts \\
        --nf-audit ~/dev/nf-audit/examples/rnaseq-star_salmon-releases.md \\
        --ribbon ribbon-1pgb.png --analysis 1pgb.json

`--ribbon` is scripts/capture_ribbon.py's render of `proteus view 1pgb.pdb --html`, and
`--analysis` the output of `proteus analyze 1pgb.pdb --json`.
"""

import argparse
import base64
import io
import json
import re
from pathlib import Path

from brand import (COIL, CREAM, DIM, HELIX, INK, KHAKI, LIFT, ROOT, SAGE, STRAND, TAN,
                   Face, card, num)

IDLE = (f'<pattern id="idle" width="4" height="4" patternUnits="userSpaceOnUse">'
        f'<rect width="4" height="4" fill="{LIFT}"/><circle cx="2" cy="2" r="0.95" fill="{SAGE}"/></pattern>')


class Fonts:
    def __init__(self, root):
        root = Path(root)
        self.mono = Face(root / "GeistMono-Regular.otf")
        self.mono_md = Face(root / "GeistMono-Medium.otf")
        self.display = Face(root / "Freigeist-Regular.woff2")


def label(f, text, w):
    return f.mono.text(text, w - 30, 34, 12, DIM, tracking=1.2, anchor="end")


def load_runs(table):
    """(date, release, cost, unused share) per star_salmon run in nf-audit's release table."""
    runs = []
    for line in Path(table).read_text().splitlines():
        m = re.match(r"\| (\S+) salmon (\d{4}-\d\d-\d\d) \|", line)
        if not m:
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        release, date = m.groups()
        cost = float(cells[8].lstrip("$").replace(",", ""))
        unused = int(cells[10].rstrip("%")) / 100
        runs.append((date, release, cost, unused))
    runs.sort()
    return runs


def columns(x0, width, y_base, height, runs, ymax=180):
    slot = width / len(runs)
    bar = slot * 0.62
    out = []
    for i, (_, _, cost, unused) in enumerate(runs):
        bx = x0 + slot * i + (slot - bar) / 2
        clipped = cost > ymax
        top = y_base - height - 6 if clipped else y_base - cost / ymax * height
        used_top = y_base - min(cost * (1 - unused), ymax) / ymax * height
        out.append(f'<rect x="{num(bx)}" y="{num(used_top)}" width="{num(bar)}" height="{num(y_base - used_top)}" fill="{TAN}"/>')
        out.append(f'<rect x="{num(bx)}" y="{num(top)}" width="{num(bar)}" height="{num(used_top - 2 - top)}" rx="2" fill="url(#idle)"/>')
        if clipped:
            out.append(f'<path d="M{num(bx - 2)} {num(top + 10)}L{num(bx + bar + 2)} {num(top + 6)}" stroke="{INK}" stroke-width="2"/>')
    return "".join(out)


def nf_audit_card(f, table):
    W, H = 540, 400
    runs = load_runs(table)
    band = [u for *_, u in runs if u <= 0.70]
    lo, hi = round(min(band) * 100), round(max(band) * 100)
    el = [
        f.mono_md.text("nf-audit", 36, 66, 28, CREAM),
        f.mono.text("where a nextflow run's cpu-hours go", 36, 94, 15.5, SAGE),
        columns(36, 468, 272, 140, runs),
    ]
    big = f"{lo}–{hi}%"
    el.append(f.mono_md.text(big, 36, 332, 36, CREAM))
    tx = 36 + f.mono_md.width(big, 36) + 16
    el.append(f.mono.text("of allocated cost never used", tx, 314, 15, KHAKI))
    el.append(f.mono.text(f"nf-core/rnaseq · {len(band)} of {len(runs)} releases", tx, 334, 13, SAGE))
    el.append(f.mono.text(f"{runs[0][1]} → {runs[-1][1]} · seqera list rates", 36, 376, 12.5, DIM))
    el.append(f.mono_md.text("repo →", 504, 376, 14, KHAKI, anchor="end"))
    return card(W, H, "".join(el), defs=IDLE, label=label(f, "02 · RUST · MIT", W),
                title=f"nf-audit: {lo}–{hi}% of allocated cost never used in {len(band)} of {len(runs)} nf-core/rnaseq releases")


def ribbon(path, box, scale=3):
    """proteus's own cartoon (scripts/capture_ribbon.py), fitted into box and embedded as WebP
    at scale× the card's units. Resized premultiplied so the keyed edge takes no dark fringe."""
    from PIL import Image

    img = Image.open(path).convert("RGBa")
    x0, y0, x1, y1 = box
    k = min((x1 - x0) / img.width, (y1 - y0) / img.height)
    w, h = img.width * k, img.height * k
    img = img.resize((round(w * scale), round(h * scale)), Image.LANCZOS).convert("RGBA")
    buf = io.BytesIO()
    img.save(buf, "WEBP", quality=90, alpha_quality=100, method=6)
    uri = base64.b64encode(buf.getvalue()).decode()
    x, y = (x0 + x1 - w) / 2, (y0 + y1 - h) / 2
    return (f'<image x="{num(x)}" y="{num(y)}" width="{num(w)}" height="{num(h)}" '
            f'href="data:image/webp;base64,{uri}"/>')


def proteus_card(f, ribbon_png, analysis):
    W, H = 540, 400
    a = json.loads(Path(analysis).read_text().splitlines()[0])

    el = [
        f.mono_md.text("proteus", 36, 66, 28, CREAM),
        f.mono.text("protein design loop, one binary", 36, 94, 15.5, SAGE),
        ribbon(ribbon_png, (36, 118, 266, 352)),
    ]
    rx = 282
    el.append(f.mono.text("1PGB · PROTEIN G", rx, 134, 12.5, SAGE, tracking=1.2))
    el.append(f.mono.text(f"{a['n_residues']} residues", rx, 158, 15, KHAKI))
    for i, (name, colour, pct) in enumerate((("helix", HELIX, a["helix_pct"]), ("strand", STRAND, a["strand_pct"]),
                                             ("coil", COIL, a["coil_pct"]))):
        y = 196 + i * 27
        el.append(f'<circle cx="{rx + 5}" cy="{y - 5}" r="5" fill="{colour}"/>')
        el.append(f.mono.text(name, rx + 20, y, 15, CREAM))
        el.append(f.mono.text(f"{pct:.0f}%", 504, y, 15, CREAM, anchor="end"))
    el.append(f.mono.text("RAMACHANDRAN", rx, 288, 12.5, SAGE, tracking=1.2))
    el.append(f.mono.text(f"{a['rama_favored_pct']:.1f}% favoured", rx, 312, 16.5, CREAM))
    el.append(f.mono.text("RADIUS OF GYRATION", rx, 340, 12.5, SAGE, tracking=1.2))
    el.append(f.mono.text(f"{a['rg']:.2f} Å", rx, 364, 16.5, CREAM))
    el.append(f.mono.text("proteus view 1pgb.pdb", 36, 376, 12.5, DIM))
    el.append(f.mono_md.text("repo →", 504, 376, 14, KHAKI, anchor="end"))
    return card(W, H, "".join(el), label=label(f, "03 · RUST · MIT / APACHE-2.0", W),
                title=(f"proteus: protein G (1PGB) as a cartoon ribbon drawn by proteus view, coloured by secondary structure; "
                       f"helix {a['helix_pct']:.0f}%, "
                       f"strand {a['strand_pct']:.0f}%, Ramachandran {a['rama_favored_pct']:.1f}% favoured"))


def contact(f, kind, value):
    W, H = 540, 120
    el = [
        f.mono.text(kind, 36, 48, 12, SAGE, tracking=1.2),
        f.mono_md.text(value, 36, 86, 20, CREAM),
        f.mono_md.text("→", 504, 86, 22, KHAKI, anchor="end"),
    ]
    return card(W, H, "".join(el), title=f"{kind.lower()}: {value}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fonts", required=True)
    ap.add_argument("--nf-audit", required=True)
    ap.add_argument("--ribbon", required=True, help="scripts/capture_ribbon.py output")
    ap.add_argument("--analysis", required=True)
    args = ap.parse_args()
    f = Fonts(args.fonts)
    out = {
        "card-nf-audit.svg": nf_audit_card(f, args.nf_audit),
        "card-proteus.svg": proteus_card(f, args.ribbon, args.analysis),
        "contact-mail.svg": contact(f, "MAIL", "sushanthona04@gmail.com"),
        "contact-linkedin.svg": contact(f, "LINKEDIN", "linkedin.com/in/sushanthona"),
    }
    for name, svg in out.items():
        (ROOT / "assets" / name).write_text(svg)
        print(f"assets/{name}: {len(svg):,} bytes")


if __name__ == "__main__":
    main()
