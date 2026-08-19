from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOWNLOADER = ROOT / "scripts" / "download_real_cosmology_inputs.sh"
WORKFLOW = ROOT / ".github" / "workflows" / "real-data-complete-execution.yml"


def test_downloader_targets_same_canonical_directory_as_verifier():
    text = DOWNLOADER.read_text(encoding="utf-8")
    assert "data/real/cosmology/pantheon_plus/Pantheon+_Data/4_DISTANCES_AND_COVAR" in text
    assert "--require-full-covariance" in text
    assert "Pantheon+SH0ES_STAT+SYS.cov.sha256" not in text  # sidecar is derived from ${path}.sha256


def test_downloader_pins_primary_source_commit_blob_hash_and_sha256():
    text = DOWNLOADER.read_text(encoding="utf-8")
    assert "PantheonPlusSH0ES/DataRelease" in text
    assert "c447f0fea703fcd0fff57de5000947b5ca81286b" in text
    assert "d1a1498154e7ba826df14bdbef35ebcb7f5efba1" in text
    assert "abf806d966485e64afdb359c87bffc0ecc00d05eff0a31ced66f247385df0fdc" in text
    assert "PANTHEON_COV_BYTES=33284960" in text


def test_legacy_path_is_compatibility_not_authority():
    text = DOWNLOADER.read_text(encoding="utf-8")
    canonical_pos = text.index("CANONICAL_PANTHEON_DIR=")
    legacy_pos = text.index("LEGACY_PANTHEON_DIR=")
    assert canonical_pos < legacy_pos
    assert "Hardlink avoids duplicate bytes when possible" in text
    assert 'fetch "$PANTHEON_COV_URL" "$COV_PATH"' in text
    assert 'compat_link_or_copy "$COV_PATH" "$LEGACY_PANTHEON_DIR/Pantheon+SH0ES_STAT+SYS.cov"' in text


def test_workflow_has_pull_request_full_covariance_gate_without_new_workflow_file():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "pull_request:" in text
    assert "pantheon-full-covariance-pr-gate:" in text
    assert "github.event_name == 'pull_request'" in text
    assert "bash scripts/download_real_cosmology_inputs.sh" in text
    assert "--require-full-covariance" in text
    assert "pantheon_full_covariance_materialization_receipt.json" in text


def test_manual_job_remains_dispatch_only():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "real-data-complete:" in text
    assert "github.event_name == 'workflow_dispatch'" in text
