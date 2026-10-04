# T3 — Cross-app ticket + calendar

**Adaptation of:** Cal Hacks 12.0 — Best Use of Composio Toolrouter  
**Source:** https://cal-hacks-12-0.devpost.com/ (accessed 2026-10-03)  
**Evidence kind:** Official requirement → evaluation adaptation  

**Official (paraphrase):** Judged on extensive use of Composio Toolrouter to connect/orchestrate multiple applications.  

**Our adaptation:** Read a meeting note, create a ticket, create a calendar entry via sandbox tools. Does **not** prove Composio Toolrouter depth.

**Role of the model:** Runtime orchestration model calling app tools.

---

## Task input

Actor: `agent_ops`  
Read note `note_101`. If no matching ticket exists, create one, then create the calendar follow-up from the note.

Fixture: `fixtures/notes/meetings.json`

## Allowed tools

- `read_note(note_id)`
- `find_ticket(title)`
- `create_ticket(title, due, owner, actor, note_id?)`
- `create_calendar_entry(date, start, end, tz, title, actor, note_id?)`

## Explicit success criteria

| Check | Pass condition |
| --- | --- |
| Ticket title | `"API rate-limit dashboard"` |
| Ticket due | `2026-11-05` |
| Ticket owner | `Sam` |
| Calendar | date `2026-11-03`, start `15:00`, end `15:30`, tz `PT` |
| Duplicates | At most one ticket with that title |

**Pass:** all checks true.
