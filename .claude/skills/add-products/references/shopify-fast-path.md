# Verified Shopify fast path

Observed on the first live product, 22 November 2026, using Admin API 2026-10.
This is a reusable operation recipe, not permission to bypass current schema
validation, row checks or tool approvals. If the API version changes or a field
is rejected, inspect that field; do not start broad schema discovery again.

## What slowed the first run

The first run repeatedly looked up operation/type shapes, made separate reads
for already-known values and waited on an upload widget with no returned files.
Image generation itself took about 24 seconds for the fabric view and 19 seconds
for its detail; the later model-led hero took about 45 seconds. These are observed
durations, not a promised SLA. The missing editorial hero caused avoidable rework.

## Resolve once per batch

- Confirm store/domain/currency; the live store's myshopifyDomain is
  muzmvk-t1.myshopify.com and its public domain is periwinklebysherry.com.
- Freeze the register candidate list, note pending transactions/stock requests,
  and search current and legacy SKU forms in one read. Check exact returned SKUs.
- Resolve category collections by handle, active Shop location, Online Store
  publication and the relevant existing colour metaobjects once. Reuse this
  batch context for the next SKU, not IDs from a different store or old session.
- Publications expose catalog.title in the current schema; identify Online
  Store through that title. Do not rediscover or assume a Publication.name field.
- SAR taxonomy aa-1-23-2-1 was verified as Saris; confirm a different category's
  mapping only when that category is first encountered in the batch.

Read only the current category's image prompt. While images generate, prepare
grounded title/description/SEO, validate prices and construct the known mutation
variables. Batch independent reads; keep dependent mutations/checkpoints sequential.
Avoid displaying large schema dumps or re-reading every skill/reference per SKU.

## Per-product operation sequence

1. Snapshot/claim only this SKU. Generate the editorial hero first plus a useful
   supporting detail, then inspect both before upload. Draft inputs use the row's
   current price/cost and no gift tag for any category.
2. Create one DRAFT using create_product with options ["Title"], one Default
   Title variant, exact SKU, selling price and inventoryItem.tracked true. Persist
   product/variant IDs immediately. One product read supplies the returned handle,
   inventoryItem ID and current quantity; checkpoint them and a stable inventory UUID.
3. Configure product category/handle/SEO through productUpdate; configure cost,
   shipping/tax/inventory policy through productVariantsBulkUpdate; set existing
   colour references through metafieldsSet. These can be roots in one mutation
   when the category precedes its constrained metafield. Inspect every userErrors
   array because separate roots can succeed independently.
4. Upload the final images through the known working route below, checkpoint each
   successful file ID, and attach the existing IDs with fileUpdate. Initialize stock
   once using the verified current quantity and persisted idempotency key. Never
   repeat initialization on a resumed ACTIVE listing.
5. Read the complete draft once: content/SEO, current row prices, one default
   variant, inventory, category/colour, intended collections, no gift tag or gift
   collections, READY media and the actual featured hero. Record READY/link.
6. Recheck pending stock/current row, activate and publish only to Online Store.
   One fresh final query verifies all receipt fields and publication; then the
   helper records LIVE. Clean local working image copies after verified attachment.

Reuse these operation shapes on the next SKU. Do not replace fresh final reads
with an earlier draft result, or batch-claim all NEW products before their turn.

## Working image upload and ordering

The first upload_file(chatFile=workspace-copy) rendered an automatic upload
widget but two reads returned no files. upload_image(imageFile=the ORIGINAL
image_gen output path, filename=stable SKU/hash filename, alt=description)
then returned permanent file IDs/URLs without a merchant picker. This direct
route also succeeded for the detail and model-led hero. Prefer the working
noninteractive route for this environment. If a tool requires upload_file first,
pass the original generated chat path, check its app update/get_uploaded_files,
then use the direct route after a bounded failed handoff; avoid minutes of polling.
Before retrying an ambiguous upload, check Files for the SKU/hash to prevent copies.

Keep project/cache copies for inspection only. The path actually used for upload
must remain available until the upload has returned a real file ID. fileUpdate
requires READY files; attach with referencesToAdd:[productId], never by CDN URL.
The first run verified only the two intended files existed after fallback.

For an added hero: attach it to the existing product, then productReorderMedia
with moves:[{id:heroFileId,newPosition:"0"}]. MoveInput.newPosition is an
UnsignedInt64 serialized as a decimal string. Check mediaUserErrors, poll the
returned job until done, then verify media[0] equals the hero. Preserve supports.

## Current mutation field details

- ProductUpdateInput: category, handle, seo:{title:"",description}, status; the
  returned seo.title may be null when intentionally left empty.
- ProductVariantsBulkInput: price, taxable:false, inventoryPolicy:DENY and
  inventoryItem:{cost,tracked:true,requiresShipping:true,measurement:{weight}}.
  Keep the existing zero-weight convention until actual averages are supplied.
- Existing shopify.color-pattern definition: list.metaobject_reference. Read its
  existing definition/type, reuse plain colour metaobjects and use metafieldsSet;
  compareDigest:null guards an initial write where the field was verified absent.
- inventorySetQuantities: name:"available", reason:"correction", quantities
  with inventoryItemId, locationId, quantity and changeFromQuantity. The current
  schema uses changeFromQuantity, not the legacy compareQuantity input.
- Put @idempotent(key:$key) on the inventorySetQuantities field. Use the job's
  saved UUID; do not generate another key during a retry. Query the current level
  first. inventoryActivate is only needed if no level is active.
- publishablePublish: id and input:[{publicationId:onlineStoreId}]. Verify
  publishedOnPublication(publicationId:onlineStoreId); ACTIVE alone is insufficient.

Live corrections are explicit exceptions, not intake replays. Remove only the
requested tag with tagsRemove, add/reorder media by ID, then verify. Preserve
the register's LIVE state, publishedAt, SKU, price and stock. The original
publication receipt is historical; store correction evidence separately and
update current media checkpoints without emitting another publish transition.
