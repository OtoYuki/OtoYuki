"""Render assets/deck.svg: a shipping log of USER's public releases and upstream
issues and pull requests, in the fastfetch deck layout.

    GH_TOKEN=... python3 scripts/deck.py OtoYuki

Standard library only; text is drawn from the Geist Mono outlines in
scripts/glyphs.json (see build_glyphs.py), because an SVG shown through <img>
on GitHub cannot load fonts.
"""

import json
import subprocess
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from brand import CREAM, DIM, KHAKI, OLIVE, ROOT, RULE, SAGE, TAN, Mono, card
from upstream import search

TZ = ZoneInfo("Asia/Kathmandu")

# What the deck says that the data can't.
NOW = "nf-audit · proteus"
STACK = "rust · typescript · python"

RELEASES = """
query($login: String!) {
  user(login: $login) {
    repositories(ownerAffiliations: OWNER, privacy: PUBLIC, isFork: false, first: 100) {
      nodes { name releases(first: 100, orderBy: {field: CREATED_AT, direction: DESC}) {
        nodes { tagName publishedAt isDraft } } }
    }
  }
}"""


def local(ts):
    return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(TZ).date()


def releases(login):
    out = subprocess.run(["gh", "api", "graphql", "-f", f"query={RELEASES}", "-F", f"login={login}"],
                         check=True, capture_output=True, text=True).stdout
    found = []
    for repo in json.loads(out)["data"]["user"]["repositories"]["nodes"]:
        for r in repo["releases"]["nodes"]:
            if not r["isDraft"] and r["publishedAt"]:
                found.append((local(r["publishedAt"]), f"{repo['name']} {r['tagName']}"))
    return sorted(found)


def ago(d, today):
    days = (today - d).days
    if days <= 0:
        return "today"
    if days == 1:
        return "yesterday"
    if days < 14:
        return f"{days} days ago"
    if days < 60:
        return f"{days // 7} weeks ago"
    return d.isoformat()


def week_start(d):
    return d - timedelta(days=(d.weekday() + 1) % 7)  # Sunday, as GitHub draws weeks


def main(login):
    today = datetime.now(TZ).date()
    shipped = releases(login)
    upstream = [(local(i["created_at"]), i) for i in search(login, 100)]
    rel_days, up_days = {}, set()
    for d, _ in shipped:
        rel_days[d] = rel_days.get(d, 0) + 1
    for d, _ in upstream:
        up_days.add(d)
    this_year = sum(1 for d, _ in shipped if d.year == today.year)

    W, H = 1000, 404
    m = Mono()
    el = []

    el.append(m.text("~/s1re.sh", 48, 56, 16, OLIVE, "medium"))
    el.append(m.text("$", 48 + m.width("~/s1re.sh ", 16), 56, 16, DIM, "medium"))
    el.append(m.text("fastfetch", 48 + m.width("~/s1re.sh $ ", 16), 56, 16, KHAKI, "medium"))

    el.append(m.text("s1re", 48, 106, 22, TAN, "medium"))
    el.append(m.text("@kathmandu", 48 + m.width("s1re", 22), 106, 22, CREAM, "medium"))
    el.append(f'<rect x="48" y="120" width="{m.width("s1re@kathmandu", 22):.1f}" height="1.5" fill="{DIM}"/>')

    latest = f"{shipped[-1][1]} · {ago(shipped[-1][0], today)}" if shipped else "—"
    if upstream:
        item = upstream[0][1]
        repo = item["repository_url"].removeprefix("https://api.github.com/repos/")
        state = "merged" if item.get("pull_request", {}).get("merged_at") else item["state"]
        up = f"{repo}#{item['number']} · {state}"
    else:
        up = "—"
    rows = [("now", NOW), ("stack", STACK), ("latest", latest), ("upstream", up)]
    for i, (key, value) in enumerate(rows):
        y = 156 + i * 30
        el.append(m.text(f"{key} ".ljust(10, "."), 48, y, 16, SAGE))
        el.append(m.text(value, 48 + m.width("x" * 11, 16), y, 16, CREAM))

    # Heatmap: the last 26 weeks, one dot per day. A release is a filled dot, an
    # upstream issue or pull request a ring, so the two differ by shape as well as colour.
    first = week_start(today) - timedelta(weeks=25)
    hx, hy, pitch = 548, 96, 15.6
    el.append(m.text("SHIPPED · LAST 26 WEEKS", hx - 4, 82, 12, SAGE, tracking=1.2))
    # Legend, right-aligned: ring "upstream", then dot "release".
    rx = 952 - m.width("release", 12)
    el.append(m.text("release", rx, 82, 12, KHAKI))
    el.append(f'<circle cx="{rx - 11:.1f}" cy="78" r="4.2" fill="{TAN}"/>')
    ux = rx - 11 - 22 - m.width("upstream", 12)
    el.append(m.text("upstream", ux, 82, 12, KHAKI))
    el.append(f'<circle cx="{ux - 11:.1f}" cy="78" r="3.6" fill="none" stroke="{KHAKI}" stroke-width="1.6"/>')
    for wi in range(26):
        for wd in range(7):
            d = first + timedelta(weeks=wi, days=wd)
            if d > today:
                continue
            x, y = hx + wi * pitch, hy + wd * pitch
            n = rel_days.get(d, 0)
            if n:
                el.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{4.4 if n == 1 else 5.6}" fill="{TAN}"/>')
            if d in up_days:
                el.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{3.6 if not n else 6.6}" fill="none" '
                          f'stroke="{KHAKI}" stroke-width="1.6"/>')
            if not n and d not in up_days:
                el.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.5" fill="{DIM}"/>')

    # Ladder: one LED per week for the last 52; lit tan in a week with a release,
    # muted in a week with only upstream work.
    this_week = week_start(today)
    lx, ly, lpitch = 48, 302, 14.4
    el.append(m.text("RELEASE WEEKS · 52", 48, 286, 12, SAGE, tracking=1.2))
    for i in range(52):
        ws = this_week - timedelta(weeks=51 - i)
        days = [ws + timedelta(days=k) for k in range(7)]
        if any(d in rel_days for d in days):
            fill = CREAM if i == 51 else TAN
        elif any(d in up_days for d in days):
            fill = DIM
        else:
            fill = RULE
        el.append(f'<rect x="{lx + i * lpitch:.1f}" y="{ly}" width="9" height="30" rx="2" fill="{fill}"/>')

    el.append(m.text(str(this_year), 952 - m.width(" RELEASES", 16), 332, 46, CREAM, "medium", anchor="end"))
    el.append(m.text(" RELEASES", 952, 332, 16, TAN, "medium", anchor="end"))
    el.append(m.text(str(today.year), 952, 286, 12, SAGE, tracking=1.2, anchor="end"))

    el.append(m.text(f"synced {today.isoformat()} · public releases and upstream issues / pull requests",
                     48, 376, 11, DIM))

    label = m.text("TTY/01", W - 30, 34, 11, DIM, tracking=1.2, anchor="end")  # before defs(): it adds glyphs
    svg = card(W, H, "".join(el), defs=m.defs(), label=label,
               title=f"s1re shipping log: {this_year} releases in {today.year}; latest {latest}; upstream {up}")
    out = ROOT / "assets/deck.svg"
    if not out.exists() or out.read_text() != svg:
        out.write_text(svg)
    print(f"deck: {len(shipped)} releases ({this_year} this year), {len(upstream)} upstream, latest {latest}, {len(svg):,} bytes")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "OtoYuki")
