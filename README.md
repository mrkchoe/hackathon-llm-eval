# hackathon-llm-eval

We give the same **9 agent tasks** to four LLMs (Claude, GPT, Gemini, Grok), run each task **3 times**, and count how often they succeed.

No app. No dashboard. Just tasks, fake tools/data, and a score.

---

## How it works (plain English)

1. The model gets a short problem (e.g. “book this meeting” or “pay this invoice”).
2. It can call **tools** (search, write memory, approve a payout, etc.). Those tools hit **local fake data**, not real browsers or banks.
3. When it’s done, it returns JSON. A **grader** checks whether it did the right thing.
4. We do that **3 times per task** so one lucky/unlucky run doesn’t decide everything.

**Pass** = grader checks all green.  
**Fail** = wrong answer, skipped a required step, or gave up (`max_turns`).

---

## The 9 tasks

| # | Plain English |
| --- | --- |
| **T1** | Find the right water bottle in a fake shop (in stock, right size/color, cheap enough) and prove which page it was on. |
| **T2** | Save a user’s food preference, then recall it later — without mixing up another user’s data. |
| **T3** | Read a meeting note and create the matching ticket + calendar event. |
| **T4** | Handle a support request in order: look it up → get approval → do the action (never act before approval). |
| **T5** | Find a scheduling agent and book a specific meeting with Alice; only count it confirmed if the booking tool actually accepted it. |
| **T6** | Match a product image/frame to the catalog and pick the cheapest *allowed* listing. |
| **T7** | Handle a refund/credit case using the written policy (customer wording can be a trap; fraud risk matters). |
| **T8** | Start from a meeting note that was later **cancelled** — don’t create ticket/calendar for the old plan. |
| **T9** | Pay a vendor invoice the hard way: use the amended amount, clear sanctions with the right code, apply tax withhold, get two eligible approvers. |

More detail (prompts + pass rules): [`tasks/`](tasks/).

---

## Results

Each model: **9 tasks × 3 trials = 27 attempts**.

| Model | Setup | Score |
| --- | --- | ---: |
| Claude Sonnet 5 | Anthropic API | **27/27** |
| GPT 6.1 Sol | OpenAI Responses API, medium reasoning | **27/27** |
| Gemini 3.5 Flash Lite | Free tier | **22/27** |
| Grok 4.7 | xAI API | **20/27** |

Who missed what: [`results/RESULTS.md`](results/RESULTS.md).

---

## Setup

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Put API keys in `.env` (never commit that file):

| Provider | Variable |
| --- | --- |
| OpenAI | `OPENAI_API_KEY` |
| Anthropic | `ANTHROPIC_API_KEY` |
| Gemini | `GOOGLE_API_KEY` |
| Grok | `XAI_API_KEY` |

## Run

```bash
python scripts/run_comparison.py --reference-check

python scripts/run_comparison.py --provider openai --model gpt-6.1-sol --trials 3
python scripts/run_comparison.py --provider anthropic --model claude-sonnet-5 --trials 3
python scripts/run_comparison.py --provider gemini --model gemini-3.5-flash-lite --trials 3 --pace-seconds 20
python scripts/run_comparison.py --provider grok --model grok-4.7 --trials 3
```

Gemini free tier is ~15 requests/minute — use `--pace-seconds 20`.

After runs: `python scripts/merge_all_summaries.py`

---

## Repo layout

| Path | What it is |
| --- | --- |
| `tasks/` | Task writeups |
| `fixtures/` | Fake shop / notes / invoices / policies |
| `scripts/` | Runner + graders |
| `results/` | Published scores |
| `sources/` | Where the hackathon ideas came from |
| `RESEARCH_REPORT.md` | Longer writeup (sources, limits) |
| `outputs/` | Raw local traces (gitignored) |

## Scope

- **In:** 9 tasks, shared tools/fixtures, live API scores, source notes  
- **Out:** product UI, claiming official hackathon endorsement, inventing scores without keys  
