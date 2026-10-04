# Measured results

Only live API runs are recorded here. Models marked “not run” were not evaluated.

## Summary

| Model | Conditions | Passes / trials |
| --- | --- | ---: |
| `claude-sonnet-5` | Anthropic Messages API + tools | **16 / 18** |
| `gemini-3.5-flash-lite` | Free tier, paced | **13 / 18** |
| `gpt-6.1-sol` | Responses API, `reasoning.effort=low` | **12 / 18** |
| `grok-4.7` | — | not run |

Machine-readable:

- [`anthropic_claude-sonnet-5_summary.json`](anthropic_claude-sonnet-5_summary.json)
- [`gemini_3.5_flash_lite_summary.json`](gemini_3.5_flash_lite_summary.json)
- [`openai_gpt-6.1-sol_summary.json`](openai_gpt-6.1-sol_summary.json)

---

## `claude-sonnet-5` by task

| Task | Passes / 3 | Mean latency (passes) |
| --- | ---: | ---: |
| T1 Web product research | 3 | ~4.5 s |
| T2 Persistent memory | 3 | ~4.8 s |
| T3 Ticket + calendar | 3 | ~8.5 s |
| T4 Durable workflow | 3 | ~6.3 s |
| T5 Agent discovery | 1 | ~14.6 s (1 pass) |
| T6 Visual catalog match | 3 | ~6.0 s |

**Tokens (18 trials):** ~106.8k input / ~10.9k output.  
**Estimated cost:** ~**$0.32** (using $2 / $10 per MTok in/out).

### Failures (`claude-sonnet-5`) — 2/18

| Task | Trial | Class | What failed |
| --- | ---: | --- | --- |
| T5 Agent discovery | 1 | `incorrect_output` | Constraints looked right, but `confirmed` was false |
| T5 Agent discovery | 3 | `max_turns` | No valid final answer; missed `specialist`, `confirmed`, `constraints` |

---

## `gpt-6.1-sol` by task

| Task | Passes / 3 | Mean latency (passes) |
| --- | ---: | ---: |
| T1 Web product research | 3 | ~6.7 s |
| T2 Persistent memory | 3 | ~7.8 s |
| T3 Ticket + calendar | 0 | — |
| T4 Durable workflow | 3 | ~7.6 s |
| T5 Agent discovery | 0 | — |
| T6 Visual catalog match | 3 | ~3.8 s |

**Tokens:** ~24.4k in / ~2.9k out. Dollar cost not estimated.

### Failures (`gpt-6.1-sol`) — 6/18

| Task | Trial | Class | What failed |
| --- | ---: | --- | --- |
| T3 Ticket + calendar | 1–3 | `incorrect_output` | Calendar fields did not match expected `2026-11-03` / `15:00` / `PT` |
| T5 Agent discovery | 1–3 | `incorrect_output` | Not confirmed; used `America/Los_Angeles` instead of `PT` |

---

## `gemini-3.5-flash-lite` by task

| Task | Passes / 3 | Mean latency (passes) |
| --- | ---: | ---: |
| T1 Web product research | 2 | ~31 s |
| T2 Persistent memory | 3 | ~32 s |
| T3 Ticket + calendar | 3 | ~49 s |
| T4 Durable workflow | 2 | ~49 s |
| T5 Agent discovery | 0 | — |
| T6 Visual catalog match | 3 | ~6.4 s |

### Failures (`gemini-3.5-flash-lite`) — 5/18

| Task | Trial | Class | What failed |
| --- | ---: | --- | --- |
| T1 Web product research | 3 | `max_turns` | Missed: `product_id`, `price_usd`, `page_url`, `in_stock` |
| T4 Durable workflow | 1 | `max_turns` | Missed: `approval_before_execute`, `action`, `duplicates` |
| T5 Agent discovery | 1–2 | `max_turns` | Missed: `specialist`, `confirmed`, `constraints` |
| T5 Agent discovery | 3 | `incorrect_output` | Missed: `confirmed`, `constraints` |

Out-of-pocket Gemini cost: **$0** (free tier; RPM-limited).

### Not claimed
- Broad superiority from this small pilot  
- Official hackathon eligibility or live sponsor-stack usage  
