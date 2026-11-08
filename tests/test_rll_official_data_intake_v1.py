import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.rll_official_data_intake_v1 import (
    POWER, DESI, SOURCES, IntakeError, _safe_profile, fetch_bounded,
    inspect_desi, inspect_power, make_receipt, run,
)


def power_bytes(fill=None):
    days = [f"2025010{i}" for i in range(1, 8)]
    data = {"type": "Feature", "header": {"fill_value": -999},
        "properties": {"parameter": {
            "T2M": {k: (22 if not (fill and i == 0) else -999) for i, k in enumerate(days)},
            "PS": {k: 100 for k in days}}}}
    return json.dumps(data).encode("utf-8")


class OfficialIntakeTests(unittest.TestCase):
    def test_allowlist(self): self.assertRaises(IntakeError, _safe_profile, "https://localhost")
    def test_https_static_urls(self):
        self.assertTrue(POWER.startswith("https://power.larc.nasa.gov/"))
        self.assertTrue(DESI.startswith("https://data.desi.lbl.gov/"))
    def test_no_redirect_handler(self):
        from tools.rll_official_data_intake_v1 import NoRedirect
        self.assertRaises(IntakeError, NoRedirect().redirect_request, None, None, 302, "", {}, "http://localhost")
    def test_power_valid(self): self.assertEqual(inspect_power(power_bytes())["non_missing_per_variable"]["PS"], 7)
    def test_power_missing_explicit(self): self.assertEqual(inspect_power(power_bytes(True))["missing_per_variable"]["T2M"], 1)
    def test_power_no_value(self):
        d=json.loads(power_bytes())
        d["properties"]["parameter"]["PS"]={k:-999 for k in d["properties"]["parameter"]["PS"]}
        self.assertRaises(IntakeError,inspect_power,json.dumps(d).encode())
    def test_power_window_incomplete(self):
        d=json.loads(power_bytes()); d["properties"]["parameter"]["PS"].pop("20250107")
        self.assertRaises(IntakeError,inspect_power,json.dumps(d).encode())
    def test_power_bad_date(self):
        d=json.loads(power_bytes()); d["properties"]["parameter"]["PS"]["20240201"]=123
        self.assertRaises(IntakeError,inspect_power,json.dumps(d).encode())
    def test_power_invalid_json(self): self.assertRaises(IntakeError,inspect_power,b"{")
    def test_desi_metadata_only(self):
        z=inspect_desi(b"DESI DR2 Publications cosmology baryon acoustic oscillations")
        self.assertFalse(z["is_numeric_ingestion"])
        self.assertEqual(z["covariance"], "TOKEN_VAZIO")
    def test_desi_bad_source(self): self.assertRaises(IntakeError,inspect_desi,b"fake table")
    def test_metadata_receipt_not_data(self):
        r=make_receipt("desi_dr2_publications","metadata_only")
        self.assertEqual(r["bytes_sha256"], "TOKEN_VAZIO")
        self.assertEqual(r["execution_state"], "NOT_FETCHED")
        self.assertFalse(r["claim_allowed"])
    def test_fetch_requires_bytes(self): self.assertRaises(IntakeError,make_receipt,"nasa_power_daily","fetch")
    def test_dry_run_rejects_bytes(self): self.assertRaises(IntakeError,make_receipt,"nasa_power_daily","metadata_only",power_bytes())
    def test_sha_raw(self):
        data=power_bytes();r=make_receipt("nasa_power_daily","fetch",data)
        self.assertEqual(r["bytes_sha256"],hashlib.sha256(data).hexdigest())
        self.assertFalse(r["model_fit_executed"])
    def test_oversize(self): self.assertRaises(IntakeError,make_receipt,"nasa_power_daily","fetch",b"0"*600000)
    def test_metadata_dir(self):
        with tempfile.TemporaryDirectory() as d:
            dst=Path(d)/"out";run("nasa_power_daily","metadata_only",dst)
            self.assertTrue((dst/"RECEIPT.json").exists())
            self.assertFalse((dst/"nasa_power_daily.json").exists())
            self.assertIn("NOT_FETCHED",(dst/"RECEIPT.json").read_text())
    def test_fetch_dir_offline_mock(self):
        with tempfile.TemporaryDirectory() as d, patch("tools.rll_official_data_intake_v1.fetch_bounded",return_value=power_bytes()):
            dst=Path(d)/"out";r=run("nasa_power_daily","fetch",dst)
            self.assertEqual(r["execution_state"],"SCHEMA_VALIDATED_REMOTE_BYTES")
            self.assertEqual((dst/"nasa_power_daily.json").read_bytes(),power_bytes())
            self.assertIn("nasa_power_daily.json",(dst/"CHECKSUMS.sha256").read_text())
    def test_profile_auth_no_secret(self):
        for p in SOURCES.values(): self.assertNotIn("token=",p["url"])
    def test_no_network_on_metadata(self):
        with tempfile.TemporaryDirectory() as d, patch("tools.rll_official_data_intake_v1.fetch_bounded",side_effect=AssertionError("must not fetch")):
            run("desi_dr2_publications","metadata_only",Path(d)/"out")

if __name__ == "__main__": unittest.main()
