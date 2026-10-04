# hackathon-llm-eval

Small reproducible evaluation of LLM agents on hackathon-derived tasks: success, tool use, latency, and cost under shared conditions.

Independent pilot — not an official hackathon benchmark or endorsement.  
Measured results come only from live runs; empty cells mean not run.

## Results

| Model | Conditions | Passes / 18 |
| --- | --- | ---: |
| `gemini-3.5-flash-lite` | Google AI Studio free tier | **13/18** |
| `gpt-6.1-sol` | — | not run |
| `claude-sonnet-5` | — | not run |
| `grok-4.7` | — | not run |

Details: [`results/RESULTS.md`](results/RESULTS.md) · [`COMPARISON_TABLE.md`](COMPARISON_TABLE.md)

## Contents

| Path | Contents |
| --- | --- |
| [`RESEARCH_REPORT.md`](RESEARCH_REPORT.md) | Sources, protocol, budgets, limitations |
| [`COMPARISON_TABLE.md`](COMPARISON_TABLE.md) | Measured and documented-capability tables |
| [`tasks/`](tasks/) | Six task inputs and success criteria |
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
