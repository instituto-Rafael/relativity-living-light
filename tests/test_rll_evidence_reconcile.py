from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from tools.rll_evidence_reconcile import (
    ReconciliationError,
    classify_bayes_proxy,
    classify_pantheon,
    read_artifact_zip,
    reconcile,
    validate_result_record,
)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write_zip(path: Path, files: dict[str, bytes]) -> None:
    checksum_lines = []
    for name, data in files.items():
        checksum_lines.append(f"{_sha(data)}  artifacts/test/{name}\n")
    all_files = dict(files)
    all_files["CHECKSUMS.sha256"] = "".join(checksum_lines).encode()
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in all_files.items():
            archive.writestr(name, data)


class EvidenceReconcileTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _pantheon_zip(self) -> Path:
        path = self.root / "pantheon.zip"
        result = {
            "delta_aic_rll_minus_lcdm": None,
            "chi2_lcdm": None,
            "chi2_rll_original": None,
            "aic_lcdm": None,
            "aic_rll": None,
            "token_vazio": True,
            "reference": {"delta_aic": 3.81, "source": "legacy.txt"},
        }
        stdout = (
            "Traceback (most recent call last):\n"
            "ModuleNotFoundError: No module named 'models'\n"
        )
        _write_zip(
            path,
            {
                "pantheon_fit_result.json": json.dumps(result).encode(),
                "fit_stdout.txt": stdout.encode(),
                "CLAIM_BOUNDARY.md": b"claim_allowed=false\n",
            },
        )
        return path

    def _bayes_zip(self) -> Path:
        path = self.root / "bayes.zip"
        result = {
            "ln_B10_rll_over_lcdm": None,
            "token_vazio_p0": True,
            "method": "BIC proxy",
        }
        log = (
            "model regime chi2 AIC BIC N k dof\n"
            "lcdm real 123.681105 131.681105 138.907755 45 4 41\n"
            "rll_like_agn real 123.597656 137.597656 150.244294 45 7 38\n"
        )
        _write_zip(
            path,
            {
                "bayes_factor_result.json": json.dumps(result).encode(),
                "bayes_bic_run.log": log.encode(),
                "CLAIM_BOUNDARY.md": b"claim_allowed=false\n",
            },
        )
        return path

    def test_pantheon_failure_is_class_p_and_reference_is_not_promoted(self) -> None:
        artifact = read_artifact_zip(self._pantheon_zip())
        result = classify_pantheon(artifact)
        self.assertEqual(result["evidence_class"], "P")
        self.assertIsNone(result["value"])
        self.assertEqual(result["failure"]["kind"], "MODULE_NOT_FOUND")
        self.assertEqual(result["failure"]["module"], "models")
        self.assertEqual(result["historical_reference_not_promoted"]["delta_aic"], 3.81)
        self.assertEqual(validate_result_record(result), [])

    def test_bic_proxy_is_calculated_as_class_c(self) -> None:
        artifact = read_artifact_zip(self._bayes_zip())
        proxy, real_bayes = classify_bayes_proxy(artifact)
        self.assertEqual(proxy["evidence_class"], "C")
        self.assertAlmostEqual(proxy["delta_bic_rll_minus_lcdm"], 11.336539)
        self.assertAlmostEqual(proxy["value"], -5.6682695)
        self.assertEqual(proxy["falsifier_gate"]["status"], "FAIL")
        self.assertEqual(real_bayes["evidence_class"], "P")
        self.assertIsNone(real_bayes["value"])

    def test_outer_digest_mismatch_fails_closed(self) -> None:
        with self.assertRaises(ReconciliationError):
            read_artifact_zip(self._bayes_zip(), expected_sha256="0" * 64)

    def test_reconcile_preserves_three_distinct_results(self) -> None:
        payload = reconcile(
            run_id=31066012098,
            source_head_sha="3191a1d289db28b09b155b4b9eba62a32ad90005",
            result_commit="cfcd8b4915fef664486bc0d93ee2a2bb6d84ec65",
            pantheon_zip=self._pantheon_zip(),
            bayes_zip=self._bayes_zip(),
            generated_at="2026-08-06T04:00:00+00:00",
        )
        self.assertFalse(payload["claim_allowed"])
        self.assertEqual(payload["results"]["pantheon_delta_aic"]["evidence_class"], "P")
        self.assertEqual(payload["results"]["bayes_bic_proxy"]["evidence_class"], "C")
        self.assertEqual(payload["results"]["bayes_real_inference"]["evidence_class"], "P")

    def test_class_c_requires_value_and_receipt(self) -> None:
        errors = validate_result_record(
            {
                "evidence_class": "C",
                "value": None,
                "state": "CALCULATED",
                "method": "x",
                "source_receipts": [],
                "claim_allowed": False,
            }
        )
        self.assertIn("class C requires a materialized value", errors)
        self.assertIn("class C requires source_receipts", errors)


if __name__ == "__main__":
    unittest.main()
