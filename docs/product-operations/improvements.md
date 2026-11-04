# Shortcut improvements

Ideas and fixes to pick up later. **None of this has been started.** It's on hold until at least
one shortcut works on the client's iPhone and can change files in the shared folder
([Installation](installation.md#3-handing-over-to-the-client)). That result may change this list.

Recorded on 4 November 2026. The bugs below were found by reading `build.py`. None has been seen
happening on a phone yet, so reproduce one before fixing it where you can. Delete an item once
it's done, and record any lasting change in [decisions.md](../decisions.md).

**When picking these up:**
- Group the changes to the client's shortcuts, because each round means reinstalling them on the
  client's phone.
- Follow [Changing a shortcut](building-and-signing.md#changing-a-shortcut). Anything marked
  *new action* has to be tried on an iPhone first, because some actions behave differently there.

## Bugs that can leave wrong records

| # | Shortcut | What can go wrong | Fix |
|---|---|---|---|
| 1 | Process Stock Requests | If a request's product has been cancelled, `find_row` finds nothing and the previous request's row is still in its variables. Completing the request saves that product's details under the cancelled SKU. If it's the first request, the row is blank and is saved to the wrong path. | Check that the row's SKU matches the request's. If not, say so and offer Reject or Skip. |
| 2 | New Product | `products/` is saved first. A run that stops just after leaves an SKU that says "already exists" but has no row, so Update Stock and Fix Product can't act on it either. | Save the row, then the log, then `products/` last, so a second run finishes the job. Make Update Stock and Fix Product stop with a clear message when there's no row. |
| 3 | Update Stock, Process Stock Requests | Repeat requests pile up, because nothing checks for a pending one on the same SKU. They aren't handled in time order either, so if `OUT_OF_STOCK` and `IN_STOCK` run in the wrong order, the recorded stock ends up wrong. | Update Stock looks for a pending request first and says what it found. Process Stock Requests handles the oldest first. Sorting may need *new action*: Filter Files. |

## Making reruns safe

Shortcuts can't catch errors or undo a stopped run, so the goal is that running it again finishes
the job.

| # | Shortcut | What can go wrong | Fix |
|---|---|---|---|
| 4 | Publish Products | If a run stops after saving `LIVE` but before moving the old row, the product shows up again. Publishing it again changes its published date and adds a second log entry. | Check for a `LIVE` row first. If there is one, clear the leftover copy, as Start a new product does. |
| 5 | Work on Product: Move a product back | If a run stops before the old row moves, the furthest status still wins, so the product looks unchanged while the log says it moved. Running it again fixes it. | Make the alert say what to do, or have Register flag it (see 7). |
| 6 | Fix Product | If the client corrects prices just as the operator starts the product, the correction lands in a leftover `NEW` row. The operator's row keeps the old prices, while the log shows the new ones. | Have Register flag it (see 7). It should be rare, so don't add more than that. |
| 7 | Register | It reads conflict copies and leftover rows, so a product can appear twice. | Skip conflict copies, as other flows do. Add a Problems view for leftover rows, rows with no submission and prices that differ from the log. |
| 8 | Work on Product | The link check allows a `"` in a URL, and a quote would make the saved row unreadable. | Tighten `URL_RULE` to reject quotes. |

## Catching setup problems

| # | Change | Why |
|---|---|---|
| 9 | Each shortcut reads `settings.json` first, and stops with a clear message if it can't. No shortcut reads that file today. | A missing folder or wrong account currently shows up as a raw error, partway through. |
| 10 | Show the build number in every shortcut, and put a minimum build in `settings.json` that older copies refuse to run below. | Only Work on Product shows its build today, so an old copy on the client's phone can't be spotted, and it could write records in an old format. |
| 11 | Store the build number in each log entry. | Shows which version wrote a record when looking into a problem. |

## Fewer client mistakes

| # | Change | Notes |
|---|---|---|
| 12 | **Confirmation screen in New Product:** the SKU, both prices and the photo count, before anything is saved. Warn if the selling price isn't above cost, without blocking it. | The change likely to prevent the most mistakes, such as ₹280 typed for ₹2,800. |
| 13 | **Ask whether the photos were posted,** and record the answer. | Products with no photos in the album would stand out. Test first whether a shortcut keeps running after the Share sheet is cancelled. |
| 14 | **A short name for each piece,** such as "teal kantha". | SKUs are hard to recognise in Update Stock and Process Stock Requests. It adds one question for the client, so weigh this against 15. |
| 15 | **A small photo for each product** in the shared folder, such as `thumbs/<sku>.jpg`. | See [Finding photos](#finding-photos). |
| 16 | Remove `STATUS: NEW` from the caption. | It goes out of date, because a caption can't be edited. |
| 17 | Consider leaving prices out of the caption. | The register holds them, and they can go out of date in the album too. |

## Easier for the operator

| # | Change | Notes |
|---|---|---|
| 18 | **Today summary:** counts of `NEW`, `IN_PROGRESS`, `READY_TO_PUBLISH` and pending stock requests. | Saves running Register just to see what's waiting. |
| 19 | Show Register's rows newest first. | They come back in no particular order today. Sorting in Numbers works in the meantime. |
| 20 | Choose from a list in Move back and Correct prices, instead of typing the full SKU. | Fewer typos, though the list gets long as the catalogue grows. |
| 21 | A daily reminder through a Personal Automation on the operator's phone. | Optional. Set up on the phone, not in `build.py`. |

## Testing

| # | Change | Why |
|---|---|---|
| 22 | Test builds that stop right after each save, then run the real shortcut again. | The only way to prove 2, 4 and 5 are safe. |
| 23 | Add the save order to `test_build.py`. | Stops item 2 from coming back unnoticed. |
| 24 | Run what the [test report](test-report.md#not-tested-yet) lists as not tested. | Includes Reject and Skip, and batches of several products. |

## Finding photos

Photos can't find an SKU in a Shared Album caption, so the operator finds photos by date today.
There are two ways to improve that.

### A small photo in the shared folder

New Product would save one resized photo per product into the shared folder. It would no longer
depend on Photos search at all, and could also:
- show the piece in Update Stock, so the client can confirm it's the right one;
- show it in Work on Product;
- let `/add-products` read it on the Mac, instead of the operator supplying a photo.

**To weigh up:** it changes the rule that photos stay out of this folder, and it adds a little
iCloud storage. Resizing and showing the photo are *new actions*. The album would still hold the
full-size photos.

### A Shared Library

New Product doesn't name an album today. It opens the Share sheet, and the client picks the album
there. A Shared Library works differently: it isn't a place to post to. A photo moves from the
Personal Library to the Shared Library, and a caption is typed on the photo itself.

**What has to be tested first:**
1. Search the Shortcuts app for **Move to Shared Library**. A
   [third-party directory](https://www.shortcutactions.com/actions/app/photos) lists it, but we
   couldn't confirm it with Apple. Check that it accepts photos from Select Photos. Don't count
   on it appearing in the Share sheet.
2. Search for an action that sets a caption. We found none, so assume it's done by hand.
3. Caption a photo on one phone, then search for its SKU on both. Allow time for it to sync.

**What would change:**

| Part | Change |
|---|---|
| New Product | The Share step becomes Move to Shared Library, then the client pastes the SKU as a caption by hand. The notification changes. The caption can shrink to the SKU. |
| Fix Product | The message about adding a new comment changes. |
| Work on Product | The message about finding photos by date changes to searching by SKU. |
| Other shortcuts, the records and the folders | Nothing |

**Limits to weigh up**, from [Apple's guide](https://support.apple.com/en-ae/118229):
- A person can only be in one Shared Library, so this fails if the client already shares one
  with their family.
- Everyone in it can edit and delete everything in it.
- All of it counts against the iCloud storage of whoever creates it.
