# T6 — Visual product match + cheapest eligible listing

**Adaptation of:** Daytona HackSprint SF rules (sponsor tools encouraged) + participant-reported “Shop the Video” theme  
**Sources:** https://daytona-hacksprint-sf-nov-25.devpost.com/rules ; https://devpost.com/software/shop-the-video (accessed 2026-10-03)  
**Evidence kind:** Official (encouraged tools) + **participant-reported** project description → evaluation adaptation  

**Official (paraphrase):** Sponsor tools encouraged, not universally mandatory; Daytona credits listed as winner prizes.  
**Participant-reported:** Product identification from video and price comparison (performance claims **not** independently verified).  

**Our adaptation:** Match synthetic frame descriptor `frame_clear_bottle` to a frozen catalog; return cheapest **eligible** listing. No purchases or affiliate actions. Does **not** reuse participant code/datasets.

**Role of the model:** Runtime multimodal model in the submitted project (if vision-capable). Unsupported vision = capability exclusion, not a normal fail for ranking text-only models.

---

## Task input

Frame id: `frame_clear_bottle` (descriptor in `fixtures/images/frames.json`).  
Match to catalog (`fixtures/catalog/products.json`). Return:

- `product_id`
- `listing_id` (cheapest with `eligible == true`)
- `price_usd`

## Allowed tools

- `search_catalog(query?, frame_id?)`
- `get_listing(product_id, listing_id?)`

## Explicit success criteria

| Check | Pass condition |
| --- | --- |
| Product | `CAT-BOTTLE-SLATE` |
| Listing | `L2` (not ineligible `L3` at $17) |
| Price | `19.99` (±0.01) |

**Capability exclusion:** If the candidate cannot accept visual/frame input under the shared settings, record `unsupported_capability` and exclude from vision success rate (still report in coverage notes).
