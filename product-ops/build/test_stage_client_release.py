"""Client packaging must not distribute operator-account bindings or helpers."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import build
from stage_client_release import stage


class ClientRelease(unittest.TestCase):
    def package(self, root, binding):
        source = root / "signed"
        source.mkdir()
        shortcut = build.client_bundle(binding)
        (source / (shortcut.name + ".shortcut")).write_bytes(b"signed-fixture")
        return source, {"WFWorkflowActions": shortcut.actions}

    def test_stages_one_self_contained_client_file_and_actual_destination_in_readme(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); folder = {"filename": "client"}
            source, workflow = self.package(root, folder)
            with patch("stage_client_release.read_folder_reference", return_value=folder), patch("stage_client_release.read_workflow", return_value=workflow):
                manifest = stage(source, root / "client-recovered", root / "client-ref")
            self.assertEqual(list(manifest["files"]), ["Periwinkle - Client.shortcut"])
            self.assertIn("shortcuts → client-recovered", (root / "client-recovered/README.txt").read_text())
            self.assertEqual(json.loads((root / "client-recovered/manifest.json").read_text()), manifest)

    def test_wrong_account_is_rejected_before_any_shared_files_are_written(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, workflow = self.package(root, {"filename": "operator"})
            with patch("stage_client_release.read_folder_reference", return_value={"filename": "client"}), patch("stage_client_release.read_workflow", return_value=workflow):
                with self.assertRaisesRegex(ValueError, "client account"):
                    stage(source, root / "shared", root / "client-ref")
            self.assertFalse((root / "shared").exists())

    def test_extra_old_operation_files_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, _ = self.package(root, {"filename": "client"})
            (source / "Periwinkle – New Product.shortcut").write_bytes(b"old-signed-file")
            with self.assertRaisesRegex(ValueError, "unexpected"):
                stage(source, root / "shared", root / "client-ref")
            self.assertFalse((root / "shared").exists())

    def test_previous_build_is_not_relabelled_as_the_current_release(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); folder = {"filename": "client"}
            source, workflow = self.package(root, folder)
            workflow["WFWorkflowActions"][1]["WFWorkflowActionParameters"]["WFMenuPrompt"] = f"Periwinkle - Client (build {build.BUILD - 1})"
            with patch("stage_client_release.read_folder_reference", return_value=folder), patch("stage_client_release.read_workflow", return_value=workflow):
                with self.assertRaisesRegex(ValueError, "role menu"):
                    stage(source, root / "shared", root / "client-ref")
            self.assertFalse((root / "shared").exists())
