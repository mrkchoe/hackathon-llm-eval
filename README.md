# HackEval

A small, reproducible **LLM evaluation** for hackathon-style agent tasks: task success, tool use, latency, and cost under shared conditions.

> Independent pilot — not an official hackathon benchmark or endorsement.  
> Measured results are recorded only from live runs; empty cells mean “not run.”

## Results (measured)

| Model | Tier | Passes / 18 |
| --- | --- | ---: |
| `gemini-3.5-flash-lite` | Google AI Studio free tier | **13/18** |
| `gpt-6.1-sol` | — | not run |
| `claude-sonnet-5` | — | not run |
| `grok-4.7` | — | not run |

Per-task breakdown and notes: [`COMPARISON_TABLE.md`](COMPARISON_TABLE.md) · [`results/RESULTS.md`](results/RESULTS.md)

## What’s in the repo

| Path | Contents |
| --- | --- |
| [`RESEARCH_REPORT.md`](RESEARCH_REPORT.md) | Sources, protocol, budgets, limitations |
| [`COMPARISON_TABLE.md`](COMPARISON_TABLE.md) | Measured + documented-capability tables |
| [`tasks/`](tasks/) | Six task inputs + explicit success criteria |
| [`sources/`](sources/) | Event/source registry + sponsor constraints |
| [`fixtures/`](fixtures/) | Synthetic fixtures |
| [`scripts/run_comparison.py`](scripts/run_comparison.py) | Minimal multi-trial runner |
| [`results/`](results/) | Published measured summaries |
| `outputs/` | Local raw run logs (gitignored) |

## Setup

```bash
cd hackeval
python -m venv .venv
.\.venv\Scripts\activate          # Windows
pip install -r requirements.txt
copy .env.example .env            # then add keys locally — never commit .env
```

## Commands

```bash
# Validate fixtures + graders only (not a model comparison)
python scripts/run_comparison.py --reference-check

# Live comparison (requires matching API key in .env)
python scripts/run_comparison.py --provider gemini --model gemini-3.5-flash-lite --trials 3 --pace-seconds 20
python scripts/run_comparison.py --provider openai --model gpt-6.1-sol --trials 3
python scripts/run_comparison.py --provider anthropic --model claude-sonnet-5 --trials 3
python scripts/run_comparison.py --provider grok --model grok-4.7 --trials 3
```

Gemini free tier is ~**15 requests/minute**; use `--pace-seconds 20` for multi-turn tool loops.

## Credentials

| Provider | Variable |
| --- | --- |
| OpenAI | `OPENAI_API_KEY` |
| Anthropic | `ANTHROPIC_API_KEY` |
| Gemini | `GOOGLE_API_KEY` |
| Grok (xAI) | `XAI_API_KEY` |

## Scope

- **In:** six adapted hackathon tasks, sources, minimal runner, measured results  
- **Out:** apps, dashboards, product UI  
- **Separate:** build-time coding assistants vs runtime models that power a submission  
