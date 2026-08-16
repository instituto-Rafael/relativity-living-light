import unittest

from scripts.validate_rll_auto_shadow_intake import validate


class AutoShadowIntakeTest(unittest.TestCase):
    def test_fail_closed_contract_and_candidate(self):
        self.assertEqual(validate(), [])


if __name__ == "__main__":
    unittest.main()
