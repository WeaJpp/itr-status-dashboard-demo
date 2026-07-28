import csv
import json
import tempfile
import unittest
from pathlib import Path

from src.itr_pipeline.adapters import CsvLedgerAdapter, XlsxLedgerAdapter
from src.itr_pipeline.engine import Pipeline
from src.itr_pipeline.models import LedgerRecord
from src.itr_pipeline.rules import identity_for_target, validate_identity


class DesktopImportTests(unittest.TestCase):
    def test_csv_aliases_and_revision_columns_are_normalized(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "ledger.csv"
            with path.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=["IR Number", "Location", "Activity", "status", "REV 00", "REV 01"],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "IR Number": "DEMO-GQC-IR-00001",
                        "Location": "Demo",
                        "Activity": "Track laying",
                        "status": "CODE-2",
                        "REV 00": "CODE-2",
                        "REV 01": "",
                    }
                )
            records = CsvLedgerAdapter(path).load()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].task_id, "ROW-00002")
        self.assertEqual(records[0].itr_id, "DEMO-GQC-IR-00001")
        self.assertEqual(records[0].revision_history["REV-00"], "CODE-2")

    def test_xlsx_active_sheet_import(self):
        try:
            from openpyxl import Workbook
        except ImportError:
            self.skipTest("openpyxl is only required for the desktop build")
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "ledger.xlsx"
            workbook = Workbook()
            sheet = workbook.active
            sheet.append(["IR Number", "Location", "Activity", "status", "REV-00", "REV-01"])
            sheet.append(["DEMO-GQC-IR-00001", "Demo", "Track laying", "UR", "UR", ""])
            workbook.save(path)
            workbook.close()
            records = XlsxLedgerAdapter(path).load()
        self.assertEqual(records[0].itr_id, "DEMO-GQC-IR-00001")


class ConfigurableIdentityTests(unittest.TestCase):
    def test_custom_contract_is_used_for_validation_and_revision(self):
        pattern = r"^(?P<base>ORG-GQC-IR-\d{5})(?:-(?P<revision>\d{2}))?$"
        record = LedgerRecord(
            task_id="T-1",
            site="Demo",
            site_zh="Demo",
            process="Inspection",
            process_zh="Inspection",
            itr_id="ORG-GQC-IR-00001",
            status="CODE-2",
            track="N/A",
            chainage="",
            submitted_date="",
            revision_history={"REV-00": "CODE-2", "REV-01": ""},
        )
        self.assertTrue(validate_identity(record, pattern)[0])
        self.assertEqual(identity_for_target(record, "REV-01", pattern), "ORG-GQC-IR-00001-01")

    def test_pipeline_emits_progress_events(self):
        root = Path(__file__).resolve().parents[1]
        events = []
        Pipeline(root, root / "config.example.json", observer=events.append).run()
        self.assertTrue(any(item["kind"] == "progress" for item in events))
        self.assertEqual(events[-1]["kind"], "complete")


if __name__ == "__main__":
    unittest.main()
