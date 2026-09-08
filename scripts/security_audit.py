"""Fail if tracked public-release text contains local paths or credential signatures."""
from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKIP = {".git", "__pycache__", "data", "reproduced_figures"}
PATTERNS = [r"C:\\\\", r"C:/", r"Users[/\\]Andre", r"gh[pous]_[A-Za-z0-9_]+", r"github_pat_", r"api[_ -]?key", r"BEGIN [A-Z ]*PRIVATE KEY"]


def main() -> None:
    hits = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.name == Path(__file__).name or any(part in SKIP for part in path.parts):
            continue
        if path.suffix.lower() in {".pdf", ".png", ".tiff"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                hits.append(f"{path.relative_to(ROOT)}: {pattern}")
    if hits:
        raise SystemExit("SECURITY AUDIT FAIL\n" + "\n".join(hits))
    print("SECURITY AUDIT PASS")


if __name__ == "__main__":
    main()
