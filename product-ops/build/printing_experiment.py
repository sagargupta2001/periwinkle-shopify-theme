#!/usr/bin/env python3
"""Build a record-free iPhone experiment for NIIMBOT label handoff.

Run with the bundled Python runtime (Pillow/ReportLab are needed), then sign/import the
generated raw shortcut. These actions are experimental, not part of CLIENT.
"""
import argparse
import base64
import io
from pathlib import Path

from shortcutlib import Shortcut, attachment, text

APP_ID = "com.suofang.jcbqdy"  # Apple's lookup API, App Store ID 1359104615
TEST_SKU = "PBS-TEST-PRINT"
NAME = "New Product – Print Test v3"
PDF_NAME = "New Product – PDF Print Test"


def label_png():
    """A 50 x 30 mm example at 203 dpi; only synthetic identification text."""
    from PIL import Image, ImageDraw, ImageFont

    image = Image.new("RGB", (400, 240), "white")
    draw = ImageDraw.Draw(image)
    font_path = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
    font = ImageFont.truetype(font_path, 38)
    draw.text((200, 120), TEST_SKU, font=font, fill="black", anchor="mm")
    stream = io.BytesIO()
    image.save(stream, format="PNG", dpi=(203, 203))
    return stream.getvalue()


def label_pdf():
    """A single vector-text label with an exact 50 x 30 mm page size."""
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas

    stream = io.BytesIO()
    width, height = 50 * mm, 30 * mm
    page = canvas.Canvas(stream, pagesize=(width, height), invariant=1)
    page.setTitle(TEST_SKU)
    page.setFont("Helvetica-Bold", 14)
    page.drawCentredString(width / 2, height / 2 - 5, TEST_SKU)
    page.showPage()
    page.save()
    return stream.getvalue()


def build_pdf_test(pdf):
    s = Shortcut(PDF_NAME, color=2071128575)
    s.add("comment", WFCommentActionText=(
        "NIIMBOT PDF import test. Only the synthetic SKU PBS-TEST-PRINT is used. "
        "No product, stock, prices, photos or register files are read or changed. "
        "The PDF is one 50 x 30 mm page. App import and physical printing are separate tests."
    ))
    sku = s.add("gettext", output="Test SKU", WFTextActionText=text(TEST_SKU))
    app_id = s.add("gettext", output="NIIMBOT app ID", WFTextActionText=text(APP_ID))
    encoded = s.add("gettext", output="Label PDF base64",
                    WFTextActionText=text(base64.b64encode(pdf).decode("ascii")))
    decoded = s.add("base64encode", output="Label PDF", WFInput=attachment(encoded), WFEncodeMode="Decode")
    file = s.add("setitemname", output="PDF label", WFInput=attachment(decoded),
                 WFName="PBS-TEST-PRINT.pdf", WFDontIncludeFileExtension=False)
    menu = s.menu("PDF test only — no product will be created",
                  ["1 · Open PDF in NIIMBOT", "2 · Share PDF to NIIMBOT"])
    s.case(menu, "1 · Open PDF in NIIMBOT")
    s.add("setclipboard", WFInput=attachment(sku), WFLocalOnly=True)
    s.add("openin", WFInput=attachment(file), WFOpenInAskWhenRun=False, WFSelectedApp=attachment(app_id))
    s.case(menu, "2 · Share PDF to NIIMBOT")
    s.add("setclipboard", WFInput=attachment(sku), WFLocalOnly=True)
    s.add("share", WFInput=attachment(file))
    s.end_menu(menu)
    return s


def build_print_test(png):
    s = Shortcut(NAME, color=2071128575)
    s.add("comment", WFCommentActionText=(
        "NIIMBOT iPhone experiment. No products, prices, photos, files or stock records are read or changed. "
        "Only PBS-TEST-PRINT is copied/shared. Image is a 50 x 30 mm example; match the app's template to your roll. "
        "An app handoff is not proof of printing. Test each option separately on iPhone."
    ))
    sku = s.add("gettext", output="Test SKU", WFTextActionText=text(TEST_SKU))
    # A static app descriptor for an iPhone-only app is rebound to a different
    # app when imported on the Mac. Resolve the ID on the device at run time.
    app_id = s.add("gettext", output="NIIMBOT app ID", WFTextActionText=text(APP_ID))
    options = ["1 · Copy SKU and open NIIMBOT", "2 · Share SKU text",
               "3 · Share label image", "4 · Send image directly to NIIMBOT",
               "5 · Choose NIIMBOT on this iPhone"]
    menu = s.menu("Printing test only — no product will be created", options)
    for index, option in enumerate(options):
        s.case(menu, option)
        s.add("setclipboard", WFInput=attachment(sku), WFLocalOnly=True)
        if index == 0:
            s.add("openapp", WFSelectedApp=attachment(app_id))
        elif index == 1:
            s.add("share", WFInput=attachment(sku))
        elif index == 4:
            # Exact encoding exported from Apple's own Ask Each Time picker.
            s.add("openapp", WFSelectedApp={"Value": {"Type": "Ask"},
                                           "WFSerializationType": "WFTextTokenAttachment"})
        else:
            encoded = s.add("gettext", output="Label PNG base64",
                            WFTextActionText=text(base64.b64encode(png).decode("ascii")))
            decoded = s.add("base64encode", output="Label PNG", WFInput=attachment(encoded), WFEncodeMode="Decode")
            file = s.add("setitemname", output="Named label", WFInput=attachment(decoded),
                         WFName="PBS-TEST-PRINT.png", WFDontIncludeFileExtension=False)
            if index == 2:
                s.add("share", WFInput=attachment(file))
            else:
                s.add("openin", WFInput=attachment(file), WFOpenInAskWhenRun=False,
                      WFSelectedApp=attachment(app_id))
    s.end_menu(menu)
    return s


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--format", choices=["png", "pdf"], default="png")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    if args.format == "pdf":
        data = label_pdf()
        shortcut = build_pdf_test(data)
    else:
        data = label_png()
        shortcut = build_print_test(data)
    (args.output / ("PBS-TEST-PRINT." + args.format)).write_bytes(data)
    target = args.output / (shortcut.name + ".raw.shortcut")
    shortcut.write(target)
    print(target)


if __name__ == "__main__":
    main()
