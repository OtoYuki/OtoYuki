"""Build the profile's static SVGs: the whoami terminal, the nf-audit and proteus
cards, and the contact keys. Run on a machine with the brand fonts:

    uv run --with fonttools --with brotli --with uharfbuzz --with numpy python scripts/build_static.py \\
        --fonts ~/dev/s1re/fonts \\
        --nf-audit ~/dev/nf-audit/examples/rnaseq-star_salmon-releases.md \\
        --pdb 1pgb.pdb --analysis 1pgb.json

`--analysis` is the output of `proteus analyze 1pgb.pdb --json`.
"""

import argparse
import json
from pathlib import Path

import numpy as np

from brand import (COIL, CREAM, DIM, HELIX, INK, KHAKI, LIFT, OLIVE, ROOT, RULE, SAGE, STRAND, TAN,
                   Face, card, num)
from rnaseq_chart import load_runs

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


def whoami(f):
    W, H = 1000, 290
    el = []
    x = 48
    el.append(f.mono_md.text("~/s1re.sh", x, 62, 16, OLIVE))
    x += f.mono_md.width("~/s1re.sh ", 16)
    el.append(f.mono_md.text("$", x, 62, 16, DIM))
    x += f.mono_md.width("$ ", 16)
    for i, (_, d) in enumerate(f.mono_md.glyph_paths("whoami", x, 62, 16)):
        el.append(f'<path class="k" style="animation-delay:{0.3 + i * 0.075:.3f}s" fill="{KHAKI}" d="{d}"/>')
    adv = f.mono_md.width("w", 16)
    el.append(f'<rect class="c1" opacity="0" x="{num(x)}" y="47" width="{num(adv)}" height="19" fill="{TAN}"/>')

    el.append(f'<g class="o" style="animation-delay:1s">{f.display.text("Sushant Hona", 45, 138, 52, CREAM, -0.6)}</g>')
    el.append(f'<g class="o" style="animation-delay:1.2s">'
              f'{f.mono_md.text("RUST · SYSTEMS · COMPUTATIONAL BIOLOGY", 48, 176, 13, KHAKI, tracking=2.4)}</g>')
    loc = [f'<circle class="p" cx="53" cy="{209 - 4.5}" r="4" fill="{TAN}"/>',
           f.mono.text("kathmandu", 68, 209, 14, CREAM)]
    lx = 68 + f.mono.width("kathmandu   ", 14)
    loc.append(f.mono.text("utc+5:45", lx, 209, 14, SAGE))
    lx += f.mono.width("utc+5:45   ", 14)
    loc.append(f.mono.text("27.72°N 85.32°E", lx, 209, 14, DIM))
    el.append(f'<g class="o" style="animation-delay:1.35s">{"".join(loc)}</g>')

    x = 48
    tail = [f.mono_md.text("~/s1re.sh", x, 254, 16, OLIVE)]
    x += f.mono_md.width("~/s1re.sh ", 16)
    tail.append(f.mono_md.text("$", x, 254, 16, DIM))
    x += f.mono_md.width("$ ", 16)
    el.append(f'<g class="o" style="animation-delay:1.6s">{"".join(tail)}</g>')
    el.append(f'<rect class="c2" x="{num(x)}" y="239" width="{num(adv)}" height="19" fill="{TAN}"/>')

    style = (
        "@keyframes on{from{opacity:0}to{opacity:1}}"
        "@keyframes off{from{opacity:1}to{opacity:0}}"
        "@keyframes rise{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}"
        f"@keyframes type{{from{{transform:translateX(0)}}to{{transform:translateX({num(adv * 6)}px)}}}}"
        "@keyframes blink{50%{opacity:0}}"
        "@keyframes pulse{0%,100%{opacity:1}50%{opacity:.3}}"
        ".k{animation:on 1ms steps(1) both}"
        ".o{animation:rise .5s ease-out both}"
        ".c1{animation:type .45s steps(6,end) .3s both,off 1ms steps(1) .95s both}"
        ".c2{animation:on 1ms steps(1) 1.6s both,blink 1.1s steps(1) 1.6s infinite}"
        ".p{animation:pulse 2.4s ease-in-out infinite}"
    )
    return card(W, H, "".join(el), style=style, label=label(f, "TTY/01", W),
                title="whoami: Sushant Hona. Rust, systems, computational biology. Kathmandu, UTC+5:45.")


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
    return card(W, H, "".join(el), defs=IDLE, label=label(f, "03 · RUST · MIT", W),
                title=f"nf-audit: {lo}–{hi}% of allocated cost never used in {len(band)} of {len(runs)} nf-core/rnaseq releases")


def backbone(pdb, n_sub=3):
    """Cα trace of chain A, smoothed with Catmull-Rom, principal axis vertical."""
    ca = []
    for line in Path(pdb).read_text().splitlines():
        if line.startswith("ATOM") and line[12:16] == " CA " and line[21] == "A" and line[16] in " A":
            ca.append([float(line[30:38]), float(line[38:46]), float(line[46:54])])
    p = np.array(ca)
    p -= p.mean(axis=0)
    _, vecs = np.linalg.eigh(np.cov(p.T))
    p = p @ vecs[:, ::-1]  # largest spread first
    p = p[:, [1, 0, 2]]  # ... on y, the spin axis
    pts, idx = [], []
    ext = np.vstack([p[0], p, p[-1]])
    for i in range(len(p) - 1):
        p0, p1, p2, p3 = ext[i], ext[i + 1], ext[i + 2], ext[i + 3]
        for t in np.linspace(0, 1, n_sub, endpoint=False):
            t2, t3 = t * t, t * t * t
            pts.append(0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
            idx.append(i if t < 0.5 else i + 1)
    pts.append(p[-1])
    idx.append(len(p) - 1)
    return np.array(pts), idx, len(p)


def proteus_card(f, pdb, analysis):
    W, H = 540, 400
    a = json.loads(Path(analysis).read_text().splitlines()[0])
    pts, idx, n_res = backbone(pdb)
    assert n_res == a["n_residues"] == len(a["dssp"])
    ss = {"H": HELIX, "G": HELIX, "I": HELIX, "E": STRAND, "B": STRAND}
    colours = [ss.get(a["dssp"][i], COIL) for i in idx]

    # Project every frame first, then fit the whole turn into the box.
    frames, period = 16, 20
    radius = np.max(np.linalg.norm(pts, axis=1))
    depth = 4 * radius
    th = 2 * np.pi * np.arange(frames + 1) / frames
    x = np.outer(pts[:, 0], np.cos(th)) + np.outer(pts[:, 2], np.sin(th))
    z = -np.outer(pts[:, 0], np.sin(th)) + np.outer(pts[:, 2], np.cos(th))
    s = depth / (depth - z)
    px, py = x * s, -pts[:, 1:2] * s
    box = (30, 114, 250, 350)  # x0, y0, x1, y1
    k = min((box[2] - box[0]) / np.ptp(px), (box[3] - box[1]) / np.ptp(py))
    ox = (box[0] + box[2]) / 2 - k * (px.max() + px.min()) / 2
    oy = (box[1] + box[3]) / 2 - k * (py.max() + py.min()) / 2
    sx, sy = ox + k * px, oy + k * py
    op = 0.35 + 0.65 * (z + radius) / (2 * radius)
    dots, css = [], []
    for j, colour in enumerate(colours):
        base = f"transform:translate({num(sx[j, 0])}px,{num(sy[j, 0])}px) scale({s[j, 0]:.2f});opacity:{op[j, 0]:.2f}"
        dots.append(f'<circle class="d d{j}" r="3.3" fill="{colour}" style="{base}"/>')
        css.append(f"@keyframes d{j}{{" + "".join(
            f"{num(fr / frames * 100)}%{{transform:translate({num(sx[j, fr])}px,{num(sy[j, fr])}px)scale({s[j, fr]:.2f});opacity:{op[j, fr]:.2f}}}"
            for fr in range(frames + 1)) + "}"
            f".d{j}{{animation-name:d{j}}}")
    style = f".d{{animation-duration:{period}s;animation-timing-function:linear;animation-iteration-count:infinite}}" + "".join(css)

    el = [
        f.mono_md.text("proteus", 36, 66, 28, CREAM),
        f.mono.text("protein design loop, one binary", 36, 94, 15.5, SAGE),
        "".join(dots),
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
    el.append(f.mono.text("proteus analyze 1pgb.pdb", 36, 376, 12.5, DIM))
    el.append(f.mono_md.text("repo →", 504, 376, 14, KHAKI, anchor="end"))
    return card(W, H, "".join(el), style=style, label=label(f, "04 · RUST · MIT / APACHE-2.0", W),
                title=(f"proteus: protein G (1PGB) backbone turning, coloured by secondary structure; helix {a['helix_pct']:.0f}%, "
                       f"strand {a['strand_pct']:.0f}%, Ramachandran {a['rama_favored_pct']:.1f}% favoured"))


def key(f, text):
    W, H = 220, 66
    lw = f.mono_md.width(text, 15, 2.5)
    body = (
        f'<rect x="2" y="8" width="216" height="56" rx="11" fill="#0B1008"/>'
        f'<rect x="2.5" y="2.5" width="215" height="55" rx="10.5" fill="{LIFT}" stroke="{RULE}"/>'
        f'<rect x="16" y="5" width="188" height="1" fill="{CREAM}" opacity="0.08"/>'
        f'<circle cx="30" cy="30" r="8" fill="{TAN}" opacity="0.14"/><circle cx="30" cy="30" r="3.5" fill="{TAN}"/>'
        + f.mono_md.text(text, 48 + (150 - lw) / 2, 35.5, 15, CREAM, tracking=2.5)
    )
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
            f'aria-label="{text.lower()}">{body}</svg>\n')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fonts", required=True)
    ap.add_argument("--nf-audit", required=True)
    ap.add_argument("--pdb", required=True)
    ap.add_argument("--analysis", required=True)
    args = ap.parse_args()
    f = Fonts(args.fonts)
    out = {
        "whoami.svg": whoami(f),
        "card-nf-audit.svg": nf_audit_card(f, args.nf_audit),
        "card-proteus.svg": proteus_card(f, args.pdb, args.analysis),
        "key-mail.svg": key(f, "MAIL"),
        "key-linkedin.svg": key(f, "LINKEDIN"),
    }
    for name, svg in out.items():
        (ROOT / "assets" / name).write_text(svg)
        print(f"assets/{name}: {len(svg):,} bytes")


if __name__ == "__main__":
    main()
