# Comparison tables

**Measured so far:** Gemini free-tier only (`gemini-3.5-flash-lite`). Other models still `—`.  
Source: `outputs/merged_gemini_3.5_flash_lite_summary.json` (merged paced free-tier runs).

`gemini-3.8-flash` was attempted but returned 503 high-demand on free tier; evaluation used `gemini-3.5-flash-lite`.

---

## A. Runtime models — measured task success (3 trials each)

Shared conditions: temperature 0; same prompts/tools/fixtures; provider-hosted extras off.

| Task | `gpt-6.1-sol` | `claude-sonnet-5` | `gemini-3.5-flash-lite` | `grok-4.7` |
| --- | ---: | ---: | ---: | ---: |
| T1 Web product research | — | — | **2/3** | — |
| T2 Persistent memory | — | — | **3/3** | — |
| T3 Ticket + calendar | — | — | **3/3** | — |
| T4 Durable workflow | — | — | **2/3** | — |
| T5 Agent discovery | — | — | **0/3** | — |
| T6 Visual catalog match | — | — | **3/3** | — |
| **Total passes / 18** | — | — | **13/18** | — |

### Latency (mean seconds; successful trials where available)

| Task | `gpt-6.1-sol` | `claude-sonnet-5` | `gemini-3.5-flash-lite` | `grok-4.7` |
| --- | ---: | ---: | ---: | ---: |
| T1 | — | — | ~31s (2 passes) | — |
| T2 | — | — | ~32s | — |
| T3 | — | — | ~49s | — |
| T4 | — | — | ~49s (2 passes) | — |
| T5 | — | — | n/a (0 passes) | — |
| T6 | — | — | ~6.4s | — |

### Cost (gross USD estimate; null if rates unknown)

| Model | Pricing status | Sum of trial estimates |
| --- | --- | ---: |
| `gpt-6.1-sol` | unknown at pin time — leave null until verified | — |
| `claude-sonnet-5` | documented estimate ($2 / $10 per MTok in/out, docs 2026-10-03) | — |
| `gemini-3.5-flash-lite` | free-tier run; dollar rate not invoiced here | **$0 out-of-pocket** (free tier; RPM-limited) |
| `grok-4.7` | documented estimate ($2 / $6 per MTok in/out, xAI docs 2026-10-03) | — |

### Failure classes observed (counts)

| Failure class | gpt-6.1-sol | claude-sonnet-5 | gemini-3.5-flash-lite | grok-4.7 |
| --- | ---: | ---: | ---: | ---: |
| incorrect_output | — | — | 1 (T5 t3) | — |
| provider_error | — | — | 0 (after pacing) | — |
| rate_limit | — | — | early unpaced only; not in final 18 | — |
| timeout / max_turns | — | — | 4 (T1 t3, T4 t1, T5 t1–t2) | — |
| unsupported_capability | — | — | 0 | — |

### Failed trials (`gemini-3.5-flash-lite`)

| Task | Trial | Class | Missed checks |
| --- | ---: | --- | --- |
| T1 | 3 | max_turns | product_id, price_usd, page_url, in_stock |
| T4 | 1 | max_turns | approval_before_execute, action, duplicates |
| T5 | 1 | max_turns | specialist, confirmed, constraints |
| T5 | 2 | max_turns | specialist, confirmed, constraints |
| T5 | 3 | incorrect_output | confirmed, constraints |

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
| Long-context | See provider docs | See provider docs | See provider docs | See xAI docs |
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
```

Then copy pass counts from each `outputs/*/summary.json` → table A.

Gemini free-tier note: without `--pace-seconds 20`, multi-turn tool loops exhaust the **15 requests/minute** free quota quickly.
