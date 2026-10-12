#!/usr/bin/env python3
"""Remove synthetic empty versions from the versionless cross-source fixture."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


APP_ID = "io.github.dengwii.crosssourcememos"


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("dist", type=Path)
    args = parser.parse_args()

    app_dir = args.dist / "apps" / APP_ID
    index = load_json(args.dist / "index.json")
    matches = [
        app
        for app in index.get("apps", [])
        if isinstance(app, dict) and app.get("id") == APP_ID
    ]
    if len(matches) != 1:
        raise ValueError(f"expected one {APP_ID} index entry, found {len(matches)}")
    if "version" in matches[0]:
        raise ValueError(f"{APP_ID} index entry unexpectedly contains version")

    metadata_paths = sorted(app_dir.glob("meta*.json"))
    if not metadata_paths:
        raise ValueError(f"no metadata files found under {app_dir}")
    for path in metadata_paths:
        metadata = load_json(path)
        if "version" not in metadata:
            continue
        if metadata["version"] not in (None, ""):
            raise ValueError(f"{path} contains non-empty version {metadata['version']!r}")
        del metadata["version"]
        path.write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
