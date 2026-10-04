# Measured results

Only live API runs are recorded here. Scores use the **current lenient graders** (regraded from saved tool traces).

**Grading note:** Pacific tz accepts `PT` ≈ `America/Los_Angeles`; common tool-arg aliases and nested wrappers (`{"id":…}`, `{"value":…}`); T5 confirmation from a complete booking payload.

## Summary

| Model | Conditions | Passes / trials |
| --- | --- | ---: |
| `claude-sonnet-5` | Anthropic Messages API + tools | **18 / 18** |
| `gpt-6.1-sol` | Responses API, `reasoning.effort=low` | **18 / 18** |
| `gemini-3.5-flash-lite` | Free tier, paced | **16 / 18** |
| `grok-4.7` | xAI OpenAI-compatible API | **15 / 18** |

Machine-readable: JSON summaries in this folder + [`regrade_overlay.json`](regrade_overlay.json).

---

## `claude-sonnet-5` / `gpt-6.1-sol`

All tasks **3/3** (18/18).

---

## `gemini-3.5-flash-lite` — **16/18**

| Task | Passes / 3 | Notes |
| --- | ---: | --- |
| T1 | 2 | Trial 3: no product answer |
| T2 | 3 | |
| T3 | 3 | |
| T4 | 2 | Trial 1: never executed after approval |
| T5 | 3 | |
| T6 | 3 | |

---

## `grok-4.7` — **15/18**

| Task | Passes / 3 | Mean latency (passes) |
| --- | ---: | ---: |
| T1 Web product research | 3 | ~6.7 s |
| T2 Persistent memory | 2 | ~8.0 s |
| T3 Ticket + calendar | 2 | ~11.7 s |
| T4 Durable workflow | 3 | ~7.6 s |
| T5 Agent discovery | 2 | ~13.0 s |
| T6 Visual catalog match | 3 | ~2.7 s |

**Tokens:** ~151.7k in / ~2.4k out. Est. cost ~**$0.32** ($2 / $6 per MTok).

### Failures — 3/18

| Task | Trial | Class | What failed |
| --- | ---: | --- | --- |
| T2 Persistent memory | 3 | `incorrect_output` | Wrote junk (`-1`) instead of vegetarian; recall wrong |
| T3 Ticket + calendar | 2 | `incorrect_output` | Never created ticket/calendar (`read_note` arg error) |
| T5 Agent discovery | 3 | `incorrect_output` | No specialist messaging; `confirmed` false |

### Not claimed
- Broad superiority from this small pilot  
- Official hackathon eligibility or live sponsor-stack usage  
