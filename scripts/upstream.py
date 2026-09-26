"""Render assets/upstream.svg: the latest issues and pull requests USER opened on
public repositories it does not own. Standard library only.

    GH_TOKEN=... python3 scripts/upstream.py OtoYuki
"""

import json
import subprocess
import sys

from brand import CREAM, DIM, INK, KHAKI, OLIVE, ROOT, SAGE, TAN, Mono, card

ROWS = 4


def search(user, n=ROWS):
    out = subprocess.run(
        ["gh", "api", "-X", "GET", "search/issues",
         "-f", f"q=author:{user} -user:{user} is:public",
         "-f", "sort=created", "-f", "order=desc", "-f", f"per_page={n}"],
        check=True, capture_output=True, text=True,
    ).stdout
    return json.loads(out)["items"]


def status(item):
    if "pull_request" in item:
        return ("PR · MERGED", "fill") if item["pull_request"].get("merged_at") else (f"PR · {item['state'].upper()}", "tan")
    return (f"ISSUE · {item['state'].upper()}", "olive" if item["state"] == "open" else "dim")


def clean(m, text, limit):
    text = "".join(c if c in m.faces["regular"] else "?" for c in text.split("; ")[0].replace("`", ""))
    if len(text) > limit:
        text = text[: limit - 1].rsplit(" ", 1)[0].rstrip(" ,:;") + "…"
    return text


def main(user):
    items = search(user)
    m = Mono()
    W = 1000
    H = 112 + 60 * max(len(items), 1) + 28
    el = [
        m.text("~/s1re.sh", 48, 58, 16, OLIVE, "medium"),
        m.text("$", 48 + m.width("~/s1re.sh ", 16), 58, 16, DIM, "medium"),
        m.text("gh upstream", 48 + m.width("~/s1re.sh $ ", 16), 58, 16, KHAKI, "medium"),
    ]
    if not items:
        el.append(m.text("nothing public yet", 48, 112, 14, SAGE))
    for i, item in enumerate(items):
        y = 112 + i * 60
        chip, tone = status(item)
        cw = m.width(chip, 11, 1.0) + 20
        stroke, fill, ink = {"fill": (TAN, TAN, INK), "tan": (TAN, "none", TAN),
                             "olive": (OLIVE, "none", OLIVE), "dim": (DIM, "none", SAGE)}[tone]
        el.append(f'<rect x="48.5" y="{y - 16.5}" width="{cw:.1f}" height="23" rx="4" fill="{fill}" stroke="{stroke}"/>')
        el.append(m.text(chip, 58, y, 11, ink, "medium", tracking=1.0))
        ref = f"{item['repository_url'].removeprefix('https://api.github.com/repos/')}#{item['number']}"
        el.append(m.text(ref, 210, y, 16, CREAM, "medium"))
        el.append(m.text(item["created_at"][:10], 952, y, 13, DIM, anchor="end"))
        el.append(m.text(clean(m, item["title"], 88), 210, y + 24, 13, KHAKI))
    el.append(m.text("all activity →", 952, H - 26, 12, KHAKI, "medium", anchor="end"))
    label = m.text("TTY/04", W - 30, 34, 11, DIM, tracking=1.2, anchor="end")  # before defs(): it adds glyphs
    svg = card(W, H, "".join(el), defs=m.defs(), label=label,
               title=f"gh upstream: the latest {len(items)} issues and pull requests on repositories I don't own")
    out = ROOT / "assets/upstream.svg"
    if not out.exists() or out.read_text() != svg:
        out.write_text(svg)
    print(f"upstream: {len(items)} items, {len(svg):,} bytes")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "OtoYuki")
