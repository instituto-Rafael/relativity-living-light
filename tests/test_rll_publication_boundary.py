from __future__ import annotations

import unittest

from tools.validate_rll_publication_boundary import denied_matches


class PublicationBoundaryTests(unittest.TestCase):
    def test_keystores_and_private_corpus_are_blocked(self) -> None:
        patterns = ["*.jks", "*.keystore", "**/conversations*.json", "**/*PRIVATE_CORPUS*"]
        blocked = denied_matches(
            [
                "android/release-key.jks",
                "secrets/debug.keystore",
                "data/conversations-004.json",
                "data/PRIVATE_CORPUS/raw.bin",
            ],
            patterns,
        )
        self.assertEqual(len(blocked), 4)

    def test_schemas_hash_receipts_and_docs_are_allowed(self) -> None:
        patterns = ["*.jks", "*.keystore", "**/conversations*.json"]
        self.assertEqual(
            denied_matches(
                ["schemas/result.schema.json", "docs/audit.md", "results/receipt.json"],
                patterns,
            ),
            [],
        )


if __name__ == "__main__":
    unittest.main()
