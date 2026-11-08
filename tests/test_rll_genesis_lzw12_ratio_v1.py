"""RLL Genesis 1: ratio first, verified lossless codec, fail-closed pins."""
import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "genesis_ratio", ROOT / "tools/ci/rll_genesis_lzw12_ratio_v1.py")
module = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(module)


class GenesisLZW12Ratio(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = module.load_contract()

    def test_01_six_rates_are_original_divided_by_compressed(self):
        rows = module.audit(self.contract)
        expected = {
            "he": ((7413, 3243), (3929, 1683)),
            "arc": ((6628, 2583), (3896, 1670)),
            "grc": ((7944, 3401), (7300, 2859)),
        }
        for lang, two in expected.items():
            for variant, pair in zip(module.VARIANTS, two):
                row = rows[lang][variant]
                self.assertEqual((row["raw_bytes"], row["packed_bytes"]), pair)
                self.assertAlmostEqual(row["compression_ratio"], pair[0] / pair[1])

    def test_02_ratio_not_economy_percentage(self):
        for lang, entries in module.audit(self.contract).items():
            for variant, row in entries.items():
                ratio = row["compression_ratio"]
                savings = 1 - row["packed_bytes"] / row["raw_bytes"]
                self.assertGreater(ratio, 2, (lang, variant))
                self.assertLess(savings, 1)
                self.assertNotAlmostEqual(ratio, savings)

    def test_03_exact_bitrate_relation(self):
        for entries in module.audit(self.contract).values():
            for row in entries.values():
                self.assertAlmostEqual(row["compressed_bits_per_original_byte"],
                                       8 / row["compression_ratio"])

    def test_04_baseline_roundtrip_ascii(self):
        for payload in (b"ABAABABAAB", b"TOBEORNOTTOBEORTOBEORNOT",
                        bytes(range(256)) * 3):
            result = module.measure(payload)
            self.assertTrue(result["roundtrip"])

    def test_05_baseline_roundtrip_unicode_utf8(self):
        for s in ("שלום", "Ἐν ἀρχῇ", "בראשית", "abc 123 Ω"):
            self.assertTrue(module.measure(s.encode("utf-8"))["roundtrip"])

    def test_06_single_byte_overhead_not_linguistic_claim(self):
        result = module.measure(b"A")
        self.assertEqual((result["raw_bytes"], result["packed_bytes"]), (1, 2))

    def test_07_corrupt_packing_trapped(self):
        with self.assertRaises(ValueError):
            module.unpack12(b"\xff", 1)

    def test_08_padding_must_be_zero(self):
        packed = bytearray(module.pack12([1]))
        packed[-1] |= 0x0F
        with self.assertRaises(ValueError):
            module.unpack12(bytes(packed), 1)

    def test_09_empty_not_observation_zero(self):
        with self.assertRaises(ValueError):
            module.measure(b"")

    def test_10_diacritic_removal_is_distinct(self):
        text = "בְּרֵאשִׁית Ἐν ἀρχῇ"
        cleaned = module.remove_marks(text)
        self.assertNotEqual(text, cleaned)
        self.assertEqual(module.remove_marks(cleaned), cleaned)

    def test_11_verse_count_invariant(self):
        with self.assertRaises(ValueError):
            module.normalize_passage(["x"] * 30)
        self.assertEqual(module.normalize_passage(["x"] * 31).count("\n"), 31)

    def test_12_missing_source_fails(self):
        c = copy.deepcopy(self.contract)
        c["sources"].pop("arc")
        with self.assertRaises(ValueError):
            module.audit(c)

    def test_13_overpromoted_claim_fails(self):
        c = copy.deepcopy(self.contract)
        c["semantic_information_invariance_claim_allowed"] = True
        with self.assertRaises(ValueError):
            module.audit(c)

    def test_14_nonpinned_source_fails(self):
        c = copy.deepcopy(self.contract)
        c["sources"]["he"]["git_blob_sha1"] = "unknown"
        with self.assertRaises(ValueError):
            module.audit(c)

    def test_15_fixture_edit_detected(self):
        c = copy.deepcopy(self.contract)
        c["measurements"]["arc"]["vocalized"]["packed_bytes"] += 1
        with self.assertRaises(ValueError):
            module.audit(c)

    def test_16_frozen_commits_used_in_url(self):
        for lang, src in self.contract["sources"].items():
            url = module.pinned_url(src)
            self.assertIn("/" + src["commit"] + "/", url)
            self.assertNotIn("/main/", url)
            self.assertNotIn("/master/", url)

    def test_17_offline_result_is_not_real_linguistic_proof(self):
        c = module.audit(self.contract)
        self.assertEqual(len(c), 3)
        self.assertFalse(self.contract["claim_allowed"])
        self.assertFalse(self.contract["physical_cosmology_claim_allowed"])

    def test_18_lzw_known_symbol_case(self):
        packed, count = module.encode12(b"ABABA")
        self.assertEqual(module.decode12(packed, count), b"ABABA")
        self.assertEqual(count, 4)

    def test_19_verse_source_parsers_fail_closed(self):
        with self.assertRaises(ValueError):
            module.extract_verses("arc", b"Chapter 1\nHello\nChapter 2\n")
        with self.assertRaises(ValueError):
            module.extract_verses("grc", b"1.1.1 Genesis\n")

    def test_20_empty_falsifier(self):
        with self.assertRaises(ValueError):
            module.pack12([4096])
        with self.assertRaises(ValueError):
            module.decode12(b"\xff\xff", 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
