# Measured results

Only live API runs are recorded here. Cells or models marked “not run” were not evaluated.

## Summary

| Model | Conditions | Passes / trials |
| --- | --- | ---: |
| `gemini-3.5-flash-lite` | Free tier, temp 0, 3 trials/task, paced | **13 / 18** |
| `gpt-6.1-sol` | — | not run |
| `claude-sonnet-5` | — | not run |
| `grok-4.7` | — | not run |

Machine-readable: [`gemini_3.5_flash_lite_summary.json`](gemini_3.5_flash_lite_summary.json)

## `gemini-3.5-flash-lite` per task

| Task | Passes / 3 | Mean latency (successful trials) |
| --- | ---: | ---: |
| T1 Web product research | 2 | ~31 s |
| T2 Persistent memory | 3 | ~32 s |
| T3 Ticket + calendar | 3 | ~49 s |
| T4 Durable workflow | 2 | ~49 s |
| T5 Agent discovery | 0 | — |
| T6 Visual catalog match | 3 | ~6.4 s |

### Failure notes
- Early unpaced run hit free-tier **429** (15 RPM). Completed with `--pace-seconds 20` and retries.
- Failures on completed suite: `max_turns` (T1, T4, T5) and incorrect output (T5).
- Out-of-pocket cost: **$0** (free tier).

### Not claimed
- Superiority over unmeasured models  
- Official hackathon eligibility or sponsor-stack usage  
