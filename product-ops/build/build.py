#!/usr/bin/env python3
"""Builds and signs the Periwinkle shortcuts for one iCloud account.

    python3 build.py <folderref.shortcut> <output dir> [--role client|operator|all] [--only NAME]

<folderref.shortcut> is a shortcut made on that person's iPhone, holding one
"Get Contents of Folder" action pointed at the shared folder. See
docs/product-operations/building-and-signing.md, which also lists the iPhone
behaviours these shortcuts are written around.
"""
import argparse
import os
import plistlib
import struct
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shortcutlib import HAS_VALUE, IS, IS_NOT, NO_VALUE, REPEAT_ITEM, Shortcut, attachment, named, text

STATUSES = ["NEW", "IN_PROGRESS", "READY_TO_PUBLISH", "LIVE"]
REQUEST_STATUSES = ["PENDING", "COMPLETED", "REJECTED"]
CATEGORIES = [("Saree", "SAR"), ("Salwar Kameez", "SKZ"), ("Miniature", "MIN"), ("Readymades", "RED"),
              ("Dupatta", "DUP"), ("Home Decor", "HOM"), ("Jewellery", "JEW")]  # See docs/sku-codes.md
SKU_RULE = r"^[A-Za-z0-9][A-Za-z0-9._-]*$"
NUMBER_RULE = r"^0*[1-9][0-9]*$"
PAD_FIND, PAD_REPLACE = r"^0*([0-9]{3,})$", "$1"  # Applied to "00" + number: 4 -> 004, 1000 -> 1000
FILE_RULE = r"^[a-z0-9][a-z0-9._-]*$"
PRICE_RULE = r"^[0-9]+(\.[0-9]+)?$"
URL_RULE = (r"^https://(www\.)?(periwinklebysherry\.com|periwinkle-by-sherry\.myshopify\.com)"
            r"/(collections/[^/\s]+/)?products/[^\s?#]+([?#]\S*)?$")
ISO = "yyyy-MM-dd'T'HH:mm:ssZZZZZ"
ID = "yyyyMMddHHmmss"
PURPLE, BLUE = 2071128575, 946986751  # client shortcuts, operator shortcuts
BUILD = 9  # Shown in Work on Product's first menu, to confirm which version a phone has. Raise on each release.


class Store(Shortcut):
    """A shortcut that reads and writes the shared folder."""

    def __init__(self, name, folder, color):
        super().__init__(name, color=color)
        self.root = self.add("file", output="Periwinkle folder", WFFile=folder)

    # Files
    def get(self, *path):
        return self.add("documentpicker.open", output="File", WFShowFilePicker=False, WFFile=attachment(self.root),
                        WFGetFilePath=text(*path), WFFileErrorIfNotFound=False)

    def lookup(self, folder, *name):
        """Gets a file that may not exist. On iPhone, Get File fails on a missing file unless
        the device has already loaded the folder, so the folder is listed first."""
        self.list_folder(folder)
        return self.get(folder, "/", *name)

    def save(self, content, *path, name="record.json"):
        # The name's extension decides the saved file's type, whatever the path says.
        named_item = self.add("setitemname", output="Named", WFInput=attachment(content), WFName=name,
                              WFDontIncludeFileExtension=False)
        return self.add("documentpicker.save", output="Saved", WFInput=attachment(named_item), WFAskWhereToSave=False,
                        WFFolder=attachment(self.root), WFFileDestinationPath=text(*path), WFSaveFileOverwrite=True)

    def archive(self, source, name, folder):
        """Moves a superseded record into its own timestamped folder, so every old version is kept.

        This must be the last thing a flow does with a record. On iPhone, using any value read
        from a file after that file has moved or been deleted stops the run with a "ToolDialogHandler"
        error, even if the value was first copied into a Text action.
        """
        date = self.add("date", output="Date", WFDateActionMode="Current Date")
        stamp = self.add("format.date", output="Time ID", WFDate=text(date), WFDateFormatStyle="Custom", WFDateFormat=ID)
        self.save(self.literal("Holds one replaced record."), folder, "/", stamp, "/_folder.json")
        target = self.get(folder, "/", stamp)
        self.add("file.move", output="Moved", WFFile=attachment(self.get(*source, "/", name, ".json")), WFFolder=attachment(target),
                 WFDestinationPath=attachment(target), WFReplaceExisting=True)

    def list_folder(self, *path):
        folder = self.get(*path)
        return self.add("file.getfoldercontents", output="Contents", WFFolder=attachment(folder), Recursive=False)

    def names_into(self, variable, *path):
        """Adds record names to a variable, skipping .DS_Store and iCloud conflict copies."""
        loop = self.each(self.list_folder(*path))
        name = self.add("properties.files", output="Name", WFInput=attachment(REPEAT_ITEM), WFContentItemPropertyName="Name")
        ok = self.add("text.match", output="Valid name", text=text(name), WFMatchTextPattern=FILE_RULE, WFMatchTextCaseSensitive=True)
        check = self.if_(ok, HAS_VALUE)
        self.add("appendvariable", WFVariableName=variable, WFInput=attachment(name))
        self.end_if(check)
        self.end_each(loop)

    # Values
    def literal(self, value, output="Text"):
        return self.add("gettext", output=output, WFTextActionText=text(value))

    def compose(self, *parts, output="Text"):
        return self.add("gettext", output=output, WFTextActionText=text(*parts))

    def stamps(self):
        date = self.add("date", output="Date", WFDateActionMode="Current Date")
        iso = self.add("format.date", output="Timestamp", WFDate=text(date), WFDateFormatStyle="Custom", WFDateFormat=ISO)
        rid = self.add("format.date", output="Time ID", WFDate=text(date), WFDateFormatStyle="Custom", WFDateFormat=ID)
        return iso, rid

    def json_safe(self, var):
        """Keeps free text from breaking a record: quotes and line breaks are replaced."""
        step = self.add("text.replace", output="Notes", WFInput=text(var), WFReplaceTextFind=r'["\\]',
                        WFReplaceTextReplace="'", WFReplaceTextRegularExpression=True, WFReplaceTextCaseSensitive=True)
        return self.add("text.replace", output="Notes", WFInput=text(step), WFReplaceTextFind=r"\s*[\r\n]+\s*",
                        WFReplaceTextReplace=" ", WFReplaceTextRegularExpression=True, WFReplaceTextCaseSensitive=True)

    def field(self, dictionary, key):
        return self.add("getvalueforkey", output=key, WFInput=attachment(dictionary), WFGetDictionaryValueType="Value",
                        WFDictionaryKey=key)

    def row_fields(self, file_var):
        dictionary = self.add("detect.dictionary", output="Record", WFInput=attachment(file_var))
        keys = ["sku", "costPrice", "sellingPrice", "productStatus", "stockStatus", "shopifyUrl", "submittedAt",
                "publishedAt", "lastStockUpdateAt", "operatorNotes"]
        return {key: self.field(dictionary, key) for key in keys}

    def save_row(self, status_folder, lower, row):
        """row maps field names to a variable or literal string."""
        content = self.compose(
            '{"sku":"', row["sku"], '","costPrice":', row["costPrice"], ',"sellingPrice":', row["sellingPrice"],
            ',"productStatus":"', row["productStatus"], '","stockStatus":"', row["stockStatus"],
            '","shopifyUrl":"', row["shopifyUrl"], '","submittedAt":"', row["submittedAt"],
            '","publishedAt":"', row["publishedAt"], '","lastStockUpdateAt":"', row["lastStockUpdateAt"],
            '","operatorNotes":"', row["operatorNotes"], '"}', output="Row")
        self.save(content, "register/", status_folder, "/", lower, ".json")

    def log(self, time_id, iso, lower, slug, sku, event, previous, new, source, notes=""):
        previous = self.compose(*previous) if isinstance(previous, tuple) else previous
        new = self.compose(*new) if isinstance(new, tuple) else new
        content = self.compose('{"timestamp":"', iso, '","sku":"', sku, '","eventType":"', event,
                               '","previousValue":"', previous, '","newValue":"', new, '","source":"', source,
                               '","notes":"', notes, '"}', output="Log entry")
        self.save(content, "log/", time_id, "-", lower, "-", slug, ".json")

    def find_row(self, lower):
        """Sets rowFile and rowStatus. The furthest status wins if a stale copy exists."""
        for status in STATUSES:
            found = self.lookup("register/" + status, lower, ".json")
            check = self.if_(found, HAS_VALUE)
            self.add("setvariable", WFVariableName="rowFile", WFInput=attachment(found))
            value = self.literal(status)
            self.add("setvariable", WFVariableName="rowStatus", WFInput=attachment(value))
            self.end_if(check)

    # Talking to the person
    def alert(self, title, *message):
        self.add("alert", WFAlertActionTitle=title, WFAlertActionMessage=text(*message), WFAlertActionCancelButtonShown=False)

    def stop(self):
        self.add("exit")

    def ask(self, prompt, kind="Text", default=None, decimals=True):
        params = {"WFAskActionPrompt": prompt, "WFInputType": kind}
        if kind == "Number":
            params.update(WFAskActionAllowsDecimalNumbers=decimals, WFAskActionAllowsNegativeNumbers=False)
        if default is not None:
            params["WFAskActionDefaultAnswer"] = default
        return self.add("ask", output="Answer", **params)

    def ask_sku(self):
        """Returns the typed SKU and its lowercase form, which names its files."""
        answer = self.ask("Enter product SKU")
        sku = self.add("text.trimwhitespace", output="SKU", WFInput=text(answer))
        valid = self.add("text.match", output="Valid SKU", text=text(sku), WFMatchTextPattern=SKU_RULE, WFMatchTextCaseSensitive=True)
        check = self.if_(valid, NO_VALUE)
        self.alert("Please check the SKU", "The SKU can't be blank, and can only use letters, numbers, hyphens, dots and underscores.")
        self.stop()
        self.end_if(check)
        lower = self.add("text.changecase", output="SKU key", text=text(sku), WFCaseType="lowercase")
        return sku, lower

    def ask_category(self):
        """Returns the chosen category's code, and the same in lowercase."""
        choice = self.pick("Which category?", [f"{name} ({code})" for name, code in CATEGORIES])
        match = self.add("text.match", output="Code", text=text(choice), WFMatchTextPattern=r"[A-Z]{3}(?=\)$)", WFMatchTextCaseSensitive=True)
        code = self.compose(match, output="Code")
        return code, self.add("text.changecase", output="Code key", text=text(code), WFCaseType="lowercase")

    def next_number(self, code, lower):
        """The highest number used in a category, or its starting point in sku-start.json, plus 1, padded."""
        names = self.add("properties.files", output="Name", WFInput=attachment(self.list_folder("products")), WFContentItemPropertyName="Name")
        joined = self.add("text.combine", output="Names", text=attachment(names), WFTextSeparator="New Lines")
        used = self.add("text.match", output="Numbers", text=text(joined), WFMatchTextPattern=text("(?m)(?<=^pbs-", lower, "-)[0-9]+"), WFMatchTextCaseSensitive=True)
        self.add("appendvariable", WFVariableName="numbers", WFInput=attachment(used))
        starts = self.add("detect.dictionary", output="Starts", WFInput=attachment(self.get("sku-start.json")))
        start = self.add("getvalueforkey", output="Start", WFInput=attachment(starts), WFGetDictionaryValueType="Value", WFDictionaryKey=text(code))
        check = self.if_(start, HAS_VALUE)
        self.add("appendvariable", WFVariableName="numbers", WFInput=attachment(start))
        self.else_(check)
        self.add("appendvariable", WFVariableName="numbers", WFInput=attachment(self.literal("0")))
        self.end_if(check)
        highest = self.add("statistics", output="Highest", Input=attachment(named("numbers")), WFStatisticsOperation="Maximum")
        following = self.add("calculateexpression", output="Next", Input=text(highest, "+1"))
        return self.add("text.replace", output="Next number", WFInput=text("00", following), WFReplaceTextFind=PAD_FIND,
                        WFReplaceTextReplace=PAD_REPLACE, WFReplaceTextRegularExpression=True, WFReplaceTextCaseSensitive=True)

    def category_sku(self, code, lower, answer):
        """Builds the SKU and its file key. The keypad drops leading zeros while typing, so numbers are padded here."""
        digits = self.add("text.trimwhitespace", output="Number", WFInput=text(answer))
        valid = self.add("text.match", output="Valid number", text=text(digits), WFMatchTextPattern=NUMBER_RULE, WFMatchTextCaseSensitive=True)
        check = self.if_(valid, NO_VALUE)
        self.alert("Please check the number", "Enter a whole number, 1 or more. Nothing has been saved. Please start again.")
        self.stop()
        self.end_if(check)
        number = self.add("text.replace", output="Padded number", WFInput=text("00", digits), WFReplaceTextFind=PAD_FIND,
                          WFReplaceTextReplace=PAD_REPLACE, WFReplaceTextRegularExpression=True, WFReplaceTextCaseSensitive=True)
        return self.compose("PBS-", code, "-", number, output="SKU"), self.compose("pbs-", lower, "-", number, output="SKU key")

    def ask_new_sku(self):
        """Category menu, then the next free number filled in, which can be changed."""
        code, lower = self.ask_category()
        suggested = self.next_number(code, lower)
        # Text, because iPhone's number keypad doesn't show a default answer.
        answer = self.ask(text(code, " number"), default=text(suggested))
        return self.category_sku(code, lower, answer)

    def ask_existing_sku(self):
        """Category menu, then the product's number."""
        code, lower = self.ask_category()
        answer = self.ask(text(code, " number"), kind="Number", decimals=False)
        return self.category_sku(code, lower, answer)

    def ask_price(self, prompt):
        answer = self.ask(prompt, kind="Number")
        cleaned = self.add("text.replace", output="Price", WFInput=text(answer), WFReplaceTextFind=r"[,\s]",
                           WFReplaceTextReplace="", WFReplaceTextRegularExpression=True, WFReplaceTextCaseSensitive=True)
        valid = self.add("text.match", output="Valid price", text=text(cleaned), WFMatchTextPattern=PRICE_RULE, WFMatchTextCaseSensitive=True)
        check = self.if_(valid, NO_VALUE)
        self.alert("Please check the price", "Enter a number in rupees, 0 or more. Nothing has been saved. Please start again.")
        self.stop()
        self.end_if(check)
        return cleaned

    def pick(self, prompt, options):
        """Asks a question and returns the answer. Branch on the answer with if_ afterwards, so
        a flow's steps read in one place rather than spread across menu cases."""
        group = self.menu(prompt, options)
        for option in options:
            self.case(group, option)
            self.literal(option, output="Choice")
        return self.end_menu(group)

    def choose(self, prompt, variable, multiple=False):
        params = {}
        if multiple:
            params.update(WFChooseFromListActionSelectMultiple=True, WFChooseFromListActionSelectAll=True)
        return self.add("choosefromlist", output="Chosen", WFInput=attachment(named(variable)),
                        WFChooseFromListActionPrompt=prompt, **params)

    def stop_if_empty(self, variable, title, message):
        count = self.add("count", output="Count", Input=attachment(named(variable)), WFCountType="Items")
        check = self.if_(count, IS, number=0)
        self.alert(title, message)
        self.stop()
        self.end_if(check)
        return count


def text_pair(cost, selling):
    """Previous or new prices, as one log value."""
    return ("cost ", cost, " selling ", selling)


def new_product(folder):
    s = Store("Periwinkle – New Product", folder, PURPLE)
    sku, lower = s.ask_new_sku()
    existing = s.lookup("products", lower, ".json")
    check = s.if_(existing, HAS_VALUE)
    record = s.add("detect.dictionary", output="Record", WFInput=attachment(existing))
    when = s.field(record, "submittedAt")
    s.alert("This SKU already exists", sku, " was submitted on ", when, ". Nothing has been saved.")
    s.stop()
    s.end_if(check)

    cost = s.ask_price(text(sku, " cost price in ₹"))
    selling = s.ask_price(text(sku, " selling price in ₹"))
    photos = s.add("selectphoto", output="Photos", WFSelectMultiplePhotos=True)
    count = s.add("count", output="Photo count", Input=attachment(photos), WFCountType="Items")
    check = s.if_(count, IS, number=0)
    s.alert("No photos selected", "Nothing has been saved. Please start again and choose at least one photo.")
    s.stop()
    s.end_if(check)

    caption = s.compose("SKU: ", sku, "\nCOST PRICE: ₹", cost, "\nSELLING PRICE: ₹", selling,
                        "\nSTATUS: NEW\nSUBMITTED VIA PERIWINKLE PRODUCT INTAKE", output="Caption")
    s.add("setclipboard", WFInput=attachment(caption), WFLocalOnly=False)

    iso, time_id = s.stamps()
    row = {"sku": sku, "costPrice": cost, "sellingPrice": selling, "productStatus": "NEW", "stockStatus": "IN_STOCK",
           "shopifyUrl": "", "submittedAt": iso, "publishedAt": "", "lastStockUpdateAt": "", "operatorNotes": ""}
    submission = s.compose('{"sku":"', sku, '","costPrice":', cost, ',"sellingPrice":', selling, ',"submittedAt":"', iso,
                           '","photoCount":', count, '}', output="Submission")
    s.save(submission, "products/", lower, ".json")
    s.save_row("NEW", lower, row)
    s.log(time_id, iso, lower, "submitted", sku, "PRODUCT_SUBMITTED", "", "NEW", "client")

    # Shown before the Share sheet, because the client needs it while choosing the album.
    s.add("notification", WFNotificationActionTitle="Periwinkle",
          WFNotificationActionBody="Product details prepared. Select the Periwinkle Shared Album and paste the copied caption.")
    s.add("share", WFInput=attachment(photos))
    return s


def update_stock(folder):
    s = Store("Periwinkle – Update Stock", folder, PURPLE)
    sku, lower = s.ask_existing_sku()
    product = s.lookup("products", lower, ".json")
    check = s.if_(product, NO_VALUE)
    s.alert("SKU not found", "We couldn't find this SKU. Please check the code.")
    s.stop()
    s.end_if(check)

    s.find_row(lower)
    row = s.row_fields(named("rowFile"))
    known = s.add("gettext", output="Current stock", WFTextActionText=text(row["stockStatus"]))
    requested = s.pick(text(row["sku"], " · ₹", row["sellingPrice"], "\nPublication: ", named("rowStatus"), "\nStock on record: ", known,
                            "\n\nWhat is the stock status now?"), ["OUT_OF_STOCK", "IN_STOCK"])
    same = s.if_(requested, IS, string=text(known))
    again = s.pick(text("This SKU is already recorded as ", known, ". Submit a request anyway?"), ["Don't submit", "Submit anyway"])
    check = s.if_(again, IS, string="Don't submit")
    s.stop()
    s.end_if(check)
    s.end_if(same)

    iso, time_id = s.stamps()
    request = s.compose('{"requestId":"', time_id, "-", lower, '","sku":"', row["sku"], '","requestedStockStatus":"', requested,
                        '","requestStatus":"PENDING","requestedAt":"', iso, '","processedAt":"","operatorNotes":""}', output="Request")
    s.save(request, "stock-requests/PENDING/", time_id, "-", lower, ".json")
    s.log(time_id, iso, lower, "stock-requested", row["sku"], "STOCK_REQUESTED", known, requested, "client")
    s.alert("Done", "Stock update request submitted.")
    return s


def fix_product(folder):
    s = Store("Periwinkle – Fix Product", folder, PURPLE)
    sku, lower = s.ask_existing_sku()
    product = s.lookup("products", lower, ".json")
    check = s.if_(product, NO_VALUE)
    s.alert("SKU not found", "We couldn't find this SKU. Please check the code.")
    s.stop()
    s.end_if(check)
    s.find_row(lower)
    started = s.if_(named("rowStatus"), IS_NOT, string="NEW")
    s.alert("Already being listed", "This product is ", named("rowStatus"), ", so it can't be changed here. Please message the operator with the correction.")
    s.stop()
    s.end_if(started)
    row = s.row_fields(named("rowFile"))
    action = s.pick(text(row["sku"], "\nCost: ₹", row["costPrice"], "\nSelling: ₹", row["sellingPrice"], "\n\nWhat needs fixing?"),
                    ["Correct the prices", "Wrong SKU: cancel this submission", "Leave it as it is"])

    prices = s.if_(action, IS, string="Correct the prices")
    cost = s.ask_price("Correct cost price in ₹")
    selling = s.ask_price("Correct selling price in ₹")
    iso, time_id = s.stamps()
    caption = s.compose("SKU: ", row["sku"], "\nCOST PRICE: ₹", cost, "\nSELLING PRICE: ₹", selling,
                        "\nSTATUS: NEW\nCORRECTED VIA PERIWINKLE PRODUCT INTAKE", output="Caption")
    s.add("setclipboard", WFInput=attachment(caption), WFLocalOnly=False)
    s.save_row("NEW", lower, {**row, "costPrice": cost, "sellingPrice": selling})
    submission = s.compose('{"sku":"', row["sku"], '","costPrice":', cost, ',"sellingPrice":', selling, ',"submittedAt":"', row["submittedAt"],
                           '","correctedAt":"', iso, '"}', output="Submission")
    s.save(submission, "products/", lower, ".json")
    s.log(time_id, iso, lower, "price-corrected", row["sku"], "PRICE_CORRECTED",
          text_pair(row["costPrice"], row["sellingPrice"]), text_pair(cost, selling), "client")
    s.alert("Prices corrected", "The register now has the new prices, and a corrected caption is copied. To keep the album clear, add it as a new comment on the product's photo.")
    s.end_if(prices)

    cancel = s.if_(action, IS, string="Wrong SKU: cancel this submission")
    sure = s.pick(text("Cancel ", row["sku"], "? The SKU can then be used again."), ["Yes, cancel it", "No, keep it"])
    confirmed = s.if_(sure, IS, string="Yes, cancel it")
    iso, time_id = s.stamps()
    s.log(time_id, iso, lower, "cancelled", row["sku"], "SUBMISSION_CANCELLED", "NEW", "CANCELLED", "client")
    s.alert("Submission cancelled", "You can now submit the product again with the right SKU. Photos already in the album stay there until you delete them from the album.")
    s.archive(("register/", named("rowStatus")), lower, "register/_cancelled")
    s.archive(("products",), lower, "products/_cancelled")
    s.end_if(confirmed)
    s.end_if(cancel)
    return s


def work_on_product(folder):
    s = Store("Periwinkle – Work on Product", folder, BLUE)
    START, LINK, BACK, FIX = "Start a new product", "Add or fix a Shopify link", "Move a product back", "Correct a product's prices"
    action = s.pick(f"What are you doing? (build {BUILD})", [START, LINK, BACK, FIX])

    branch = s.if_(action, IS, string=START)
    s.names_into("choices", "register/NEW")
    s.stop_if_empty("choices", "Nothing new", "There are no NEW products.")
    lower = s.add("text.changecase", output="SKU key", text=text(s.choose("Choose a product", "choices")), WFCaseType="lowercase")
    s.find_row(lower)
    stale = s.if_(named("rowStatus"), IS_NOT, string="NEW")
    # An earlier run stopped before archiving this copy. The furthest status is the real one.
    s.archive(("register/NEW",), lower, "register/_replaced")
    s.alert("Already started", "This product is already ", named("rowStatus"), ". The leftover NEW copy has been cleared.")
    s.stop()
    s.end_if(stale)
    row = s.row_fields(named("rowFile"))
    details = s.compose("SKU: ", row["sku"], "\nCost: ₹", row["costPrice"], "\nSelling: ₹", row["sellingPrice"],
                        "\nSubmitted: ", row["submittedAt"], output="Details")
    s.add("setclipboard", WFInput=attachment(details), WFLocalOnly=False)
    iso, time_id = s.stamps()
    s.save_row("IN_PROGRESS", lower, {**row, "productStatus": "IN_PROGRESS"})
    s.log(time_id, iso, lower, "processing-started", row["sku"], "PROCESSING_STARTED", "NEW", "IN_PROGRESS", "operator")
    s.alert("Now IN_PROGRESS", details, "\n\nThese details are copied. Find the photos in the Shared Album around the submitted date, then list it in Shopify with Claude.")
    s.archive(("register/", named("rowStatus")), lower, "register/_replaced")
    s.end_if(branch)

    branch = s.if_(action, IS, string=LINK)
    for status in ["IN_PROGRESS", "NEW", "READY_TO_PUBLISH"]:
        s.names_into("choices", "register/", status)
    s.stop_if_empty("choices", "Nothing to do", "No product is waiting for a link.")
    lower = s.add("text.changecase", output="SKU key", text=text(s.choose("Choose a product", "choices")), WFCaseType="lowercase")
    s.find_row(lower)
    row = s.row_fields(named("rowFile"))
    answer = s.ask("Paste the product's Shopify URL", kind="URL")
    url = s.add("text.trimwhitespace", output="URL", WFInput=text(answer))
    valid = s.add("text.match", output="Valid URL", text=text(url), WFMatchTextPattern=URL_RULE, WFMatchTextCaseSensitive=False)
    check = s.if_(valid, NO_VALUE)
    s.alert("That link doesn't look right", "Use the product's store link, for example https://periwinklebysherry.com/products/name. Nothing has been changed.")
    s.stop()
    s.end_if(check)
    READY, LIVE = "Not yet: mark READY_TO_PUBLISH", "I've checked it's live: mark LIVE"
    choice = s.pick(text(row["sku"], "\nA link alone doesn't make a product LIVE. Is it published in Shopify?"), [READY, LIVE])
    iso, time_id = s.stamps()
    s.log(time_id, iso, lower, "url-recorded", row["sku"], "SHOPIFY_URL_RECORDED", row["shopifyUrl"], url, "operator")

    ready = s.if_(choice, IS, string=READY)
    s.save_row("READY_TO_PUBLISH", lower, {**row, "productStatus": "READY_TO_PUBLISH", "shopifyUrl": url})
    s.alert("Saved", row["sku"], " is READY_TO_PUBLISH. Run Publish Products once it's live in Shopify.")
    moved = s.if_(named("rowStatus"), IS_NOT, string="READY_TO_PUBLISH")
    s.archive(("register/", named("rowStatus")), lower, "register/_replaced")
    s.end_if(moved)
    s.end_if(ready)

    live = s.if_(choice, IS, string=LIVE)
    s.save_row("LIVE", lower, {**row, "productStatus": "LIVE", "shopifyUrl": url, "publishedAt": iso})
    s.log(time_id, iso, lower, "published", row["sku"], "PRODUCT_PUBLISHED", named("rowStatus"), "LIVE", "operator")
    s.alert("Saved", row["sku"], " is LIVE.")
    s.archive(("register/", named("rowStatus")), lower, "register/_replaced")
    s.end_if(live)
    s.end_if(branch)

    branch = s.if_(action, IS, string=BACK)
    sku, lower = s.ask_sku()
    s.find_row(lower)
    missing = s.if_(named("rowFile"), NO_VALUE)
    s.alert("SKU not found", "We couldn't find this SKU.")
    s.stop()
    s.end_if(missing)
    row = s.row_fields(named("rowFile"))
    back = ["NEW", "IN_PROGRESS", "READY_TO_PUBLISH", "Leave it as it is"]
    target = s.pick(text(row["sku"], " is ", named("rowStatus"), ".\nMove it back to:"), back)
    leave = s.if_(target, IS, string="Leave it as it is")
    s.stop()
    s.end_if(leave)
    same = s.if_(target, IS, string=text(named("rowStatus")))
    s.alert("No change", row["sku"], " is already ", named("rowStatus"), ".")
    s.stop()
    s.end_if(same)
    iso, time_id = s.stamps()
    s.save_row(target, lower, {**row, "productStatus": target, "publishedAt": ""})
    s.log(time_id, iso, lower, "moved-back", row["sku"], "STATUS_MOVED_BACK", named("rowStatus"), target, "operator")
    s.alert("Moved back", row["sku"], " is now ", target, ". Shopify hasn't changed, so unpublish it there if it shouldn't be on sale.")
    s.archive(("register/", named("rowStatus")), lower, "register/_replaced")
    s.end_if(branch)

    branch = s.if_(action, IS, string=FIX)
    sku, lower = s.ask_sku()
    s.find_row(lower)
    missing = s.if_(named("rowFile"), NO_VALUE)
    s.alert("SKU not found", "We couldn't find this SKU.")
    s.stop()
    s.end_if(missing)
    row = s.row_fields(named("rowFile"))
    cost = s.ask_price("Correct cost price in ₹")
    selling = s.ask_price("Correct selling price in ₹")
    iso, time_id = s.stamps()
    s.save_row(named("rowStatus"), lower, {**row, "costPrice": cost, "sellingPrice": selling})
    s.log(time_id, iso, lower, "price-corrected", row["sku"], "PRICE_CORRECTED",
          text_pair(row["costPrice"], row["sellingPrice"]), text_pair(cost, selling), "operator")
    s.alert("Prices corrected", row["sku"], " now shows cost ₹", cost, " and selling ₹", selling, ". Update Shopify too if the selling price is already live.")
    s.end_if(branch)
    return s


def publish_products(folder):
    s = Store("Periwinkle – Publish Products", folder, BLUE)
    s.names_into("ready", "register/READY_TO_PUBLISH")
    s.stop_if_empty("ready", "Nothing to publish", "No products are marked READY_TO_PUBLISH.")

    loop = s.each(named("ready"))
    row = s.row_fields(s.get("register/READY_TO_PUBLISH/", REPEAT_ITEM, ".json"))
    valid = s.add("text.match", output="Valid URL", text=text(row["shopifyUrl"]), WFMatchTextPattern=URL_RULE, WFMatchTextCaseSensitive=False)
    check = s.if_(valid, HAS_VALUE)
    s.add("appendvariable", WFVariableName="publishable", WFInput=attachment(REPEAT_ITEM))
    line = s.compose(row["sku"], ": ", row["shopifyUrl"], output="Line")
    s.add("appendvariable", WFVariableName="reviewLines", WFInput=attachment(line))
    s.else_(check)
    s.add("appendvariable", WFVariableName="needUrl", WFInput=attachment(row["sku"]))
    s.end_if(check)
    s.end_each(loop)

    need_count = s.add("count", output="Need URL count", Input=attachment(named("needUrl")), WFCountType="Items")
    has_need = s.if_(need_count, IS_NOT, number=0)
    joined = s.add("text.combine", output="SKUs", text=attachment(named("needUrl")), WFTextSeparator="New Lines")
    s.alert("These need a valid Shopify URL", joined, "\n\nThey will stay READY_TO_PUBLISH. Add links with Work on Product.")
    s.end_if(has_need)

    ok_count = s.add("count", output="Publishable count", Input=attachment(named("publishable")), WFCountType="Items")
    none = s.if_(ok_count, IS, number=0)
    s.alert("Batch summary", "Published: 0\nSkipped: 0\nNeed URLs: ", need_count)
    s.stop()
    s.end_if(none)

    review = s.add("text.combine", output="Review", text=attachment(named("reviewLines")), WFTextSeparator="New Lines")
    s.alert("Review before marking LIVE", review, "\n\nNext, choose which are confirmed live in Shopify.")
    chosen = s.choose("Mark these LIVE", "publishable", multiple=True)
    chosen_count = s.add("count", output="Published count", Input=attachment(chosen), WFCountType="Items")

    iso, time_id = s.stamps()
    loop = s.each(chosen)
    current = s.get("register/READY_TO_PUBLISH/", REPEAT_ITEM, ".json")
    row = s.row_fields(current)
    valid = s.add("text.match", output="Valid URL", text=text(row["shopifyUrl"]), WFMatchTextPattern=URL_RULE, WFMatchTextCaseSensitive=False)
    check = s.if_(valid, HAS_VALUE)
    s.save_row("LIVE", REPEAT_ITEM, {**row, "productStatus": "LIVE", "publishedAt": iso})
    s.log(time_id, iso, REPEAT_ITEM, "published", row["sku"], "PRODUCT_PUBLISHED", "READY_TO_PUBLISH", "LIVE", "operator")
    s.archive(("register/READY_TO_PUBLISH",), REPEAT_ITEM, "register/_replaced")
    s.end_if(check)
    s.end_each(loop)

    skipped = s.add("calculateexpression", output="Skipped", Input=text(ok_count, "-", chosen_count))
    s.alert("Batch summary", "Published: ", chosen_count, "\nSkipped: ", skipped, "\nNeed URLs: ", need_count)
    return s


def process_stock_requests(folder):
    s = Store("Periwinkle – Process Stock Requests", folder, BLUE)
    s.names_into("pending", "stock-requests/PENDING")
    s.stop_if_empty("pending", "All clear", "There are no pending stock requests.")

    loop = s.each(named("pending"))
    current = s.get("stock-requests/PENDING/", REPEAT_ITEM, ".json")
    request = s.add("detect.dictionary", output="Request", WFInput=attachment(current))
    sku = s.field(request, "sku")
    wanted = s.field(request, "requestedStockStatus")
    asked_at = s.field(request, "requestedAt")
    lower = s.add("text.changecase", output="SKU key", text=text(sku), WFCaseType="lowercase")
    s.find_row(lower)
    row = s.row_fields(named("rowFile"))

    DONE, REJECT = "Shopify updated: complete", "Reject"
    choice = s.pick(text(sku, "\nRequested: ", wanted, "\nOn record: ", row["stockStatus"], "\nPublication: ", named("rowStatus"),
                         "\nAsked: ", asked_at, "\n", row["shopifyUrl"], "\n\nUpdate Shopify first, then choose."),
                    [DONE, REJECT, "Skip for now"])
    complete = s.if_(choice, IS, string=DONE)
    iso, time_id = s.stamps()
    s.save_row(named("rowStatus"), lower, {**row, "stockStatus": wanted, "lastStockUpdateAt": iso})
    done = s.compose('{"requestId":"', REPEAT_ITEM, '","sku":"', sku, '","requestedStockStatus":"', wanted,
                     '","requestStatus":"COMPLETED","requestedAt":"', asked_at, '","processedAt":"', iso, '","operatorNotes":""}', output="Request")
    s.save(done, "stock-requests/COMPLETED/", REPEAT_ITEM, ".json")
    s.log(time_id, iso, lower, "stock-completed", sku, "STOCK_REQUEST_COMPLETED", row["stockStatus"], wanted, "operator")
    s.archive(("stock-requests/PENDING",), REPEAT_ITEM, "stock-requests/_handled")
    s.end_if(complete)

    reject = s.if_(choice, IS, string=REJECT)
    answer = s.ask("Why is it being rejected? (optional)")
    note = s.json_safe(answer)
    iso, time_id = s.stamps()
    done = s.compose('{"requestId":"', REPEAT_ITEM, '","sku":"', sku, '","requestedStockStatus":"', wanted,
                     '","requestStatus":"REJECTED","requestedAt":"', asked_at, '","processedAt":"', iso, '","operatorNotes":"', note, '"}', output="Request")
    s.save(done, "stock-requests/REJECTED/", REPEAT_ITEM, ".json")
    s.log(time_id, iso, lower, "stock-rejected", sku, "STOCK_REQUEST_REJECTED", row["stockStatus"], wanted, "operator", note)
    s.archive(("stock-requests/PENDING",), REPEAT_ITEM, "stock-requests/_handled")
    s.end_if(reject)
    s.end_each(loop)
    s.alert("Finished", "You've been through all the pending requests.")
    return s


def register(folder):
    s = Store("Periwinkle – Register", folder, BLUE)

    def csv_rows(variable, folders, fields, source):
        for path in folders:
            loop = s.each(s.list_folder(*path))
            dictionary = s.add("detect.dictionary", output="Record", WFInput=attachment(REPEAT_ITEM))
            values = {key: s.field(dictionary, key) for key in fields}
            has_sku = s.if_(values[source], HAS_VALUE)
            parts = ['="', values[source], '"']
            for key in fields:
                if key != source:
                    parts += [',"', values[key], '"'] if key in ("operatorNotes", "notes") else [",", values[key]]
            line = s.compose(*parts, output="Line")
            s.add("appendvariable", WFVariableName=variable, WFInput=attachment(line))
            s.end_if(has_sku)
            s.end_each(loop)

    def publish(header, variable, filename):
        rows = s.add("text.combine", output="Rows", text=attachment(named(variable)), WFTextSeparator="New Lines")
        csv = s.compose(header, "\n", rows, "\n", output="CSV")
        old = s.lookup("views", filename, ".numbers")
        check = s.if_(old, HAS_VALUE)
        # The only delete in the system: a rebuilt copy holds nothing the records don't, and
        # keeping every one would slowly fill iCloud storage.
        s.add("file.delete", WFInput=attachment(old), WFDeleteFileConfirmDeletion=False)
        s.end_if(check)
        saved = s.save(csv, "views/", filename, ".csv", name=filename + ".csv")
        s.add("openin", WFInput=attachment(saved), WFOpenInAskWhenRun=False, WFOpenInAppIdentifier="com.apple.Numbers",
              WFApp={"BundleIdentifier": "com.apple.Numbers", "Name": "Numbers", "TeamIdentifier": "0000000000"})

    view = s.pick("Which view?", ["Products", "Stock requests", "Activity log"])
    branch = s.if_(view, IS, string="Products")
    fields = ["sku", "costPrice", "sellingPrice", "productStatus", "stockStatus", "shopifyUrl", "submittedAt", "publishedAt",
              "lastStockUpdateAt", "operatorNotes"]
    csv_rows("rows", [("register/" + status,) for status in STATUSES], fields, "sku")
    publish("SKU,CostPrice,SellingPrice,ProductStatus,StockStatus,ShopifyURL,SubmittedAt,PublishedAt,LastStockUpdateAt,OperatorNotes",
            "rows", "Product Register")
    s.end_if(branch)
    branch = s.if_(view, IS, string="Stock requests")
    fields = ["sku", "requestId", "requestedStockStatus", "requestStatus", "requestedAt", "processedAt", "operatorNotes"]
    csv_rows("rows", [("stock-requests/" + status,) for status in REQUEST_STATUSES], fields, "sku")
    publish("SKU,RequestID,RequestedStockStatus,RequestStatus,RequestedAt,ProcessedAt,OperatorNotes", "rows", "Stock Requests")
    s.end_if(branch)
    branch = s.if_(view, IS, string="Activity log")
    fields = ["sku", "timestamp", "eventType", "previousValue", "newValue", "source", "notes"]
    csv_rows("rows", [("log",)], fields, "sku")
    publish("SKU,Timestamp,EventType,PreviousValue,NewValue,Source,Notes", "rows", "Activity Log")
    s.end_if(branch)
    return s


CLIENT = [new_product, update_stock, fix_product]
OPERATOR = [work_on_product, publish_products, process_stock_requests, register]


def read_folder_reference(path):
    """Reads the folder reference out of a signed shortcut made on the iPhone."""
    data = open(path, "rb").read()
    if data[:6] == b"bplist":
        workflow = plistlib.loads(data)
    else:
        size = struct.unpack("<I", data[8:12])[0]
        chain = plistlib.loads(data[12:12 + size])["SigningCertificateChain"]
        with tempfile.TemporaryDirectory() as tmp:
            cert, pem, archive, out = (os.path.join(tmp, n) for n in ("leaf.der", "pub.pem", "out.aar", "x"))
            open(cert, "wb").write(chain[0])
            key = subprocess.run(["openssl", "x509", "-inform", "DER", "-in", cert, "-pubkey", "-noout"], capture_output=True, check=True).stdout
            open(pem, "wb").write(key)
            subprocess.run(["aea", "decrypt", "-i", path, "-o", archive, "-sign-pub", pem], check=True)
            os.mkdir(out)
            subprocess.run(["aa", "extract", "-i", archive, "-d", out], check=True)
            workflow = plistlib.load(open(os.path.join(out, "Shortcut.wflow"), "rb"))
    return workflow["WFWorkflowActions"][0]["WFWorkflowActionParameters"]["WFFolder"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folderref")
    parser.add_argument("output")
    parser.add_argument("--role", choices=["client", "operator", "all"], default="all")
    parser.add_argument("--only", help="build only shortcuts whose name contains this text")
    args = parser.parse_args()
    folder = read_folder_reference(args.folderref)
    builders = {"client": CLIENT, "operator": OPERATOR, "all": CLIENT + OPERATOR}[args.role]
    os.makedirs(args.output, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        for builder in builders:
            shortcut = builder(folder)
            if args.only and args.only.lower() not in shortcut.name.lower():
                continue
            raw = os.path.join(tmp, "raw.shortcut")
            shortcut.write(raw)
            # The file name becomes the shortcut's name on import.
            signed = os.path.join(args.output, shortcut.name + ".shortcut")
            # Apple's signing server sometimes answers 502 when called quickly in a row.
            for attempt in range(5):
                if subprocess.run(["shortcuts", "sign", "--mode", "anyone", "--input", raw, "--output", signed]).returncode == 0:
                    break
                time.sleep(10 * (attempt + 1))
            else:
                sys.exit(f"Signing failed: {shortcut.name}")
            print(f"{len(shortcut.actions):4d} actions  {signed}")
            time.sleep(5)


if __name__ == "__main__":
    main()
