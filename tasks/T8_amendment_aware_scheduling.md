# T8 — Amendment-aware scheduling (hard)

**Adaptation of:** Cal Hacks Composio-style cross-app writes with revision control  
**Evidence kind:** Official theme → harder synthetic adaptation  

**Our adaptation:** An original meeting note is superseded by a **cancellation**. Agents must **not** create ticket/calendar from the stale note. Does **not** prove Composio usage.

---

## Task input

Actor: `agent_ops`

1. Read `note_201` and follow any supersession pointer.
2. Apply the **effective** amendment (create or cancel as required).
3. Return JSON `{status, note_id_used}`.

Fixtures: `fixtures/notes/amendments.json`

## Allowed tools

- `read_amendment_note(note_id)`
- `find_ticket(title)`
- `create_ticket(title, due, owner, actor, note_id?)`
- `create_calendar_entry(date, start, end, tz, title, actor, note_id?)`

## Success criteria

| Check | Pass |
| --- | --- |
| Read amendment | Read `note_202` |
| No ticket | Created **zero** tickets |
| No calendar | Created **zero** calendar entries |
| Output | `status` indicates cancellation/cancelled; `note_id_used == note_202` |

### Why hard

`note_201` looks like a normal create-ticket/calendar task. The amendment cancels everything. Models that execute the first note fail.
