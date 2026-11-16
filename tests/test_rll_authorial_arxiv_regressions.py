import importlib.util
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "tools" / "ingest_arxiv_candidate.py"
spec = importlib.util.spec_from_file_location("ingest_arxiv_candidate", MODULE)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(mod)


def atom(entry_id: str) -> bytes:
    return (f'<feed xmlns="http://www.w3.org/2005/Atom"><entry>'
            f'<id>{entry_id}</id><title>Sample</title>'
            f'<summary>abstract</summary></entry></feed>').encode("utf-8")


class LegacyArxivAtomTests(unittest.TestCase):
    def test_legacy_id_preserved_from_atom(self):
        doc = mod.parse_arxiv_atom(atom("http://arxiv.org/abs/astro-ph/0601234v1"),
                                   "astro-ph/0601234")
        self.assertEqual(doc["returned_arxiv_id"], "astro-ph/0601234v1")
        self.assertEqual(doc["source_locator"], "https://arxiv.org/abs/astro-ph/0601234v1")

    def test_legacy_url_normalization(self):
        self.assertEqual(mod.normalize_arxiv_identifier(
            "https://arxiv.org/abs/astro-ph/0601234v1"),
            ("astro-ph/0601234", "v1"))
        self.assertEqual(mod.normalize_arxiv_identifier(
            "https://arxiv.org/pdf/astro-ph/0601234v1.pdf"),
            ("astro-ph/0601234", "v1"))

    def test_current_id_preserved(self):
        doc = mod.parse_arxiv_atom(atom("https://arxiv.org/abs/2503.14738v2"),
                                   "2503.14738")
        self.assertEqual(doc["returned_arxiv_id"], "2503.14738v2")

    def test_atom_malicious_domain_rejected(self):
        with self.assertRaises(ValueError):
            mod.parse_arxiv_atom(atom("https://arxiv.org.evil.example/abs/2503.14738"),
                                 "2503.14738")

    def test_candidate_accepts_matching_legacy(self):
        doc = mod.make_candidate(atom("http://arxiv.org/abs/astro-ph/0601234v1"),
                                 "astro-ph/0601234", [], "", {"nodes": []},
                                 "2026-11-16T00:00:00Z")
        self.assertEqual(doc["work_id"], "arxiv:astro-ph/0601234v1")
        self.assertFalse(doc["claim_allowed"])


if __name__ == "__main__":
    unittest.main()
