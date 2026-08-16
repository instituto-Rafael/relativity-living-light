from tools.branch_divergence_inventory import (
    domain_for,
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


def test_parse_name_status_preserves_renames() -> None:
    rows = parse_name_status("M\t.github/workflow-contract.yml\nR100\told.md\tnew.md\n")
    assert rows[0] == {"status": "M", "path": ".github/workflow-contract.yml"}
    assert rows[1] == {"status": "R100", "path": "new.md", "previous_path": "old.md"}


def test_domains_are_deterministic_and_non_epistemic() -> None:
    assert domain_for(".github/workflows/x.yml") == "workflow"
    assert domain_for("data/governance/x.json") == "governance"
    assert domain_for("data/inputs/x.csv") == "data"
    assert domain_for("tools/x.py") == "implementation"
    assert domain_for("tests/test_x.py") == "tests"
    assert domain_for("docs/x.md") == "documentation"
    assert summarize_domains(["tools/a.py", "tools/b.py", "docs/c.md"]) == {
        "documentation": 1,
        "implementation": 2,
    }
