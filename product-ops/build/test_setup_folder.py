"""Verify complete empty-folder recovery without overwriting existing records."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class FolderSetup(unittest.TestCase):
    def run_setup(self, root):
        subprocess.run([sys.executable, str(Path(__file__).with_name("setup_folder.py")), str(root)],
                       check=True, capture_output=True, text=True)

    def test_recreates_the_entire_empty_operations_structure(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "Periwinkle Product Operations"
            self.run_setup(root)
            for folder in ["products", "products/_cancelled", "log", "views", "photo-links", "photo-pending", "shortcuts",
                           "register/NEW", "register/IN_PROGRESS", "register/READY_TO_PUBLISH", "register/LIVE",
                           "register/_replaced", "register/_cancelled", "stock-requests/PENDING",
                           "stock-requests/COMPLETED", "stock-requests/REJECTED", "stock-requests/_handled"]:
                self.assertTrue((root / folder / "_keep.txt").is_file(), folder)
            self.assertEqual(json.loads((root / "settings.json").read_text())["defaultCurrency"], "INR")
            self.assertTrue(all(value == 0 for value in json.loads((root / "sku-start.json").read_text()).values()))

    def test_rerun_preserves_records_photo_references_and_sku_high_water_marks(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.run_setup(root)
            payloads = {
                "settings.json": '{"defaultCurrency":"INR","custom":true}',
                "sku-start.json": '{"SAR":408,"MIN":1000}',
                "products/pbs-sar-409.json": '{"sku":"PBS-SAR-409"}',
                "photo-links/pbs-sar-409.json": '{"source":"shared_album_confirmed","photoName":"upload-uuid"}',
                "photo-pending/pbs-min-1001.json": '{"state":"pending","beforeNames":"␟existing␟"}',
            }
            for name, content in payloads.items():
                (root / name).write_text(content)
            # Simulate accidentally losing an empty structural folder.
            (root / "views/_keep.txt").unlink()
            (root / "views").rmdir()
            self.run_setup(root)
            for name, content in payloads.items():
                self.assertEqual((root / name).read_text(), content, name)
            self.assertTrue((root / "views/_keep.txt").is_file())
