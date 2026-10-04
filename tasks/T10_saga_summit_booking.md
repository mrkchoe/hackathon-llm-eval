# T10 — Saga summit booking (extreme)

**Adaptation of:** Cal Hacks 12.0 Conversion/Temporal durable-workflow emphasis + multi-step AgentX-style completion  
**Sources:** https://cal-hacks-12-0.devpost.com/ (accessed 2026-10-03)  
**Evidence kind:** Official theme → adversarial synthetic adaptation  

**Our adaptation:** Book a partner-summit package as a **saga** (room → catering → AV → finalize) under a strict policy. Sales suggestion, invite headcount, and a one-click tool are traps. Possibly too hard for current tool-calling LLMs.

---

## Task input

Book the partner summit package under policy **`summit_v1`**.

Return JSON:

```json
{
  "room_id": "...",
  "headcount": 0,
  "total_usd": 0,
  "conf_code": "...",
  "auth_token": "...",
  "status": "finalized"
}
```

Fixtures: `fixtures/policy/summit_policy.json`, `fixtures/events/summit.json`, `fixtures/events/roster.json`

## Allowed tools

- `read_policy(policy_id)`
- `get_meeting()`
- `list_rooms()`
- `read_roster()`
- `suggest_package()`
- `book_room(room_id)`
- `book_catering(headcount)`
- `book_av(conf_code)`
- `cancel_av()` / `cancel_catering()` / `cancel_room()`
- `quick_book_suggested()`
- `finalize_package(auth_token)`

## Success criteria

| Check | Pass |
| --- | --- |
| Policy | Read `summit_v1` |
| Headcount | Catering for **15** exact `confirmed` rows (not invite 20; not `Confirmed`/`CONFIRMED`) |
| Room | `R-BLUE` |
| Saga complete | Room + catering + AV all active |
| Budget | Total **2400** (<= 2400) |
| Auth | Correct `auth_token` from live `conf_code` |
| Finalize | `finalize_package` succeeded |
| Output | Fields match |

### Why this is extreme

- Roster is **paginated** (5/page); miss a page and the count is wrong.
- Status match is **exact** `confirmed` (decoy casings exist).
- Invite headcount and `suggest_package` push an over-budget package.
- `quick_book_suggested` poisons state.
- `conf_code` is issued at booking time (not knowable in advance); auth_token must use it.
- Wrong mid-saga choices require reverse cancels before retry.
