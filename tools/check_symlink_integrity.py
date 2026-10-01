#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git"}


def scan(root: Path):
    records = []
    root_real = root.resolve()

    for current, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in sorted(set(dirs + files)):
            path = Path(current) / name
            if not path.is_symlink():
                continue

            target = os.readlink(path)
            resolved = (path.parent / target).resolve(strict=False)
            try:
                resolved.relative_to(root_real)
                escapes = False
            except ValueError:
                escapes = True

            exists = path.exists()
            records.append(
                {
                    "path": path.relative_to(root).as_posix(),
                    "target": target,
                    "resolved": str(resolved),
                    "exists": exists,
                    "escapes_repository": escapes,
                    "state": "PASS" if exists and not escapes else "FAIL",
                }
            )

    return sorted(records, key=lambda item: item["path"])


def main() -> int:
    records = scan(ROOT)
    broken = [r for r in records if r["state"] == "FAIL"]
    payload = {
        "schema": "rll.symlink-integrity/v1",
        "root": str(ROOT),
        "symlink_count": len(records),
        "fail_count": len(broken),
        "state": "PASS" if not broken else "FAIL",
        "records": records,
    }
    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False))
    if broken:
        print(
            f"FAIL symlink integrity: {len(broken)} of {len(records)} symlinks are broken or escape the repository",
            file=sys.stderr,
        )
        return 1
    print(f"PASS symlink integrity: {len(records)} symlinks resolved inside repository")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
