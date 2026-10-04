"""Re-score recorded trials with current graders/sandbox (no API calls)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from grade import grade  # noqa: E402
from sandbox_tools import Sandbox  # noqa: E402

OUT = ROOT / "outputs"
RESULTS = ROOT / "results"


def replay(task_id: str, tool_calls: list[dict], output: dict | None) -> dict:
    sb = Sandbox()
    for tc in tool_calls or []:
        name = tc.get("name")
        if not name:
            continue
        sb.call(name, tc.get("arguments") or {})
    g = grade(task_id, output or {}, sb)
    return g


def failure_class(row: dict, g: dict) -> str | None:
    if g.get("success"):
        return None
    hf = row.get("failure")
    if hf == "max_turns":
        # If tools actually completed the task, treat as incorrect_output rather than max_turns.
        if g.get("passed", 0) > 0 and all(c["pass"] for c in g.get("checks", [])):
            return None
        # If all substantive checks now pass, success already handled.
        if g.get("success"):
            return None
        # Keep max_turns only when still failing after lenient grade.
        failed = [c["name"] for c in g.get("checks", []) if not c["pass"]]
        if failed:
            return "max_turns" if not row.get("output") else "incorrect_output"
        return "max_turns"
    if hf and "429" in str(hf):
        return "rate_limit"
    if hf:
        return "provider_or_harness_error"
    return "incorrect_output"


def regrade_rows(rows: list[dict]) -> list[dict]:
    out = []
    for r in rows:
        g = replay(r["task_id"], r.get("tool_calls") or [], r.get("output"))
        nr = dict(r)
        nr["grade"] = g
        nr["success"] = bool(g.get("success"))
        # Clear harness failure when lenient grade now passes.
        if nr["success"]:
            nr["failure"] = None
        out.append(nr)
    return out


def summarize(rows: list[dict], model_id: str, provider: str, extra: dict | None = None) -> dict:
    rates = {}
    fails = []
    tok_in = tok_out = 0
    tasks = sorted({r["task_id"] for r in rows}) or ["T1", "T2", "T3", "T4", "T5", "T6", "T7"]
    for task in tasks:
        tr = [r for r in rows if r["task_id"] == task]
        passes = sum(1 for r in tr if r.get("success"))
        rates[task] = {"passes": passes, "trials": len(tr), "rate": (passes / len(tr) if tr else None)}
        for r in tr:
            cost = r.get("cost") or {}
            tok_in += cost.get("input_tokens") or 0
            tok_out += cost.get("output_tokens") or 0
            if r.get("success"):
                continue
            checks = (r.get("grade") or {}).get("checks") or []
            failed = [c.get("name") for c in checks if c.get("pass") is False]
            cls = failure_class(r, r.get("grade") or {})
            fails.append(
                {
                    "task_id": task,
                    "trial": r["trial"],
                    "class": cls,
                    "detail": r.get("failure"),
                    "failed_checks": failed,
                    "elapsed_seconds": r.get("elapsed_seconds"),
                    "output": r.get("output"),
                }
            )
    total_p = sum(v["passes"] for v in rates.values())
    total_n = sum(v["trials"] for v in rates.values())
    merged = {
        "model_id": model_id,
        "provider": provider,
        "status": "measured",
        "grading_note": (
            "Regraded with lenient Pacific tz aliases (PT ≈ America/Los_Angeles), "
            "common tool arg aliases, and T5 booking confirmation from complete payloads "
            "(dict, constraints sibling, or clear prose)."
        ),
        "task_success_rates": rates,
        "total_passes": total_p,
        "total_trials": total_n,
        "failures": fails,
        "token_usage": {"input_tokens": tok_in, "output_tokens": tok_out},
    }
    if extra:
        merged.update(extra)
    return merged


def latest_full(glob: str, model_id: str) -> list[dict]:
    runs = sorted(OUT.glob(glob), key=lambda p: p.stat().st_mtime)
    best = None
    for path in runs:
        rows = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines()]
        rows = [r for r in rows if r.get("model_id") == model_id]
        if len(rows) >= 18:
            best = rows
    if best is None and runs:
        best = [
            json.loads(l)
            for l in runs[-1].read_text(encoding="utf-8").splitlines()
            if json.loads(l).get("model_id") == model_id
        ]
    return best or []


def merge_gemini(model_id: str = "gemini-3.5-flash-lite") -> list[dict]:
    by: dict[tuple[str, int], dict] = {}
    for path in sorted(OUT.glob("live_gemini_*/trials.jsonl"), key=lambda p: p.stat().st_mtime):
        for line in path.read_text(encoding="utf-8").splitlines():
            r = json.loads(line)
            if r.get("model_id") != model_id:
                continue
            key = (r["task_id"], int(r["trial"]))
            prev = by.get(key)
            if prev is None or (r.get("success") and not prev.get("success")):
                by[key] = r
            else:
                by[key] = r
    rows = []
    tasks = sorted({k[0] for k in by}) or ["T1", "T2", "T3", "T4", "T5", "T6", "T7"]
    for task in tasks:
        for t in range(1, 4):
            if (task, t) in by:
                rows.append(by[(task, t)])
    return rows


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)

    # OpenAI
    oai = regrade_rows(latest_full("live_openai_*/trials.jsonl", "gpt-6.1-sol"))
    oai_sum = summarize(
        oai,
        "gpt-6.1-sol",
        "openai",
        {
            "settings": {"api": "responses", "reasoning_effort": "medium"},
            "run_id": oai[0]["run_id"] if oai else None,
            "gross_usd_estimate": None,
            "pricing_status": "unknown_do_not_invent",
        },
    )
    (RESULTS / "openai_gpt-6.1-sol_summary.json").write_text(
        json.dumps(oai_sum, indent=2) + "\n", encoding="utf-8"
    )
    print("OpenAI", f"{oai_sum['total_passes']}/{oai_sum['total_trials']}")
    for f in oai_sum["failures"]:
        print(f"  {f['task_id']} t{f['trial']}: {f['class']} {f['failed_checks']}")

    # Anthropic
    ant = regrade_rows(latest_full("live_anthropic_*/trials.jsonl", "claude-sonnet-5"))
    ant_sum = summarize(
        ant,
        "claude-sonnet-5",
        "anthropic",
        {
            "run_id": ant[0]["run_id"] if ant else None,
            "gross_usd_estimate": round((106841 / 1e6) * 2 + (10865 / 1e6) * 10, 6)
            if ant
            else None,
            "pricing_status": "estimate_$2_in_$10_out_per_MTok",
        },
    )
    # Keep recorded token usage from rows
    (RESULTS / "anthropic_claude-sonnet-5_summary.json").write_text(
        json.dumps(ant_sum, indent=2) + "\n", encoding="utf-8"
    )
    print("Anthropic", f"{ant_sum['total_passes']}/{ant_sum['total_trials']}")
    for f in ant_sum["failures"]:
        print(f"  {f['task_id']} t{f['trial']}: {f['class']} {f['failed_checks']}")

    # Gemini merged
    gem = regrade_rows(merge_gemini())
    gem_sum = summarize(
        gem,
        "gemini-3.5-flash-lite",
        "gemini",
        {
            "tier": "free_tier",
            "note": (
                "Merged free-tier runs; regraded with lenient tz/aliases. "
                "Out-of-pocket $0."
            ),
            "gross_usd_estimate": 0,
        },
    )
    (RESULTS / "gemini_3.5_flash_lite_summary.json").write_text(
        json.dumps(gem_sum, indent=2) + "\n", encoding="utf-8"
    )
    (OUT / "merged_gemini_3.5_flash_lite_summary.json").write_text(
        json.dumps(gem_sum, indent=2) + "\n", encoding="utf-8"
    )
    print("Gemini", f"{gem_sum['total_passes']}/{gem_sum['total_trials']}")
    for f in gem_sum["failures"]:
        print(f"  {f['task_id']} t{f['trial']}: {f['class']} {f['failed_checks']}")

    # Grok
    grok = regrade_rows(latest_full("live_grok_*/trials.jsonl", "grok-4.7"))
    grok_sum = summarize(
        grok,
        "grok-4.7",
        "grok",
        {
            "settings": {"api": "openai_compatible", "base_url": "https://api.x.ai/v1", "temperature": 0},
            "run_id": grok[0]["run_id"] if grok else None,
            "pricing_status": "estimate_$2_in_$6_out_per_MTok",
        },
    )
    # Fill cost estimate from token usage if present
    tin = grok_sum["token_usage"]["input_tokens"]
    tout = grok_sum["token_usage"]["output_tokens"]
    grok_sum["gross_usd_estimate"] = round((tin / 1e6) * 2 + (tout / 1e6) * 6, 6)
    (RESULTS / "grok-4.7_summary.json").write_text(
        json.dumps(grok_sum, indent=2) + "\n", encoding="utf-8"
    )
    print("Grok", f"{grok_sum['total_passes']}/{grok_sum['total_trials']}")
    for f in grok_sum["failures"]:
        print(f"  {f['task_id']} t{f['trial']}: {f['class']} {f['failed_checks']}")

    print("wrote summaries")


if __name__ == "__main__":
    main()
