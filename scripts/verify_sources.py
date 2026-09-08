"""Verify checksums of locally acquired, gitignored upstream files."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=ROOT / "data" / "raw")
    args = parser.parse_args()
    manifest = json.loads((ROOT / "manifests" / "source_manifest.json").read_text(encoding="utf-8"))
    failed = []
    for item in manifest["sources"]:
        path = args.input / item["name"]
        if not path.is_file() or sha256(path) != item["sha256"]:
            failed.append(item["name"])
        else:
            print(f"verified {item['name']}")
    if failed:
        raise SystemExit("Verification failed: " + ", ".join(failed))


if __name__ == "__main__":
    main()
