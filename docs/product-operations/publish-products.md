# Periwinkle – Publish Products

**Who runs it:** the operator. **Source:** `publish_products` in
[`build.py`](../../product-ops/build/build.py).

Marks a batch of `READY_TO_PUBLISH` products as `LIVE` in the register. It doesn't
publish anything in Shopify: do that first, then run this to record it.

## What happens

```mermaid
flowchart TD
    A["List register/READY_TO_PUBLISH"] --> B{"Any?"}
    B -->|No| B1[/"No products are marked<br/>READY_TO_PUBLISH."/] --> STOP([Stop])
    B -->|Yes| C["Check each product's URL"]
    C --> D{"Any invalid or missing?"}
    D -->|Yes| D1[/"These need a valid Shopify URL.<br/>They stay READY_TO_PUBLISH."/] --> E
    D -->|No| E{"Any with valid URLs?"}
    E -->|No| E1[/"Summary: Published 0"/] --> STOP
    E -->|Yes| F[/"Review: each SKU and its link"/]
    F --> G["Choose which are confirmed live<br/>(all are selected to start)"]
    G --> H["For each chosen product:<br/>Save to register/LIVE with the published time<br/>Write PRODUCT_PUBLISHED<br/>Move the old row to _replaced/"]
    H --> I[/"Batch summary: published,<br/>skipped, need URLs"/]
```

## Rules

- A product without a valid URL can't become `LIVE` here.
- Products you don't select stay `READY_TO_PUBLISH` and count as skipped.
- Stock status isn't touched.

If a product is already live when you add its link, use **I've checked it's live**
in [Work on Product](work-on-product.md) and skip this shortcut.
