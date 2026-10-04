# Measured results

Scores use lenient graders on saved traces. Suite is **T1–T8** (24 trials/model).

**Hard tasks added:**  
- **T7** policy-gated remediation (hidden fraud risk → escalate)  
- **T8** amendment cancellation (must not create from stale note)

## Summary

| Model | Passes / 24 | T7 | T8 | Notes |
| --- | ---: | ---: | ---: | --- |
| `claude-sonnet-5` | **24 / 24** | 3/3 | 3/3 | Fastest on hard tasks (~9.8s mean T7+T8) |
| `gpt-6.1-sol` | **24 / 24** | 3/3 | 3/3 | Tied on pass rate; ~11.0s mean T7+T8 |
| `grok-4.7` | **19 / 24** | 3/3 | 1/3 | Misses on T2/T3/T5 + T8 |
| `gemini-3.5-flash-lite` | **19 / 24** | 0/3 | 3/3 | Free tier; fails T7 |

Claude and GPT both clean-sweep pass rate; T7/T8 separate the field below them. Tie-break among perfect scores: latency on hard tasks (Claude faster).

---

## By task (passes / 3)

| Task | Claude | GPT | Gemini | Grok |
| --- | ---: | ---: | ---: | ---: |
| T1 Web research | 3 | 3 | 2 | 3 |
| T2 Memory | 3 | 3 | 3 | 2 |
| T3 Ticket + calendar | 3 | 3 | 3 | 2 |
| T4 Durable workflow | 3 | 3 | 2 | 3 |
| T5 Agent discovery | 3 | 3 | 3 | 2 |
| T6 Visual catalog | 3 | 3 | 3 | 3 |
| T7 Policy remediation | 3 | 3 | 0 | 3 |
| T8 Amendment cancel | 3 | 3 | 3 | 1 |

### Remaining failures

**Gemini:** T1 t3, T4 t1, T7 t1–t3 (max_turns / incomplete remediation).  
**Grok:** T2 t3, T3 t2, T5 t3, T8 t1 & t3.

### Cost (approx.)

| Model | Estimate |
| --- | --- |
| Claude | ~$0.3+ (full T1–T8 token mix) |
| GPT | rates not pinned |
| Grok | ~$0.3+ |
| Gemini | $0 free tier |
