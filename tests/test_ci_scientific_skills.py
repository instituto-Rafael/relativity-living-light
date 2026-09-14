import json
from pathlib import Path

import numpy as np
import pandas as pd

from tools.ci_scientific_skills import (
    anomaly_diagnostic,
    bayes_proxy_diagnostic,
    fourier_torus_diagnostic,
    robust_anomaly_scores,
    run,
)


def test_robust_anomaly_detects_large_outlier():
    scores = robust_anomaly_scores([1.0, 1.1, 0.9, 1.05, 40.0])
    assert int(np.argmax(np.abs(scores))) == 4
    assert abs(scores[4]) > 3.5


def test_anomaly_diagnostic_records_input_hash(tmp_path: Path):
    path = tmp_path / "observations.csv"
    pd.DataFrame({"value": [1.0, 1.1, 0.9, 1.05, 40.0]}).to_csv(path, index=False)
    report = anomaly_diagnostic(path)
    assert report["status"] == "EVIDENCED_ON_REPOSITORY_DATA"
    assert report["anomaly_indices"] == [4]
    assert len(report["input_sha256"]) == 64


def test_fourier_torus_method_is_deterministic_and_precise():
    report = fourier_torus_diagnostic(samples=2048, max_mode=32)
    assert report["status"] == "VERIFIED_METHOD"
    assert report["rmse"] < 1e-12
    assert report["space"] == "T^1"


def test_bayes_proxy_prefers_lower_bic(tmp_path: Path):
    path = tmp_path / "comparison.csv"
    pd.DataFrame(
        [
            {"model": "lcdm", "BIC": 110.0},
            {"model": "rll", "BIC": 116.0},
        ]
    ).to_csv(path, index=False)
    report = bayes_proxy_diagnostic(path)
    assert report["preferred_by_bic"] == "lcdm"
    assert report["delta_bic_alternative_minus_preferred"] == 6.0
    assert report["log_bayes_proxy_preferred_vs_alternative"] == 3.0


def test_run_preserves_missing_evidence_as_token_vazio(tmp_path: Path):
    output = tmp_path / "artifact" / "report.json"
    payload = run(tmp_path, output, strict=False)
    assert payload["overall_status"] == "TOKEN_VAZIO"
    assert payload["skills"]["C1_anomaly_diagnostic"]["status"] == "TOKEN_VAZIO"
    assert payload["skills"]["D1_bayes_proxy"]["status"] == "TOKEN_VAZIO"
    assert output.is_file()
    assert json.loads(output.read_text(encoding="utf-8"))["schema"] == payload["schema"]
