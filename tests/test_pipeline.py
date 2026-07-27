import json
import tempfile
import unittest
from pathlib import Path

from src.itr_pipeline.engine import Pipeline
from src.itr_pipeline.models import LedgerRecord
from src.itr_pipeline.rules import (
    compute_revision_target,
    identity_for_target,
    normalize_status,
    resolve_final_submission,
    validate_identity,
)


def make_record(**changes):
    values = {
        "task_id": "T-1",
        "itr_id": "DEMO-GQC-IR-00002",
        "site": "Demo",
        "site_zh": "样例",
        "process": "Track laying",
        "process_zh": "铺轨",
        "status": "CODE-2",
        "track": "Right",
        "chainage": "K1+000",
        "submitted_date": "2026-07-20",
        "revision_history": {"REV-00": "CODE-2", "REV-01": "", "REV-02": ""},
    }
    values.update(changes)
    return LedgerRecord(**values)


class RulesTests(unittest.TestCase):
    def test_exact_status_mapping(self):
        self.assertEqual(normalize_status("Issued For Inspection"), "UR")
        self.assertEqual(normalize_status("Ready for Sign Out"), "READY")

    def test_pending_is_rejected(self):
        valid, _ = validate_identity(make_record(itr_id="pending"))
        self.assertFalse(valid)

    def test_cancelled_submission_is_not_a_status(self):
        status, _ = resolve_final_submission({"submissions": [
            {"label": "CODE-4", "lifecycle": "Cancelled"},
            {"label": "CODE-1", "lifecycle": "Active"},
        ]})
        self.assertEqual(status, "CODE-1")

    def test_conflicting_final_labels_fail_closed(self):
        with self.assertRaises(ValueError):
            resolve_final_submission({"submissions": [
                {"labels": ["CODE-1", "CODE-2"], "lifecycle": "Active"}
            ]})

    def test_transition_uses_next_revision(self):
        self.assertEqual(compute_revision_target(make_record(), "CODE-1"), "REV-01")

    def test_missing_next_revision_blocks_writeback(self):
        with self.assertRaises(ValueError):
            compute_revision_target(
                make_record(revision_history={"REV-00": "CODE-2"}), "CODE-1"
            )

    def test_base_identity_is_not_truncated(self):
        self.assertEqual(
            identity_for_target(make_record(), "REV-01"),
            "DEMO-GQC-IR-00002-01",
        )

    def test_special_20_suffix_is_preserved(self):
        item = make_record(itr_id="DEMO-GQC-IR-00015-20")
        self.assertEqual(identity_for_target(item, "REV-01"), item.itr_id)


class PipelineTests(unittest.TestCase):
    def test_public_pipeline_runs_without_writeback(self):
        root = Path(__file__).resolve().parents[1]
        result = Pipeline(root, root / "config.example.json").run()
        self.assertEqual(result["summary"]["source_rows"], 16)
        self.assertEqual(result["summary"]["scanned"], 11)
        self.assertEqual(result["summary"]["unresolved"], 1)
        self.assertNotIn("T-016", result["safety"]["portal_queries"])
        self.assertFalse(result["safety"]["writeback_enabled"])
        self.assertTrue((root / "public/data/dashboard.json").exists())

    def test_writeback_must_be_disabled(self):
        root = Path(__file__).resolve().parents[1]
        config = json.loads((root / "config.example.json").read_text(encoding="utf-8"))
        config["writeback"]["enabled"] = True
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "config.json"
            path.write_text(json.dumps(config), encoding="utf-8")
            with self.assertRaises(ValueError):
                Pipeline(root, path).run()


if __name__ == "__main__":
    unittest.main()
