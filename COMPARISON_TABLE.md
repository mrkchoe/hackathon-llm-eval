# Comparison tables

**Measured so far:** Anthropic `claude-sonnet-5` **18/18**, OpenAI `gpt-6.1-sol` **18/18**, Gemini free-tier `gemini-3.5-flash-lite` **16/18**. Grok still `—`.

Scores use lenient graders (Pacific tz aliases; common tool arg aliases; T5 complete booking payload). Regraded from saved tool traces — not re-called APIs.

`gemini-3.8-flash` was attempted but returned 503 high-demand on free tier; evaluation used `gemini-3.5-flash-lite`.

---

## A. Runtime models — measured task success (3 trials each)

Shared conditions: temperature 0 where supported; same prompts/tools/fixtures; provider-hosted extras off.

| Task | `gpt-6.1-sol` | `claude-sonnet-5` | `gemini-3.5-flash-lite` | `grok-4.7` |
| --- | ---: | ---: | ---: | ---: |
| T1 Web product research | **3/3** | **3/3** | **2/3** | — |
| T2 Persistent memory | **3/3** | **3/3** | **3/3** | — |
| T3 Ticket + calendar | **3/3** | **3/3** | **3/3** | — |
| T4 Durable workflow | **3/3** | **3/3** | **2/3** | — |
| T5 Agent discovery | **3/3** | **3/3** | **3/3** | — |
| T6 Visual catalog match | **3/3** | **3/3** | **3/3** | — |
| **Total passes / 18** | **18/18** | **18/18** | **16/18** | — |

`gpt-6.1-sol` settings: OpenAI **Responses API**, `reasoning.effort=low`.  
`claude-sonnet-5` settings: Anthropic **Messages API** + tools (no `temperature`; model rejected it).

### Latency (mean seconds; successful trials where available)

| Task | `gpt-6.1-sol` | `claude-sonnet-5` | `gemini-3.5-flash-lite` | `grok-4.7` |
| --- | ---: | ---: | ---: | ---: |
| T1 | ~6.7 | ~4.5 | ~31 (2 passes) | — |
| T2 | ~7.8 | ~4.8 | ~32 | — |
| T3 | ~14.1 | ~8.5 | ~49 | — |
| T4 | ~7.6 | ~6.3 | ~49 (2 passes) | — |
| T5 | ~10.8 | ~15.2 | ~48 | — |
| T6 | ~3.8 | ~6.0 | ~6.4 | — |

### Cost (gross USD estimate; null if rates unknown)

| Model | Pricing status | Sum of trial estimates |
| --- | --- | ---: |
| `gpt-6.1-sol` | rates not pinned here; ~24.4k in / 2.9k out tokens recorded | null |
| `claude-sonnet-5` | ~106.8k in / 10.9k out; $2 / $10 per MTok in/out | **~$0.32** |
| `gemini-3.5-flash-lite` | free-tier run; dollar rate not invoiced here | **$0 out-of-pocket** |
| `grok-4.7` | documented estimate ($2 / $6 per MTok in/out, xAI docs 2026-10-03) | — |

### Failure classes observed (counts)

| Failure class | gpt-6.1-sol | claude-sonnet-5 | gemini-3.5-flash-lite | grok-4.7 |
| --- | ---: | ---: | ---: | ---: |
| incorrect_output | 0 | 0 | 0 | — |
| provider_error | 0 | 0 | 0 (after pacing) | — |
| rate_limit | 0 | 0 | early unpaced only | — |
| timeout / max_turns | 0 | 0 | 2 (T1 t3, T4 t1) | — |
| unsupported_capability | 0 | 0 | 0 | — |

### Failed trials (`gemini-3.5-flash-lite`)

| Task | Trial | Class | Missed checks |
| --- | ---: | --- | --- |
| T1 | 3 | max_turns | product_id, price_usd, page_url, in_stock |
| T4 | 1 | max_turns | approval_before_execute, action, duplicates |

Full writeup: [`results/RESULTS.md`](results/RESULTS.md)


---

## B. Build-time assistants vs runtime models (not scored together)

| Dimension | Build-time assistant | Runtime model (T1–T6) |
| --- | --- | --- |
| Job | Help humans write/debug the hack | Power the submitted agent/app |
| Examples at these events | Claude Code prize framing; IDE assistants; workshop tools | API IDs above inside the project |
| Success signal | Shipping a demo | Passing task criteria / user outcomes |
| Paid by | Often subscription or free IDE tier | API tokens, sometimes sponsor credits |
| In this evaluation | **Described only** | **Measured when keys available** |

---

## C. Documented capabilities (not measured scores)

| Capability | gpt-6.1-sol | claude-sonnet-5 | gemini-3.8-flash | grok-4.7 |
| --- | --- | --- | --- | --- |
| Tool calling | Documented | Documented | Documented | Documented |
| Multimodal input | Documented (family) | Documented | Documented | Documented (image input) |
| Long-context | See provider docs | See provider docs | See provider docs | See provider docs |
| Free/trial access | See OpenAI plan docs | See Anthropic plan docs | See Google AI Studio docs | See xAI console |

---

## D. Sponsor / budget practicality (qualitative)

| Constraint | Affects runtime model choice? | Affects build assistant? | Notes |
| --- | --- | --- | --- |
| Browserbase required for prize | Indirect (agent must call BB) | No | T1 sandbox ≠ eligibility |
| Agentverse + chat protocol | LLM can be Claude or other | No | Registration is separate |
| TiDB Serverless required | Data/retrieval layer | No | Online event |
| Composio Toolrouter depth | Tool wiring | Maybe via docs/examples | T3 sandbox ≠ Composio |
| Winner-only API credits | **After** win | Sometimes prize is Claude Code related | Not weekend funding |
| Historical DO $200 / Snowflake trial | Infra, not arbitrary LLM | No | Eligibility unverified now |

---

## How to populate table A

```bash
python scripts/run_comparison.py --provider openai --model gpt-6.1-sol --trials 3
python scripts/run_comparison.py --provider anthropic --model claude-sonnet-5 --trials 3
python scripts/run_comparison.py --provider gemini --model gemini-3.5-flash-lite --trials 3 --pace-seconds 20
python scripts/run_comparison.py --provider grok --model grok-4.7 --trials 3
python scripts/regrade_all.py
```

Then copy pass counts from each summary → table A.

Gemini free-tier note: without `--pace-seconds 20`, multi-turn tool loops exhaust the **15 requests/minute** free quota quickly.
