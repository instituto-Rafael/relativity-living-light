"""Dependabot YAML must be unambiguous before version-update execution."""
from pathlib import Path

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]
DEPENDABOT = ROOT / ".github" / "dependabot.yml"


class NoDuplicateYamlKeys(yaml.SafeLoader):
    pass


def _mapping_reject_duplicates(loader: NoDuplicateYamlKeys, node: yaml.nodes.MappingNode):
    seen = set()
    for key_node, _ in node.value:
        key = loader.construct_object(key_node, deep=True)
        if key in seen:
            raise ValueError(f"Duplicate YAML mapping key: {key!r}")
        seen.add(key)
    return loader.construct_mapping(node, deep=True)


NoDuplicateYamlKeys.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _mapping_reject_duplicates
)


def test_dependabot_group_config_is_unique_and_safely_pinned_to_lab():
    parsed = yaml.load(DEPENDABOT.read_text(encoding="utf-8"), Loader=NoDuplicateYamlKeys)
    assert parsed["version"] == 2
    assert len(parsed["updates"]) == 1
    update = parsed["updates"][0]
    assert update["package-ecosystem"] == "github-actions"
    assert update["directory"] == "/"
    assert update["target-branch"] == "rll/lab"
    assert update["schedule"] == {
        "interval": "weekly", "day": "monday", "time": "05:17",
        "timezone": "America/Sao_Paulo",
    }
    assert update["open-pull-requests-limit"] == 5
    assert update["commit-message"]["prefix"] == "chore(actions)"
    assert update["labels"] == ["dependencies", "github-actions"]
    groups = update["groups"]
    assert list(groups) == ["codeql-actions"]
    assert groups["codeql-actions"]["patterns"] == ["github/codeql-action*"]
    assert groups["codeql-actions"]["update-types"] == ["minor", "patch"]
    assert groups["codeql-actions"]["applies-to"] == "version-updates"


def test_negative_duplicate_groups_fail_closed():
    fixture = (
        "updates:\n"
        "  - package-ecosystem: github-actions\n"
        "    groups:\n"
        "      codeql-lockstep: {}\n"
        "    groups:\n"
        "      codeql-actions: {}\n"
    )
    with pytest.raises(ValueError, match="Duplicate YAML mapping key"):
        yaml.load(fixture, Loader=NoDuplicateYamlKeys)


def test_nested_duplicate_keys_fail_closed():
    fixture = "outer:\n  a: 1\n  a: 2\n"
    with pytest.raises(ValueError, match="Duplicate YAML mapping key"):
        yaml.load(fixture, Loader=NoDuplicateYamlKeys)
