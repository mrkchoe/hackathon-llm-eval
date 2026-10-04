# Measured results

Suite **T1–T9** (27 trials/model). Lenient graders on T1–T6; hard compliance tasks T7–T9.

## Summary

| Model | Passes / 27 | T7 | T8 | T9 |
| --- | ---: | ---: | ---: | ---: |
| `claude-sonnet-5` | **27 / 27** | 3/3 | 3/3 | 3/3 |
| `gpt-6.1-sol` | **27 / 27** | 3/3 | 3/3 | 3/3 |
| `gemini-3.5-flash-lite` | **22 / 27** | 0/3 | 3/3 | 3/3 |
| `grok-4.7` | **20 / 27** | 3/3 | 1/3 | 1/3 |

GPT: `reasoning.effort=medium`. Claude/GPT still tie on pass rate; Claude faster on hard tasks. **T9** (amended payout + sanctions code + 2% withhold + dual approval) is the stress test — Grok drops to 1/3.

---

## T9 — Dual-control amended payout (very hard)

Stacked traps: superseded invoice amount, consulting 2% withhold (8500 → **8330**), sanctions hold cleared only with code `FP-SIM-44`, dual eligible approvers (not preferred `charlie`).

| Model | Passes / 3 |
| --- | ---: |
| Claude | 3 |
| GPT | 3 |
| Gemini | 3 |
| Grok | 1 |

---

## By task (passes / 3)

| Task | Claude | GPT | Gemini | Grok |
| --- | ---: | ---: | ---: | ---: |
| T1–T6 | 3 each | 3 each | see fails | see fails |
| T7 Policy remediation | 3 | 3 | 0 | 3 |
| T8 Amendment cancel | 3 | 3 | 3 | 1 |
| T9 Amended payout | 3 | 3 | 3 | 1 |

### Failures

**Gemini:** T1 t3, T4 t1, T7×3.  
**Grok:** T2 t3, T3 t2, T5 t3, T8 t1/t3, T9 t2/t3.
