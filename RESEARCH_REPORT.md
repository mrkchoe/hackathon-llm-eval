# Evaluation report

**Status:** Claude **24/24**; GPT **24/24**; Grok **19/24**; Gemini **19/24** (T1–T8, incl. hard T7/T8).  
**Sources accessed:** 2026-10-03  
**Purpose:** Compare exact model versions on hackathon-derived agent tasks under shared conditions.

---

## 1. Question

For hackathon-style agent work, which **exact model versions** succeed on concrete tasks under shared tools/prompts, and how do **free access**, **sponsor credits**, and **sponsor-tool requirements** change the practical stack choice?

Two roles are kept separate:

| Role | What it is | How we treat it |
| --- | --- | --- |
| **Build-time assistant** | Model helping participants write code (Cursor, Claude Code, Copilot, etc.) | Documented from event tooling; **not** scored in T1–T6 |
| **Runtime model** | Model that powers the submitted agent/app via API | **What T1–T6 measure** |

Winner API-credit prizes are **not** the same as participant build budgets.

---

## 2. Sources used (verified pages)

Full cards: [`sources/registry.yaml`](sources/registry.yaml), [`sources/sponsor_constraints.yaml`](sources/sponsor_constraints.yaml).

| Event | Organizer | Where | Dates | Why it informs a task |
| --- | --- | --- | --- | --- |
| [UC Berkeley AI Hackathon 2026](https://ai-hackathon-2026.devpost.com/) | Hackathons @ Berkeley | Berkeley, CA | 2026-06-20–21 | Browserbase web-agent requirement; Redis-beyond-caching memory emphasis |
| [Cal Hacks 12.0](https://cal-hacks-12-0.devpost.com/) | Cal Hacks | San Francisco, CA | 2025-10-24–26 | Composio Toolrouter; Conversion/Temporal workflows; Letta memory; historical DO $200 / Snowflake trial offers |
| [Fetch.ai @ Cal Hacks 12.0](https://www.fetch.ai/events/cal-hacks-12-0) | Fetch.ai | San Francisco, CA | 2025-10 weekend | Agentverse registration + chat protocol + LLM reasoning |
| [UK AI Agent Hackathon](https://www.fetch.ai/events/hackathons/uk-ai-agent-hackathon/hackpack) | Fetch.ai | London, UK | 2025-03-15 → demo 2025-04-13 | Search/Discover multi-agent coordination |
| [TiDB AgentX 2025](https://tidb-2025-hackathon.devpost.com/) | PingCAP / TiDB | Online | 2025-08-01–09-15 | Multi-step agentic workflow ending in action |
| [Daytona HackSprint SF](https://daytona-hacksprint-sf-nov-25.devpost.com/rules) + [Shop the Video](https://devpost.com/software/shop-the-video) | Daytona / participants | San Francisco, CA | 2025-11-15 | Encouraged tools (official); video→product/price theme (**participant-reported**, unverified metrics) |

**Evidence labels:** official requirement ≠ participant-reported claim ≠ our adaptation.

---

## 3. Six concrete tasks

Published under [`tasks/`](tasks/) with inputs and explicit success criteria.

| ID | Task | Adapted from | Runtime skills tested |
| --- | --- | --- | --- |
| **T1** | Web product research with evidence | Browserbase track | Retrieval, constraints, citations |
| **T2** | Persistent preference memory | Redis / Letta tracks | Write/recall, isolation |
| **T3** | Ticket + calendar from a note | Composio Toolrouter | Multi-app fields, authorized writes |
| **T4** | Support workflow with approval | Conversion/Temporal + TiDB AgentX | Ordered tools, side-effect control |
| **T5** | Discover agent + schedule | Fetch UK + Cal Hacks Fetch | Delegation, constraint preservation |
| **T6** | Visual catalog match + price | Daytona / Shop the Video theme | Multimodal match; cheapest eligible listing |

Each task is an **adaptation** with synthetic fixtures. Passing a task does not prove live sponsor-product usage.

---

## 4. Comparison protocol

**Candidates (exact IDs):**

- OpenAI `gpt-6.1-sol` — **measured 24/24** (Responses API, `reasoning.effort=low`)  
- Anthropic `claude-sonnet-5` — **measured 24/24** (Messages API + tools)  
- Google `gemini-3.5-flash-lite` — **measured 19/24** (free tier; fails hard T7)  
- xAI Grok `grok-4.7` — **measured 19/24** (OpenAI-compatible API at `api.x.ai`)  

Graders accept Pacific tz aliases and common tool-arg shapes. Hard tasks: T7 policy+fraud, T8 amendment cancel.

**Shared conditions:** same task prompts, same sandbox tools, temperature `0`, three trials per task, reset state each trial, provider-hosted extras off.

**Recorded per trial:** model id, settings, raw output, tool calls, pass/fail, failure class, elapsed seconds, token usage, cost estimate when rates are known.

**Not claimed:** equal reasoning budgets across vendors.

```bash
python scripts/run_comparison.py --provider <openai|anthropic|gemini|grok> --trials 3
```

---

## 5. Measured results

Suite **T1–T8** (24 trials). See [`results/RESULTS.md`](results/RESULTS.md).

| Model | Total | T7 | T8 |
| --- | ---: | ---: | ---: |
| `claude-sonnet-5` | **24/24** | 3/3 | 3/3 |
| `gpt-6.1-sol` | **24/24** | 3/3 | 3/3 |
| `grok-4.7` | **19/24** | 3/3 | 1/3 |
| `gemini-3.5-flash-lite` | **19/24** | 0/3 | 3/3 |

Claude/GPT tie on pass rate; Claude lower hard-task latency. Gemini free-tier RPM still shapes that run ($0 out-of-pocket).

---

## 6. Documented capabilities (separate from measurement)

Do **not** treat the table below as measured evaluation scores.

| Topic | OpenAI `gpt-6.1-sol` | Anthropic `claude-sonnet-5` | Gemini `gemini-3.5-flash-lite` | Grok `grok-4.7` |
| --- | --- | --- | --- | --- |
| Text + tools (API) | Documented | Documented | Documented / measured | Documented (xAI API) |
| Vision / image input | Documented family support | Documented | Documented / T6 measured | Documented image input |
| Provider-hosted tools | Disabled in shared harness | Disabled here | Disabled here | Disabled here |

---

## 7. Free access, sponsor credits, and requirements

Practical stack choice ≠ pure accuracy.

| Factor | How it changes the choice | Pitfall |
| --- | --- | --- |
| **Recurring free tiers** | Prefer models you can call within RPM/day caps | Free quota ≠ headroom for multi-turn agents |
| **Participant promo credits** | e.g. historical DigitalOcean $200 / Snowflake trial at Cal Hacks 12 | Not unrestricted LLM credits; may be expired |
| **Subscription access** | e.g. ASI:One / Agentverse offers if advertised | Subscription ≠ API budget |
| **Winner prizes** | Redis / Claude / Daytona credits | Awarded after winning — not build funding |
| **Sponsor requirements** | Browserbase / Agentverse / TiDB / Composio / Temporal-preferred | Task success ≠ track eligibility |
| **Out-of-pocket** | Runtime tokens + hosted tools/infra | Unknown price ≠ $0 |

---

## 8. Credentials required before live runs

| Provider | Environment variable | Optional install |
| --- | --- | --- |
| OpenAI | `OPENAI_API_KEY` | `pip install openai` |
| Anthropic | `ANTHROPIC_API_KEY` | `pip install anthropic` |
| Gemini | `GOOGLE_API_KEY` | `pip install google-genai` |
| Grok (xAI) | `XAI_API_KEY` | `pip install openai` (base URL `https://api.x.ai/v1`) |

Copy `.env.example` → `.env`. Without keys, the runner refuses live mode rather than inventing scores. **Never commit `.env`.**

---

## 9. Limitations

- Small pilot (6 tasks × 3 trials). Small gaps are not overall superiority.  
- Adaptations ≠ official contest tests.  
- Participant-reported metrics are unverified.  
- Sandbox tools ≠ proof of sponsor-stack integration.  
- Cost estimates incomplete when provider rates are unknown.  
- Free-tier Gemini RPM shaped that run; other providers used paid API keys.  
- Lenient grading can credit complete tool bookings even when the final JSON was empty or used equivalent tz labels.
