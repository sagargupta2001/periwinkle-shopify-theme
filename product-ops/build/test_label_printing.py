"""Validate fixed-field PDF integrity and label integration ordering."""
import io
import re
import unittest

import build
from label_printing import pdf_for_sku
from test_build import action_name, references


class LabelPdfChecks(unittest.TestCase):
    def test_variable_length_skus_keep_valid_pdf_offsets_and_stream_lengths(self):
        from pypdf import PdfReader
        sizes = set()
        examples = [("PBS-DUP-001", "3500"), ("PBS-SAR-999", "4999.50"),
                    ("PBS-MIN-1000", "1"), ("PBS-JEW-123456789", "0.01"),
                    ("PBS-HOM-" + "9" * 56, "9" * 56 + ".99")]
        for sku, price in examples:
            pdf = pdf_for_sku(sku, price)
            sizes.add(len(pdf))
            reader = PdfReader(io.BytesIO(pdf), strict=True)
            self.assertEqual(len(reader.pages), 1)
            page = reader.pages[0]
            self.assertEqual([line.strip() for line in page.extract_text().strip().splitlines()], [sku, "Rs. " + price])
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
            font, price_font = [float(value) for value in re.findall(rb"/F1 ([0-9. ]+) Tf", stream)]
            self.assertAlmostEqual(font * len(sku) * .6, 120, places=5)
            self.assertAlmostEqual(price_font * len("Rs. " + price) * .6, 72, places=5)
            positions = [tuple(map(float, pair)) for pair in re.findall(rb"([0-9.]+) ([0-9.]+) Td", stream)]
            self.assertGreater(positions[0][1], positions[1][1] + price_font)
        self.assertEqual(len(sizes), 1)

    def test_unsupported_strings_are_never_truncated_or_injected_into_pdf(self):
        for sku in ["PBS-DUP-1", "PBS-DUP-(001)", "PBS-DUP-001\\", "PBS-DUP-001\n", "PBS-HOM-" + "1" * 57]:
            with self.assertRaises(ValueError):
                pdf_for_sku(sku, "3500")

    def test_invalid_prices_cannot_be_injected_truncated_or_silently_reinterpreted(self):
        for price in ["", "0", "0.00", "-1", "3,500", "3500,50", "NaN", "1e3", "10.123", "3500\n", "3500) Tj", "9" * 57]:
            with self.subTest(price=price), self.assertRaises(ValueError):
                pdf_for_sku("PBS-SAR-001", price)

    def test_label_preparation_follows_album_sharing_and_contains_two_fixed_lines(self):
        shortcut = build.new_product({"filename": "test"})
        actions = shortcut.actions
        share = next(i for i, a in enumerate(actions) if action_name(a) == "share")
        end = actions[share + 1:]
        self.assertFalse({"file.move", "file.delete"}.intersection(action_name(a) for a in end))
        for action in end:
            if action_name(action) == "documentpicker.save":
                path = action["WFWorkflowActionParameters"]["WFFileDestinationPath"]["Value"]["string"]
                self.assertTrue(path.startswith(("photo-links/", "photo-pending/")), path)
        pdf = next(a["WFWorkflowActionParameters"] for a in end
                   if a["WFWorkflowActionParameters"].get("WFTextActionText", {}).get("Value", {}).get("string", "").startswith("%PDF-1.4"))
        self.assertEqual(len(list(references(pdf))), 4)  # two fonts and two text fields
        self.assertNotIn("COST PRICE", str(pdf))
        calc = next(a["WFWorkflowActionParameters"] for a in end if action_name(a) == "calculateexpression")
        self.assertIn("Input", calc)
        self.assertNotIn("WFExpression", calc)

    def test_reprinting_is_read_only(self):
        shortcut = build.print_product_label({"filename": "test"})
        names = {action_name(a) for a in shortcut.actions}
        self.assertIn("documentpicker.open", names)
        self.assertFalse(names.intersection({"documentpicker.save", "file.move", "file.delete"}))

    def test_reprints_use_current_register_selling_price_instead_of_original_submission(self):
        shortcut = build.print_product_label({"filename": "test"})
        params = [a["WFWorkflowActionParameters"] for a in shortcut.actions]
        paths = [p["WFGetFilePath"]["Value"]["string"] for p in params if "WFGetFilePath" in p]
        self.assertTrue(any(path.startswith("register/NEW/") for path in paths))
        self.assertFalse(any(path.startswith("products") for path in paths))
        self.assert_price_source(shortcut, "sellingPrice")

    def assert_price_source(self, shortcut, expected_key):
        actions = shortcut.actions
        by_uuid = {a["WFWorkflowActionParameters"]["UUID"]: a for a in actions}
        price_lines = [a for a in actions if a["WFWorkflowActionParameters"].get("WFTextActionText", {}).get("Value", {}).get("string") == "Rs. ￼"]
        self.assertEqual(len(price_lines), 1)
        pending = list(references(price_lines[0]["WFWorkflowActionParameters"]))
        reached = set()
        while pending:
            node = pending.pop()
            if node in reached: continue
            reached.add(node)
            pending.extend(references(by_uuid[node]["WFWorkflowActionParameters"]))
        keys = {by_uuid[node]["WFWorkflowActionParameters"].get("WFDictionaryKey") for node in reached}
        self.assertIn(expected_key, keys)
        self.assertNotIn("costPrice", keys)

    def test_operator_register_print_uses_selling_price_without_cost(self):
        shortcut = build.Store("Details", {"filename": "test"}, build.BLUE)
        build.register_product_details(shortcut, build.named("key"))
        self.assert_price_source(shortcut, "sellingPrice")


if __name__ == "__main__":
    unittest.main()
