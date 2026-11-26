import hashlib
import json
import unittest

from tools.rll_literature_append_plan import plan_append
from tools.rll_literature_writer_preflight import blob


class LiteratureAppendPlanTests(unittest.TestCase):
    def setUp(self):
        self.doi = "10.1234/old"
        self.old = {"provider": "Crossref", "records": {self.doi: {
            "source": "https://doi.org/" + self.doi, "title": "Previous title",
            "claim_allowed": False, "questions": {}}}}
        self.raw = json.dumps(self.old, sort_keys=True).encode()
        self.sha = blob(self.raw)

    def search(self, query):
        if query.startswith("globular"):
            return [{"DOI": doi, "title": ["Globular cluster age"],
                     "abstract": "Age 13 Gyr"}
                    for doi in (self.doi, "10.1234/new")]
        return []

    def test_append_and_revision_are_separate(self):
        result = plan_append(self.raw, self.sha, self.search)
        candidate = json.loads(result["candidate"])
        self.assertEqual(candidate["records"][self.doi], self.old["records"][self.doi])
        self.assertEqual(candidate["added_dois"], ["10.1234/new"])
        self.assertEqual(candidate["baseline_sha256"], hashlib.sha256(self.raw).hexdigest())
        self.assertIn(self.doi, result["deferred_revisions"])
        self.assertEqual(result["deferred_revisions"][self.doi]["state"], "REVIEW_REQUIRED")
        self.assertEqual(result["receipt"]["state"], "CANDIDATE_REQUIRES_AUTHORITY")
        self.assertEqual(result["receipt"]["deferred_revision_count"], 1)
        self.assertFalse(result["receipt"]["write_allowed"])
        self.assertFalse(result["receipt"]["claim_allowed"])
        self.assertEqual(json.loads(self.raw), self.old)

    def test_stale_predecessor_never_searches(self):
        def forbidden(_):
            self.fail("search called for stale predecessor")
        result = plan_append(self.raw, "0" * 40, forbidden)
        self.assertIsNone(result["candidate"])
        self.assertEqual(result["receipt"]["reason"], "STALE_PREDECESSOR")

    def test_replay_is_noop(self):
        result = plan_append(self.raw, self.sha, lambda _: [])
        self.assertEqual(result["receipt"]["state"], "NOOP_NO_WRITE")
        self.assertEqual(result["deferred_revisions"], {})
        self.assertFalse(result["receipt"]["write_allowed"])

    def test_invalid_new_doi_is_rejected(self):
        def malformed(query):
            return [{"DOI": "10.bad/invalid", "title": ["Globular cluster age"]}] if query.startswith("globular") else []
        result = plan_append(self.raw, self.sha, malformed)
        self.assertIsNone(result["candidate"])
        self.assertEqual(result["receipt"]["state"], "REJECTED")
        self.assertFalse(result["receipt"]["write_allowed"])

    def test_deterministic_candidate_and_receipt(self):
        self.assertEqual(plan_append(self.raw, self.sha, self.search),
                         plan_append(self.raw, self.sha, self.search))
