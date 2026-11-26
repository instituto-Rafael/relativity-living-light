"""Offline literature forward-port: synthetic inputs only, no secrets or HTTP."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools import rll_literature as literature
from tools import rll_publication_cross as cross


class LiteratureOfflineTests(unittest.TestCase):
    def test_offline_catalog_keeps_source_and_timestamp(self):
        with tempfile.TemporaryDirectory() as d:
            src, out = Path(d) / "baseline.json", Path(d) / "out.json"
            initial = {"retrieved_utc": "2025-01-01T00:00:00Z", "records": {
                "10.1234/example": {"status": "negative", "claim_allowed": False}}}
            src.write_text(json.dumps(initial), encoding="utf-8")
            before = src.read_bytes()
            with patch.object(literature, "crossref", side_effect=AssertionError("network")), patch(
                "sys.argv", ["literature", "--baseline", str(src), "--output", str(out), "--offline"]):
                literature.main()
            result = json.loads(out.read_text())
            self.assertEqual(src.read_bytes(), before)
            self.assertEqual(result["records"], initial["records"])
            self.assertEqual(result["retrieved_utc"], initial["retrieved_utc"])
            self.assertEqual(result["added_dois"], [])
            self.assertEqual(result["baseline_sha256"], hashlib.sha256(before).hexdigest())
            self.assertEqual(result["execution_mode"], "OFFLINE_REPLAY")
            self.assertFalse(result["claim_allowed"])

    def test_offline_cross_preserves_input_no_feed_claim(self):
        with tempfile.TemporaryDirectory() as d:
            src, out = Path(d) / "baseline.json", Path(d) / "out.json"
            src.write_text('{"records": {}}', encoding="utf-8")
            before = src.read_bytes()
            with patch.object(cross, "fetch", side_effect=AssertionError("network")), patch(
                "sys.argv", ["cross", str(src), "--offline", "--output", str(out)]):
                cross.main()
            result = json.loads(out.read_text())
            self.assertEqual(src.read_bytes(), before)
            self.assertEqual(result["feed_status"], "NOT_RUN_OFFLINE")
            self.assertEqual(result["catalog_input_sha256"], hashlib.sha256(before).hexdigest())
            self.assertIsNone(result["unavailable_feeds"])
            self.assertFalse(result["claim_allowed"])
            self.assertTrue(result["publication_crosses"])
            self.assertTrue(all(r["claim_allowed"] is False for r in result["publication_crosses"].values()))

    def test_offline_requires_distinct_output(self):
        with tempfile.TemporaryDirectory() as d:
            src = Path(d) / "baseline.json"
            src.write_text("{}", encoding="utf-8")
            before = src.read_bytes()
            for module, argv in (
                (literature, ["lit", "--baseline", str(src), "--output", str(src), "--offline"]),
                (cross, ["cross", str(src), "--offline", "--output", str(src)]),
                (cross, ["cross", str(src), "--offline"]),
            ):
                with self.subTest(argv=argv), patch("sys.argv", argv), self.assertRaises(SystemExit):
                    module.main()
            self.assertEqual(src.read_bytes(), before)

    def test_negative_measurement_does_not_become_claim(self):
        record = cross.observation("Hubble", "H0 = 73.04 ± 0 km/s/Mpc")
        cross.evaluate(record, [])
        self.assertEqual(record["tests"], [])
        self.assertEqual(record["status"], "missing_executable_binding_or_measurement")
        self.assertFalse(record["claim_allowed"])

    def test_predictable_temp_name_never_consumes_source(self):
        for module, suffix in ((literature, ".tmp"), (cross, ".json.tmp")):
            with self.subTest(module=module.__name__), tempfile.TemporaryDirectory() as d:
                out = Path(d) / "out.json"
                src = Path(d) / ("out" + suffix)
                src.write_text('{"records": {}}', encoding="utf-8")
                before = src.read_bytes()
                argv = (["lit", "--baseline", str(src), "--output", str(out), "--offline"]
                        if module is literature else ["cross", str(src), "--output", str(out), "--offline"])
                with patch("sys.argv", argv):
                    module.main()
                self.assertEqual(src.read_bytes(), before)
                self.assertTrue(out.is_file())
                self.assertEqual(sorted(Path(d).iterdir()), sorted([src, out]))

    def test_active_or_ambiguous_claim_is_rejected(self):
        for value in (True, None, "false", 0):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    literature.require_unpromoted({"records": [{"claim_allowed": value}]})
        literature.require_unpromoted({"records": [{"claim_allowed": False}]})

    def test_seed_is_never_an_output(self):
        seed = Path("data/chronology/publication_seed.json")
        before = seed.read_bytes()
        with tempfile.TemporaryDirectory() as d:
            src = Path(d) / "baseline.json"
            src.write_text("{}", encoding="utf-8")
            with patch("sys.argv", ["cross", str(src), "--offline", "--output", str(seed)]), self.assertRaises(SystemExit):
                cross.main()
        self.assertEqual(seed.read_bytes(), before)
