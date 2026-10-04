# HackEval

Research packet: **concrete LLM comparisons for hackathon use cases** — for a LinkedIn discussion, not a product.

> Independent pilot. Not an official hackathon benchmark or endorsement.  
> **No fabricated live results.** Measured tables stay empty until API runs are executed.

## Deliverables

| File | Contents |
| --- | --- |
| [`RESEARCH_REPORT.md`](RESEARCH_REPORT.md) | Sources, 6 tasks, protocol, budgets, credentials, limitations |
| [`COMPARISON_TABLE.md`](COMPARISON_TABLE.md) | Runtime vs build-time tables; measured cells awaiting live runs |
| [`tasks/`](tasks/) | Task inputs + explicit success criteria |
| [`sources/`](sources/) | Source registry + sponsor constraint notes |
| [`fixtures/`](fixtures/) | Synthetic fixtures |
| [`scripts/run_comparison.py`](scripts/run_comparison.py) | Minimal 3-trial comparison runner |
| [`outputs/`](outputs/) | Live run artifacts only (gitignored except README) |

## Setup

```bash
cd hackeval
python -m venv .venv
.\.venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

## Commands

```bash
# Validate fixtures + graders only (NOT a model comparison)
python scripts/run_comparison.py --reference-check

# Live comparison — requires the matching API key in .env
python scripts/run_comparison.py --provider openai --model gpt-6.1-sol --trials 3
python scripts/run_comparison.py --provider anthropic --model claude-sonnet-5 --trials 3
python scripts/run_comparison.py --provider gemini --model gemini-3.8-flash --trials 3
```

## Credentials (before live runs)

| Provider | Variable |
| --- | --- |
| OpenAI | `OPENAI_API_KEY` |
| Anthropic | `ANTHROPIC_API_KEY` |
| Gemini | `GOOGLE_API_KEY` |

See `.env.example`. Without keys, live mode exits rather than inventing scores.

## Scope boundaries

- **In:** six adapted tasks, sources, minimal runner, report + tables  
- **Out:** apps, dashboards, viewers, sponsor SDKs, leaderboard product UI  
- **Separate:** models that *help you build* vs models that *power the submission*
