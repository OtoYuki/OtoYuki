"""Render assets/rnaseq-idle-share.svg from nf-audit's star_salmon release table.

    uv run --with fonttools --with brotli --with uharfbuzz python scripts/rnaseq_chart.py \
        ~/dev/nf-audit/examples/rnaseq-star_salmon-releases.md ~/dev/s1re/fonts assets/rnaseq-idle-share.svg

Text is converted to outlines so the brand faces render inside an <img>, where
GitHub cannot load web fonts. The numbers come only from the table.
"""

import io
import re
import sys
from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

INK = "#141C10"
LIFT = "#1E2718"
RULE = "#2C3524"
DIM = "#5A6042"
SAGE = "#8A9A86"
KHAKI = "#D1CF8B"
OLIVE = "#99920B"
TAN = "#D8A664"
CREAM = "#FBFFE1"

# nf-core/rnaseq 3.13.x reports carry `master` as the revision
# (nf-audit examples/README.md); the commits resolve to these tags.
MASTER_TAGS = {"2023-11-17": "3.13.1", "2023-11-21": "3.13.2"}


def num(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


class Face:
    def __init__(self, path):
        tt = TTFont(path)
        tt.flavor = None
        buf = io.BytesIO()
        tt.save(buf)
        self.upem = tt["head"].unitsPerEm
        self.glyphs = tt.getGlyphSet()
        self.order = tt.getGlyphOrder()
        self.font = hb.Font(hb.Face(buf.getvalue()))

    def _shape(self, text):
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(self.font, buf, {"kern": True, "liga": True})
        return buf.glyph_infos, buf.glyph_positions

    def width(self, text, size, tracking=0.0):
        _, pos = self._shape(text)
        return sum(p.x_advance for p in pos) * size / self.upem + tracking * (len(pos) - 1)

    def text(self, text, x, y, size, fill, tracking=0.0, anchor="start"):
        infos, pos = self._shape(text)
        s = size / self.upem
        w = self.width(text, size, tracking)
        cx = x - {"start": 0, "middle": w / 2, "end": w}[anchor]
        d = []
        for info, p in zip(infos, pos):
            pen = SVGPathPen(self.glyphs, ntos=num)
            ox, oy = cx + p.x_offset * s, y - p.y_offset * s
            self.glyphs[self.order[info.codepoint]].draw(TransformPen(pen, (s, 0, 0, -s, ox, oy)))
            d.append(pen.getCommands())
            cx += p.x_advance * s + tracking
        return f'<path fill="{fill}" d="{"".join(d)}"/>'


def load_runs(table):
    runs = []
    for line in Path(table).read_text().splitlines():
        m = re.match(r"\| (\S+) salmon (\d{4}-\d\d-\d\d) \|", line)
        if not m:
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        release, date = m.groups()
        release = MASTER_TAGS.get(date, release) if release == "master" else release
        cost = float(cells[8].lstrip("$").replace(",", ""))
        unused = int(cells[10].rstrip("%")) / 100
        runs.append((date, release, cost, unused))
    runs.sort()
    return runs


def column(x, w, y0, y1, fill, top_round):
    """A column segment from y0 (bottom) to y1 (top); 4px rounded data-end on top."""
    h = y0 - y1
    if h <= 0:
        return ""
    if not top_round:
        return f'<rect x="{num(x)}" y="{num(y1)}" width="{num(w)}" height="{num(h)}" fill="{fill}"/>'
    r = min(4, h, w / 2)
    return (
        f'<path fill="{fill}" d="M{num(x)} {num(y0)}V{num(y1 + r)}Q{num(x)} {num(y1)} {num(x + r)} {num(y1)}'
        f'H{num(x + w - r)}Q{num(x + w)} {num(y1)} {num(x + w)} {num(y1 + r)}V{num(y0)}Z"/>'
    )


def main(table, fonts, out):
    fonts = Path(fonts)
    display = Face(fonts / "Freigeist-Regular.woff2")
    mono = Face(fonts / "GeistMono-Regular.otf")
    mono_md = Face(fonts / "GeistMono-Medium.otf")

    runs = load_runs(table)
    assert len(runs) == 30, f"expected 30 star_salmon releases, got {len(runs)}"
    first, last = runs[0], runs[-1]
    drop = 1 - last[2] / first[2]
    in_band = sum(1 for r in runs if 0.62 <= r[3] <= 0.68)

    W, H = 1000, 540
    left, right = 92, 872
    top, base = 262, 440
    ymax = 180
    slot = (right - left) / len(runs)
    bar = 18
    py = lambda v: base - v / ymax * (base - top)

    el = []
    el.append(mono_md.text("~/nf-audit", 48, 62, 16, OLIVE))
    x = 48 + mono_md.width("~/nf-audit ", 16)
    el.append(mono_md.text("$", x, 62, 16, DIM))
    x += mono_md.width("$ ", 16)
    el.append(mono_md.text("compare nf-core/rnaseq  aligner=star_salmon", x, 62, 16, KHAKI))

    el.append(display.text(f"Runs got {round(drop * 100)}% cheaper.", 45, 122, 46, CREAM, -0.5))
    el.append(display.text("The idle share barely moved.", 45, 174, 46, CREAM, -0.5))

    sub = f"ALLOCATED COST PER FULL-SIZE AWS TEST, {len(runs)} RELEASES"
    el.append(mono.text(sub, 48, 218, 13, SAGE, 1.0))

    # Legend, right of the subtitle: both series, never color alone.
    lx = right
    for label, fill in (("reserved, never used", "url(#idle)"), ("used", TAN)):
        tw = mono.width(label, 13)
        el.append(mono.text(label, lx, 218, 13, KHAKI, anchor="end"))
        el.append(f'<rect x="{num(lx - tw - 21)}" y="206" width="13" height="13" rx="2" fill="{fill}"/>')
        lx -= tw + 42

    for v in (0, 50, 100, 150):
        y = py(v)
        el.append(f'<rect x="{left}" y="{num(y - 0.5)}" width="{right - left}" height="1" fill="{RULE}"/>')
        el.append(mono.text(f"${v}", left - 12, y + 4, 12, SAGE, anchor="end"))

    seen_years = set()
    for i, (date, release, cost, unused) in enumerate(runs):
        cx = left + slot * (i + 0.5)
        bx = cx - bar / 2
        clipped = cost > ymax
        total_top = top - 12 if clipped else py(cost)
        used_top = base - (base - total_top) * (1 - unused) if not clipped else py(cost * (1 - unused))
        el.append(column(bx, bar, base, used_top, TAN, False))
        el.append(column(bx, bar, used_top - 2, total_top, "url(#idle)", True))
        if clipped:
            # Break marks: the column continues past the axis to its value.
            for dy in (8, 14):
                yy = total_top + dy
                el.append(
                    f'<path d="M{num(bx - 3)} {num(yy + 3)}L{num(bx + bar + 3)} {num(yy - 3)}" '
                    f'stroke="{INK}" stroke-width="2.5"/>'
                )
            el.append(mono.text(
                f"{release}  ${cost:.0f}  {round(unused * 100)}% unused  (-resume run)",
                bx, total_top - 10, 12, SAGE))
        year = date[:4]
        if year not in seen_years:
            seen_years.add(year)
            el.append(f'<rect x="{num(bx)}" y="{base + 4}" width="1" height="7" fill="{DIM}"/>')
            el.append(mono.text(year, bx, base + 27, 12, SAGE))
        if i == 0:
            el.append(mono_md.text(f"${cost:.2f}", bx, total_top - 42, 13, CREAM))
            el.append(mono.text(f"{round(unused * 100)}% unused", bx, total_top - 26, 13, KHAKI))
            el.append(mono.text(release, bx, total_top - 10, 13, SAGE))
        if i == len(runs) - 1:
            el.append(mono_md.text(f"${cost:.2f}", right + 14, total_top + 5, 13, CREAM))
            el.append(mono.text(f"{round(unused * 100)}% unused", right + 14, total_top + 22, 13, KHAKI))
            el.append(mono.text(release, right + 14, total_top + 39, 13, SAGE))

    el.append(f'<rect x="{left}" y="{base}" width="{right - left}" height="1" fill="{DIM}"/>')

    el.append(mono.text(
        f"Unused 62–68% in {in_band} of {len(runs)} releases. Seqera Compute list rates: a yardstick "
        "across runs, not nf-core's AWS bill.",
        48, 510, 12, SAGE))

    title = f"nf-core/rnaseq: runs got {round(drop * 100)}% cheaper, the idle share barely moved"
    desc = (
        f"Stacked columns for {len(runs)} nf-core/rnaseq star_salmon releases, {first[1]} to {last[1]}: allocated cost per "
        f"full-size AWS test run at Seqera Compute list rates, split into used and never-used allocation. Cost fell from "
        f"${first[2]:.2f} to ${last[2]:.2f}; the unused share stayed between 62% and 68% in {in_band} of {len(runs)} releases."
    )
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t d">
<title id="t">{title}</title>
<desc id="d">{desc}</desc>
<defs>
<pattern id="grid" width="16" height="16" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="0.8" fill="{DIM}" opacity="0.35"/></pattern>
<pattern id="idle" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="4" fill="{LIFT}"/><circle cx="2" cy="2" r="0.95" fill="{SAGE}"/></pattern>
<clipPath id="card"><rect width="{W}" height="{H}" rx="12"/></clipPath>
</defs>
<g clip-path="url(#card)">
<rect width="{W}" height="{H}" fill="{INK}"/>
<rect width="{W}" height="{H}" fill="url(#grid)"/>
{chr(10).join(e for e in el if e)}
</g>
</svg>
"""
    Path(out).write_text(svg)
    print(f"{out}: {len(svg):,} bytes, {len(runs)} runs, drop {drop:.1%}, in band {in_band}/{len(runs)}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
