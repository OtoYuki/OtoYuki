"""Rewrite the UPSTREAM block in README.md with the issues and pull requests
USER opened on public repositories it does not own, newest first.

    GH_TOKEN=... python3 scripts/upstream.py OtoYuki
"""

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


def short(title, limit=110):
    title = title.split("; ")[0]
    if len(title) > limit:
        title = title[: limit - 1].rstrip() + "…"
    if title.count("`") % 2:
        title += "`"
    return title


def status(item):
    if "pull_request" in item:
        if item["pull_request"].get("merged_at"):
            return "pull request · merged"
        return f"pull request · {item['state']}"
    return f"issue · {item['state']}"


def main(user):
    readme = Path(__file__).resolve().parent.parent / "README.md"
    text = readme.read_text()
    lines = []
    for item in search(user):
        repo = item["repository_url"].removeprefix("https://api.github.com/repos/")
        lines.append(
            f"- [{repo}#{item['number']}]({item['html_url']}): {short(item['title'])} "
            f"<sub>{status(item)} · {item['created_at'][:10]}</sub>"
        )
    block = "\n".join(lines) or "- Nothing public yet."
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
