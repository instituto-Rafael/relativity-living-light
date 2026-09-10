from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"


def workflow_texts():
    for path in sorted(WORKFLOWS.glob("*.y*ml")):
        yield path, path.read_text(encoding="utf-8")


def test_no_unsupported_top_level_x_canonical_policy():
    offenders = []
    for path, text in workflow_texts():
        if re.search(r"(?m)^x-canonical-real-data-policy:", text):
            offenders.append(path.name)
    assert offenders == []


def test_no_secrets_context_directly_in_if_expression():
    offenders = []
    for path, text in workflow_texts():
        if re.search(r"(?m)^\s*if:\s*\$\{\{[^}]*\bsecrets\.", text):
            offenders.append(path.name)
    assert offenders == []


def test_no_javascript_ternary_inside_github_expression():
    offenders = []
    pattern = re.compile(r"\$\{\{[^}\n]*\?[^}\n]*:[^}\n]*\}\}")
    for path, text in workflow_texts():
        if pattern.search(text):
            offenders.append(path.name)
    assert offenders == []
