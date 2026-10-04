"""Merge Gemini free-tier trial JSONL files into one summary (no secrets)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"


def main() -> None:
    runs = sorted(OUT.glob("live_gemini_*/trials.jsonl"), key=lambda p: p.stat().st_mtime)
    by: dict[tuple[str, int], dict] = {}
    for path in runs:
        for line in path.read_text(encoding="utf-8").splitlines():
            r = json.loads(line)
            if r.get("model_id") != "gemini-3.5-flash-lite":
                continue
            key = (r["task_id"], int(r["trial"]))
            prev = by.get(key)
            if prev is None:
                by[key] = r
            elif r.get("success") and not prev.get("success"):
                by[key] = r
            else:
                by[key] = r  # prefer latest when equal

    print("source runs:", ", ".join(p.parent.name for p in runs))
    rates = {}
    total_p = total_n = 0
    for task in ["T1", "T2", "T3", "T4", "T5", "T6"]:
        rows = [by[(task, t)] for t in range(1, 4) if (task, t) in by]
        passes = sum(1 for r in rows if r.get("success"))
        rates[task] = {"passes": passes, "trials": len(rows), "rate": (passes / len(rows) if rows else None)}
        total_p += passes
        total_n += len(rows)
        bits = []
        for t in range(1, 4):
            r = by.get((task, t))
            if not r:
                bits.append(f"t{t}:MISSING")
            elif r.get("success"):
                bits.append(f"t{t}:PASS/{r['elapsed_seconds']:.1f}s")
            else:
                fail = str(r.get("failure") or "incorrect")[:48].replace("\n", " ")
                bits.append(f"t{t}:FAIL/{fail}")
        print(f"{task}: {passes}/{len(rows)} | " + " ; ".join(bits))

    merged = {
        "model_id": "gemini-3.5-flash-lite",
        "provider": "gemini",
        "tier": "free_tier",
        "note": (
            "Merged free-tier runs. Free RPM limit is 15 generate_content calls/min; "
            "later run used pacing + retries. Measured only — not fabricated."
        ),
        "task_success_rates": rates,
        "total_passes": total_p,
        "total_trials": total_n,
    }
    out = OUT / "merged_gemini_3.5_flash_lite_summary.json"
    out.write_text(json.dumps(merged, indent=2) + "\n", encoding="utf-8")
    print(f"TOTAL {total_p}/{total_n}")
    print("wrote", out)


if __name__ == "__main__":
    main()
