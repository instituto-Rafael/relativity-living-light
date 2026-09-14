from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from rll import latentes

CATALOG = Path("data/rll_latentes/observations.yml")
SCHEMA = Path("schemas/rll_latentes_observations.schema.json")
INVALID = Path("data/rll_latentes/examples/invalid_missing_falsifier.yml")


def test_validate_catalog_accepts_main_catalog() -> None:
    payload = latentes.validate_catalog(CATALOG, SCHEMA)

    assert len(payload["sources"]) == 10
    assert [item["step"] for item in payload["future_steps"]] == list(range(1, 8))


def test_validate_catalog_rejects_missing_falsifier() -> None:
    with pytest.raises(Exception):
        latentes.validate_catalog(INVALID, SCHEMA)


def test_score_latent_boundaries_and_control_status() -> None:
    score = latentes.score_latent(C=0.9, I=0.99, P=1.0, E=0.88, Rc=0.95, Ru=0.3, Am=0.2, Vb=0.1)

    assert score.S_L == pytest.approx(0.4655475)
    assert score.status == "fertile_candidate"
    assert latentes.classify_control(score, controls_present=False, null_rejected=False) == "provisional"
    assert latentes.classify_control(score, controls_present=True, null_rejected=False) == "rejected_noise"


def test_score_latent_rejects_invalid_domain() -> None:
    with pytest.raises(ValueError, match="C must be in"):
        latentes.score_latent(C=1.1, I=1.0, P=1.0, E=1.0, Rc=1.0, Ru=0.0, Am=0.0, Vb=0.0)
    with pytest.raises(ValueError, match="Ru must be"):
        latentes.score_latent(C=1.0, I=1.0, P=1.0, E=1.0, Rc=1.0, Ru=-0.1, Am=0.0, Vb=0.0)


def test_build_semantic_token_unit_preserves_ucase_and_seven_directions() -> None:
    unit = latentes.build_semantic_token_unit("força disponível: prova?")

    assert unit["raw_span"] == "FORÇA DISPONÍVEL: PROVA?"
    assert tuple(unit["views_7d"]) == latentes.SEMANTIC_DIRECTIONS
    assert unit["views_7d"]["d5_causal_temporal"]["forward_paths"] == []
    assert unit["views_7d"]["d5_causal_temporal"]["backward_paths"] == []
    assert unit["views_7d"]["d6_epistemic_gap"]["token_vazio"] is True
    assert unit["views_7d"]["d7_operational_governance"]["execution_gate"] == "human_review"


def test_ucase_prompt_rejects_empty_input() -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        latentes.ucase_prompt(" \n\t")


def test_entropy_hash_and_toroidal_map_are_deterministic() -> None:
    data = b"RLL-LATENTES"
    entropy = latentes.entropy_milli(data)
    digest = f"{latentes.fnv1a64(data):016x}"

    first = latentes.toroidal_map(data, entropy, digest, "candidate")
    second = latentes.toroidal_map(data, entropy, digest, "candidate")

    assert entropy > 0
    assert len(first) == 7
    assert first == second
    assert all(0.0 <= item < 1.0 for item in first)


def test_run_dry_pipeline_materializes_all_guardrail_artifacts(tmp_path: Path) -> None:
    result = latentes.run_dry_pipeline(CATALOG, SCHEMA, tmp_path, "desi_dr2_bao_supplement_2025")

    assert result["catalog_sources"] == 10
    assert result["future_steps"] == 7
    assert result["control_status"] == "rejected_noise"
    for key in ("null_model", "score", "provenance", "report"):
        assert Path(result[key]).exists()
    provenance = json.loads(Path(result["provenance"]).read_text(encoding="utf-8"))
    assert provenance["artifact_count"] >= 12
    assert len(provenance["merkle_root"]) == 64


def test_latentes_cli_validate_and_report(tmp_path: Path) -> None:
    env = {"PYTHONPATH": str(Path.cwd() / "src")}
    validate_run = subprocess.run(
        [sys.executable, "-m", "rll.latentes", "validate"],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    assert validate_run.returncode == 0, validate_run.stderr
    assert '"future_steps": 7' in validate_run.stdout

    report_run = subprocess.run(
        [sys.executable, "-m", "rll.latentes", "--root", str(tmp_path), "report", "--source-id", "desi_dr2_bao_supplement_2025"],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    assert report_run.returncode == 0, report_run.stderr
    payload = json.loads(report_run.stdout)
    assert Path(payload["report"]).exists()


def test_rll_cli_latentes_delegates_to_submodule(tmp_path: Path) -> None:
    env = {"PYTHONPATH": str(Path.cwd() / "src")}
    completed = subprocess.run(
        [sys.executable, "-m", "rll.cli", "latentes", "report", "--root", str(tmp_path), "--source-id", "desi_dr2_bao_supplement_2025"],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["selected_source"] == "desi_dr2_bao_supplement_2025"


def test_observation_suggested_commands_are_parser_compatible() -> None:
    import importlib.util
    import shlex

    import yaml

    spec = importlib.util.spec_from_file_location("fetch_real_sources", Path("scripts/fetch_real_sources.py"))
    assert spec and spec.loader
    fetch_real_sources = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fetch_real_sources)
    parser = fetch_real_sources.build_parser()
    catalog = yaml.safe_load(CATALOG.read_text(encoding="utf-8"))

    supported_external_shapes = {
        ("cernopendata-client", "search"),
        ("curl", "-L"),
        ("openneuro", "download"),
    }
    for source in catalog["sources"]:
        argv = shlex.split(source["suggested_command"])
        if argv[:2] == ["python3", "scripts/fetch_real_sources.py"]:
            parsed = parser.parse_args(argv[2:])
            assert parsed.source == source["source_id"]
            assert source["source_id"] in fetch_real_sources.SOURCES
            continue
        assert tuple(argv[:2]) in supported_external_shapes


def test_fetch_real_sources_euclid_source_materializes_manual_manifest(tmp_path: Path) -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/fetch_real_sources.py",
            "--source",
            "euclid_q1_data_release_2025",
            "--output-dir",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    manifest = tmp_path / "raw" / "euclid_q1_data_release_2025" / "manifest.json"
    assert manifest.exists()
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    assert payload["source"] == "euclid_q1_data_release_2025"
    assert payload["group"] == "cosmology"
    assert payload["status"] == "manual_materialization_required"
    assert payload["url"] == "https://www.euclid-ec.org/science/q1/"
    assert "portal" in payload["reason"].lower()
    assert "run_utc" in payload
