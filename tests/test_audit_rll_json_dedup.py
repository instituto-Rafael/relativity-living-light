"""Adversarial tests for read-only git JSON/JSONL content dedup."""
from __future__ import annotations
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "audit_rll_json_dedup.py"
spec = importlib.util.spec_from_file_location("audit_json", SCRIPT)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], check=True, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE).stdout.decode().strip()


class JsonDedupAdversarialTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name)
        git(self.repo, "init", "-q")
        git(self.repo, "config", "user.name", "Test")
        git(self.repo, "config", "user.email", "test@example.invalid")

    def create(self, name, data):
        p = self.repo / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)

    def commit(self):
        git(self.repo, "add", "--all")
        git(self.repo, "commit", "-qm", "fixtures")

    def test_exact_raw_vs_canonical_vs_same_filename(self):
        self.create("a/data.json", b'{"x":1,"y":false}')
        self.create("b/data.json", b'{"x":1,"y":false}')
        self.create("c/data.json", b'{ "y": false, "x" : 1 }')
        self.create("d/data.json", b'{"x":1,"y":true}')
        self.commit()
        x = audit.inspect_repository(self.repo, "HEAD")
        self.assertEqual(x["counts"]["json_like_paths"], 4)
        self.assertEqual(x["counts"]["exact_git_blob_duplicate_groups"], 1)
        self.assertEqual(x["counts"]["extra_paths_sharing_git_blob"], 1)
        self.assertEqual(x["counts"]["canonical_different_oid_equal_groups"], 1)
        self.assertEqual(x["counts"]["parsed_files"], 4)
        self.assertEqual(x["counts"]["cross_file_record_equal_groups"], 1)
        self.assertFalse(x["boundary"]["claim_allowed"])

    def test_null_zero_false_empty_and_blank_not_equal(self):
        for i, literal in enumerate((b'null',b'0',b'false',b'""',b'"    "')):
            self.create(f"{i}.json",literal)
        self.commit()
        x = audit.inspect_repository(self.repo, "HEAD")
        self.assertEqual(x["counts"]["parsed_files"], 5)
        self.assertEqual(len({v["canonical_json_sha256"] for v in x["file_receipts"]}),5)

    def test_jsonl_line_order_is_not_deduplicated(self):
        self.create("first.jsonl",b'{"n":1}\n{"n":2}\n')
        self.create("second.jsonl",b'{"n":2}\n{"n":1}\n')
        self.create("third.jsonl.txt",b'{"n":1}\n{"n":2}\n')
        self.commit()
        x = audit.inspect_repository(self.repo, "HEAD")
        self.assertEqual(x["counts"]["exact_git_blob_duplicate_groups"],1)
        self.assertEqual(x["counts"]["canonical_different_oid_equal_groups"],0)
        self.assertEqual(x["counts"]["cross_file_record_equal_groups"],2)

    def test_bad_json_and_duplicate_keys_do_not_canonicalize(self):
        self.create("bad.json", b'{"n":NaN}')
        self.create("repeat.json", b'{"a":1,"a":2}')
        self.create("empty.jsonl", b' \n \n')
        self.create("valid.json", b'{"a":1}')
        self.commit()
        x=audit.inspect_repository(self.repo,"HEAD")
        self.assertEqual(x["counts"]["parsed_files"],1)
        self.assertEqual(x["counts"]["parse_failed_unique_blobs"],3)
        self.assertTrue(all(v["canonical_json_sha256"] is None for v in x["file_receipts"] if v["state"]=="PARSE_FAILED"))

    def test_same_blob_in_json_and_jsonl_has_separate_parsers(self):
        self.create("one.json", b'{"n":1}\n{ "n":2 }\n')
        self.create("two.jsonl", b'{"n":1}\n{ "n":2 }\n')
        self.commit()
        x = audit.inspect_repository(self.repo, "HEAD")
        self.assertEqual(x["counts"]["exact_git_blob_duplicate_groups"],1)
        self.assertEqual(x["counts"]["parsed_files"],1)
        self.assertEqual(x["counts"]["parse_failed_unique_blobs"],1)

    def test_limit_skips_without_fabricating_digest(self):
        self.create("large.json",b'{"x": "' + b'1'*512 + b'"}')
        self.commit()
        x=audit.inspect_repository(self.repo,"HEAD",max_file_bytes=32)
        self.assertEqual(x["counts"]["size_limit_files"],1)
        self.assertIsNone(x["file_receipts"][0]["raw_sha256"])

    def test_symlink_ignored(self):
        self.create("src.json", b'{"n":1}')
        (self.repo/"link.json").symlink_to("src.json")
        self.commit()
        x=audit.inspect_repository(self.repo,"HEAD")
        self.assertEqual(x["counts"]["json_like_paths"],1)
        self.assertEqual(x["counts"]["symlink_skipped"],1)

    def test_cli_refuses_overwrite_and_no_source_mutation(self):
        self.create("src.json",b'{"n":1}')
        self.commit()
        receipt=self.repo.parent/"dedup_test_output.json"
        self.addCleanup(lambda:receipt.unlink(missing_ok=True))
        args=[sys.executable,str(SCRIPT),"--repo",str(self.repo),"--output",str(receipt)]
        a=subprocess.run(args,capture_output=True,text=True)
        b=subprocess.run(args,capture_output=True,text=True)
        self.assertEqual(a.returncode,0)
        self.assertEqual(b.returncode,2)
        self.assertIn("BLOCKED",b.stderr)
        self.assertEqual(git(self.repo,"status","--porcelain"),"")
        self.assertFalse(json.loads(receipt.read_text())["boundary"]["claim_allowed"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
