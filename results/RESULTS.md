# Measured results

Only live API runs are recorded here. Models marked “not run” were not evaluated.

## Summary

| Model | Conditions | Passes / trials |
| --- | --- | ---: |
| `gemini-3.5-flash-lite` | Free tier, temp 0, 3 trials/task, paced | **13 / 18** |
| `gpt-6.1-sol` | — | not run |
| `claude-sonnet-5` | — | not run |
| `grok-4.7` | — | not run |

Machine-readable: [`gemini_3.5_flash_lite_summary.json`](gemini_3.5_flash_lite_summary.json)

## `gemini-3.5-flash-lite` per task

| Task | Passes / 3 | Mean latency (passes) |
| --- | ---: | ---: |
| T1 Web product research | 2 | ~31 s |
| T2 Persistent memory | 3 | ~32 s |
| T3 Ticket + calendar | 3 | ~49 s |
| T4 Durable workflow | 2 | ~49 s |
| T5 Agent discovery | 0 | — |
| T6 Visual catalog match | 3 | ~6.4 s |

## Failures (`gemini-3.5-flash-lite`)

5 failed trials out of 18:

| Task | Trial | Class | What failed |
| --- | ---: | --- | --- |
| T1 Web product research | 3 | `max_turns` | No valid final answer within turn limit. Missed checks: `product_id`, `price_usd`, `page_url`, `in_stock` |
| T4 Durable workflow | 1 | `max_turns` | Did not complete approval→execute. Missed checks: `approval_before_execute`, `action`, `duplicates` |
| T5 Agent discovery | 1 | `max_turns` | No confirmed specialist result. Missed checks: `specialist`, `confirmed`, `constraints` |
| T5 Agent discovery | 2 | `max_turns` | Same as trial 1. Missed checks: `specialist`, `confirmed`, `constraints` |
| T5 Agent discovery | 3 | `incorrect_output` | Finished a response but failed checks: `confirmed`, `constraints` (specialist check passed) |

### Notes
- An earlier unpaced run also hit free-tier **429** (15 RPM). Those rate-limit attempts were superseded by paced retries and are not counted above.
- Out-of-pocket cost: **$0** (free tier).
- Not claimed: superiority over unmeasured models, or official hackathon / sponsor-stack eligibility.
