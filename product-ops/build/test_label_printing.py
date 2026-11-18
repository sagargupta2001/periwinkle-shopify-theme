"""Validate fixed-field PDF integrity and label integration ordering."""
import io
import re
import unittest

import build
from label_printing import FONT_WIDTH, SKU_WIDTH, pdf_for_sku
from test_build import action_name, references


class LabelPdfChecks(unittest.TestCase):
    def test_variable_length_skus_keep_valid_pdf_offsets_and_stream_lengths(self):
        from pypdf import PdfReader
        sizes = set()
        for sku in ["PBS-DUP-001", "PBS-SAR-999", "PBS-MIN-1000", "PBS-JEW-123456789", "PBS-HOM-" + "9" * 56]:
            pdf = pdf_for_sku(sku)
            sizes.add(len(pdf))
            reader = PdfReader(io.BytesIO(pdf), strict=True)
            self.assertEqual(len(reader.pages), 1)
            page = reader.pages[0]
            self.assertEqual(page.extract_text().strip(), sku)
            self.assertAlmostEqual(float(page.mediabox.width), 50 * 72 / 25.4, places=4)
            self.assertAlmostEqual(float(page.mediabox.height), 30 * 72 / 25.4, places=4)
            xref = int(re.search(rb"startxref\n(\d+)\n", pdf).group(1))
            self.assertEqual(pdf[xref:xref + 4], b"xref")
            entries = re.search(rb"xref\n0 6\n0000000000 65535 f \n(.*?)trailer", pdf, re.S).group(1).splitlines()
            for number, entry in enumerate(entries, 1):
                offset = int(entry.split()[0])
                self.assertTrue(pdf[offset:].startswith(f"{number} 0 obj\n".encode()))
            length, stream = re.search(rb"/Length (\d+) >>\nstream\n(.*?)endstream", pdf, re.S).groups()
            self.assertEqual(int(length), len(stream))
            font = float(re.search(rb"/F1 ([0-9. ]+) Tf", stream).group(1))
            self.assertAlmostEqual(font * len(sku) * .6, 120, places=5)
        self.assertEqual(len(sizes), 1)

    def test_unsupported_strings_are_never_truncated_or_injected_into_pdf(self):
        for sku in ["PBS-DUP-1", "PBS-DUP-(001)", "PBS-DUP-001\\", "PBS-DUP-001\n", "PBS-HOM-" + "1" * 57]:
            with self.assertRaises(ValueError):
                pdf_for_sku(sku)

    def test_label_preparation_follows_album_sharing_and_uses_only_sku(self):
        shortcut = build.new_product({"filename": "test"})
        actions = shortcut.actions
        share = next(i for i, a in enumerate(actions) if action_name(a) == "share")
        end = actions[share + 1:]
        self.assertFalse({"documentpicker.save", "file.move", "file.delete"}.intersection(action_name(a) for a in end))
        pdf = next(a["WFWorkflowActionParameters"] for a in end
                   if a["WFWorkflowActionParameters"].get("WFTextActionText", {}).get("Value", {}).get("string", "").startswith("%PDF-1.4"))
        self.assertEqual(len(list(references(pdf))), 2)  # font field and SKU field, never the intake caption
        self.assertNotIn("PRICE", str(pdf))
        calc = next(a["WFWorkflowActionParameters"] for a in end if action_name(a) == "calculateexpression")
        self.assertIn("Input", calc)
        self.assertNotIn("WFExpression", calc)

    def test_reprinting_is_read_only(self):
        shortcut = build.print_product_label({"filename": "test"})
        names = {action_name(a) for a in shortcut.actions}
        self.assertIn("documentpicker.open", names)
        self.assertFalse(names.intersection({"documentpicker.save", "file.move", "file.delete"}))


if __name__ == "__main__":
    unittest.main()
