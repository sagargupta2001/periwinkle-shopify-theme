# Periwinkle – Process Stock Requests

**Who runs it:** the operator. **Source:** `process_stock_requests` in
[`build.py`](../../product-ops/build/build.py).

Goes through the client's pending stock requests one at a time. Update Shopify
yourself first, because this shortcut only records the result.

## What happens

```mermaid
flowchart TD
    A["List stock-requests/PENDING"] --> B{"Any?"}
    B -->|No| B1[/"There are no pending<br/>stock requests."/] --> STOP([Stop])
    B -->|Yes| C["For each request, show the SKU, requested status,<br/>recorded stock, publication status, time asked and link"]
    C --> D{"Choose"}
    D -->|"Shopify updated: complete"| E["Update the row's stock and update time<br/>Save stock-requests/COMPLETED/id.json<br/>Write STOCK_REQUEST_COMPLETED<br/>Move the original to _handled/"]
    D -->|"Reject"| F["Ask for an optional reason<br/>Save stock-requests/REJECTED/id.json<br/>Write STOCK_REQUEST_REJECTED<br/>Move the original to _handled/"]
    D -->|"Skip for now"| G[No change. It comes back next time]
    E --> H{"More requests?"}
    F --> H
    G --> H
    H -->|Yes| C
    H -->|No| I[/"You've been through all<br/>the pending requests."/]
```

## Rules

- Viewing a request doesn't complete it. Only tapping **complete** does.
- Publication status never changes here, so a `LIVE` product can be `OUT_OF_STOCK`.
- A rejected request leaves the product's stock unchanged.
- The original request is kept in `_handled/`, and its outcome stays in `COMPLETED`
  or `REJECTED`.

## Updating Shopify

- **Out of stock:** set the quantity to 0.
- **Back in stock:** enter the quantity. The client doesn't report one, and most
  pieces are one of a kind, so it's usually 1. Ask if unsure.
