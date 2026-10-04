# hackathon-llm-eval

Small reproducible evaluation of LLM agents on hackathon-derived tasks: success, tool use, latency, and cost under shared conditions.

Independent pilot — not an official hackathon benchmark or endorsement.  
Measured results come only from live runs; empty cells mean not run.

## Tasks

Each **task (T1–T8)** is one hackathon-style agent problem. A **trial** is one independent attempt (fresh state). We run **3 trials per task** → **24** attempts per model.

| ID | What the model must do |
| --- | --- |
| **T1** Web product research | Find an in-stock slate 750 ml bottle ≤ $23 on fixture retailer pages; return id, price, and evidence URL |
| **T2** Persistent memory | Save `user_a` cuisine preference, then recall it in a later session (no cross-user leak) |
| **T3** Ticket + calendar | Read a meeting note; create the matching project ticket and calendar entry |
| **T4** Durable workflow | Process support request REQ-1: look up → get approval → execute sandbox action (no action before approval) |
| **T5** Agent discovery | Discover a scheduling specialist; book Nov 10 2026 10:00–10:30 PT with Alice; return confirmed constraints |
| **T6** Visual catalog match | Match frame `frame_clear_bottle` to the catalog; return cheapest *eligible* listing |
| **T7** Policy remediation | Resolve INC-220 under `refund_v1` (hidden fraud risk; quote/apply/notify) |
| **T8** Amendment cancel | Follow `note_201` → amendment; cancel instead of creating stale ticket/calendar |

Full prompts and pass/fail checks: [`tasks/`](tasks/).

## Results

| Model | Conditions | Passes / 24 |
| --- | --- | ---: |
| `claude-sonnet-5` | Anthropic Messages API + tools | **24/24** |
| `gpt-6.1-sol` | Responses API, `reasoning.effort=low` | **24/24** |
| `grok-4.7` | xAI API (`api.x.ai`) | **19/24** |
| `gemini-3.5-flash-lite` | Google AI Studio free tier | **19/24** |

Hard tasks T7–T8 separate Grok/Gemini from the top. Claude and GPT both clean-sweep pass rate; Claude is slightly faster on T7+T8.

### Failures (non-perfect models)

**Gemini:** T1 t3, T4 t1, T7×3.  
**Grok:** T2 t3, T3 t2, T5 t3, T8 t1 & t3.  

More detail: [`results/RESULTS.md`](results/RESULTS.md) · [`COMPARISON_TABLE.md`](COMPARISON_TABLE.md)


## Contents

| Path | Contents |
| --- | --- |
| [`RESEARCH_REPORT.md`](RESEARCH_REPORT.md) | Sources, protocol, budgets, limitations |
| [`COMPARISON_TABLE.md`](COMPARISON_TABLE.md) | Measured and documented-capability tables |
| [`tasks/`](tasks/) | Eight task inputs and success criteria |
| [`sources/`](sources/) | Event sources and sponsor-constraint notes |
| [`fixtures/`](fixtures/) | Synthetic fixtures |
| [`scripts/run_comparison.py`](scripts/run_comparison.py) | Multi-trial runner |
| [`results/`](results/) | Published measured summaries |
| `outputs/` | Local raw traces (gitignored) |

## Setup

```bash
cd hackathon-llm-eval   # or whatever the local folder is named
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env   # add keys locally; never commit .env
```

## Run

```bash
python scripts/run_comparison.py --reference-check

python scripts/run_comparison.py --provider gemini --model gemini-3.5-flash-lite --trials 3 --pace-seconds 20
python scripts/run_comparison.py --provider openai --model gpt-6.1-sol --trials 3
python scripts/run_comparison.py --provider anthropic --model claude-sonnet-5 --trials 3
python scripts/run_comparison.py --provider grok --model grok-4.7 --trials 3
```

Gemini free tier is about 15 requests/minute; use `--pace-seconds 20` for multi-turn tool loops.

## Credentials

| Provider | Variable |
| --- | --- |
| OpenAI | `OPENAI_API_KEY` |
| Anthropic | `ANTHROPIC_API_KEY` |
| Gemini | `GOOGLE_API_KEY` |
| Grok (xAI) | `XAI_API_KEY` |

## Scope

- Six adapted tasks, sources, minimal runner, measured results  
- No app or dashboard  
- Build-time coding assistants are documented separately from runtime models under test  
