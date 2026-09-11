from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


trinity = load_module("rll_noaa_trinity_cycle", ROOT / "scripts" / "rll_noaa_trinity_cycle.py")


class NoaaTrinity633Tests(unittest.TestCase):
    def setUp(self):
        self.contract = json.loads((ROOT / "data" / "contracts" / "rll_noaa_trinity_633.v1.json").read_text(encoding="utf-8"))
        self.registry = json.loads((ROOT / "data" / "climate" / "rll_climate_source_registry.v1.json").read_text(encoding="utf-8"))
        self.governance = json.loads((ROOT / "data" / "governance" / "rll_noaa_trinity633_data_governance.v1.json").read_text(encoding="utf-8"))

    def test_cycle_is_exactly_6_3_3(self):
        self.assertEqual(self.contract["cycle_hours"], [6, 3, 3])
        self.assertEqual(self.contract["cycle_total_hours"], 12)

    def test_state_chain_preserves_new_vacua(self):
        self.assertEqual(
            self.contract["state_chain"],
            ["TOKEN_VAZIO", "VERBO", "CHEIO", "NOVO_VAZIO", "RETROALIMENTAR", "NOVOS_VAZIOS"],
        )

    def test_schedule_routes_each_trinity_phase(self):
        for schedule, phase in trinity.SCHEDULE_TO_PHASE.items():
            self.assertEqual(trinity.resolve_phase("auto", schedule), phase)

    def test_all_bound_sources_are_declared_noaa_https(self):
        bound = trinity.validate_source_bindings(self.contract, self.registry, self.governance)
        self.assertEqual(len(bound), 5)
        self.assertEqual(len({item["measurement_family"] for item in bound}), 5)
        self.assertTrue(all(item["url"].startswith("https://") for item in bound))

    def test_dry_run_never_promotes_cross_domain_or_claim(self):
        fake = {"mode": "DRY_RUN", "returncode": 0, "claim_allowed": False}
        with tempfile.TemporaryDirectory() as temp, mock.patch.object(trinity, "run_fetch", return_value=fake):
            receipt = trinity.build_receipt(
                self.contract,
                self.registry,
                "LUX_6H",
                Path(temp),
                execute_network=False,
                governance=self.governance,
            )
        self.assertEqual(receipt["gate_status"], "DRY_RUN")
        self.assertFalse(receipt["observed_cross_domain"])
        self.assertFalse(receipt["statistical_independence_established"])
        self.assertFalse(receipt["claim_allowed"])
        self.assertFalse(receipt["privacy"]["personal_data_expected"])
        self.assertTrue(receipt["zero_trust"]["deny_by_default"])
        self.assertEqual(receipt["cause"], "TOKEN_VAZIO_CAUSA")

    def test_partial_custody_is_not_physical_correlation(self):
        def fake_fetch(source_id, output_dir, execute_network, timeout_seconds, max_bytes):
            if source_id in {"noaa_swpc_realtime_solar_wind", "noaa_swpc_realtime_imf", "noaa_swpc_kp"}:
                return {
                    "returncode": 0,
                    "status": 200,
                    "sha256": "a" * 64,
                    "bytes": 2,
                    "content_type": "application/json",
                    "claim_allowed": False,
                }
            return {"returncode": 2, "status": "FAIL", "claim_allowed": False}

        with tempfile.TemporaryDirectory() as temp, mock.patch.object(trinity, "run_fetch", side_effect=fake_fetch):
            receipt = trinity.build_receipt(
                self.contract,
                self.registry,
                "SPIRITUM_3H",
                Path(temp),
                execute_network=True,
                governance=self.governance,
            )
        self.assertEqual(receipt["gate_status"], "SOURCE_CUSTODY_PARTIAL")
        self.assertTrue(receipt["cross_domain_readiness"])
        self.assertFalse(receipt["observed_cross_domain"])
        self.assertFalse(receipt["claim_allowed"])


if __name__ == "__main__":
    unittest.main()

    def test_content_type_mismatch_does_not_create_custody(self):
        source = {
            "required_content_type_contains": "json",
        }
        result = {
            "returncode": 0,
            "status": 200,
            "sha256": "a" * 64,
            "bytes": 10,
            "content_type": "text/html",
        }
        self.assertFalse(trinity.source_custody_ok(result, source, self.governance))

    def test_query_parameter_binding_is_rejected(self):
        registry = json.loads(json.dumps(self.registry))
        source = next(item for item in registry["sources"] if item["id"] == "noaa_swpc_kp")
        source["sample_url"] += "?device=abc"
        with self.assertRaises(ValueError):
            trinity.validate_source_bindings(self.contract, registry, self.governance)
