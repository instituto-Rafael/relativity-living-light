from __future__ import annotations

import json
import os
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest

from data.pipelines.structure_d import run_all_real


ACTIVE_FULL_PROFILE = [
    "real_hz",
    "real_bao",
    "real_cmb_shift",
    "real_fsigma8",
]


def test_legacy_execution_contract_separates_declared_from_consumed() -> None:
    contract = run_all_real.build_legacy_execution_contract(
        ACTIVE_FULL_PROFILE,
        "prefer_full",
    )

    assert contract["route_scope"] == "background_three_axis"
    assert contract["active_datasets_declared"] == ACTIVE_FULL_PROFILE
    assert contract["datasets_consumed_in_objective"] == [
        "real_hz",
        "real_bao",
        "real_cmb_shift",
    ]
    assert contract["unconsumed_active_datasets"] == ["real_fsigma8"]
    assert contract["full_profile_consumed"] is False
    assert contract["datasets_used_semantics"] == "objective_consumed_only"
    assert contract["covariance_policy_requested"] == "prefer_full"
    assert contract["covariance_policy_effective"] == "diagonal_only"
    assert contract["covariance_gap"]
    assert contract["claim_allowed"] is False
    assert contract["scientific_confirmation"] is False


def test_full_required_fails_closed_before_fit() -> None:
    with patch(
        "data.pipelines.structure_d.run_all_real.differential_evolution"
    ) as optimizer:
        with pytest.raises(RuntimeError, match="full_required.*incompatible"):
            run_all_real.main(covariance_policy="full_required")
        optimizer.assert_not_called()


def test_missing_required_background_dataset_fails_closed() -> None:
    with pytest.raises(RuntimeError, match="missing from profile"):
        run_all_real.build_legacy_execution_contract(
            ["real_hz", "real_cmb_shift", "real_fsigma8"],
            "diagonal_only",
        )


def test_legacy_outputs_report_only_objective_consumed_datasets() -> None:
    output_csv = "test_legacy_consumption_truth.csv"
    csv_path = os.path.join(run_all_real.RESULTS, output_csv)
    metadata_path = os.path.splitext(csv_path)[0] + "_fit_metadata.json"
    error_mode_path = os.path.join(run_all_real.RESULTS, "error_mode_usage.csv")
    timing_csv = os.path.join(run_all_real.RESULTS, "execution_timing_real.csv")
    timing_json = os.path.join(run_all_real.RESULTS, "execution_timing_real.json")

    cleanup_paths = [
        csv_path,
        metadata_path,
        error_mode_path,
        timing_csv,
        timing_json,
    ]

    class _Result:
        def __init__(self, x, fun):
            self.x = np.asarray(x, dtype=float)
            self.fun = float(fun)

    fake_results = [
        _Result([67.7, 0.31, 0.69, 0.0224], 11.2),
        _Result([68.0, 0.30, 0.70, 0.04, 2.1, 0.5, 0.0221], 10.8),
    ]

    try:
        with patch(
            "data.pipelines.structure_d.run_all_real.differential_evolution",
            side_effect=fake_results,
        ):
            df = run_all_real.main(
                output_filename=output_csv,
                covariance_policy="prefer_full",
            )

        assert set(df["datasets_used"]) == {
            "real_hz,real_bao,real_cmb_shift"
        }
        assert set(df["covariance_policy"]) == {"diagonal_only"}

        with open(metadata_path, "r", encoding="utf-8") as fp:
            metadata = json.load(fp)

        assert metadata["route_scope"] == "background_three_axis"
        assert metadata["active_datasets_declared"] == ACTIVE_FULL_PROFILE
        assert metadata["datasets_used"] == [
            "real_hz",
            "real_bao",
            "real_cmb_shift",
        ]
        assert metadata["datasets_consumed_in_objective"] == metadata["datasets_used"]
        assert metadata["unconsumed_active_datasets"] == ["real_fsigma8"]
        assert metadata["full_profile_consumed"] is False
        assert metadata["covariance_policy_requested"] == "prefer_full"
        assert metadata["covariance_policy_effective"] == "diagonal_only"
        assert metadata["claim_allowed"] is False

        error_modes = pd.read_csv(error_mode_path)
        consumed = dict(
            zip(error_modes["dataset_id"], error_modes["consumed_in_objective"])
        )
        assert bool(consumed["real_hz"]) is True
        assert bool(consumed["real_bao"]) is True
        assert bool(consumed["real_cmb_shift"]) is True
        assert bool(consumed["real_fsigma8"]) is False
    finally:
        for path in cleanup_paths:
            if os.path.exists(path):
                os.remove(path)
