# HackEval — Research report for LinkedIn discussion

**Status:** Sources and tasks prepared; **live model measurements not yet run** (credentials required).  
**Accessed sources:** 2026-10-03  
**Purpose:** Evidence for choosing an LLM stack for hackathon builds — not an official benchmark or product ranking.

---

## 1. Question

For a concrete hackathon project, which **exact model versions** are practical under shared task conditions, and how do **free access**, **sponsor credits**, and **sponsor-tool requirements** change the choice?

Two different “models” get confused in writeups:

| Role | What it is | How we treat it |
| --- | --- | --- |
| **Build-time assistant** | Model helping participants write code (Cursor, Claude Code, Copilot, etc.) | Document from event prizes/tooling; **not** scored in T1–T6 |
| **Runtime model** | Model that powers the submitted agent/app via API | **What T1–T6 measure** when live runs are executed |

Winner API-credit prizes are **not** the same as participant build budgets.

---

## 2. Sources used (verified pages)

Full cards: [`sources/registry.yaml`](sources/registry.yaml), [`sources/sponsor_constraints.yaml`](sources/sponsor_constraints.yaml).

| Event | Organizer | Where | Dates | Why it informs a task |
| --- | --- | --- | --- | --- |
| [UC Berkeley AI Hackathon 2026](https://ai-hackathon-2026.devpost.com/) | Hackathons @ Berkeley | Berkeley, CA | 2026-06-20–21 | Browserbase web-agent requirement; Redis-beyond-caching memory emphasis |
| [Cal Hacks 12.0](https://cal-hacks-12-0.devpost.com/) | Cal Hacks | San Francisco, CA | 2025-10-24–26 | Composio Toolrouter; Conversion/Temporal workflows; Letta memory; historical DO $200 / Snowflake trial offers |
| [Fetch.ai @ Cal Hacks 12.0](https://www.fetch.ai/events/cal-hacks-12-0) | Fetch.ai | San Francisco, CA | 2025-10 weekend | Agentverse registration + chat protocol + LLM reasoning |
| [UK AI Agent Hackathon](https://www.fetch.ai/events/hackathons/uk-ai-agent-hackathon/hackpack) | Fetch.ai | **London, UK** | 2025-03-15 → demo 2025-04-13 | Outside Bay Area; Search/Discover multi-agent coordination |
| [TiDB AgentX 2025](https://tidb-2025-hackathon.devpost.com/) | PingCAP / TiDB | **Online** | 2025-08-01–09-15 | Multi-step agentic workflow ending in action |
| [Daytona HackSprint SF](https://daytona-hacksprint-sf-nov-25.devpost.com/rules) + [Shop the Video](https://devpost.com/software/shop-the-video) | Daytona / participants | San Francisco, CA | 2025-11-15 | Encouraged tools (official); video→product/price theme (**participant-reported**, unverified metrics) |

**Evidence labels:** official requirement ≠ participant blog claim ≠ our adaptation.

---

## 3. Six concrete tasks

Published under [`tasks/`](tasks/) with **inputs** and **explicit success criteria**.

| ID | Task | Adapted from | Runtime skills tested |
| --- | --- | --- | --- |
| **T1** | Web product research with evidence | Browserbase track | Retrieval, constraint satisfaction, citations |
| **T2** | Persistent preference memory | Redis / Letta tracks | Write/recall across sessions, isolation |
| **T3** | Ticket + calendar from a note | Composio Toolrouter | Multi-app fields, authorized writes |
| **T4** | Support workflow with approval | Conversion/Temporal + TiDB AgentX | Ordered tools, no premature side effects |
| **T5** | Discover agent + schedule | Fetch UK + Cal Hacks Fetch | Delegation, constraint preservation |
| **T6** | Visual catalog match + price | Daytona / Shop the Video theme | Multimodal match; cheapest *eligible* listing |

Each task is an **adaptation** with synthetic fixtures. Passing T1 does not prove Browserbase; passing T5 does not prove Agentverse registration.

---

## 4. Comparison protocol (when credentials are available)

**Candidates (exact IDs, docs checked 2026-10-03):**

- OpenAI `gpt-6.1-sol`
- Anthropic `claude-sonnet-5`
- Google `gemini-3.8-flash`

**Shared conditions:** same task prompts, same sandbox tools, temperature `0`, three independent trials per task, reset state each trial, provider-hosted extras off unless given to every candidate.

**Recorded per trial:** model id, settings, raw output, tool calls, pass/fail vs criteria, failure class, elapsed seconds, token usage, cost estimate when rates are known.

**Not claimed:** equal “reasoning budgets” across vendors (settings differ; we record as-configured).

**Script:** `python scripts/run_comparison.py --provider <openai|anthropic|gemini> --trials 3`

---

## 5. Measured results

**None yet.** Live API evaluations were not executed. Do not invent a leaderboard.

Placeholder table: [`COMPARISON_TABLE.md`](COMPARISON_TABLE.md).  
After runs, fill from `outputs/<run_id>/summary.json` and `trials.jsonl`.

Reference-only check (fixtures/graders, **not** a model score):

```bash
python scripts/run_comparison.py --reference-check
```

---

## 6. Documented capabilities (separate from measurement)

Use for stack design discussion; **do not** treat as HackEval scores.

| Topic | OpenAI `gpt-6.1-sol` | Anthropic `claude-sonnet-5` | Gemini `gemini-3.8-flash` |
| --- | --- | --- | --- |
| Text + tools (API) | Documented | Documented | Documented |
| Vision / image input | Documented family support | Documented | Documented |
| Provider-hosted tools (search, etc.) | Available on platform; **disabled** in our shared harness | Computer use / hosted tools exist; **disabled** here | Grounding/search exist; **disabled** here |
| Typical hackathon “build assistant” branding | Often via ChatGPT / Codex-class tools | Claude Code prize tracks at Berkeley/Cal Hacks | Gemini API prizes appear at some MLH-linked tracks |

Re-check provider docs before publishing any capability claim.

---

## 7. Free access, sponsor credits, and requirements

Practical choice ≠ pure accuracy.

| Factor | How it changes the choice | Pitfall |
| --- | --- | --- |
| **Recurring free tiers** | Prefer models you can actually call during the weekend | Free quota ≠ rate-limit headroom |
| **Participant promo credits** | e.g. historical DigitalOcean $200 signup, Snowflake student trial at Cal Hacks 12 | **Not** unrestricted LLM credits; eligibility may have expired |
| **Subscription access** | e.g. ASI:One / Agentverse offers if advertised | Subscription ≠ API budget |
| **Winner prizes** | Redis Cloud credits, Claude API credit prizes, Daytona credits | Awarded **after** winning — not build funding |
| **Sponsor requirements** | Browserbase / Agentverse / TiDB / Composio / Temporal-preferred | Technical task success ≠ track eligibility |
| **Out-of-pocket** | Runtime tokens + hosted browser/DB | Track channels separately; unknown price ≠ $0 |

**Rule of thumb for LinkedIn takeaways:**

1. Pick the **runtime** model that clears *your* task under a spend cap you can pay.  
2. Separately pick a **build-time** assistant you already have access to.  
3. Satisfy **sponsor constraints** only if you want that prize track.  
4. Never assume last year’s promo still funds this weekend.

---

## 8. Credentials required before live runs

| Provider | Environment variable | Optional install |
| --- | --- | --- |
| OpenAI | `OPENAI_API_KEY` | `pip install openai` |
| Anthropic | `ANTHROPIC_API_KEY` | `pip install anthropic` |
| Gemini | `GOOGLE_API_KEY` | `pip install google-genai` |

Copy `.env.example` → `.env`. Without keys, the runner **refuses** live mode rather than inventing scores.

---

## 9. Limitations

- Small pilot (6 tasks × 3 trials). Tiny gaps are not “overall superiority.”  
- Adaptations ≠ official contest tests.  
- Participant-reported metrics (e.g. Shop the Video) are unverified.  
- Sandbox tools ≠ proof of sponsor-stack integration.  
- Cost estimates incomplete when provider rates are unknown.  
- No live measurements in this packet yet.

---

## 10. Suggested LinkedIn framing

> We adapted six real hackathon challenge patterns (web agent, memory, multi-app tools, durable workflow, agent discovery, visual match) into explicit tasks with pass/fail criteria, then compared pinned model IDs under the same tools and prompts — separately from “which coding assistant you use to build.” Sponsor credits and required sponsor tools often dominate the practical stack choice more than a one-point accuracy gap.

Only post measured numbers **after** `outputs/` contains real `trials.jsonl` for each model.
