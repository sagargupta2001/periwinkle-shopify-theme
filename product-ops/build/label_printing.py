"""Build a SKU-only PDF on iPhone using native Shortcuts actions.

PDF text and font-size fields have fixed byte widths, so replacing them does
not change stream lengths or cross-reference offsets. The allowed ASCII SKU
alphabet needs no PDF string escaping. No server or Python runs on the phone.
"""
import re

from shortcutlib import NO_VALUE, attachment, text

APP_ID = "com.suofang.jcbqdy"
SKU_WIDTH = 64
FONT_WIDTH = 12
SKU_MARKER = "S" * SKU_WIDTH
FONT_MARKER = "F" * FONT_WIDTH
LABEL_SKU_RULE = r"^PBS-[A-Z]{3}-[0-9]{3,56}$"


def pdf_template():
    """A 50 x 30 mm PDF; Courier-Bold makes runtime width calculation exact."""
    stream = ("BT\n/F1 " + FONT_MARKER + " Tf\n10.866142 36 Td\n("
              + SKU_MARKER + ") Tj\nET\n")
    objects = [
        "<< /Type /Catalog /Pages 2 0 R >>",
        "<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 141.732284 85.039370] "
        "/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        "<< /Type /Font /Subtype /Type1 /BaseFont /Courier-Bold >>",
        f"<< /Length {len(stream)} >>\nstream\n{stream}endstream",
    ]
    document, offsets = "%PDF-1.4\n", [0]
    for index, obj in enumerate(objects, 1):
        offsets.append(len(document.encode("ascii")))
        document += f"{index} 0 obj\n{obj}\nendobj\n"
    xref = len(document.encode("ascii"))
    document += f"xref\n0 {len(offsets)}\n0000000000 65535 f \n"
    document += "".join(f"{offset:010d} 00000 n \n" for offset in offsets[1:])
    document += f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n"
    return document


def pdf_for_sku(sku):
    """Equivalent fixed-field rendering for build-time validation and preview."""
    if not re.fullmatch(LABEL_SKU_RULE, sku):
        raise ValueError("Expected a generated Periwinkle SKU, up to 64 ASCII characters")
    font = (str(200 / len(sku)) + " " * FONT_WIDTH)[:FONT_WIDTH]
    return pdf_template().replace(FONT_MARKER, font).replace(SKU_MARKER, sku.ljust(SKU_WIDTH)).encode("ascii")


def add_label_handoff(s, sku):
    """Append a retryable app handoff; this function never touches records."""
    s.add("setclipboard", WFInput=attachment(sku), WFLocalOnly=True)
    valid = s.add("text.match", output="Printable SKU", text=text(sku),
                  WFMatchTextPattern=LABEL_SKU_RULE, WFMatchTextCaseSensitive=True)
    invalid = s.if_(valid, NO_VALUE)
    s.add("alert", WFAlertActionTitle="Label could not be prepared",
          WFAlertActionMessage="The SKU was copied. Check it before making a label manually. Do not submit the product again.",
          WFAlertActionCancelButtonShown=False)
    s.add("exit")
    s.end_if(invalid)

    padded = s.add("gettext", output="Padded SKU", WFTextActionText=text(sku, " " * SKU_WIDTH))
    sku_slot = s.add("text.match", output="PDF SKU field", text=text(padded),
                     WFMatchTextPattern=f"^.{{{SKU_WIDTH}}}", WFMatchTextCaseSensitive=True)
    length = s.add("count", output="SKU length", Input=attachment(sku), WFCountType="Characters")
    font = s.add("calculateexpression", output="Label font size", Input=text("200 / ", length))
    # Shortcuts formats numbers using the phone's locale. PDF requires a dot.
    font_ascii = s.add("text.replace", output="PDF font size", WFInput=text(font), WFReplaceTextFind=",",
                       WFReplaceTextReplace=".", WFReplaceTextRegularExpression=False, WFReplaceTextCaseSensitive=True)
    padded_font = s.add("gettext", output="Padded font", WFTextActionText=text(font_ascii, " " * FONT_WIDTH))
    font_slot = s.add("text.match", output="PDF font field", text=text(padded_font),
                      WFMatchTextPattern=f"^.{{{FONT_WIDTH}}}", WFMatchTextCaseSensitive=True)
    before, rest = pdf_template().split(FONT_MARKER)
    middle, after = rest.split(SKU_MARKER)
    pdf = s.add("gettext", output="SKU label PDF", WFTextActionText=text(before, font_slot, middle, sku_slot, after))
    file = s.add("setitemname", output="SKU label", WFInput=attachment(pdf),
                 WFName=text(sku, ".pdf"), WFDontIncludeFileExtension=False)
    app_id = s.add("gettext", output="NIIMBOT app ID", WFTextActionText=text(APP_ID))
    s.add("openin", WFInput=attachment(file), WFOpenInAskWhenRun=False, WFSelectedApp=attachment(app_id))
