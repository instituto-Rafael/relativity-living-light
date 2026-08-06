from __future__ import annotations

import json
from pathlib import Path

from tools import build_rll_route_forest_effective as effective


def test_effective_compiler_validates_and_writes_artifacts(tmp_path: Path, capsys) -> None:
    artifact_dir = tmp_path / "route-forest"
    result = effective.main(
        [
            "--strict",
            "--write-report",
            "--artifact-dir",
            str(artifact_dir),
        ]
    )
    assert result == 0
    summary = json.loads(capsys.readouterr().out)
    assert summary["passed"] is True
    assert summary["forest_id"] == "RLL-OMEGA-ROUTE-FOREST-20260731"
    assert summary["nodes"] == 31
    assert summary["routes"] == 32
    assert summary["events"] == 40
    assert summary["claim_allowed"] is False
    assert (artifact_dir / "route_forest_report.json").is_file()
    assert (artifact_dir / "rll_route_forest.graphml").is_file()
    assert (artifact_dir / "CHECKSUMS.sha256").is_file()
