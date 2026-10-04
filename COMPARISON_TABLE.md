# Comparison tables

**Measured:** Claude **18/18**, GPT **18/18**, Gemini **16/18**, Grok **15/18**.

Lenient graders (Pacific tz aliases; tool-arg aliases / nested wrappers; T5 complete booking payload). Regraded from saved traces.

---

## A. Runtime models — measured task success (3 trials each)

| Task | `gpt-6.1-sol` | `claude-sonnet-5` | `gemini-3.5-flash-lite` | `grok-4.7` |
| --- | ---: | ---: | ---: | ---: |
| T1 Web product research | **3/3** | **3/3** | **2/3** | **3/3** |
| T2 Persistent memory | **3/3** | **3/3** | **3/3** | **2/3** |
| T3 Ticket + calendar | **3/3** | **3/3** | **3/3** | **2/3** |
| T4 Durable workflow | **3/3** | **3/3** | **2/3** | **3/3** |
| T5 Agent discovery | **3/3** | **3/3** | **3/3** | **2/3** |
| T6 Visual catalog match | **3/3** | **3/3** | **3/3** | **3/3** |
| **Total passes / 18** | **18/18** | **18/18** | **16/18** | **15/18** |

### Latency (mean seconds; successful trials)

| Task | `gpt-6.1-sol` | `claude-sonnet-5` | `gemini-3.5-flash-lite` | `grok-4.7` |
| --- | ---: | ---: | ---: | ---: |
| T1 | ~6.7 | ~4.5 | ~31 (2 passes) | ~6.7 |
| T2 | ~7.8 | ~4.8 | ~32 | ~8.0 (2 passes) |
| T3 | ~14.1 | ~8.5 | ~49 | ~11.7 (2 passes) |
| T4 | ~7.6 | ~6.3 | ~49 (2 passes) | ~7.6 |
| T5 | ~10.8 | ~15.2 | ~48 | ~13.0 (2 passes) |
| T6 | ~3.8 | ~6.0 | ~6.4 | ~2.7 |

### Cost (gross USD estimate)

| Model | Pricing status | Sum of trial estimates |
| --- | --- | ---: |
| `gpt-6.1-sol` | ~24.4k in / 2.9k out; rates not pinned | null |
| `claude-sonnet-5` | ~106.8k in / 10.9k out; $2 / $10 per MTok | **~$0.32** |
| `gemini-3.5-flash-lite` | free tier | **$0** |
| `grok-4.7` | ~151.7k in / 2.4k out; $2 / $6 per MTok | **~$0.32** |

### Failure classes observed (counts)

| Failure class | gpt-6.1-sol | claude-sonnet-5 | gemini-3.5-flash-lite | grok-4.7 |
| --- | ---: | ---: | ---: | ---: |
| incorrect_output | 0 | 0 | 0 | 3 |
| max_turns | 0 | 0 | 2 | 0 |

### Failed trials (`gemini-3.5-flash-lite`)

| Task | Trial | Class | Missed checks |
| --- | ---: | --- | --- |
| T1 | 3 | max_turns | product_id, price_usd, page_url, in_stock |
| T4 | 1 | max_turns | approval_before_execute, action, duplicates |

### Failed trials (`grok-4.7`)

| Task | Trial | Class | Missed checks |
| --- | ---: | --- | --- |
| T2 | 3 | incorrect_output | write, recall |
| T3 | 2 | incorrect_output | ticket_title, ticket_due, ticket_owner, calendar |
| T5 | 3 | incorrect_output | specialist, confirmed |

Full writeup: [`results/RESULTS.md`](results/RESULTS.md)

---

## B. Build-time assistants vs runtime models (not scored together)

| Dimension | Build-time assistant | Runtime model (T1–T6) |
| --- | --- | --- |
| Job | Help humans write/debug the hack | Power the submitted agent/app |
| In this evaluation | **Described only** | **Measured when keys available** |

---

## How to populate table A

```bash
python scripts/run_comparison.py --provider openai --model gpt-6.1-sol --trials 3
python scripts/run_comparison.py --provider anthropic --model claude-sonnet-5 --trials 3
python scripts/run_comparison.py --provider gemini --model gemini-3.5-flash-lite --trials 3 --pace-seconds 20
python scripts/run_comparison.py --provider grok --model grok-4.7 --trials 3
python scripts/regrade_all.py
```
