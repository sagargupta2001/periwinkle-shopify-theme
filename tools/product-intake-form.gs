/**
 * NOT IN USE: superseded on 1 Nov 2026 by the shared-album workflow in
 * docs/adding-products.md (decision 21). Kept in case a form is needed again.
 *
 * Periwinkle product intake: a Google Form for the client and a linked Google
 * Sheet for whoever lists products in Shopify.
 *
 * Setup (once, about 5 minutes):
 *   1. Go to https://script.google.com, signed in as the person who will own
 *      the form and sheet (the one listing products). Click New project.
 *   2. Replace the contents of Code.gs with this file and save.
 *   3. Choose `setup` in the function menu and click Run. Approve the
 *      permissions when asked.
 *   4. Open View → Logs (or Execution log). It prints three links: the form to
 *      send the client, the form editor, and the sheet.
 *   5. In the form editor, add the photo question by hand, because Google
 *      doesn't let scripts create file-upload questions:
 *      - Go to the "Piece details" section and click + (Add question).
 *      - Pick the "File upload" type and title it exactly "Photos". The script
 *        looks for that title.
 *      - Allow only images, at most 10 files, and set the maximum size to 100 MB.
 *      - Make it required, then drag it to the top of the section.
 *   6. Open the sheet's "SKU counters" tab and check the next number for each
 *      category before the first real submission.
 *
 * What happens on each submission:
 *   - Google writes the raw answers to "Form responses 1".
 *   - onSubmit() takes the next SKU for the category from "SKU counters", in
 *     the format PBS-SAR-409, and adds a row to the "Products" tab with
 *     Status = New.
 *   - The lister works from "Products": they set Status as they go and paste
 *     the Shopify link when the product is live.
 */

// Category label, SKU code, Shopify product type, first number to hand out.
// Check the starting numbers against Shopify before first use. They can be
// changed later in the "SKU counters" tab without touching this script.
const CATEGORIES = [
  ['Saree', 'SAR', 'Saree', 409],
  ['Dupatta / stole', 'DUP', 'Dupatta', 41],
  ['Suit set', 'SKZ', 'Unstitched Salwar Suit', 200],
  ['Jewellery', 'EPJ', 'European earrings / necklace / ring', 44],
  ['Miniature', 'MIN', 'Miniature', 23],
  ['Home decor / ceramics', 'CMS', 'Ceramics', 12],
  ['Bag / accessory', 'BAG', 'Bag', 1],
];

const PRODUCTS_SHEET = 'Products';
const COUNTERS_SHEET = 'SKU counters';
const STATUSES = ['New', 'In progress', 'Listed', 'On hold'];

// Products tab columns, in order. Values come from the form question with the
// same title, except the columns the script or the lister fills in.
const PRODUCT_COLUMNS = [
  'Submitted', 'SKU', 'Category', 'Shopify type', 'Status', 'Shopify link',
  'Photos', 'Price (₹)', 'Quantity', 'Colour', 'Fabric', 'Craft',
  'Weight (grams)', 'Good as a gift?', 'Saree length', 'Blouse piece',
  'Pieces included', 'Stitching', 'The story', 'Anything else', 'Lister notes',
];

function setup() {
  const form = FormApp.create('Periwinkle — New product');
  form
    .setDescription(
      'One form per piece. Fill in what you know; leave a field blank if ' +
      "you're not sure, and we will ask. Photos: natural light, the full " +
      'piece plus close-ups of the border, pallu and any detail.'
    )
    .setProgressBar(true)
    .setCollectEmail(false)
    .setConfirmationMessage('Thank you! The piece is in the queue to be listed.');

  // Section 1: category. The choice decides which section comes next.
  const category = form.addMultipleChoiceItem()
    .setTitle('Category')
    .setRequired(true);

  // Section 2: sarees only.
  const sareePage = form.addPageBreakItem().setTitle('Saree details');
  form.addMultipleChoiceItem()
    .setTitle('Saree length')
    .setChoiceValues(['5.5 m', '6 m', '6.3 m', 'Not sure'])
    .showOtherOption(true);
  form.addMultipleChoiceItem()
    .setTitle('Blouse piece')
    .setChoiceValues(['Included', 'Not included', 'Not sure']);

  // Section 3: suit sets only.
  const suitPage = form.addPageBreakItem().setTitle('Suit set details');
  form.addCheckboxItem()
    .setTitle('Pieces included')
    .setChoiceValues(['Kurta', 'Dupatta', 'Bottom / pants']);
  form.addMultipleChoiceItem()
    .setTitle('Stitching')
    .setChoiceValues(['Unstitched', 'Semi-stitched', 'Stitched', 'Not sure']);

  // Section 4: every piece.
  const detailsPage = form.addPageBreakItem()
    .setTitle('Piece details')
    .setHelpText('Add the Photos (file upload) question at the top of this section. See the setup notes.');
  form.addTextItem()
    .setTitle('Price (₹)')
    .setRequired(true)
    .setValidation(FormApp.createTextValidation().requireNumberGreaterThan(0).build());
  form.addTextItem()
    .setTitle('Quantity')
    .setHelpText('Usually 1 for one-of-a-kind pieces.')
    .setRequired(true)
    .setValidation(FormApp.createTextValidation().requireWholeNumber().build());
  form.addTextItem()
    .setTitle('Colour')
    .setHelpText('Main colour, plus border or pallu colours if different.')
    .setRequired(true);
  form.addTextItem()
    .setTitle('Fabric')
    .setHelpText('For example cotton, Chanderi silk, Kota doria, tussar. Leave blank if not sure.');
  form.addCheckboxItem()
    .setTitle('Craft')
    .setChoiceValues(['Handloom', 'Hand block print', 'Hand-painted', 'Embroidery',
      'Zari weave', 'Ikat', 'Printed'])
    .showOtherOption(true);
  form.addTextItem()
    .setTitle('Weight (grams)')
    .setHelpText('Only if you know it. Used for shipping charges.')
    .setValidation(FormApp.createTextValidation().requireNumberGreaterThan(0).build());
  form.addMultipleChoiceItem()
    .setTitle('Good as a gift?')
    .setChoiceValues(['Yes', 'No']);
  form.addParagraphTextItem()
    .setTitle('The story')
    .setHelpText('Where it comes from, who made it, what makes it special. A sentence or two is plenty.');
  form.addParagraphTextItem()
    .setTitle('Anything else');

  // Branching. A page break's go-to applies when the section before it is
  // finished, so the break after the saree section sends sarees on to Piece
  // details, skipping the suit section.
  category.setChoices(CATEGORIES.map(([label]) => {
    if (label === 'Saree') return category.createChoice(label, sareePage);
    if (label === 'Suit set') return category.createChoice(label, suitPage);
    return category.createChoice(label, detailsPage);
  }));
  suitPage.setGoToPage(detailsPage);

  // Linked sheet.
  const ss = SpreadsheetApp.create('Periwinkle — Product intake');
  form.setDestination(FormApp.DestinationType.SPREADSHEET, ss.getId());
  SpreadsheetApp.flush();

  // Products tab: the working list.
  const products = ss.insertSheet(PRODUCTS_SHEET, 0);
  products.getRange(1, 1, 1, PRODUCT_COLUMNS.length)
    .setValues([PRODUCT_COLUMNS])
    .setFontWeight('bold')
    .setBackground('#E8E6F2');
  products.setFrozenRows(1);
  products.setFrozenColumns(2);
  const statusCol = PRODUCT_COLUMNS.indexOf('Status') + 1;
  products.getRange(2, statusCol, 999, 1).setDataValidation(
    SpreadsheetApp.newDataValidation().requireValueInList(STATUSES, true).build()
  );

  // SKU counters tab.
  const counters = ss.insertSheet(COUNTERS_SHEET);
  counters.getRange(1, 1, 1, 4)
    .setValues([['Category', 'Code', 'Shopify type', 'Next number']])
    .setFontWeight('bold')
    .setBackground('#E8E6F2');
  counters.getRange(2, 1, CATEGORIES.length, 4).setValues(CATEGORIES);
  counters.setFrozenRows(1);

  // Drop the empty default sheet if it is still there.
  const blank = ss.getSheetByName('Sheet1');
  if (blank && blank.getLastRow() === 0) ss.deleteSheet(blank);

  ScriptApp.newTrigger('onSubmit').forSpreadsheet(ss).onFormSubmit().create();

  Logger.log('Send this to the client: ' + form.getPublishedUrl());
  Logger.log('Form editor (add the Photos question): ' + form.getEditUrl());
  Logger.log('Sheet: ' + ss.getUrl());
}

/** Runs on every form submission: assigns a SKU and adds a Products row. */
function onSubmit(e) {
  const ss = e.source;
  const answers = e.namedValues; // { 'Question title': ['answer'] }
  const get = (title) => (answers[title] ? answers[title].join(', ').trim() : '');

  const categoryLabel = get('Category');
  const category = CATEGORIES.find(([label]) => label === categoryLabel);
  const sku = category ? nextSku(ss, category[1]) : '';

  const values = {
    'Submitted': get('Timestamp'),
    'SKU': sku,
    'Category': categoryLabel,
    'Shopify type': category ? category[2] : '',
    'Status': 'New',
    'Shopify link': '',
    'Lister notes': category ? '' : 'Unknown category: assign the SKU by hand.',
  };
  PRODUCT_COLUMNS.forEach((col) => {
    if (!(col in values)) values[col] = get(col);
  });

  ss.getSheetByName(PRODUCTS_SHEET)
    .appendRow(PRODUCT_COLUMNS.map((col) => values[col]));
}

/** Returns the next SKU for a code and advances its counter. Locked, so two
 *  submissions at the same moment can't get the same number. */
function nextSku(ss, code) {
  const lock = LockService.getScriptLock();
  lock.waitLock(30000);
  try {
    const sheet = ss.getSheetByName(COUNTERS_SHEET);
    const rows = sheet.getRange(2, 1, sheet.getLastRow() - 1, 4).getValues();
    const i = rows.findIndex((row) => row[1] === code);
    if (i === -1) return '';
    const number = Number(rows[i][3]) || 1;
    sheet.getRange(i + 2, 4).setValue(number + 1);
    return `PBS-${code}-${String(number).padStart(3, '0')}`;
  } finally {
    lock.releaseLock();
  }
}
