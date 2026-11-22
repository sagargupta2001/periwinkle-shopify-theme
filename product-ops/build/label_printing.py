"""Build a SKU and selling-price PDF on iPhone using native Shortcuts actions.

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
PRICE_WIDTH = 64
PRICE_MARKER = "P" * PRICE_WIDTH
PRICE_FONT_MARKER = "G" * FONT_WIDTH
LABEL_SKU_RULE = r"^PBS-[A-Z]{3}-[0-9]{3,56}$"
LABEL_PRICE_RULE = r"^(?=[0-9.]*[1-9])[0-9]{1,56}(?:\.[0-9]{1,2})?$"


def pdf_template():
    """A 50 x 30 mm PDF; Courier-Bold makes runtime width calculation exact."""
    # ASCII Rs. is deliberate: the standard PDF Courier font has no rupee glyph.
    # Both lines are centred; the price is narrower than the SKU.
    stream = ("BT\n/F1 " + FONT_MARKER + " Tf\n10.866142 51 Td\n("
              + SKU_MARKER + ") Tj\nET\nBT\n/F1 " + PRICE_FONT_MARKER
              + " Tf\n34.866142 23 Td\n(" + PRICE_MARKER + ") Tj\nET\n")
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


def pdf_for_sku(sku, selling_price):
    """Equivalent fixed-field rendering for build-time validation and preview."""
    if not re.fullmatch(LABEL_SKU_RULE, sku):
        raise ValueError("Expected a generated Periwinkle SKU, up to 64 ASCII characters")
    price = str(selling_price)
    if not re.fullmatch(LABEL_PRICE_RULE, price):
        raise ValueError("Expected a positive selling price with at most two decimal places")
    price = "Rs. " + price
    font = (str(200 / len(sku)) + " " * FONT_WIDTH)[:FONT_WIDTH]
    price_font = (str(120 / len(price)) + " " * FONT_WIDTH)[:FONT_WIDTH]
    return (pdf_template().replace(FONT_MARKER, font).replace(SKU_MARKER, sku.ljust(SKU_WIDTH))
            .replace(PRICE_FONT_MARKER, price_font).replace(PRICE_MARKER, price.ljust(PRICE_WIDTH)).encode("ascii"))


def add_label_handoff(s, sku, selling_price):
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

    # Materialize dictionary numbers before validation. Reject unexpected locale
    # formatting instead of silently changing a decimal separator or price.
    price = s.add("gettext", output="Label selling price", WFTextActionText=text(selling_price))
    valid_price = s.add("text.match", output="Printable selling price", text=text(price),
                        WFMatchTextPattern=LABEL_PRICE_RULE, WFMatchTextCaseSensitive=True)
    invalid_price = s.if_(valid_price, NO_VALUE)
    s.add("alert", WFAlertActionTitle="Label price could not be prepared",
          WFAlertActionMessage="The SKU was copied. Check the current selling price in the register. Labels require a positive number with at most two decimal places. Do not submit the product again.",
          WFAlertActionCancelButtonShown=False)
    s.add("exit")
    s.end_if(invalid_price)
    price_text = s.add("gettext", output="Label price line", WFTextActionText=text("Rs. ", price))

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
    padded_price = s.add("gettext", output="Padded price", WFTextActionText=text(price_text, " " * PRICE_WIDTH))
    price_slot = s.add("text.match", output="PDF price field", text=text(padded_price),
                       WFMatchTextPattern=f"^.{{{PRICE_WIDTH}}}", WFMatchTextCaseSensitive=True)
    price_length = s.add("count", output="Price line length", Input=attachment(price_text), WFCountType="Characters")
    price_font = s.add("calculateexpression", output="Price font size", Input=text("120 / ", price_length))
    price_font_ascii = s.add("text.replace", output="PDF price font size", WFInput=text(price_font), WFReplaceTextFind=",",
                            WFReplaceTextReplace=".", WFReplaceTextRegularExpression=False, WFReplaceTextCaseSensitive=True)
    padded_price_font = s.add("gettext", output="Padded price font", WFTextActionText=text(price_font_ascii, " " * FONT_WIDTH))
    price_font_slot = s.add("text.match", output="PDF price font field", text=text(padded_price_font),
                            WFMatchTextPattern=f"^.{{{FONT_WIDTH}}}", WFMatchTextCaseSensitive=True)
    before, rest = pdf_template().split(FONT_MARKER)
    sku_before, rest = rest.split(SKU_MARKER)
    price_font_before, rest = rest.split(PRICE_FONT_MARKER)
    price_before, after = rest.split(PRICE_MARKER)
    pdf = s.add("gettext", output="Product label PDF", WFTextActionText=text(
        before, font_slot, sku_before, sku_slot, price_font_before, price_font_slot, price_before, price_slot, after))
    file = s.add("setitemname", output="SKU label", WFInput=attachment(pdf),
                 WFName=text(sku, ".pdf"), WFDontIncludeFileExtension=False)
    app_id = s.add("gettext", output="NIIMBOT app ID", WFTextActionText=text(APP_ID))
    s.add("openin", WFInput=attachment(file), WFOpenInAskWhenRun=False, WFSelectedApp=attachment(app_id))
