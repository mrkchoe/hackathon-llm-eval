"""Merge Gemini free-tier trial JSONL files into published results (no secrets)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
RESULTS = ROOT / "results"
MODEL = "gemini-3.5-flash-lite"


def _pick(prev: dict | None, r: dict) -> dict:
    if prev is None:
        return r
    if r.get("success") and not prev.get("success"):
        return r
    return r  # latest when equal


def main() -> None:
    runs = sorted(OUT.glob("live_gemini_*/trials.jsonl"), key=lambda p: p.stat().st_mtime)
    by: dict[tuple[str, int], dict] = {}
    for path in runs:
        for line in path.read_text(encoding="utf-8").splitlines():
            r = json.loads(line)
            if r.get("model_id") != MODEL:
                continue
            key = (r["task_id"], int(r["trial"]))
            by[key] = _pick(by.get(key), r)

    rates = {}
    failures = []
    total_p = total_n = 0
    for task in ["T1", "T2", "T3", "T4", "T5", "T6"]:
        rows = [by[(task, t)] for t in range(1, 4) if (task, t) in by]
        passes = sum(1 for r in rows if r.get("success"))
        rates[task] = {
            "passes": passes,
            "trials": len(rows),
            "rate": (passes / len(rows) if rows else None),
        }
        total_p += passes
        total_n += len(rows)
        for t in range(1, 4):
            r = by.get((task, t))
            if not r:
                failures.append(
                    {
                        "task_id": task,
                        "trial": t,
                        "class": "missing_trial",
                        "detail": "No recorded trial for this slot",
                        "failed_checks": [],
                    }
                )
                continue
            if r.get("success"):
                continue
            checks = (r.get("grade") or {}).get("checks") or []
            failed_checks = [c.get("name") for c in checks if c.get("pass") is False]
            harness_fail = r.get("failure")
            if harness_fail and "429" in str(harness_fail):
                cls = "rate_limit"
            elif harness_fail == "max_turns":
                cls = "max_turns"
            elif harness_fail:
                cls = "provider_or_harness_error"
            else:
                cls = "incorrect_output"
            failures.append(
                {
                    "task_id": task,
                    "trial": t,
                    "class": cls,
                    "detail": harness_fail,
                    "failed_checks": failed_checks,
                    "elapsed_seconds": r.get("elapsed_seconds"),
                }
            )

    merged = {
        "model_id": MODEL,
        "provider": "gemini",
        "tier": "free_tier",
        "note": (
            "Merged free-tier runs. Free RPM limit is 15 generate_content calls/min; "
            "later run used pacing + retries. Measured only."
        ),
        "task_success_rates": rates,
        "total_passes": total_p,
        "total_trials": total_n,
        "failures": failures,
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    out = RESULTS / "gemini_3.5_flash_lite_summary.json"
    out.write_text(json.dumps(merged, indent=2) + "\n", encoding="utf-8")
    (OUT / "merged_gemini_3.5_flash_lite_summary.json").write_text(
        json.dumps(merged, indent=2) + "\n", encoding="utf-8"
    )
    print(f"TOTAL {total_p}/{total_n}")
    print(f"FAILURES {len(failures)}")
    for f in failures:
        print(
            f"  {f['task_id']} trial {f['trial']}: {f['class']}"
            + (f" / checks={f['failed_checks']}" if f["failed_checks"] else "")
        )
    print("wrote", out)


if __name__ == "__main__":
    main()
