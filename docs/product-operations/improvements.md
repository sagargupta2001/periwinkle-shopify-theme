# Shortcut improvements

Open ideas and fixes, with completed work noted below. This list was on hold
until a shortcut worked on the client's iPhone and could change files in the
shared folder, which passed on 5 November 2026
([test report](test-report.md#passed-on-the-clients-iphone)).

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
| 7 | Register exports | CSV export can read conflict copies and leftover rows, so a product can appear twice. Build 12's browser skips conflicts and deduplicates by furthest status. | Apply equivalent handling to exports. Add a Problems view for leftover rows, rows with no submission and prices that differ from the log. |
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
| 15 | **Select one photo in New Product,** not several, or open the camera directly. | The client only sends one original of each piece. See [Finding photos](#finding-photos). |
| 16 | Remove `STATUS: NEW` from the caption. | It goes out of date, because a caption can't be edited. |
| 17 | Consider leaving prices out of the caption. | The register holds them, and they can go out of date in the album too. |

## Easier for the operator

| # | Change | Notes |
|---|---|---|
| 18 | **Today summary:** counts of `NEW`, `IN_PROGRESS`, `READY_TO_PUBLISH` and pending stock requests. | Saves running Register just to see what's waiting. |
| 19 | Show Register's rows newest first. | They come back in no particular order today. Sorting in Numbers works in the meantime. |
| 26 | **Make the client's shortcuts start from the Home Screen.** Icons and widgets don't work on the client's phone today, though an icon works on the operator's ([test report](test-report.md#home-screen)). Starting each one by opening the Shortcuts app might help. | Optional: running them from the Shortcuts app works. *New action*: Open App. Users [report mixed results](https://applevis.com/comment/160823) with this workaround. |
| 21 | A daily reminder through a Personal Automation on the operator's phone. | Optional. Set up on the phone, not in `build.py`. |

## Testing

| # | Change | Why |
|---|---|---|
| 22 | Test builds that stop right after each save, then run the real shortcut again. | The only way to prove 2, 4 and 5 are safe. |
| 23 | Add the save order to `test_build.py`. | Stops item 2 from coming back unnoticed. |
| 24 | Run what the [test report](test-report.md#not-tested-yet) lists as not tested. | Includes Reject and Skip, and batches of several products. |

## Implemented in builds 10–11

- **25 — SKU labels:** New Product offers Prepare SKU label after album sharing,
  copies only the SKU, and opens its PDF in NIIMBOT. Print Product Label handles
  retries without another submission. PDF import passed on the operator's phone;
  dynamic SKU generation and physical printing still need confirmation. See
  [New Product](new-product.md#print-again-without-resubmitting).
- **20 — operator SKU entry:** Move back and Correct prices now use category
  plus number, as requested, instead of a full typed SKU. Existing list pickers
  remain lists. See [Work on Product](work-on-product.md#move-a-product-back).

## Posting with fewer manual steps

The client has to choose the album in the Share sheet, paste the caption and tap Post.

**A custom script can't do this.** Apple engineers have said there's
[no API to post to Shared Albums](https://developer.apple.com/forums/thread/717066) (2022) and
[none to add to a Shared Library](https://developer.apple.com/forums/thread/776959) (2025). Scripting
apps such as Scriptable would need one of those. As far as we know, an iPhone app also can't tap or
paste inside another app, though we didn't find Apple saying so directly. Scripting the Mac's screen
would need a Mac always on, and would break whenever Apple changed a screen.

**Apple's Post to Shared Album action doesn't help either.** It's already been tested. Its only field
is the photo, and it posts to the last-used Shared Album, so the album can't be chosen and no comment
can be set.

**What could work, best first:**

| Option | What it would remove | What to test |
|---|---|---|
| **Save the original photo to the shared folder,** as `photos/<sku>.jpg`, instead of posting to the album. See [Finding photos](#finding-photos). | All three steps, and finding photos by date | Saving a photo from a shortcut, and that it reaches the other phone. |
| **Open Shared Album action,** after copying the caption. The client adds the photos in the album. | Choosing the album. New Product would no longer pick the photos or count them. | Whether it opens the right album, and whether the client finds this easier. |
| **Tidy the Share sheet.** Move Add to Shared Album to the top with Edit Actions. | Some scrolling | The [older action](https://matthewcassinelli.com/actions/save-to-shared-album/) reused the last album, so check whether the Share sheet does too. |

A public album link doesn't help. It's for viewing and joining, not posting, and a public link would
expose the cost prices in the captions.

## Finding photos

**Current (build 18):** Register and Work on Product preview metadata-linked
Shared Album photos. Register's existing PBS-SAR-006 preview passed on the
operator's iPhone after the Text typing fix. New Product captures a before-post
name snapshot and the client confirms the actual uploaded asset; Fix Product
resumes pending confirmation. This replaces the assumption that original file
names survive upload. Full intake/resume, cross-account and deletion tests
remain rollout checks. See [Register](register.md#shared-album-photo-links).

The client sends one original photo of each piece, taken on the spot. The operator uses it to make
the Gemini images, and plans to keep it in Shopify for reference.

**The album also does a job for the client.** It shows each piece's photo next to its SKU, and the
client prints that SKU on a label and sticks it on the piece. A replacement has to keep that, so the
album stays unless there's another way to see each piece with its SKU.

Photos can't find an SKU in a Shared Album caption, so the operator finds it by date today.

### The original photo in the shared folder

New Product would save the photo as `photos/<sku>.jpg`, and skip the Share sheet, album and caption.
- **Viewing:** in Files on both phones, and in Finder on the Mac, where `/add-products` could read it.
- **Finding it:** by SKU, in Files search or with a shortcut that opens that exact file.
- **Prices:** they stay in the register. The photo holds no details that could go out of date.
- **Storage:** roughly 3–5 GB per 1,000 products if kept, and almost nothing if each photo is removed
  once it's safely in Shopify. Keep them to begin with, because they also help with
  [telling whether a piece is already added](#telling-whether-a-piece-is-already-added). Removing them
  later would need its own decision.

On its own this would remove the view the client relies on for labels. It could only replace the album
alongside something like a shortcut that shows each piece waiting for a label, with its photo and SKU.

**To test:** saving a photo from a shortcut, and how long it takes to reach the other phone. This
changes the rule that photos stay out of this folder, so record it in decisions.md.

### Telling whether a piece is already added

Removing a photo wouldn't affect tracking. The register and activity log hold each product's status,
and they don't depend on the photo.

The harder question is whether the piece in the client's hands has been added at all. The register
only knows SKUs, so it can't recognise a piece. A piece submitted twice under two numbers gets two
SKUs, with no warning. The client's Photos library alone doesn't settle it either, because a photo there may
never have been submitted, or may belong to a cancelled submission.

| Option | How it helps | To test or weigh up |
|---|---|---|
| **The printed SKU label on the piece.** | A labelled piece has been added, and its SKU can be looked up straight away. | Works once labels are a habit. Older pieces won't have one. |
| **The Shared Album.** | Shows every posted piece with its SKU in the caption. | Only if the photo was posted. A cancelled submission stays until it's deleted from the album. |
| **Keep the photos in the shared folder.** | Both phones can look through them by category, with the SKU as the file name. | Uses the storage above. |
| **The live store or Shopify admin.** | Covers older products, which aren't in the register. | Slower, and only finds what's already listed. |

### Keeping the original in Shopify, hidden from the storefront

Not decided yet. We didn't find a Shopify setting that hides one image on a product.

| Option | How it works | Risk |
|---|---|---|
| **A product metafield** (`file_reference`, such as `custom.original_photo`), with no storefront access. | The photo isn't in the product's media, so the gallery, product cards and sales channels don't use it. The admin shows it on the product page. | Needs one metafield definition, and `/add-products` has to upload it. |
| **A gallery image hidden by the theme,** for example by alt text. | It sits with the other images, and `product-media-gallery` and `card-product` skip it. | Everything that reads the product's media has to skip it: thumbnails, hover images, the product's public JSON, and feeds to sales channels. A theme update or a mistake could show it. |

Either way the file sits on Shopify's public image servers, so it's out of sight rather than private.
`/add-products` and the [listing checklist](listing-checklist.md) need updating once this is decided.

### A Shared Library: tested and ruled out

Searching for a caption in a Shared Library didn't work when tested on 5 November 2026, so the
album stays ([decision 26](../decisions.md#26-stay-with-the-shared-album-not-a-shared-library)).
