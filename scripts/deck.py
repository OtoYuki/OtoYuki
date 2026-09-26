"""Render assets/deck.svg from USER's GitHub contribution calendar.

    GH_TOKEN=... python3 scripts/deck.py OtoYuki

Standard library only; text is drawn from the Geist Mono outlines in
scripts/glyphs.json (see build_glyphs.py), because an SVG shown through <img>
on GitHub cannot load fonts.
"""

import json
import subprocess
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
TZ = ZoneInfo("Asia/Kathmandu")

# What the deck says that the calendar can't.
NOW = "nf-audit · proteus"
STACK = "rust · typescript · python"

INK = "#141C10"
LIFT = "#1E2718"
RULE = "#2C3524"
DIM = "#5A6042"
SAGE = "#8A9A86"
KHAKI = "#D1CF8B"
OLIVE = "#99920B"
TAN = "#D8A664"
CREAM = "#FBFFE1"

QUERY = """
query($login: String!, $from: DateTime, $to: DateTime) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionYears
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount contributionLevel } }
      }
    }
  }
}"""


def calendar(login, start=None, end=None):
    args = ["gh", "api", "graphql", "-f", f"query={QUERY}", "-F", f"login={login}"]
    if start:
        args += ["-F", f"from={start}T00:00:00Z", "-F", f"to={end}T23:59:59Z"]
    data = json.loads(subprocess.run(args, check=True, capture_output=True, text=True).stdout)
    return data["data"]["user"]["contributionsCollection"]


def weeks_of(collection, today):
    weeks = []
    for w in collection["contributionCalendar"]["weeks"]:
        days = [d for d in w["contributionDays"] if date.fromisoformat(d["date"]) <= today]
        if days:
            weeks.append(days)
    return weeks


def weekly_streak(login, weeks, years):
    """Consecutive calendar weeks with a contribution, ending now. A week still
    in progress with nothing in it yet does not break the run."""
    totals = [sum(d["contributionCount"] for d in w) for w in weeks]
    if totals and totals[-1] == 0:
        totals.pop()
    run = 0
    for t in reversed(totals):
        if t == 0:
            return run
        run += 1
    # The run reaches the start of the window: walk back a year at a time.
    first = date.fromisoformat(weeks[0][0]["date"])
    while first.year > min(years):
        end = first - timedelta(days=1)
        older = weeks_of(calendar(login, (end - timedelta(days=364)).isoformat(), end.isoformat()), end)
        for w in reversed(older):
            if sum(d["contributionCount"] for d in w) == 0:
                return run
            run += 1
        first = date.fromisoformat(older[0][0]["date"])
    return run


class Mono:
    def __init__(self):
        g = json.loads((ROOT / "scripts/glyphs.json").read_text())
        self.faces = g["faces"]
        self.advance = g["advance"]
        self.used = {}

    def width(self, text, size, tracking=0.0):
        return len(text) * self.advance * size / 1000 + tracking * (len(text) - 1)

    def text(self, text, x, y, size, fill, face="regular", tracking=0.0, anchor="start"):
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
        return f'<g fill="{fill}" transform="translate({x:.1f} {y:.1f}) scale({k:g} {-k:g})">{"".join(uses)}</g>'

    def defs(self):
        return "".join(f'<path id="{gid}" d="{d}"/>' for gid, d in sorted(self.used.items()))


def main(login):
    today = datetime.now(TZ).date()
    col = calendar(login)
    weeks = weeks_of(col, today)
    days = [d for w in weeks for d in w]
    year_total = col["contributionCalendar"]["totalContributions"]
    last365 = [d for d in days if date.fromisoformat(d["date"]) > today - timedelta(days=365)]
    active = sum(1 for d in last365 if d["contributionCount"] > 0)
    streak = weekly_streak(login, weeks, col["contributionYears"])

    W, H = 1000, 404
    m = Mono()
    el = []

    el.append(m.text("~/s1re.sh", 48, 56, 16, OLIVE, "medium"))
    el.append(m.text("$", 48 + m.width("~/s1re.sh ", 16), 56, 16, DIM, "medium"))
    el.append(m.text("fastfetch", 48 + m.width("~/s1re.sh $ ", 16), 56, 16, KHAKI, "medium"))

    el.append(m.text("s1re", 48, 106, 22, TAN, "medium"))
    el.append(m.text("@kathmandu", 48 + m.width("s1re", 22), 106, 22, CREAM, "medium"))
    el.append(f'<rect x="48" y="120" width="{m.width("s1re@kathmandu", 22):.1f}" height="1.5" fill="{DIM}"/>')

    rows = [
        ("now", NOW),
        ("stack", STACK),
        ("year", f"{year_total:,} contributions"),
        ("active", f"{active} of 365 days"),
    ]
    for i, (key, value) in enumerate(rows):
        y = 156 + i * 30
        el.append(m.text(f"{key} ".ljust(10, "."), 48, y, 16, SAGE))
        el.append(m.text(value, 48 + m.width("x" * 11, 16), y, 16, CREAM))

    # Heatmap: the last 26 calendar weeks as halftone dots, sized and lit by
    # GitHub's own quartile level for the day.
    level = {
        "NONE": (1.5, DIM),
        "FIRST_QUARTILE": (3.0, SAGE),
        "SECOND_QUARTILE": (4.0, OLIVE),
        "THIRD_QUARTILE": (4.9, TAN),
        "FOURTH_QUARTILE": (5.6, CREAM),
    }
    recent = weeks[-26:]
    hx, hy, pitch = 548, 96, 15.6
    el.append(m.text("LAST 26 WEEKS", hx - 4, 82, 12, SAGE, tracking=1.2))
    for wi, w in enumerate(recent):
        for d in w:
            wd = (date.fromisoformat(d["date"]).weekday() + 1) % 7  # Sunday = 0, as GitHub draws it
            r, fill = level[d["contributionLevel"]]
            el.append(f'<circle cx="{hx + wi * pitch:.1f}" cy="{hy + wd * pitch:.1f}" r="{r}" fill="{fill}"/>')

    # Cadence: one LED per calendar week for the last 52; the unbroken run is lit.
    ladder = weeks[-52:]
    totals = [sum(d["contributionCount"] for d in w) for w in ladder]
    run_start = len(ladder) - streak - (1 if totals[-1] == 0 else 0)
    lx, ly, lpitch = 48, 302, 14.4
    el.append(m.text("CADENCE · 52 WEEKS", 48, 286, 12, SAGE, tracking=1.2))
    for i, t in enumerate(totals):
        if i >= run_start and t > 0:
            fill = CREAM if i == len(totals) - 1 else TAN
        elif t > 0:
            fill = DIM
        else:
            fill = RULE
        el.append(f'<rect x="{lx + i * lpitch:.1f}" y="{ly}" width="9" height="30" rx="2" fill="{fill}"/>')

    num = f"{streak}"
    el.append(m.text(num, 952 - m.width(" WK", 18), 332, 46, CREAM, "medium", anchor="end"))
    el.append(m.text(" WK", 952, 332, 18, TAN, "medium", anchor="end"))
    el.append(m.text("UNBROKEN", 952, 286, 12, SAGE, tracking=1.2, anchor="end"))

    el.append(m.text(
        f"synced {today.isoformat()} · github contribution calendar, private contributions included",
        48, 376, 11, DIM))

    alt_title = f"s1re: {streak}-week unbroken contribution streak, {year_total:,} contributions in the past year"
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t">'
        f'<title id="t">{alt_title}</title>'
        f'<defs><pattern id="grid" width="16" height="16" patternUnits="userSpaceOnUse">'
        f'<circle cx="2" cy="2" r="0.8" fill="{DIM}" opacity="0.35"/></pattern>'
        f'<clipPath id="card"><rect width="{W}" height="{H}" rx="12"/></clipPath>{m.defs()}</defs>'
        f'<g clip-path="url(#card)"><rect width="{W}" height="{H}" fill="{INK}"/>'
        f'<rect width="{W}" height="{H}" fill="url(#grid)"/>{"".join(el)}</g></svg>\n'
    )
    out = ROOT / "assets/deck.svg"
    if not out.exists() or out.read_text() != svg:
        out.write_text(svg)
    print(f"deck: streak {streak} wk, year {year_total}, active {active}/365, {len(svg):,} bytes")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "OtoYuki")
