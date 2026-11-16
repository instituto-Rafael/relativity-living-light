"""Fail-closed static guards for two zero-job workflow preflight repairs."""

from pathlib import Path
import re

WORKFLOWS = Path(__file__).resolve().parents[1] / ".github" / "workflows"
TARGETS = ("import-data.yml", "rll-book-data-pipeline.yml")


def test_canonical_policy_is_comment_not_unsupported_top_level_key():
    for name in TARGETS:
        text = (WORKFLOWS / name).read_text(encoding="utf-8")
        assert re.search(r"(?m)^# x-canonical-real-data-policy: ", text)
        assert not re.search(r"(?m)^x-canonical-real-data-policy\s*:", text)


def test_dispatch_and_claim_boundary_preserved_without_implicit_push():
    for name in TARGETS:
        text = (WORKFLOWS / name).read_text(encoding="utf-8")
        assert "on:\n  workflow_dispatch:" in text
        assert not re.search(r"(?m)^  push:", text)
        assert "CANONICAL_REAL_DATA_WORKFLOW:" in text
        assert "CLAIM_BOUNDARY:" in text
        assert "permissions:\n  contents: read" in text
