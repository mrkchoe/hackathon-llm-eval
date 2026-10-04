"""Merge T1–T6 base runs with latest T7/T8 task runs into published summaries."""
from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from grade import grade  # noqa: E402
from sandbox_tools import Sandbox  # noqa: E402

OUT = ROOT / "outputs"
RESULTS = ROOT / "results"


def replay(row: dict) -> dict:
    sb = Sandbox()
    for tc in row.get("tool_calls") or []:
        if tc.get("name"):
            sb.call(tc["name"], tc.get("arguments") or {})
    g = grade(row["task_id"], row.get("output") or {}, sb)
    row = dict(row)
    row["grade"] = g
    row["success"] = bool(g.get("success"))
    if row["success"]:
        row["failure"] = None
    return row


def latest_rows(glob: str, model_id: str, min_n: int | None = None) -> list[dict]:
    best = None
    for path in sorted(OUT.glob(glob), key=lambda p: p.stat().st_mtime):
        rows = [
            json.loads(l)
            for l in path.read_text(encoding="utf-8").splitlines()
            if json.loads(l).get("model_id") == model_id
        ]
        if min_n is None or len(rows) >= min_n:
            best = rows
    return best or []


def latest_task(glob: str, model_id: str, task_id: str) -> list[dict]:
    best = None
    for path in sorted(OUT.glob(glob), key=lambda p: p.stat().st_mtime):
        rows = [
            replay(json.loads(l))
            for l in path.read_text(encoding="utf-8").splitlines()
            if (lambda r: r.get("model_id") == model_id and r.get("task_id") == task_id)(
                json.loads(l)
            )
        ]
        # re-parse cleanly
    best = None
    for path in sorted(OUT.glob(glob), key=lambda p: p.stat().st_mtime):
        raw = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines()]
        rows = [replay(r) for r in raw if r.get("model_id") == model_id and r.get("task_id") == task_id]
        if len(rows) >= 3:
            best = rows
    return best or []


def merge_gemini_base(model_id: str = "gemini-3.5-flash-lite") -> list[dict]:
    by: dict[tuple[str, int], dict] = {}
    for path in sorted(OUT.glob("live_gemini_*/trials.jsonl"), key=lambda p: p.stat().st_mtime):
        for line in path.read_text(encoding="utf-8").splitlines():
            r = json.loads(line)
            if r.get("model_id") != model_id:
                continue
            if r.get("task_id") in {"T7", "T8", "T9"}:
                continue
            key = (r["task_id"], int(r["trial"]))
            by[key] = r
    return [replay(by[k]) for k in sorted(by)]


def summarize(rows: list[dict], model_id: str, provider: str, extra: dict | None = None) -> dict:
    rates = {}
    fails = []
    tin = tout = 0
    for task in ["T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8", "T9"]:
        tr = [r for r in rows if r["task_id"] == task]
        passes = sum(1 for r in tr if r.get("success"))
        xs = [r["elapsed_seconds"] for r in tr if r.get("success") and r.get("elapsed_seconds") is not None]
        rates[task] = {
            "passes": passes,
            "trials": len(tr),
            "rate": (passes / len(tr) if tr else None),
            "mean_latency_s": (round(statistics.mean(xs), 2) if xs else None),
        }
        for r in tr:
            c = r.get("cost") or {}
            tin += c.get("input_tokens") or 0
            tout += c.get("output_tokens") or 0
            if r.get("success"):
                continue
            checks = (r.get("grade") or {}).get("checks") or []
            failed = [c.get("name") for c in checks if c.get("pass") is False]
            cls = "max_turns" if r.get("failure") == "max_turns" else "incorrect_output"
            if r.get("failure") and r.get("failure") != "max_turns":
                cls = "provider_or_harness_error"
            fails.append(
                {
                    "task_id": task,
                    "trial": r["trial"],
                    "class": cls,
                    "detail": r.get("failure"),
                    "failed_checks": failed,
                    "output": r.get("output"),
                }
            )
    total_p = sum(v["passes"] for v in rates.values())
    total_n = sum(v["trials"] for v in rates.values())
    out = {
        "model_id": model_id,
        "provider": provider,
        "status": "measured",
        "tasks": "T1-T8",
        "task_success_rates": rates,
        "total_passes": total_p,
        "total_trials": total_n,
        "failures": fails,
        "token_usage": {"input_tokens": tin, "output_tokens": tout},
    }
    if extra:
        out.update(extra)
    return out


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)

    configs = [
        (
            "openai",
            "gpt-6.1-sol",
            "live_openai_*/trials.jsonl",
            {
                "settings": {"api": "responses", "reasoning_effort": "medium"},
                "pricing_status": "unknown_do_not_invent",
                "gross_usd_estimate": None,
            },
            "results/openai_gpt-6.1-sol_summary.json",
        ),
        (
            "anthropic",
            "claude-sonnet-5",
            "live_anthropic_*/trials.jsonl",
            {"pricing_status": "estimate_$2_in_$10_out_per_MTok"},
            "results/anthropic_claude-sonnet-5_summary.json",
        ),
        (
            "grok",
            "grok-4.7",
            "live_grok_*/trials.jsonl",
            {
                "settings": {"api": "openai_compatible", "base_url": "https://api.x.ai/v1"},
                "pricing_status": "estimate_$2_in_$6_out_per_MTok",
            },
            "results/grok-4.7_summary.json",
        ),
    ]

    for provider, model, glob, extra, out_name in configs:
        base = [replay(r) for r in latest_rows(glob, model, min_n=18) if r.get("task_id") not in {"T7", "T8"}]
        # Keep only one set of T1-T6 (3 each)
        by = {(r["task_id"], r["trial"]): r for r in base}
        base = [by[k] for k in sorted(by)]
        t7 = latest_task(glob, model, "T7")
        t8 = latest_task(glob, model, "T8")
        t9 = latest_task(glob, model, "T9")
        # Prefer a single full run that already includes T9 when present.
        full = [replay(r) for r in latest_rows(glob, model, min_n=27)]
        if full and any(r.get("task_id") == "T9" for r in full):
            by = {(r["task_id"], r["trial"]): r for r in full}
            rows = [by[k] for k in sorted(by)]
        else:
            rows = base + t7 + t8 + t9
        summary = summarize(rows, model, provider, extra)
        if provider == "anthropic":
            tin, tout = summary["token_usage"]["input_tokens"], summary["token_usage"]["output_tokens"]
            summary["gross_usd_estimate"] = round((tin / 1e6) * 2 + (tout / 1e6) * 10, 6)
        if provider == "grok":
            tin, tout = summary["token_usage"]["input_tokens"], summary["token_usage"]["output_tokens"]
            summary["gross_usd_estimate"] = round((tin / 1e6) * 2 + (tout / 1e6) * 6, 6)
        Path(ROOT / out_name).write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        print(provider, f"{summary['total_passes']}/{summary['total_trials']}")
        for f in summary["failures"]:
            print(f"  {f['task_id']} t{f['trial']}: {f['class']} {f['failed_checks']}")

    # Gemini: merge T1-T6 across runs + latest T7/T8
    gem_base = merge_gemini_base()
    gem_t7 = latest_task("live_gemini_*/trials.jsonl", "gemini-3.5-flash-lite", "T7")
    gem_t8 = latest_task("live_gemini_*/trials.jsonl", "gemini-3.5-flash-lite", "T8")
    gem_t9 = latest_task("live_gemini_*/trials.jsonl", "gemini-3.5-flash-lite", "T9")
    gem = summarize(
        gem_base + gem_t7 + gem_t8 + gem_t9,
        "gemini-3.5-flash-lite",
        "gemini",
        {"tier": "free_tier", "gross_usd_estimate": 0},
    )
    Path(RESULTS / "gemini_3.5_flash_lite_summary.json").write_text(
        json.dumps(gem, indent=2) + "\n", encoding="utf-8"
    )
    print("gemini", f"{gem['total_passes']}/{gem['total_trials']}")
    for f in gem["failures"]:
        print(f"  {f['task_id']} t{f['trial']}: {f['class']} {f['failed_checks']}")


if __name__ == "__main__":
    main()
