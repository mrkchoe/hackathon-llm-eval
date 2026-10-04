# T2 — Persistent preference memory

**Adaptation of:** Berkeley AI Hackathon 2026 Redis “beyond caching” + Cal Hacks 12.0 Letta memory track  
**Sources:** https://ai-hackathon-2026.devpost.com/ ; https://cal-hacks-12-0.devpost.com/ (accessed 2026-10-03)  
**Evidence kind:** Official requirement → evaluation adaptation  

**Official (paraphrase):** Redis prize emphasizes agent memory / vector search / context retrieval; Letta track requires meaningful persistent memory across sessions.  

**Our adaptation:** Sandbox `write_memory` / `read_memory` across two sessions for `user_a`. Does **not** prove Redis or Letta integration.

**Role of the model:** Runtime agent model maintaining user state.

---

## Task input

**Session 1:** For `user_a`, save preference `cuisine = vegetarian`.  
**Session 2:** Recall `user_a` cuisine and return it as the current preference. Do not use `user_b` data.

Fixture seed: `fixtures/memory/seed.json`

## Allowed tools

- `write_memory(user, key, value)`
- `read_memory(user, key?)`

## Explicit success criteria

| Check | Pass condition |
| --- | --- |
| Write | A `write_memory` call stores `user_a.cuisine = vegetarian` |
| Recall | Final output `cuisine` / `final_cuisine` is `vegetarian` |
| Isolation | Final answer does not present `user_b` preferences as `user_a`’s |

**Pass:** all checks true.
