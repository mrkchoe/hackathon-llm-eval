# Measured results

Only live API runs are recorded here. Scores below use the **current lenient graders** (regraded from saved tool traces; no fabricated trials).

**Grading note:** Pacific timezone accepts `PT` ≈ `America/Los_Angeles`; sandbox accepts common tool arg aliases; T5 confirmation accepts a complete booking payload (structured dict, `constraints` sibling, or clear prose), not only a literal `"PT"` + nested dict.

## Summary

| Model | Conditions | Passes / trials |
| --- | --- | ---: |
| `claude-sonnet-5` | Anthropic Messages API + tools | **18 / 18** |
| `gpt-6.1-sol` | Responses API, `reasoning.effort=low` | **18 / 18** |
| `gemini-3.5-flash-lite` | Free tier, paced | **16 / 18** |
| `grok-4.7` | — | not run |

Machine-readable:

- [`anthropic_claude-sonnet-5_summary.json`](anthropic_claude-sonnet-5_summary.json)
- [`openai_gpt-6.1-sol_summary.json`](openai_gpt-6.1-sol_summary.json)
- [`gemini_3.5_flash_lite_summary.json`](gemini_3.5_flash_lite_summary.json)
- [`regrade_overlay.json`](regrade_overlay.json)

---

## `claude-sonnet-5` by task

| Task | Passes / 3 |
| --- | ---: |
| T1–T6 | 3 each |

**Tokens (18 trials):** ~106.8k input / ~10.9k output. Est. cost ~**$0.32**.

Previously under strict grading: 16/18 (T5 label/payload pedantry). Regrade: **18/18**.

---

## `gpt-6.1-sol` by task

| Task | Passes / 3 |
| --- | ---: |
| T1–T6 | 3 each |

**Tokens:** ~24.4k in / ~2.9k out.

Previously under strict grading: 12/18 (T3/T5 failed on `America/Los_Angeles` vs `PT` and rigid `message` shape). Regrade: **18/18**.

---

## `gemini-3.5-flash-lite` by task

| Task | Passes / 3 | Notes |
| --- | ---: | --- |
| T1 Web product research | 2 | Trial 3: no product answer (`max_turns`) |
| T2 Persistent memory | 3 | |
| T3 Ticket + calendar | 3 | |
| T4 Durable workflow | 2 | Trial 1: never executed after approval (`max_turns`) |
| T5 Agent discovery | 3 | |
| T6 Visual catalog match | 3 | |

### Remaining failures (`gemini-3.5-flash-lite`) — 2/18

| Task | Trial | Class | What failed |
| --- | ---: | --- | --- |
| T1 Web product research | 3 | `max_turns` | Missed: `product_id`, `price_usd`, `page_url`, `in_stock` |
| T4 Durable workflow | 1 | `max_turns` | Missed: `approval_before_execute`, `action`, `duplicates` |

Out-of-pocket Gemini cost: **$0** (free tier).

### Not claimed
- Broad superiority from this small pilot  
- Official hackathon eligibility or live sponsor-stack usage  
