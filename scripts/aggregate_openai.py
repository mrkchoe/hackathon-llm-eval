"""Aggregate latest full OpenAI run into results/ (no secrets)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
RESULTS = ROOT / "results"
MODEL = "gpt-6.1-sol"


def main() -> None:
    runs = sorted(OUT.glob("live_openai_*/trials.jsonl"), key=lambda p: p.stat().st_mtime)
    best = None
    for path in runs:
        n = len(path.read_text(encoding="utf-8").strip().splitlines())
        if n >= 18:
            best = path
    if best is None:
        best = runs[-1]
    rows = [json.loads(line) for line in best.read_text(encoding="utf-8").splitlines()]
    rows = [r for r in rows if r.get("model_id") == MODEL]

    rates = {}
    fails = []
    tok_in = tok_out = 0
    for task in ["T1", "T2", "T3", "T4", "T5", "T6"]:
        tr = [r for r in rows if r["task_id"] == task]
        passes = sum(1 for r in tr if r.get("success"))
        rates[task] = {
            "passes": passes,
            "trials": len(tr),
            "rate": (passes / len(tr) if tr else None),
        }
        for r in tr:
            tok_in += (r.get("cost") or {}).get("input_tokens") or 0
            tok_out += (r.get("cost") or {}).get("output_tokens") or 0
            if r.get("success"):
                continue
            checks = (r.get("grade") or {}).get("checks") or []
            failed = [c.get("name") for c in checks if c.get("pass") is False]
            hf = r.get("failure")
            if hf == "max_turns":
                cls = "max_turns"
            elif hf and "429" in str(hf):
                cls = "rate_limit"
            elif hf:
                cls = "provider_or_harness_error"
            else:
                cls = "incorrect_output"
            fails.append(
                {
                    "task_id": task,
                    "trial": r["trial"],
                    "class": cls,
                    "detail": hf,
                    "failed_checks": failed,
                    "elapsed_seconds": r.get("elapsed_seconds"),
                    "output": r.get("output"),
                }
            )
        print(f"{task}: {passes}/{len(tr)}")

    total_p = sum(v["passes"] for v in rates.values())
    total_n = sum(v["trials"] for v in rates.values())
    merged = {
        "model_id": MODEL,
        "provider": "openai",
        "status": "measured",
        "settings": {"api": "responses", "reasoning_effort": "medium"},
        "run_id": rows[0]["run_id"] if rows else None,
        "note": (
            "Measured with OpenAI Responses API, reasoning.effort=medium. "
            "Chat Completions cannot tool-call gpt-6.1-sol."
        ),
        "task_success_rates": rates,
        "total_passes": total_p,
        "total_trials": total_n,
        "failures": fails,
        "token_usage": {"input_tokens": tok_in, "output_tokens": tok_out},
        "gross_usd_estimate": None,
        "pricing_status": "unknown_do_not_invent",
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    out = RESULTS / "openai_gpt-6.1-sol_summary.json"
    out.write_text(json.dumps(merged, indent=2) + "\n", encoding="utf-8")
    print(f"TOTAL {total_p}/{total_n}")
    print(f"FAILURES {len(fails)}")
    for f in fails:
        print(f"  {f['task_id']} t{f['trial']}: {f['class']} checks={f['failed_checks']}")
    print("wrote", out)


if __name__ == "__main__":
    main()
