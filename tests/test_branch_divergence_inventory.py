import subprocess
from pathlib import Path

from tools.branch_divergence_inventory import (
    domain_for,
    classify_topology,
    inventory,
    parse_left_right_count,
    parse_name_status,
    summarize_domains,
)


def test_parse_left_right_count_accepts_git_format() -> None:
    assert parse_left_right_count("98\t44") == (98, 44)
    assert parse_left_right_count("0  0") == (0, 0)


def test_parse_left_right_count_rejects_invalid_shape() -> None:
    try:
        parse_left_right_count("98")
    except ValueError as exc:
        assert "two rev-list counts" in str(exc)
    else:
        raise AssertionError("invalid count shape must fail")


def test_topology_distinguishes_one_sided_advancement_without_legacy_breakage() -> None:
    assert classify_topology(0, 0) == "IDENTICAL"
    assert classify_topology(3, 0) == "LEFT_AHEAD"
    assert classify_topology(0, 7) == "RIGHT_AHEAD"
    assert classify_topology(1, 8) == "DIVERGED"
    for left, right in ((-1, 0), (0, -1)):
        try:
            classify_topology(left, right)
        except ValueError:
            pass
        else:
            raise AssertionError("negative commit counts must fail closed")


def test_one_sided_inventory_is_not_mislabeled_two_sided(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-b", "base")
    _git(root, "config", "user.name", "RLL Test")
    _git(root, "config", "user.email", "rll-test@example.invalid")
    (root / "base.txt").write_text("base\n", encoding="utf-8")
    _git(root, "add", ".")
    _git(root, "commit", "-m", "base")
    _git(root, "switch", "-c", "advanced")
    (root / "advance.txt").write_text("one sided\n", encoding="utf-8")
    _git(root, "add", ".")
    _git(root, "commit", "-m", "advance")
    advanced = subprocess.run(
        ["git", "rev-parse", "advanced"], cwd=root, check=True,
        capture_output=True, text=True
    ).stdout.strip()

    left = inventory(root, "advanced", "base")
    right = inventory(root, "base", "advanced")
    equal = inventory(root, "base", "base")
    assert left["topology_status"] == "LEFT_AHEAD"
    assert right["topology_status"] == "RIGHT_AHEAD"
    assert equal["topology_status"] == "IDENTICAL"
    # Original v1 clients may still consume status, unchanged.
    assert left["status"] == right["status"] == "DIVERGED"
    assert equal["status"] == "IDENTICAL"
    assert left["claim_allowed"] is right["claim_allowed"] is False
    assert left["decision"] == right["decision"] == "AUDIT_ONLY_NO_MUTATION"
    assert subprocess.run(
        ["git", "rev-parse", "advanced"], cwd=root, check=True,
        capture_output=True, text=True
    ).stdout.strip() == advanced


def test_parse_name_status_preserves_renames() -> None:
    rows = parse_name_status("M\t.github/workflow-contract.yml\nR100\told.md\tnew.md\n")
    assert rows[0] == {"status": "M", "path": ".github/workflow-contract.yml"}
    assert rows[1] == {"status": "R100", "path": "new.md", "previous_path": "old.md"}


def test_domains_are_deterministic_and_non_epistemic() -> None:
    assert domain_for(".github/workflows/x.yml") == "workflow"
    assert domain_for("./.github/workflows/x.yml") == "workflow"
    assert domain_for(".github/workflow-contract.yml") == "governance"
    assert domain_for("./.github/workflow-contract.yml") == "governance"
    assert domain_for("data/governance/x.json") == "governance"
    assert domain_for("data/inputs/x.csv") == "data"
    assert domain_for("tools/x.py") == "implementation"
    assert domain_for("tests/test_x.py") == "tests"
    assert domain_for("docs/x.md") == "documentation"
    assert summarize_domains(["tools/a.py", "tools/b.py", "docs/c.md"]) == {
        "documentation": 1,
        "implementation": 2,
    }


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True)


def test_inventory_detects_real_two_sided_overlap_without_mutating_refs(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-b", "base")
    _git(root, "config", "user.name", "RLL Test")
    _git(root, "config", "user.email", "rll-test@example.invalid")

    shared = root / "shared.txt"
    shared.write_text("base\n", encoding="utf-8")
    (root / "base-only.txt").write_text("base\n", encoding="utf-8")
    _git(root, "add", ".")
    _git(root, "commit", "-m", "base")

    _git(root, "switch", "-c", "left")
    shared.write_text("left\n", encoding="utf-8")
    (root / "left.txt").write_text("left\n", encoding="utf-8")
    _git(root, "add", ".")
    _git(root, "commit", "-m", "left")

    _git(root, "switch", "base")
    _git(root, "switch", "-c", "right")
    shared.write_text("right\n", encoding="utf-8")
    (root / "right.txt").write_text("right\n", encoding="utf-8")
    _git(root, "add", ".")
    _git(root, "commit", "-m", "right")

    before_left = subprocess.run(
        ["git", "rev-parse", "left"], cwd=root, check=True, capture_output=True, text=True
    ).stdout.strip()
    before_right = subprocess.run(
        ["git", "rev-parse", "right"], cwd=root, check=True, capture_output=True, text=True
    ).stdout.strip()

    payload = inventory(root, "left", "right")

    after_left = subprocess.run(
        ["git", "rev-parse", "left"], cwd=root, check=True, capture_output=True, text=True
    ).stdout.strip()
    after_right = subprocess.run(
        ["git", "rev-parse", "right"], cwd=root, check=True, capture_output=True, text=True
    ).stdout.strip()

    assert payload["status"] == "DIVERGED"
    assert payload["topology_status"] == "DIVERGED"
    assert payload["left"]["unique_commits"] == 1
    assert payload["right"]["unique_commits"] == 1
    assert payload["overlap_paths"] == ["shared.txt"]
    assert payload["overlap_path_count"] == 1
    assert payload["decision"] == "AUDIT_ONLY_NO_MUTATION"
    assert payload["claim_allowed"] is False
    assert payload["history_reconciliation"] == "TOKEN_VAZIO_HISTORY_RECONCILIATION"
    assert before_left == after_left
    assert before_right == after_right
