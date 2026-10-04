# Measured results

Suite **T1–T10** (30 trials/model).

## Summary

| Model | Passes / 30 | T10 (extreme saga) |
| --- | ---: | ---: |
| `claude-sonnet-5` | **30 / 30** | 3/3 |
| `gpt-6.1-sol` | **30 / 30** | 3/3 |
| `gemini-3.5-flash-lite` | **22 / 30** | 0/3 |
| `grok-4.7` | **20 / 30** | 0/3 |

**T10** (paginated roster count, exact `confirmed`, budget, saga order, live auth token) fails Grok/Gemini hard. Claude and GPT still both clear it — pass-rate tie unbroken. On T10 latency, GPT was ~19s mean vs Claude ~34s.

### Other misses

**Gemini:** T1 t3, T4 t1, T7×3, T10×3.  
**Grok:** T2 t3, T3 t2, T5 t3, T8 t1/t3, T9 t2/t3, T10×3.
