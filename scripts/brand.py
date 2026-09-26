"""Shared pieces for the profile's SVGs: palette, text as outlines, card chrome.

`Mono` draws Geist Mono from scripts/glyphs.json with the standard library only,
for the jobs that run in Actions. `Face` shapes any local font with HarfBuzz
(`uv run --with fonttools --with brotli --with uharfbuzz`), for assets built
once on a machine that has the brand fonts.
"""

import io
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

INK = "#141C10"
LIFT = "#1E2718"
RULE = "#2C3524"
DIM = "#5A6042"
SAGE = "#8A9A86"
KHAKI = "#D1CF8B"
OLIVE = "#99920B"
TAN = "#D8A664"
CREAM = "#FBFFE1"
# proteus structure colours (proteus docs/design/2026-09-23-proteus-identity-design.md)
HELIX, STRAND, COIL = "#D8A664", "#4F9A94", "#E7E9C8"

REDUCED_MOTION = "@media (prefers-reduced-motion: reduce) { * { animation: none !important; } }"


def num(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


class Mono:
    """Geist Mono from pre-extracted outlines; each glyph is defined once and reused."""

    def __init__(self):
        g = json.loads((ROOT / "scripts/glyphs.json").read_text())
        self.faces = g["faces"]
        self.advance = g["advance"]
        self.used = {}

    def width(self, text, size, tracking=0.0):
        return len(text) * self.advance * size / 1000 + tracking * (len(text) - 1)

    def text(self, text, x, y, size, fill, face="regular", tracking=0.0, anchor="start", attrs=""):
        k = size / 1000
        x -= {"start": 0, "middle": self.width(text, size, tracking) / 2, "end": self.width(text, size, tracking)}[anchor]
        step = self.advance + tracking / k
        uses = []
        for i, ch in enumerate(text):
            if ch == " ":
                continue
            if ch not in self.faces[face]:
                raise KeyError(f"no glyph for {ch!r} in {face}")
            gid = f"{face[0]}{ord(ch):x}"
            self.used[gid] = self.faces[face][ch]
            uses.append(f'<use href="#{gid}" x="{round(i * step)}"/>')
        return f'<g fill="{fill}" transform="translate({x:.1f} {y:.1f}) scale({k:g} {-k:g})"{attrs}>{"".join(uses)}</g>'

    def defs(self):
        return "".join(f'<path id="{gid}" d="{d}"/>' for gid, d in sorted(self.used.items()))


class Face:
    """Any local font, shaped with HarfBuzz and emitted as one path per run."""

    def __init__(self, path):
        import uharfbuzz as hb
        from fontTools.ttLib import TTFont

        self._hb = hb
        tt = TTFont(path)
        tt.flavor = None
        buf = io.BytesIO()
        tt.save(buf)
        self.upem = tt["head"].unitsPerEm
        self.glyphs = tt.getGlyphSet()
        self.order = tt.getGlyphOrder()
        self.font = hb.Font(hb.Face(buf.getvalue()))

    def _shape(self, text):
        buf = self._hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        self._hb.shape(self.font, buf, {"kern": True, "liga": True})
        return buf.glyph_infos, buf.glyph_positions

    def width(self, text, size, tracking=0.0):
        _, pos = self._shape(text)
        return sum(p.x_advance for p in pos) * size / self.upem + tracking * (len(pos) - 1)

    def glyph_paths(self, text, x, y, size, tracking=0.0, anchor="start"):
        """One (x_advance_start, d) pair per glyph, for per-glyph animation."""
        from fontTools.pens.svgPathPen import SVGPathPen
        from fontTools.pens.transformPen import TransformPen

        infos, pos = self._shape(text)
        s = size / self.upem
        w = self.width(text, size, tracking)
        cx = x - {"start": 0, "middle": w / 2, "end": w}[anchor]
        out = []
        for info, p in zip(infos, pos):
            pen = SVGPathPen(self.glyphs, ntos=num)
            self.glyphs[self.order[info.codepoint]].draw(
                TransformPen(pen, (s, 0, 0, -s, cx + p.x_offset * s, y - p.y_offset * s)))
            out.append((cx, pen.getCommands()))
            cx += p.x_advance * s + tracking
        return out

    def text(self, text, x, y, size, fill, tracking=0.0, anchor="start", attrs=""):
        d = "".join(d for _, d in self.glyph_paths(text, x, y, size, tracking, anchor))
        return f'<path fill="{fill}" d="{d}"{attrs}/>'


def card(w, h, body, defs="", style="", title="", label=""):
    """Ink card with the banner's dot grid, corner register marks and a micro label."""
    marks = []
    for cx, cy in ((14, 14), (w - 14, 14), (14, h - 14), (w - 14, h - 14)):
        marks.append(f'<path d="M{cx - 4} {cy}H{cx + 4}M{cx} {cy - 4}V{cy + 4}" stroke="{SAGE}" stroke-width="1" opacity="0.6"/>')
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-labelledby="t">'
        f'<title id="t">{title}</title>'
        + (f"<style>{style} {REDUCED_MOTION}</style>" if style else "")
        + f'<defs><pattern id="grid" width="16" height="16" patternUnits="userSpaceOnUse">'
        f'<circle cx="2" cy="2" r="0.8" fill="{DIM}" opacity="0.35"/></pattern>'
        f'<clipPath id="card"><rect width="{w}" height="{h}" rx="12"/></clipPath>{defs}</defs>'
        f'<g clip-path="url(#card)"><rect width="{w}" height="{h}" fill="{INK}"/>'
        f'<rect width="{w}" height="{h}" fill="url(#grid)"/>{"".join(marks)}{label}{body}</g></svg>\n'
    )
