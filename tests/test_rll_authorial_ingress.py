import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "tools" / "rll_authorial_ingress.py"
spec = importlib.util.spec_from_file_location("rll_authorial_ingress", MODULE)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)


class TestRllAuthorialIngress(unittest.TestCase):
    def good(self):
        return {
            "schema": mod.SCHEMA,
            "sources": [
                {
                    "id": "x",
                    "kind": "pdf",
                    "url": "https://example.org/x.pdf",
                    "filename": "x.pdf",
                    "expected_sha256": mod.TOKEN_VAZIO,
                    "max_bytes": 1024,
                    "credential_profile": "none",
                    "authority": "example",
                    "license": mod.TOKEN_VAZIO,
                }
            ],
        }

    def test_good_manifest(self):
        self.assertEqual(mod.validate_manifest(self.good()), [])

    def test_http_rejected(self):
        doc = self.good()
        doc["sources"][0]["url"] = "http://example.org/x.pdf"
        self.assertTrue(any("https" in error for error in mod.validate_manifest(doc)))

    def test_bad_hash_rejected(self):
        doc = self.good()
        doc["sources"][0]["expected_sha256"] = "abc"
        self.assertTrue(
            any("expected_sha256" in error for error in mod.validate_manifest(doc))
        )

    def test_pat_is_github_contents_only(self):
        doc = self.good()
        doc["sources"][0]["credential_profile"] = "pat_actions"
        self.assertTrue(
            any("api.github.com" in error for error in mod.validate_manifest(doc))
        )

    def test_kind_signatures(self):
        self.assertTrue(mod._kind_check("pdf", b"%PDF-1.7\n"))
        self.assertTrue(mod._kind_check("image", b"\x89PNG\r\n\x1a\nabc"))
        self.assertFalse(mod._kind_check("pdf", b"not a pdf"))

    def test_token_vazio_requires_explicit_discovery_flag(self):
        source = self.good()["sources"][0]
        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaises(ValueError):
                mod.acquire_source(source, Path(temp_dir), None, False)


if __name__ == "__main__":
    unittest.main()
