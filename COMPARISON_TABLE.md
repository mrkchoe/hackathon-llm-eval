# Comparison tables

**Measured performance:** not run yet — cells say `—`.  
**Do not** fill these with reference-check or guessed numbers.

After live runs, replace `—` using `outputs/<run_id>/summary.json` (passes / 3 trials).

---

## A. Runtime models — measured task success (3 trials each)

Shared conditions: temperature 0; same prompts/tools/fixtures; provider-hosted extras off.

| Task | `gpt-6.1-sol` | `claude-sonnet-5` | `gemini-3.8-flash` |
| --- | ---: | ---: | ---: |
| T1 Web product research | — | — | — |
| T2 Persistent memory | — | — | — |
| T3 Ticket + calendar | — | — | — |
| T4 Durable workflow | — | — | — |
| T5 Agent discovery | — | — | — |
| T6 Visual catalog match | — | — | — |
| **Total passes / 18** | — | — | — |

### Latency (mean seconds over attempts that were not coverage-exclusions)

| Task | `gpt-6.1-sol` | `claude-sonnet-5` | `gemini-3.8-flash` |
| --- | ---: | ---: | ---: |
| T1–T6 (per-task rows to fill from JSONL) | — | — | — |

### Cost (gross USD estimate; null if rates unknown)

| Model | Pricing status | Sum of trial estimates |
| --- | --- | ---: |
| `gpt-6.1-sol` | unknown at pin time — leave null until verified | — |
| `claude-sonnet-5` | documented estimate ($2 / $10 per MTok in/out, docs 2026-10-03) | — |
| `gemini-3.8-flash` | unknown at pin time — leave null until verified | — |

### Failure classes observed (counts)

| Failure class | gpt-6.1-sol | claude-sonnet-5 | gemini-3.8-flash |
| --- | ---: | ---: | ---: |
| incorrect_output | — | — | — |
| provider_error | — | — | — |
| rate_limit | — | — | — |
| timeout / max_turns | — | — | — |
| unsupported_capability | — | — | — |

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

## C. Documented capabilities (not HackEval scores)

| Capability | gpt-6.1-sol | claude-sonnet-5 | gemini-3.8-flash |
| --- | --- | --- | --- |
| Tool calling | Documented | Documented | Documented |
| Multimodal input | Documented (family) | Documented | Documented |
| Long-context | See provider docs | See provider docs | See provider docs |
| Free/trial access | See OpenAI plan docs | See Anthropic plan docs | See Google AI Studio docs |

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
# For each provider after setting the matching API key:
python scripts/run_comparison.py --provider openai --model gpt-6.1-sol --trials 3
python scripts/run_comparison.py --provider anthropic --model claude-sonnet-5 --trials 3
python scripts/run_comparison.py --provider gemini --model gemini-3.8-flash --trials 3
```

Then copy pass counts from each `outputs/*/summary.json` → table A.
