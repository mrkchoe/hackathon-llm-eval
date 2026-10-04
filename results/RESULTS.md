# Measured results

Only live API runs are recorded here. Models marked “not run” were not evaluated.

## Summary

| Model | Conditions | Passes / trials |
| --- | --- | ---: |
| `gemini-3.5-flash-lite` | Free tier, temp 0, 3 trials/task, paced | **13 / 18** |
| `gpt-6.1-sol` | Responses API, `reasoning.effort=low`, 3 trials/task | **12 / 18** |
| `claude-sonnet-5` | — | not run |
| `grok-4.7` | — | not run |

Machine-readable:

- [`gemini_3.5_flash_lite_summary.json`](gemini_3.5_flash_lite_summary.json)
- [`openai_gpt-6.1-sol_summary.json`](openai_gpt-6.1-sol_summary.json)

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

**Tokens (18 trials):** ~24.4k input / ~2.9k output. Dollar cost not estimated (OpenAI rates not pinned in this repo).

### Failures (`gpt-6.1-sol`) — 6/18

| Task | Trial | Class | What failed |
| --- | ---: | --- | --- |
| T3 Ticket + calendar | 1–3 | `incorrect_output` | Ticket created, but **calendar** check failed (date/start/tz fields did not match expected `2026-11-03` / `15:00` / `PT`) |
| T5 Agent discovery | 1–3 | `incorrect_output` | Specialist found, but `confirmed` was false; constraints used `tz=America/Los_Angeles` instead of required `PT` |

### OpenAI notes
- Chat Completions cannot tool-call `gpt-6.1-sol`; runner uses **Responses API** with `reasoning.effort=low`.
- Earlier attempts: exhausted credits, then Chat Completions 400s — superseded by this measured run.

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
| T1 Web product research | 3 | `max_turns` | No valid final answer. Missed: `product_id`, `price_usd`, `page_url`, `in_stock` |
| T4 Durable workflow | 1 | `max_turns` | Approval→execute incomplete. Missed: `approval_before_execute`, `action`, `duplicates` |
| T5 Agent discovery | 1–2 | `max_turns` | No confirmed specialist result. Missed: `specialist`, `confirmed`, `constraints` |
| T5 Agent discovery | 3 | `incorrect_output` | Missed: `confirmed`, `constraints` |

### Gemini notes
- Free-tier **15 RPM**; paced with `--pace-seconds 20`. Out-of-pocket: **$0**.

### Not claimed
- Broad superiority from this small pilot  
- Official hackathon eligibility or live sponsor-stack usage  
