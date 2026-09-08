"""Acquire upstream files locally after the user accepts their original terms."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--accept-source-terms", action="store_true")
    parser.add_argument("--output", type=Path, default=ROOT / "data" / "raw")
    args = parser.parse_args()
    if not args.accept_source_terms:
        raise SystemExit("Refusing download: review docs/DATA_RIGHTS.md and rerun with --accept-source-terms.")
    manifest = json.loads((ROOT / "manifests" / "source_manifest.json").read_text(encoding="utf-8"))
    args.output.mkdir(parents=True, exist_ok=True)
    for item in manifest["sources"]:
        destination = args.output / item["name"]
        with urlopen(item["url"], timeout=60) as response:
            destination.write_bytes(response.read())
        observed = sha256(destination)
        if observed != item["sha256"]:
            destination.unlink(missing_ok=True)
            raise SystemExit(f"Checksum mismatch for {item['name']}: {observed}")
        print(f"verified {item['name']}")


if __name__ == "__main__":
    main()
