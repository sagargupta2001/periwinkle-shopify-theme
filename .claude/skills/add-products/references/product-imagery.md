# Product heroes and category prompts

Use this when preparing product images. Read the matching category section;
adapt its prompt to the actual source rather than copying product facts from a
style example. Sagar's 22 November direction is premium Indian editorial imagery
for the storefront hero, with fabric/detail photographs later in the gallery.

## Shared art direction

Create one portrait 4:5 hero. Target 1600 × 2000 px where supported; inspect the
actual returned dimensions and ratio rather than claiming requested dimensions.
The first built-in outputs were 1122 × 1402, visually 4:5 with minor pixel rounding.
Use soft directional daylight, realistic shadows, restrained warm-neutral plaster,
stone/dark wood and subtle patina. Let the actual product supply the colour;
do not force a brand palette. Keep breathing room for a Shopify card, with the
product dominant and sharply visible. No text, branding, watermark, graphic
frame, collage, dramatic palace, fantasy architecture or excessive bokeh.

For people, use a beautiful adult Indian model with natural features/skin,
understated makeup and an elegant comfortable pose. Styling is contemporary and
timeless, without Bollywood/bridal glamour or heavy jewellery. Check anatomy,
hands, fabric folds and jewellery geometry. Styling garments and props must not
be described as included in the sale.

Before the category prompt, write a short fact lock from the source: exact base
colour, motif shape/scale/spacing, border, visible material texture, item shape,
and included pieces. Repeat these invariants in each edit. A Banarasi editorial
example supplies aesthetic direction only: silk, zari, origin, handloom and craft
claims belong in a prompt/listing only when supported for this specific SKU.
Do not introduce richer-looking construction to make the product seem premium.

## SAR — sarees

> Create a premium Indian textile-house editorial product photograph of an adult
> Indian woman wearing the ACTUAL saree in the reference. Use a natural drape and
> a three-quarter/full-length composition showing the body, pleats and border.
> Preserve [base colour], [exact motifs and spacing], [border] and [visible texture].
> Continue only the evidenced body pattern; do not invent an ornate pallu, zari,
> silk sheen or new motifs. Use a restrained plain blouse as styling, soft daylight
> and a quiet heritage interior. The saree dominates the portrait 4:5 frame.

For PBS-SAR-001 the lock was muted lavender-grey, pink floral sprigs with black
outlines and a narrow pink triangular/orange patterned border. The Banarasi
example did not authorize gold zari or a silk finish on this saree.

## DUP — dupattas

> Photograph an adult Indian woman showcasing the ACTUAL dupatta over a plain,
> understated neutral outfit. Drape it naturally across her shoulders/arms so the
> reference's border, motifs and any visible end finishing are readable. Preserve
> [colour], [motif geometry/scale], [border] and [texture]. Show the product clearly
> in a three-quarter 4:5 editorial portrait with soft daylight and restrained Indian
> architectural texture. Do not invent tassels, embroidery or an unseen reverse.

## SKZ — unstitched salwar suit sets

Sagar requested a model wearing a salwar kameez visualization on 24 November
2026. When the source establishes the neckline/front panel, motifs and hem,
use this prompt. Keep the listing type unstitched and state that the model image
illustrates one possible tailored look; plain styling trousers are not evidence
of an included piece. Preserve the evidenced coordinating fabric and trim.

> Create a premium 4:5 Indian fashion editorial of an adult Indian woman wearing
> a conservative salwar kameez styling visualization made from the ACTUAL
> unstitched fabric. Preserve [base colour], [neckline decoration], [motifs and
> spacing], [hem/border] and [visible coordinating fabric/trim]. Use a simple
> silhouette and plain sleeves/trousers as styling without invented decorative
> details. Show the front and neckline clearly in a quiet heritage setting with
> soft daylight. Do not imply the tailored cut is supplied or invent additional
> matching pieces, fabric composition, embroidery or a reverse view.

If the source cannot establish the defining front design, present the actual
fabric instead of inventing it:

> Create an Indian fashion editorial featuring an adult model presenting the
> ACTUAL unstitched fabric set. Arrange/drape only the pieces visible in the
> reference over restrained plain styling; show [body fabric], [borders] and any
> confirmed coordinating pieces clearly. Preserve each fabric's colour, pattern
> and texture. Keep it visibly a presentation of unstitched material, not proof of
> a finished tailored suit. Use a premium 4:5 portrait and quiet heritage setting.

Do not invent neckline decoration, matching trousers, dupatta or stitched
embellishment. A finished-suit visualization needs enough design evidence;
otherwise showcase the actual fabric without claiming a cut.

## RED — ready-made clothing

> Create a premium 4:5 fashion portrait of an adult Indian model wearing the
> ACTUAL [garment type] from the reference. Match its silhouette, length, sleeves,
> neckline, closures, fit details, pattern and colour. Choose framing that shows
> the garment fully and a natural pose that leaves its defining details visible.
> Use understated styling, soft daylight and restrained Indian architectural
> textures. Keep the garment, rather than props or glamour, the focal point.

If a source omits a defining cut/detail needed for this view, request another
source rather than deciding what the hidden garment should look like.

## JEW — jewellery

> Create a premium 4:5 editorial photograph of an adult Indian model wearing the
> ACTUAL [earring/necklace/ring]. Use an ear/neck/hand composition appropriate to
> the piece and make it the clear focal point. Match its exact silhouette, metal
> colour, stones, fastenings, number of elements and evidenced scale. Use natural
> skin, restrained styling and soft light that reveals genuine surface detail.
> Avoid added jewellery, invented matching pieces, skin smoothing or false sparkle.

Do not invent a second earring, gemstone type, metal purity or dimensions. If
scale is unknown, keep framing neutral rather than implying a measured size.

## MIN — miniatures

> Create a premium 4:5 product editorial still life of the ACTUAL miniature on
> a restrained neutral surface with subtle Indian heritage material textures.
> Preserve every visible component, count, colour, shape and surface detail.
> Use a clean three-quarter view only where the reference supports it, realistic
> lighting and crisp focus on the object. Keep supporting surroundings minimal;
> do not add pieces, mechanisms, packaging or misleading full-size context.

Prefer the supplied viewpoint if another angle would require inventing geometry.
Do not introduce a model/hand or props that assert an unsupported physical size.

## HOM — home decor

> Create a premium 4:5 interior/product editorial with the ACTUAL [object] as
> the hero, against understated warm plaster, stone or dark wood appropriate to
> its visible finish. Match the reference's form, colour, material appearance,
> handles, openings, design and included item count. Show its defining details
> clearly under soft natural light. Keep the scene uncluttered and scale neutral;
> avoid adding contents, plants, stands or accessories that appear included.

For functional items, do not invent capacity, unseen openings or how they work.
Use an existing evidenced viewpoint when the source does not establish the back.

## Gallery and QA

Order: editorial hero first, then the cleaned product/fabric view, then a genuine
detail where useful. One source may support a hero plus one detail; do not create
extra filler views. Preserve useful existing supporting images during corrections.
Compare the hero against the source for colour, pattern, border, item geometry
and included pieces, then check pose/anatomy and storefront thumbnail readability.
Inspect detail crops for added construction or invented fine detail.

Upload and attach by file ID. If the hero was the third upload, use
productReorderMedia to move it to zero; poll its job and verify the actual first
media ID/featured image. Do not recreate a live product or reset its inventory.
