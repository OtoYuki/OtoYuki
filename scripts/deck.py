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
from datetime import date, datetime, timedelta
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


MONTHS = "jan feb mar apr may jun jul aug sep oct nov dec".split()


def window(first, today):
    """Buckets sized to the history there is: days while it is short (at least
    14), then weeks (8 to 26), then months (6 to 24). Returns (unit, [(start, end)])."""
    span = (today - first).days + 1
    if span <= 28:
        n = max(span, 14)
        return "DAYS", [(today - timedelta(days=n - 1 - i),) * 2 for i in range(n)]
    if span <= 26 * 7:
        n = min(max(-(-span // 7), 8), 26)
        this = week_start(today)
        return "WEEKS", [(this - timedelta(weeks=n - 1 - i), this - timedelta(weeks=n - 1 - i) + timedelta(days=6))
                         for i in range(n)]
    months = (today.year - first.year) * 12 + today.month - first.month + 1
    n = min(max(months, 6), 24)
    out = []
    for i in range(n):
        k = today.year * 12 + today.month - 1 - (n - 1 - i)
        start = date(k // 12, k % 12 + 1, 1)
        nxt = date((k + 1) // 12, (k + 1) % 12 + 1, 1)
        out.append((start, nxt - timedelta(days=1)))
    return "MONTHS", out


def main(login):
    today = datetime.now(TZ).date()
    shipped = releases(login)
    upstream = [(local(i["created_at"]), i) for i in search(login, 100)]
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

    events = [d for d, _ in shipped] + [d for d, _ in upstream]
    unit, buckets = window(min(events, default=today), today)
    n = len(buckets)

    def bucket(d):
        for i, (start, end) in enumerate(buckets):
            if start <= d <= end:
                return i
        return None

    # Grid: one row per repo that released in the window, plus upstream; one
    # column per bucket. A release is a filled dot and upstream work a ring, so
    # the two differ by shape as well as colour. Dot size is relative to the
    # busiest cell in the window.
    counts = {}
    for d, name in shipped:
        i = bucket(d)
        if i is not None:
            counts.setdefault(name.split()[0], [0] * n)[i] += 1
    repos = sorted(counts, key=lambda r: -sum(counts[r]))[:4]
    grid = [(r, counts[r], False) for r in repos]
    ups = [0] * n
    for d, _ in upstream:
        i = bucket(d)
        if i is not None:
            ups[i] += 1
    if any(ups):
        grid.append(("upstream", ups, True))

    hx, dx0, dx1, hy, rp = 544, 640, 948, 108, 24
    pitch = (dx1 - dx0) / max(n - 1, 1)
    rmax = min(pitch * 0.42, 6.4)
    rmin = min(3.4, rmax)
    peak = max([c for _, row, _ in grid for c in row], default=1)
    el.append(m.text(f"SHIPPED · LAST {n} {unit}", hx, 82, 12, SAGE, tracking=1.2))
    rx = 952 - m.width("release", 12)
    el.append(m.text("release", rx, 82, 12, KHAKI))
    el.append(f'<circle cx="{rx - 11:.1f}" cy="78" r="4.2" fill="{TAN}"/>')
    ux = rx - 11 - 22 - m.width("upstream", 12)
    el.append(m.text("upstream", ux, 82, 12, KHAKI))
    el.append(f'<circle cx="{ux - 11:.1f}" cy="78" r="3.6" fill="none" stroke="{KHAKI}" stroke-width="1.6"/>')
    if not grid:
        el.append(m.text("nothing shipped yet", hx, hy + 4, 14, SAGE))
    for ri, (name, row, ring) in enumerate(grid):
        y = hy + ri * rp
        el.append(m.text(name[:10], hx, y + 4, 13, SAGE))
        for i, c in enumerate(row):
            x = dx0 + i * pitch
            if not c:
                el.append(f'<circle cx="{x:.1f}" cy="{y}" r="1.5" fill="{DIM}"/>')
                continue
            r = rmin + (rmax - rmin) * ((c - 1) / (peak - 1) if peak > 1 else 1)
            if ring:
                el.append(f'<circle cx="{x:.1f}" cy="{y}" r="{r:.1f}" fill="none" stroke="{KHAKI}" stroke-width="1.6"/>')
            else:
                el.append(f'<circle cx="{x:.1f}" cy="{y}" r="{r:.1f}" fill="{TAN}"/>')
    start = buckets[0][0]
    ay = hy + max(len(grid), 1) * rp
    el.append(m.text(f"{MONTHS[start.month - 1]} {start.day}", dx0, ay, 11, DIM, anchor="middle"))
    el.append(m.text({"DAYS": "today", "WEEKS": "this week", "MONTHS": "this month"}[unit], dx1, ay, 11, DIM, anchor="middle"))

    # Ladder: one LED per bucket; tan with a release, muted with only upstream work.
    lx, ly, lw = 48, 302, 740
    lpitch = lw / n
    led = min(lpitch * 0.62, 26)
    el.append(m.text(f"RELEASE {unit} · {n}", 48, 286, 12, SAGE, tracking=1.2))
    for i in range(n):
        if any(counts[r][i] for r in counts):
            fill = CREAM if i == n - 1 else TAN
        elif ups[i]:
            fill = DIM
        else:
            fill = RULE
        el.append(f'<rect x="{lx + i * lpitch:.1f}" y="{ly}" width="{led:.1f}" height="30" rx="2" fill="{fill}"/>')

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
    print(f"deck: window {n} {unit.lower()}, {len(shipped)} releases ({this_year} this year), {len(upstream)} upstream, latest {latest}, {len(svg):,} bytes")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "OtoYuki")
