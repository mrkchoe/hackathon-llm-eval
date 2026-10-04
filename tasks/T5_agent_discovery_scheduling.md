# T5 — Agent discovery and scheduling delegation

**Adaptation of:** Fetch.ai UK AI Agent Hackathon (London) Search/Discover criteria + Fetch.ai @ Cal Hacks 12.0 Agentverse/chat protocol  
**Sources:** https://www.fetch.ai/events/hackathons/uk-ai-agent-hackathon/hackpack ; https://www.fetch.ai/events/cal-hacks-12-0 (accessed 2026-10-03)  
**Evidence kind:** Official requirement → evaluation adaptation  

**Official (paraphrase):** UK judging includes Agentverse registration and whether an assistant uses Search/Discover to coordinate agents. Cal Hacks Fetch track requires Agentverse registration, chat protocol, and an LLM reasoning engine.  

**Our adaptation:** Discover a scheduling specialist, delegate a constrained meeting, return confirmation. Does **not** prove Agentverse registration.

**Role of the model:** Runtime coordinator / reasoning engine.

---

## Task input

Discover a scheduling specialist. Delegate a meeting:

- date `2026-11-10`
- `10:00`–`10:30` PT
- with `Alice`

Return the specialist id, confirmation status, and preserved constraints.

Fixture: `fixtures/agents/directory.json`

## Allowed tools

- `discover_agent(skill)`
- `message_agent(agent_id, message)`
- `check_status(agent_id)`

## Explicit success criteria

| Check | Pass condition |
| --- | --- |
| Specialist | `agent_scheduler` |
| Confirmed | Booking accepted by the specialist tool (model may report `confirmed`, or a complete booking payload may confirm it) |
| Constraints | date/start/end/tz/with preserved; Pacific tz may be `PT` or `America/Los_Angeles` |
| No false confirmation | Does not claim confirmed when no complete booking was delegated |

**Pass:** all checks true.
