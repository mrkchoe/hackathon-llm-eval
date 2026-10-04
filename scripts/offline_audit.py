"""Rebuild published trial sets from traces (same merge rules) and audit metrics.
Does not rewrite pass/fail; compares against committed summaries.
No API calls.
"""
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
TASKS = [f"T{i}" for i in range(1, 11)]


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
            if l.strip() and json.loads(l).get("model_id") == model_id
        ]
        if min_n is None or len(rows) >= min_n:
            best = rows
    return best or []


def latest_task(glob: str, model_id: str, task_id: str) -> list[dict]:
    best = None
    for path in sorted(OUT.glob(glob), key=lambda p: p.stat().st_mtime):
        raw = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
        rows = [replay(r) for r in raw if r.get("model_id") == model_id and r.get("task_id") == task_id]
        if len(rows) >= 3:
            best = rows
    return best or []


def merge_gemini_base(model_id: str = "gemini-3.5-flash-lite") -> list[dict]:
    by: dict[tuple[str, int], dict] = {}
    for path in sorted(OUT.glob("live_gemini_*/trials.jsonl"), key=lambda p: p.stat().st_mtime):
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            if r.get("model_id") != model_id:
                continue
            if r.get("task_id") in {"T7", "T8", "T9", "T10"}:
                continue
            key = (r["task_id"], int(r["trial"]))
            by[key] = r
    return [replay(by[k]) for k in sorted(by)]


def build_standard(provider: str, model: str, glob: str) -> list[dict]:
    base = [replay(r) for r in latest_rows(glob, model, min_n=18) if r.get("task_id") not in {"T7", "T8"}]
    by = {(r["task_id"], r["trial"]): r for r in base}
    base = [by[k] for k in sorted(by)]
    t7 = latest_task(glob, model, "T7")
    t8 = latest_task(glob, model, "T8")
    t9 = latest_task(glob, model, "T9")
    t10 = latest_task(glob, model, "T10")
    full = [replay(r) for r in latest_rows(glob, model, min_n=30)]
    if full and any(r.get("task_id") == "T10" for r in full):
        by = {(r["task_id"], r["trial"]): r for r in full}
        rows = [by[k] for k in sorted(by)]
    else:
        rows = base + t7 + t8 + t9 + t10
    return rows


def tok(r: dict) -> tuple[int, int]:
    c = r.get("cost") or {}
    return int(c.get("input_tokens") or 0), int(c.get("output_tokens") or 0)


def audit(name: str, rows: list[dict], pub_path: Path, rates: dict | None) -> dict:
    pub = json.loads(pub_path.read_text(encoding="utf-8"))
    tin = sum(tok(r)[0] for r in rows)
    tout = sum(tok(r)[1] for r in rows)
    passes = sum(1 for r in rows if r.get("success"))
    lat_all = [float(r["elapsed_seconds"]) for r in rows if r.get("elapsed_seconds") is not None]
    lat_pass = [
        float(r["elapsed_seconds"])
        for r in rows
        if r.get("success") and r.get("elapsed_seconds") is not None
    ]
    per_task = {}
    for t in TASKS:
        tr = [r for r in rows if r["task_id"] == t]
        xs_all = [float(r["elapsed_seconds"]) for r in tr if r.get("elapsed_seconds") is not None]
        xs_pass = [
            float(r["elapsed_seconds"])
            for r in tr
            if r.get("success") and r.get("elapsed_seconds") is not None
        ]
        per_task[t] = {
            "slots": len(tr),
            "passes_regrade": sum(1 for r in tr if r.get("success")),
            "pub_passes": (pub.get("task_success_rates") or {}).get(t, {}).get("passes"),
            "pub_trials": (pub.get("task_success_rates") or {}).get(t, {}).get("trials"),
            "pub_mean_latency_s": (pub.get("task_success_rates") or {}).get(t, {}).get("mean_latency_s"),
            "mean_latency_all_s": round(statistics.mean(xs_all), 2) if xs_all else None,
            "mean_latency_pass_s": round(statistics.mean(xs_pass), 2) if xs_pass else None,
            "sum_latency_all_s": round(sum(xs_all), 2) if xs_all else None,
            "tokens_in": sum(tok(r)[0] for r in tr),
            "tokens_out": sum(tok(r)[1] for r in tr),
        }

    cost = None
    pricing = "unknown"
    if rates:
        cost = round((tin / 1e6) * rates["in"] + (tout / 1e6) * rates["out"], 6)
        pricing = rates["label"]

    out = {
        "model": name,
        "n_rows": len(rows),
        "missing_slots": [f"{t} need 3 have {per_task[t]['slots']}" for t in TASKS if per_task[t]["slots"] != 3],
        "tokens_in": tin,
        "tokens_out": tout,
        "pub_tokens_in": pub["token_usage"]["input_tokens"],
        "pub_tokens_out": pub["token_usage"]["output_tokens"],
        "tokens_match_published": tin == pub["token_usage"]["input_tokens"]
        and tout == pub["token_usage"]["output_tokens"],
        "passes_regrade": passes,
        "pub_passes": pub["total_passes"],
        "pub_trials": pub["total_trials"],
        "pass_match_if_regrade": passes == pub["total_passes"],
        "latency_sum_all_s": round(sum(lat_all), 2) if lat_all else None,
        "latency_mean_all_s": round(statistics.mean(lat_all), 2) if lat_all else None,
        "latency_mean_pass_s": round(statistics.mean(lat_pass), 2) if lat_pass else None,
        "gross_usd_estimate": cost,
        "pricing_status": pricing,
        "pub_gross_usd_estimate": pub.get("gross_usd_estimate"),
        "pub_pricing_status": pub.get("pricing_status"),
        "pub_tasks_label": pub.get("tasks"),
        "per_task": per_task,
    }
    print(f"\n===== {name} =====")
    print(json.dumps({k: v for k, v in out.items() if k != "per_task"}, indent=2))
    for t in TASKS:
        p = per_task[t]
        print(
            f"  {t}: slots={p['slots']} regrade={p['passes_regrade']}/{p['pub_trials']} "
            f"pub={p['pub_passes']} lat_all={p['mean_latency_all_s']} lat_pass={p['mean_latency_pass_s']} "
            f"pub_lat={p['pub_mean_latency_s']} tok={p['tokens_in']}/{p['tokens_out']}"
        )
    return out


def main() -> None:
    report = {}
    report["openai"] = audit(
        "gpt-6.1-sol",
        build_standard("openai", "gpt-6.1-sol", "live_openai_*/trials.jsonl"),
        RESULTS / "openai_gpt-6.1-sol_summary.json",
        None,
    )
    report["anthropic"] = audit(
        "claude-sonnet-5",
        build_standard("anthropic", "claude-sonnet-5", "live_anthropic_*/trials.jsonl"),
        RESULTS / "anthropic_claude-sonnet-5_summary.json",
        {"in": 2.0, "out": 10.0, "label": "estimate_$2_in_$10_out_per_MTok"},
    )
    gem = merge_gemini_base() + latest_task("live_gemini_*/trials.jsonl", "gemini-3.5-flash-lite", "T7")
    gem += latest_task("live_gemini_*/trials.jsonl", "gemini-3.5-flash-lite", "T8")
    gem += latest_task("live_gemini_*/trials.jsonl", "gemini-3.5-flash-lite", "T9")
    gem += latest_task("live_gemini_*/trials.jsonl", "gemini-3.5-flash-lite", "T10")
    report["gemini"] = audit(
        "gemini-3.5-flash-lite",
        gem,
        RESULTS / "gemini_3.5_flash_lite_summary.json",
        {"in": 0.0, "out": 0.0, "label": "free_tier_recorded_as_$0"},
    )
    report["grok"] = audit(
        "grok-4.7",
        build_standard("grok", "grok-4.7", "live_grok_*/trials.jsonl"),
        RESULTS / "grok-4.7_summary.json",
        {"in": 2.0, "out": 6.0, "label": "estimate_$2_in_$6_out_per_MTok"},
    )
    out = RESULTS / "offline_audit.json"
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("\nwrote", out)


if __name__ == "__main__":
    main()
