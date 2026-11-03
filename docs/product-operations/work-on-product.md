# Periwinkle – Work on Product

**Who runs it:** the operator. **Source:** `work_on_product` in
[`build.py`](../../product-ops/build/build.py).

The operator's main shortcut, covering each change to a single product. The first
menu shows a build number, which confirms which version a phone has.

```mermaid
flowchart TD
    A{"What are you doing?"}
    A --> S[Start a new product]
    A --> L[Add or fix a Shopify link]
    A --> B[Move a product back]
    A --> F["Correct a product's prices"]
```

## Start a new product

```mermaid
flowchart TD
    A["List register/NEW"] --> B{"Any?"}
    B -->|No| B1[/"There are no NEW products."/] --> STOP([Stop])
    B -->|Yes| C[Choose one]
    C --> D{"Already further along?"}
    D -->|Yes| D1["Clear the leftover NEW copy<br/>and say which status it's in"] --> STOP
    D -->|No| E["Copy its details for Claude"]
    E --> F["Save register/IN_PROGRESS/sku.json<br/>Write PROCESSING_STARTED to the log"]
    F --> G[/"Now IN_PROGRESS, with the details"/]
    G --> H["Move the NEW row to register/_replaced/"]
```

Find the photos in the album using the submitted date, because Photos can't
search by SKU. Then list the piece using the
[listing checklist](listing-checklist.md).

## Add or fix a Shopify link

```mermaid
flowchart TD
    A["List NEW, IN_PROGRESS and<br/>READY_TO_PUBLISH"] --> B{"Any?"}
    B -->|No| STOP([Stop with a message])
    B -->|Yes| C[Choose one, then paste the URL]
    C --> D{"A valid product URL?"}
    D -->|No| D1[/"That link doesn't look right.<br/>Nothing has been changed."/] --> STOP
    D -->|Yes| E{"Is it published in Shopify?"}
    E --> F["Write SHOPIFY_URL_RECORDED to the log"]
    F -->|"Not yet"| G["Save to READY_TO_PUBLISH"]
    G --> G1[/"Saved"/] --> G2{"Was it elsewhere?"}
    G2 -->|Yes| G3["Move the old row to _replaced/"]
    F -->|"I've checked it's live"| H["Save to LIVE with the published time<br/>Write PRODUCT_PUBLISHED"]
    H --> H1[/"Saved"/] --> H2["Move the old row to _replaced/"]
```

A valid URL starts with `https://periwinklebysherry.com/` or
`https://periwinkle-by-sherry.myshopify.com/` and contains `/products/`. Admin
links are rejected, because the register keeps the public link.

**I've checked it's live** is for products already published, so they don't need a
second step through Publish Products.

## Move a product back

```mermaid
flowchart TD
    A[Enter SKU] --> B{"Found?"}
    B -->|No| STOP([Stop with a message])
    B -->|Yes| C{"Move to which status?"}
    C -->|Leave it| STOP
    C -->|Same as now| STOP
    C -->|"NEW, IN_PROGRESS or<br/>READY_TO_PUBLISH"| D["Save the row there, clearing the published date<br/>Write STATUS_MOVED_BACK to the log"]
    D --> E[/"Moved back. Shopify hasn't changed."/]
    E --> F["Move the old row to _replaced/"]
```

The link is kept. If the product was live, unpublish it in Shopify yourself if it
shouldn't be on sale.

## Correct a product's prices

```mermaid
flowchart TD
    A[Enter SKU] --> B{"Found?"}
    B -->|No| STOP([Stop with a message])
    B -->|Yes| C[Enter both prices]
    C --> D["Overwrite the row in its current folder<br/>Write PRICE_CORRECTED with old and new"]
    D --> E[/"Prices corrected. Update Shopify too<br/>if the selling price is already live."/]
```

This works at any status. It doesn't change the original submission in `products/`,
which keeps what the client first sent.
