import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from tools import rll_literature_writer_preflight as gate


class WriterPreflightTests(unittest.TestCase):
    def setUp(self):
        self.doi = "10.1234/old"
        self.old = {"records": {self.doi: self.record(self.doi)}, "provider": "Crossref"}
        self.raw = self.encode(self.old)
        self.expected = gate.blob(self.raw)

    @staticmethod
    def record(doi):
        return {"source": "https://doi.org/" + doi, "claim_allowed": False}

    @staticmethod
    def encode(value):
        return json.dumps(value, sort_keys=True).encode()

    def check(self, candidate, expected=None):
        raw = candidate if isinstance(candidate, bytes) else self.encode(candidate)
        result = gate.preflight(self.raw, raw, self.expected if expected is None else expected)
        self.assertFalse(result["write_allowed"])
        self.assertFalse(result["claim_allowed"])
        self.assertEqual(result["writer_execution"], "NOT_RUN")
        return result

    def test_noop_and_stale(self):
        self.assertEqual(self.check(self.old)["state"], "NOOP_NO_WRITE")
        self.assertEqual(self.check(self.old, "0" * 40)["reason"], "STALE_PREDECESSOR")
        self.assertEqual(gate.preflight(self.raw + b" ", self.raw, self.expected)["reason"], "STALE_PREDECESSOR")

    def test_record_falsifiers(self):
        for mutate, reason in (
            (lambda d: d["records"].clear(), "RECORD_REMOVAL"),
            (lambda d: d["records"][self.doi].update(title="changed"), "UNARCHIVED_RECORD_MUTATION"),
            (lambda d: d["records"][self.doi].update(claim_allowed=True), "CLAIM_NOT_FALSE"),
            (lambda d: d["records"][self.doi].pop("claim_allowed"), "DOI_RECORD_CONTRACT"),
            (lambda d: d["records"].update({"10.1234/ALIAS": self.record("10.1234/ALIAS")}), "DOI_RECORD_CONTRACT"),
            (lambda d: d.update(provider="other"), "UNREVIEWED_METADATA_CHANGE"),
        ):
            with self.subTest(reason=reason):
                c = copy.deepcopy(self.old)
                mutate(c)
                self.assertEqual(self.check(c)["reason"], reason)

    def test_duplicate_and_nonfinite(self):
        self.assertEqual(self.check(b'{"records":{},"records":{}}')["reason"], "DUPLICATE_JSON_KEY")
        self.assertEqual(self.check(b'{"records":{},"x":NaN}')["reason"], "NONFINITE_JSON")
        self.assertEqual(self.check(b'{"records":{},"retrieved_utc":1e999}')["reason"], "NONFINITE_JSON")

    def test_new_record_requires_authority_and_binding(self):
        c = copy.deepcopy(self.old)
        doi = "10.1234/new"
        c["records"][doi] = self.record(doi)
        self.assertEqual(self.check(c)["reason"], "DELTA_BINDING_MISMATCH")
        c.update(added_dois=[doi], baseline_sha256=hashlib.sha256(self.raw).hexdigest())
        self.assertEqual(self.check(c)["state"], "CANDIDATE_REQUIRES_AUTHORITY")

    def test_cli_never_writes(self):
        with tempfile.TemporaryDirectory() as d:
            a, b = Path(d) / "old.json", Path(d) / "candidate.json"
            a.write_bytes(self.raw)
            b.write_bytes(self.raw)
            result = subprocess.run([sys.executable, "-I", str(Path(gate.__file__)), "--baseline", str(a),
                                     "--candidate", str(b), "--expected-blob", self.expected],
                                    capture_output=True, text=True, check=True)
            self.assertEqual(json.loads(result.stdout)["state"], "NOOP_NO_WRITE")
            self.assertEqual(a.read_bytes(), self.raw)
            self.assertEqual(b.read_bytes(), self.raw)
            self.assertEqual(set(Path(d).iterdir()), {a, b})
