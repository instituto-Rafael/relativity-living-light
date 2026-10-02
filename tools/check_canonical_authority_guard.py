#!/usr/bin/env python3
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / ".github" / "workflows" / "canonical-institute-authority-guard.yml"
CANONICAL = "instituto-Rafael/relativity-living-light"
FULL_SHA = re.compile(r"actions/checkout@([0-9a-f]{40})(?:\s|$)")


def require(ok: bool, message: str) -> None:
    if not ok:
        raise AssertionError(message)


def main() -> int:
    text = PATH.read_text(encoding="utf-8")
    require(f"CANONICAL_REPOSITORY: {CANONICAL}" in text, "canonical repository binding missing")
    require('if [ "${GITHUB_REPOSITORY}" != "${CANONICAL_REPOSITORY}" ]; then' in text,
            "PR routing is not conditioned on repository identity")
    require("PR targets the declared canonical repository" in text,
            "canonical acceptance path missing")
    require("if: github.event_name == 'pull_request'\n        run:" not in text,
            "legacy unconditional pull-request failure pattern remains")
    require(bool(FULL_SHA.search(text)), "manual checkout is not pinned to a full commit SHA")
    print(f"PASS canonical authority guard: canonical={CANONICAL}; repository-identity gate bound")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL canonical authority guard: {exc}", file=sys.stderr)
        raise SystemExit(1)
