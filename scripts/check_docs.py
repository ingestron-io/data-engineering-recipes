"""Check local Markdown destinations, headings and runnable catalogue paths."""

import json
from pathlib import Path
import re
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]


def check_links(root):
    pages = [
        path
        for path in root.rglob("*.md")
        if not any(
            part.startswith(".") or part in ("outputs", "node_modules", "__pycache__")
            for part in path.relative_to(root).parts
        )
    ]
    for page in pages:
        text = re.sub(r"```.*?```", "", page.read_text(), flags=re.S)
        assert len(re.findall(r"^# ", text, re.M)) == 1, (
            f"{page}: expected one page title"
        )
        for url in re.findall(r"\[[^\]]*\]\(([^)]+)\)", text):
            parsed = urlparse(url)
            if parsed.scheme or not parsed.path:
                continue
            destination = (page.parent / unquote(parsed.path)).resolve()
            assert destination.is_relative_to(root), (
                f"{page}: path leaves repository: {url}"
            )
            assert destination.exists(), f"{page}: missing {url}"
    return len(pages)


if __name__ == "__main__":
    count = check_links(ROOT)
    catalog = json.loads((ROOT / "catalog.json").read_text())
    seen = set()
    for item in catalog["resources"]:
        assert item["id"] not in seen, f"Duplicate {item['id']}"
        seen.add(item["id"])
        assert (ROOT / item["path"]).is_file(), f"Missing {item['path']}"
        assert f"]({item['path']})" in (ROOT / "README.md").read_text()
    print(f"Checked {count} Markdown pages and {len(seen)} catalogue entries.")
