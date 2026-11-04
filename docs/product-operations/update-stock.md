# Periwinkle – Update Stock

**Who runs it:** the client. **Source:** `update_stock` in
[`build.py`](../../product-ops/build/build.py).

Reports that a piece is out of stock or back in stock. It only creates a request
for the operator. It doesn't change Shopify or the product's recorded stock.

## What happens

```mermaid
flowchart TD
    A[Choose a category] --> A2[Enter the product's number]
    A2 --> B{"A whole number, 1 or more?"}
    B -->|No| B1[/"Please check the number"/] --> STOP([Stop])
    B -->|Yes| C{"In products/?"}
    C -->|No| C1[/"We couldn't find this SKU.<br/>Please check the code."/] --> STOP
    C -->|Yes| D["Find its current row"]
    D --> E["Show SKU, price, publication<br/>status and stock on record"]
    E --> F{"Choose OUT_OF_STOCK<br/>or IN_STOCK"}
    F --> G{"Same as on record?"}
    G -->|Yes| H{"Submit anyway?"}
    H -->|"Don't submit"| STOP
    H -->|"Submit anyway"| I
    G -->|No| I["Save stock-requests/PENDING/id.json<br/>Write STOCK_REQUESTED to the log"]
    I --> J[/"Stock update request submitted."/]
```

## Rules

- It never asks for a quantity or photos.
- The client never types `PBS-` or the code, and leading zeros are optional: `4` finds
  `PBS-DUP-004`.
- Each request is a new file named with the time and SKU, so earlier requests are
  never overwritten.
- The recorded stock only changes when the operator completes the request, so
  a second report before then is treated as a real change.

## Good to know

Only products submitted through New Product can be found. Older Shopify products
aren't in the register.
