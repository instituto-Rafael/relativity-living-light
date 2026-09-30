import importlib.util
import json
import os
from pathlib import Path
import random
import sqlite3
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("ingest", ROOT / "tools/reconstruction_v3/ingest.py")
INGEST = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(INGEST)

class ReconstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.dir = Path(cls.temp.name)
        cls.scan = cls.dir / "scan"
        cc = os.environ.get("CC", "cc")
        common = [cc, "-std=c99", "-Wall", "-Wextra", "-Werror"]
        core = str(ROOT / "native/reconstruction_v3/rv3.c")
        subprocess.run(common + ["-O2", core, str(ROOT / "tools/reconstruction_v3/scan.c"), "-o", str(cls.scan)], check=True)
        boundary = cls.dir / "boundaries"
        subprocess.run(common + [core, str(ROOT / "tests/reconstruction_v3/boundaries.c"), "-o", str(boundary)], check=True)
        subprocess.run([str(boundary)], check=True)
        obj = cls.dir / "kernel.o"
        subprocess.run(common + ["-O2", "-ffreestanding", "-fno-builtin", "-fno-stack-protector", "-c", core, "-o", str(obj)], check=True)
        symbols = subprocess.run(["nm", "-u", str(obj)], check=True, capture_output=True, text=True).stdout
        if symbols.strip():
            raise AssertionError("freestanding kernel has unresolved dependencies: " + symbols)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def run_scan(self, raw):
        source = self.dir / "input.json"
        source.write_bytes(raw)
        return subprocess.run([str(self.scan), str(source)], capture_output=True, text=True)

    def test_valid_and_offsets(self):
        raw = b'{"x": [1, -0.2e+4, null, true], "x":"\\uD83D\\uDE00"}'
        result = self.run_scan(raw)
        self.assertEqual(result.returncode, 0, result.stderr)
        rows = [list(map(int, line.split())) for line in result.stdout.splitlines()]
        for _, _, start, end, _, _, _ in rows:
            json.loads(raw[start:end])
        self.assertEqual(len(rows), 7)
        self.assertEqual(sum(row[5] >= 0 for row in rows), 2)

    def test_malformed_no_output(self):
        invalid = [b'', b'{', b'[1,]', b'{"a":1,}', b'{"a" 1}', b'01', b'1.', b'-',
                   b'true false', b'[false null]', b'"\\q"', b'"\\uDC00"',
                   b'"\\uD800"', b'"\xff"', b'"\xc0\x80"', b'"\xed\xa0\x80"',
                   b'"\xf4\x90\x80\x80"', b'"\n"', b'[[[[']
        for raw in invalid:
            with self.subTest(raw=raw):
                r = self.run_scan(raw)
                self.assertNotEqual(r.returncode, 0)
                self.assertEqual(r.stdout, '')

    def test_generated_documents(self):
        rng = random.Random(144)
        for _ in range(100):
            doc = {"items": [rng.randint(-1000, 1000), rng.random(), None, "Ω😀\\\""], "flag": True}
            raw = json.dumps(doc, ensure_ascii=rng.choice([True, False])).encode()
            r = self.run_scan(raw)
            self.assertEqual(r.returncode, 0, r.stderr)

    def test_private_database_reconstruction_and_gaps(self):
        raw = b'{"id":"t1","previous_turn_id":"absent","repo_id":"r","files":[{"path":"core/a.c","content":"int x;"},{"path":"../escape","content":"bad"},{"path":"missing.c","missing_reason":"unknown_error"}],"diff":null,"external_storage_diff":{"file_id":"external"},"math":"$$E^2(a)=1$$"}'
        path = self.dir / "corpus.json"
        path.write_bytes(raw)
        db = sqlite3.connect(":memory:")
        db.executescript(INGEST.SCHEMA)
        digest, status = INGEST.ingest(db, self.scan, path)
        self.assertEqual(status, "INGESTED")
        self.assertEqual(db.execute("SELECT bytes FROM sources").fetchone()[0], raw)
        self.assertEqual(INGEST.ingest(db, self.scan, path)[1], "ALREADY_PRESENT")
        self.assertEqual(db.execute("SELECT count(*) FROM ledger").fetchone()[0], 1)
        self.assertEqual(db.execute("SELECT count(*) FROM references_observed WHERE resolution='PENDING'").fetchone()[0], 3)
        self.assertEqual(db.execute("SELECT count(*) FROM observations WHERE category='gap_observation'").fetchone()[0], 1)
        self.assertEqual(db.execute("SELECT state FROM candidates").fetchone()[0], "AUDIT")
        export = self.dir / "export"
        INGEST.export_snapshots(db, export)
        files = list(export.rglob("a.c"))
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0].read_bytes(), b'int x;')
        self.assertFalse((self.dir / "escape").exists())
        self.assertEqual(db.execute("SELECT count(*) FROM snapshots").fetchone()[0], 2)
        path.write_bytes(b'{invalid')
        with self.assertRaises(subprocess.CalledProcessError):
            INGEST.ingest(db, self.scan, path)
        self.assertEqual(db.execute("SELECT count(*) FROM sources").fetchone()[0], 1)
        db.close()

    def test_duplicate_keys_not_silently_merged(self):
        path = self.dir / "duplicates.json"
        path.write_bytes(b'{"path":"a","path":"b","content":"x"}')
        db = sqlite3.connect(":memory:")
        db.executescript(INGEST.SCHEMA)
        INGEST.ingest(db, self.scan, path)
        self.assertEqual(db.execute("SELECT count(*) FROM tokens WHERE key='path'").fetchone()[0], 2)
        self.assertEqual(db.execute("SELECT count(*) FROM snapshots").fetchone()[0], 0)
        db.close()

if __name__ == '__main__':
    unittest.main()
