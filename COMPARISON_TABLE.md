# Comparison tables

**Measured:** Claude **24/24**, GPT **24/24**, Grok **19/24**, Gemini **19/24** (T1–T8).

Hard tasks: **T7** (policy + hidden fraud risk) and **T8** (amendment cancellation).

---

## A. Runtime models — measured task success (3 trials each)

| Task | `gpt-6.1-sol` | `claude-sonnet-5` | `gemini-3.5-flash-lite` | `grok-4.7` |
| --- | ---: | ---: | ---: | ---: |
| T1 Web product research | **3/3** | **3/3** | **2/3** | **3/3** |
| T2 Persistent memory | **3/3** | **3/3** | **3/3** | **2/3** |
| T3 Ticket + calendar | **3/3** | **3/3** | **3/3** | **2/3** |
| T4 Durable workflow | **3/3** | **3/3** | **2/3** | **3/3** |
| T5 Agent discovery | **3/3** | **3/3** | **3/3** | **2/3** |
| T6 Visual catalog match | **3/3** | **3/3** | **3/3** | **3/3** |
| T7 Policy remediation | **3/3** | **3/3** | **0/3** | **3/3** |
| T8 Amendment cancel | **3/3** | **3/3** | **3/3** | **1/3** |
| **Total passes / 24** | **24/24** | **24/24** | **19/24** | **19/24** |

GPT settings: Responses API, `reasoning.effort=medium`.  
Pass-rate tie at the top: Claude mean latency on T7+T8 ≈ **9.8s** vs GPT medium ≈ **11.0s**.

### Hard-task latency (mean seconds, passes)

| Task | GPT (medium) | Claude | Gemini | Grok |
| --- | ---: | ---: | ---: | ---: |
| T7 | ~16.3 | ~12.9 | n/a | ~11.5 |
| T8 | ~5.6 | ~6.7 | ~32.3 | ~10.3 (1 pass) |

---

## Failed trials

### Gemini

| Task | Trials | Class |
| --- | --- | --- |
| T1 | 3 | max_turns |
| T4 | 1 | max_turns |
| T7 | 1–3 | max_turns / incomplete |

### Grok

| Task | Trials | Class |
| --- | --- | --- |
| T2 | 3 | incorrect_output |
| T3 | 2 | incorrect_output |
| T5 | 3 | incorrect_output |
| T8 | 1, 3 | max_turns |

Full writeup: [`results/RESULTS.md`](results/RESULTS.md)

```bash
python scripts/run_comparison.py --provider <openai|anthropic|gemini|grok> --trials 3
python scripts/run_comparison.py --provider <...> --tasks T7 T8 --trials 3
python scripts/merge_all_summaries.py
```
