# Measured results

Suite **T1–T10** (30 trials/model). Pass/fail outcomes unchanged from the published runs. Tokens, wall-clock timing, and cost estimates below were verified offline from saved `outputs/` traces (no re-runs, no API calls).

## Summary

| Model | Passes / 30 | T10 | Input tok | Output tok | Wall time (sum) | Est. USD |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `claude-sonnet-5` | **30 / 30** | 3/3 | 353,803 | 26,835 | 340.7 s | **~$0.98** |
| `gpt-6.1-sol` | **30 / 30** | 3/3 | 106,666 | 6,049 | 339.7 s | **~$0.27** |
| `gemini-3.5-flash-lite` | **22 / 30** | 0/3 | 199,321 | 6,784 | 1831.4 s | **$0** (free tier) |
| `grok-4.7` | **20 / 30** | 0/3 | 440,495 | 5,078 | 321.6 s | **~$0.91** |

**Coverage label:** all four published summaries cover **T1–T10** (earlier `T1-T8` labels were stale and have been corrected).

**T10** (paginated roster count, exact `confirmed`, budget, saga order, live auth token) fails Grok/Gemini hard. Claude and GPT both clear it — pass-rate tie unbroken. On T10 mean latency (pass-only): GPT ~19.0 s vs Claude ~33.7 s.

### Timing notes

- Wall time is sum of `elapsed_seconds` across the published 30 trials (includes failures).
- Per-task `mean_latency_s` in the JSON summaries remains **pass-only** (null when a task has 0 passes).
- Gemini wall time is much higher because free-tier pacing / long failing T10 attempts (~233 s mean across its 3 T10 trials); one Gemini T10 trial hit free-tier quota (`429 RESOURCE_EXHAUSTED`).

### Cost notes

| Model | Pricing basis | Estimate |
| --- | --- | --- |
| Claude | Documented harness rates $2 in / $10 out per MTok | `(353803/1e6)*2 + (26835/1e6)*10 = $0.975956` |
| GPT | OpenAI list rates $2 in / $10 out per MTok for `gpt-6.1-sol` | `(106666/1e6)*2 + (6049/1e6)*10 = $0.273822` |
| Gemini | Free-tier run | **$0** recorded; paid Flash Lite list price not applied |
| Grok | Documented harness rates $2 in / $6 out per MTok | `(440495/1e6)*2 + (5078/1e6)*6 = $0.911458` |

Token totals match the reconstructed published trial sets exactly.

### Other misses

**Gemini:** T1 t3, T4 t1, T7×3, T10×3.  
**Grok:** T2 t3, T3 t2, T5 t3, T8 t1/t3, T9 t2/t3, T10×3.

Machine-readable: `*_summary.json` in this folder. Offline audit artifact: `offline_audit.json`.
