"""Rewrite the UPSTREAM block in README.md (inside a <pre>) with the issues and
pull requests USER opened on public repositories it does not own, newest first.

    GH_TOKEN=... python3 scripts/upstream.py OtoYuki
"""

import html
import json
import re
import subprocess
import sys
from pathlib import Path

START, END = "<!-- UPSTREAM:START -->", "<!-- UPSTREAM:END -->"


def search(user):
    out = subprocess.run(
        ["gh", "api", "-X", "GET", "search/issues",
         "-f", f"q=author:{user} -user:{user} is:public",
         "-f", "sort=created", "-f", "order=desc", "-f", "per_page=15"],
        check=True, capture_output=True, text=True,
    ).stdout
    return json.loads(out)["items"]


def short(title, limit=76):
    title = title.split("; ")[0].replace("`", "")
    if len(title) > limit:
        title = title[: limit - 1].rsplit(" ", 1)[0].rstrip(" ,:;") + "…"
    return html.escape(title)


def status(item):
    if "pull_request" in item:
        return "pr · merged" if item["pull_request"].get("merged_at") else f"pr · {item['state']}"
    return f"issue · {item['state']}"


def main(user):
    readme = Path(__file__).resolve().parent.parent / "README.md"
    text = readme.read_text()
    items = search(user)
    refs = [f"{i['repository_url'].removeprefix('https://api.github.com/repos/')}#{i['number']}" for i in items]
    pad = max((len(r) for r in refs), default=0) + 2
    lines = []
    for item, ref in zip(items, refs):
        lines.append(
            f'<a href="{item["html_url"]}">{ref}</a>{" " * (pad - len(ref))}'
            f"{status(item):<14}{item['created_at'][:10]}\n  {short(item['title'])}"
        )
    block = "\n".join(lines) or "nothing public yet"
    new = re.sub(
        re.escape(START) + r".*?" + re.escape(END),
        lambda _: f"{START}\n{block}\n{END}",
        text,
        flags=re.S,
    )
    if new != text:
        readme.write_text(new)
    print(f"{len(lines)} upstream items")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "OtoYuki")
