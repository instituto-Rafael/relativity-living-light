"""No-network adversarial intake tests for the 2026 relational-time dataset."""
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "rll_barontini_time_intake.py"
spec = importlib.util.spec_from_file_location("rll_barontini_time_intake", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class BarontiniIntakeTests(unittest.TestCase):
    SAMPLE = ("t tau phi sigma\n"
              "4 200 1e-5 2e-6\n"
              "2 100 2e-5 0\n"
              "6 200 1e-5 1e-6\n")

    def make_file(self, directory, name="Fig2Fig3V0.dat", content=None):
        path = Path(directory) / name
        path.write_text(self.SAMPLE if content is None else content, encoding="utf-8")
        return path

    def test_t_order_and_tau_plateau_are_not_erased(self):
        with tempfile.TemporaryDirectory() as d:
            self.make_file(d)
            result = mod.read_table(Path(d) / "Fig2Fig3V0.dat", "Fig2Fig3V0.dat")
            self.assertEqual(result["numeric_rows"], 3)
            self.assertEqual(result["diagnostics"]["out_of_order_t_pairs"], 1)
            self.assertEqual(result["diagnostics"]["tau_plateaus_adjacent_by_t"], 1)
            self.assertEqual(result["sigma_zeros"], 1)

    def test_no_file_means_token_vazio_not_pass(self):
        with tempfile.TemporaryDirectory() as d:
            out = mod.audit(d, {"Fig2Fig3V0.dat": "deadbeef"})
            self.assertEqual(out["intake_status"], "BLOCKED_OR_REVIEW_REQUIRED")
            self.assertEqual(out["files"]["Fig2Fig3V0.dat"]["status"], "TOKEN_VAZIO_NOT_MATERIALIZED")
            self.assertFalse(out["claim_allowed"])

    def test_pinned_md5_and_sha256(self):
        with tempfile.TemporaryDirectory() as d:
            path = self.make_file(d)
            md5 = hashlib.md5(path.read_bytes()).hexdigest()
            report = mod.audit(d, {path.name: md5})
            self.assertEqual(report["intake_status"], "PASS_SCOPED_INTEGRITY")
            self.assertEqual(report["files"][path.name]["sha256"], hashlib.sha256(path.read_bytes()).hexdigest())
            self.assertEqual(report["physical_replication"], "TOKEN_VAZIO_NOT_EXECUTED")

    def test_wrong_checksum_blocked(self):
        with tempfile.TemporaryDirectory() as d:
            path = self.make_file(d)
            status = mod.audit(d, {path.name: "0" * 32})["files"][path.name]["status"]
            self.assertEqual(status, "BLOCKED_DIGEST_MISMATCH")

    def test_nonfinite_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path = self.make_file(d, content="t tau phi sigma\n2 1 NaN 0.1\n")
            with self.assertRaisesRegex(ValueError, "nonfinite"):
                mod.read_table(path, path.name)

    def test_negative_sigma_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path = self.make_file(d, content="t tau phi sigma\n2 1 0.1 -0.1\n")
            with self.assertRaisesRegex(ValueError, "negative"):
                mod.read_table(path, path.name)

    def test_missing_header_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path = self.make_file(d, content="t tau what sigma\n2 1 0.1 0.1\n")
            with self.assertRaisesRegex(ValueError, "missing"):
                mod.read_table(path, path.name)

    def test_incomplete_numeric_row_is_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            path = self.make_file(d, name="Fig3numerics.dat", content="column sigma\n1 0.1\n2\n")
            r = mod.read_table(path, path.name)
            self.assertEqual(r["numeric_rows"], 1)
            self.assertEqual(r["malformed_rows"], [{"line": 3, "columns": 1}])

    def test_matrix_width_change_is_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            path = self.make_file(d, name="Fig4.dat", content="1 2 3\n4 5\n6 7 8\n")
            r = mod.read_table(path, path.name)
            self.assertEqual(r["numeric_rows"], 2)
            self.assertEqual(r["malformed_rows"][0]["reason"], "inconsistent_matrix_width")

    def test_duplicate_t_requires_review(self):
        with tempfile.TemporaryDirectory() as d:
            path = self.make_file(d, content="t tau phi sigma\n2 1 0.1 0.1\n2 2 0.2 0.2\n")
            checksum = hashlib.md5(path.read_bytes()).hexdigest()
            out = mod.audit(d, {path.name: checksum})
            self.assertEqual(out["files"][path.name]["status"], "REVIEW_REQUIRED")

    def test_download_never_overwrites_mismatched_file(self):
        with tempfile.TemporaryDirectory() as d:
            path = self.make_file(d)
            before = path.read_bytes()
            with self.assertRaisesRegex(ValueError, "not overwritten"):
                mod.fetch_one(d, path.name, "0" * 32)
            self.assertEqual(path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
