# T1 — Web product research

**Adaptation of:** UC Berkeley AI Hackathon 2026 — Best Use of Browserbase  
**Source:** https://ai-hackathon-2026.devpost.com/ (accessed 2026-10-03)  
**Evidence kind:** Official requirement → evaluation adaptation  

**Official requirement (paraphrase):** Build a web agent using any model/framework; it must be powered by Browserbase (browsers, search, fetch, Stagehand, or Browse CLI).  

**Our adaptation:** Same goal (find a product with constraints + cite evidence) using **frozen fixture retailer pages** and tools `search_pages` / `fetch_page`. This does **not** prove Browserbase usage.

**Role of the model in a real hack:** Typically the **runtime** model inside the submitted agent (not the coding assistant used to write the code).

---

## Task input

Find an **in-stock** water bottle that is:

- color: `slate`
- capacity_ml: `750`
- price_usd: `<= 23`

Search only the fixture retailer index. Return:

- `product_id`
- `name`
- `price_usd`
- `page_url`
- `in_stock`

Do not invent availability. Prefer verified page fetch over search-index prices when they conflict.

Fixture: `fixtures/retailers/pages.json`

## Allowed tools

- `search_pages(query)`
- `fetch_page(url)`

## Explicit success criteria

| Check | Pass condition |
| --- | --- |
| Product | `product_id == "GD-9"` |
| Price | `price_usd == 19.99` (±0.01) |
| Evidence | `page_url == "https://fixture.shop/gamma/deals"` |
| Stock | `in_stock == true` |
| No fabrication | Does not claim in-stock crimson BO-88 or invent IDs |

**Pass:** all checks true. **Fail:** any check false, timeout, or provider error (record failure class).
