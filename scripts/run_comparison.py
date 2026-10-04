#!/usr/bin/env python3
"""
Minimal multi-trial LLM comparison runner for tasks T1–T9.

Does not fabricate live results. Without API keys, only --reference-check
(validates fixtures/graders) is available — that is NOT a model comparison.

Usage:
  python scripts/run_comparison.py --reference-check
  python scripts/run_comparison.py --provider openai --model gpt-6.1-sol
  python scripts/run_comparison.py --provider anthropic --model claude-sonnet-5 --trials 3
  python scripts/run_comparison.py --provider grok --model grok-4.7 --trials 3
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from grade import grade  # noqa: E402
from sandbox_tools import Sandbox  # noqa: E402

try:
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
except ImportError:
    pass

TASKS = {
    "T1": {
        "file": "tasks/T1_web_product_research.md",
        "prompt": (
            "Find the cheapest in-stock slate water bottle with capacity_ml=750 and price_usd<=23 "
            "across the fixture retailers. Return JSON with product_id, name, price_usd, page_url, in_stock. "
            "Verify with fetch_page. Tools: search_pages, fetch_page."
        ),
        "tools": ["search_pages", "fetch_page"],
        "vision": False,
    },
    "T2": {
        "file": "tasks/T2_persistent_preference_memory.md",
        "prompt": (
            "Session1: for user_a write_memory cuisine=vegetarian. "
            "Session2: read_memory and return JSON {cuisine|final_cuisine}. "
            "Do not use user_b. Tools: write_memory, read_memory."
        ),
        "tools": ["write_memory", "read_memory"],
        "vision": False,
    },
    "T3": {
        "file": "tasks/T3_cross_app_ticket_calendar.md",
        "prompt": (
            "Actor agent_ops. Read note_101. Create ticket and calendar from the note. "
            "Return JSON {status}. Tools: read_note, find_ticket, create_ticket, create_calendar_entry."
        ),
        "tools": ["read_note", "find_ticket", "create_ticket", "create_calendar_entry"],
        "vision": False,
    },
    "T4": {
        "file": "tasks/T4_durable_support_workflow.md",
        "prompt": (
            "Process REQ-1: lookup_request, request_approval, then execute_action. "
            "Never execute before approval. Return JSON {status, action}. "
            "Tools: lookup_request, request_approval, execute_action."
        ),
        "tools": ["lookup_request", "request_approval", "execute_action"],
        "vision": False,
    },
    "T5": {
        "file": "tasks/T5_agent_discovery_scheduling.md",
        "prompt": (
            "Discover scheduling specialist, delegate meeting 2026-11-10 10:00-10:30 PT with Alice. "
            "Return JSON {specialist, confirmed, constraints:{date,start,end,tz,with}}. "
            "Tools: discover_agent, message_agent, check_status."
        ),
        "tools": ["discover_agent", "message_agent", "check_status"],
        "vision": False,
    },
    "T6": {
        "file": "tasks/T6_visual_catalog_match.md",
        "prompt": (
            "frame_id=frame_clear_bottle. Match catalog and return cheapest eligible listing JSON "
            "{product_id, listing_id, price_usd}. Tools: search_catalog, get_listing."
        ),
        "tools": ["search_catalog", "get_listing"],
        "vision": True,
    },
    "T7": {
        "file": "tasks/T7_policy_gated_remediation.md",
        "prompt": (
            "Resolve support incident INC-220. Follow authoritative policy refund_v1. "
            "Use only the provided tools. When finished return JSON "
            "{incident_id, remediation_id, amount_usd, policy_basis}. "
            "Tools: read_policy, lookup_incident, risk_check, list_remediations, "
            "quote_remediation, apply_remediation, notify_user."
        ),
        "tools": [
            "read_policy",
            "lookup_incident",
            "risk_check",
            "list_remediations",
            "quote_remediation",
            "apply_remediation",
            "notify_user",
        ],
        "vision": False,
    },
    "T8": {
        "file": "tasks/T8_amendment_aware_scheduling.md",
        "prompt": (
            "Actor agent_ops. Start from note_201. "
            "Apply the effective plan from the amendment notes. "
            "Return JSON {status, note_id_used}. "
            "Tools: read_amendment_note, find_ticket, create_ticket, create_calendar_entry."
        ),
        "tools": [
            "read_amendment_note",
            "find_ticket",
            "create_ticket",
            "create_calendar_entry",
        ],
        "vision": False,
    },
    "T9": {
        "file": "tasks/T9_dual_control_amended_payout.md",
        "prompt": (
            "Process payout starting from invoice INV-900 under authoritative policy payout_v1. "
            "Use only the provided tools. When finished return JSON "
            "{invoice_id, amount_usd, approvers, sanctions_case, status}. "
            "Tools: read_policy, lookup_invoice, sanctions_screen, clear_sanctions, "
            "list_approvers, request_payout_approval, execute_payout, notify_vendor."
        ),
        "tools": [
            "read_policy",
            "lookup_invoice",
            "sanctions_screen",
            "clear_sanctions",
            "list_approvers",
            "request_payout_approval",
            "execute_payout",
            "notify_vendor",
        ],
        "vision": False,
        "max_turns": 16,
    },
}

# Exact model IDs to compare under shared settings (temperature 0, same tools/prompts).
# Grok via xAI OpenAI-compatible API (https://api.x.ai/v1); ID checked 2026-10-03.
DEFAULT_MODELS = {
    "openai": "gpt-6.1-sol",
    "anthropic": "claude-sonnet-5",
    # 3.8-flash hit free-tier 503s; 2.5-flash-lite blocked for new users (2026-10-03).
    "gemini": "gemini-3.5-flash-lite",
    "grok": "grok-4.7",
}

CREDENTIALS = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "gemini": "GOOGLE_API_KEY",
    "grok": "XAI_API_KEY",
}


def reference_solver(task_id: str, sb: Sandbox) -> dict:
    """Known-good tool script to validate fixtures/graders. NOT a model under test."""
    if task_id == "T1":
        sb.call("search_pages", {"query": "slate 750"})
        sb.call("fetch_page", {"url": "https://fixture.shop/gamma/deals"})
        return {
            "product_id": "GD-9",
            "name": "TrailBottle 750",
            "price_usd": 19.99,
            "page_url": "https://fixture.shop/gamma/deals",
            "in_stock": True,
        }
    if task_id == "T2":
        sb.call("write_memory", {"user": "user_a", "key": "cuisine", "value": "vegetarian"})
        sb.call("read_memory", {"user": "user_a", "key": "cuisine"})
        return {"cuisine": "vegetarian", "final_cuisine": "vegetarian"}
    if task_id == "T3":
        sb.call("read_note", {"note_id": "note_101"})
        sb.call("find_ticket", {"title": "API rate-limit dashboard"})
        sb.call(
            "create_ticket",
            {
                "title": "API rate-limit dashboard",
                "due": "2026-11-05",
                "owner": "Sam",
                "actor": "agent_ops",
                "note_id": "note_101",
            },
        )
        sb.call(
            "create_calendar_entry",
            {
                "date": "2026-11-03",
                "start": "15:00",
                "end": "15:30",
                "tz": "PT",
                "title": "Launch sync follow-up",
                "actor": "agent_ops",
                "note_id": "note_101",
            },
        )
        return {"status": "created"}
    if task_id == "T4":
        sb.call("lookup_request", {"request_id": "REQ-1"})
        sb.call(
            "request_approval",
            {"request_id": "REQ-1", "action": "reset_widget", "target": "W-9"},
        )
        sb.call(
            "execute_action",
            {"request_id": "REQ-1", "action": "reset_widget", "target": "W-9"},
        )
        return {"status": "done", "action": "reset_widget"}
    if task_id == "T5":
        sb.call("discover_agent", {"skill": "scheduling"})
        sb.call(
            "message_agent",
            {
                "agent_id": "agent_scheduler",
                "message": {
                    "date": "2026-11-10",
                    "start": "10:00",
                    "end": "10:30",
                    "tz": "PT",
                    "with": "Alice",
                },
            },
        )
        sb.call("check_status", {"agent_id": "agent_scheduler"})
        return {
            "specialist": "agent_scheduler",
            "confirmed": True,
            "constraints": {
                "date": "2026-11-10",
                "start": "10:00",
                "end": "10:30",
                "tz": "PT",
                "with": "Alice",
            },
        }
    if task_id == "T6":
        sb.call("search_catalog", {"frame_id": "frame_clear_bottle"})
        sb.call("get_listing", {"product_id": "CAT-BOTTLE-SLATE"})
        return {"product_id": "CAT-BOTTLE-SLATE", "listing_id": "L2", "price_usd": 19.99}
    if task_id == "T7":
        sb.call("read_policy", {"policy_id": "refund_v1"})
        sb.call("lookup_incident", {"incident_id": "INC-220"})
        sb.call("risk_check", {"incident_id": "INC-220"})
        sb.call("list_remediations", {"incident_id": "INC-220"})
        sb.call(
            "quote_remediation",
            {"incident_id": "INC-220", "remediation_id": "escalate"},
        )
        sb.call(
            "apply_remediation",
            {"incident_id": "INC-220", "remediation_id": "escalate", "amount_usd": 0.0},
        )
        sb.call(
            "notify_user",
            {"user_id": "cust_9", "amount_usd": 0.0, "note": "escalated due to high fraud_risk"},
        )
        return {
            "incident_id": "INC-220",
            "remediation_id": "escalate",
            "amount_usd": 0.0,
            "policy_basis": "risk_check fraud_risk=high → escalate only, no credit/refund",
        }
    if task_id == "T8":
        sb.call("read_amendment_note", {"note_id": "note_201"})
        sb.call("read_amendment_note", {"note_id": "note_202"})
        # Cancellation: create nothing.
        return {"status": "cancelled", "note_id_used": "note_202"}
    if task_id == "T9":
        sb.call("read_policy", {"policy_id": "payout_v1"})
        sb.call("lookup_invoice", {"invoice_id": "INV-900"})
        sb.call("lookup_invoice", {"invoice_id": "INV-900A"})
        sb.call("sanctions_screen", {"vendor_id": "V-44"})
        sb.call("clear_sanctions", {"case_id": "S-12", "confirmation_code": "FP-SIM-44"})
        sb.call("list_approvers", {"category": "consulting"})
        sb.call(
            "request_payout_approval",
            {"approver": "alice", "invoice_id": "INV-900A", "amount_usd": 8330.0},
        )
        sb.call(
            "request_payout_approval",
            {"approver": "bob", "invoice_id": "INV-900A", "amount_usd": 8330.0},
        )
        sb.call("execute_payout", {"invoice_id": "INV-900A", "amount_usd": 8330.0})
        sb.call(
            "notify_vendor",
            {"vendor_id": "V-44", "amount_usd": 8330.0, "invoice_id": "INV-900A"},
        )
        return {
            "invoice_id": "INV-900A",
            "amount_usd": 8330.0,
            "approvers": ["alice", "bob"],
            "sanctions_case": "S-12",
            "status": "paid",
        }
    raise ValueError(task_id)


def _parse_json_object(text: str) -> dict:
    text = (text or "").strip()
    if not text:
        return {}
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start >= 0 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                return {"raw_text": text}
        return {"raw_text": text}


def run_openai_compatible(
    model: str,
    prompt: str,
    tools: list[str],
    sb: Sandbox,
    *,
    api_key: str | None = None,
    base_url: str | None = None,
    max_turns: int = 10,
    extra_create: dict | None = None,
) -> dict:
    from openai import OpenAI

    kwargs: dict = {}
    if api_key:
        kwargs["api_key"] = api_key
    if base_url:
        kwargs["base_url"] = base_url
    client = OpenAI(**kwargs)
    tool_defs = [
        {
            "type": "function",
            "function": {
                "name": n,
                "description": n,
                "parameters": {"type": "object", "additionalProperties": True},
            },
        }
        for n in tools
    ]
    messages = [
        {
            "role": "system",
            "content": "Use tools as needed. When done, reply with a single JSON object only.",
        },
        {"role": "user", "content": prompt},
    ]
    usage = {"input_tokens": 0, "output_tokens": 0}
    for _ in range(max_turns):
        create_kwargs = {
            "model": model,
            "messages": messages,
            "tools": tool_defs,
            "temperature": 0,
        }
        if extra_create:
            create_kwargs.update(extra_create)
        resp = client.chat.completions.create(**create_kwargs)
        if resp.usage:
            usage["input_tokens"] += resp.usage.prompt_tokens or 0
            usage["output_tokens"] += resp.usage.completion_tokens or 0
        msg = resp.choices[0].message
        if msg.tool_calls:
            messages.append(
                {
                    "role": "assistant",
                    "content": msg.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            },
                        }
                        for tc in msg.tool_calls
                    ],
                }
            )
            for tc in msg.tool_calls:
                args = json.loads(tc.function.arguments or "{}")
                result = sb.call(tc.function.name, args)
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": json.dumps(result),
                    }
                )
            continue
        return {"output": _parse_json_object(msg.content or ""), "usage": usage, "error": None}
    return {"output": {}, "usage": usage, "error": "max_turns"}


def run_openai(model: str, prompt: str, tools: list[str], sb: Sandbox, max_turns: int = 10) -> dict:
    """OpenAI GPT-6.1 Sol requires the Responses API for function tools (not Chat Completions)."""
    from openai import OpenAI

    client = OpenAI()
    tool_defs = [
        {
            "type": "function",
            "name": n,
            "description": n,
            "parameters": {"type": "object", "additionalProperties": True},
        }
        for n in tools
    ]
    usage = {"input_tokens": 0, "output_tokens": 0}
    reasoning = {"effort": "medium"}

    try:
        resp = client.responses.create(
            model=model,
            instructions="Use tools as needed. When done, reply with a single JSON object only.",
            input=prompt,
            tools=tool_defs,
            reasoning=reasoning,
        )
    except Exception as exc:  # noqa: BLE001
        return {"output": {}, "usage": usage, "error": str(exc)}

    for _ in range(max_turns):
        if getattr(resp, "usage", None):
            usage["input_tokens"] += getattr(resp.usage, "input_tokens", 0) or 0
            usage["output_tokens"] += getattr(resp.usage, "output_tokens", 0) or 0

        fcalls = [
            item
            for item in (resp.output or [])
            if getattr(item, "type", None) == "function_call"
        ]
        if not fcalls:
            text = getattr(resp, "output_text", None) or ""
            return {"output": _parse_json_object(text), "usage": usage, "error": None}

        tool_outputs = []
        for fc in fcalls:
            args = json.loads(fc.arguments or "{}")
            result = sb.call(fc.name, args)
            tool_outputs.append(
                {
                    "type": "function_call_output",
                    "call_id": fc.call_id,
                    "output": json.dumps(result),
                }
            )
        try:
            resp = client.responses.create(
                model=model,
                previous_response_id=resp.id,
                input=tool_outputs,
                tools=tool_defs,
                reasoning=reasoning,
            )
        except Exception as exc:  # noqa: BLE001
            return {"output": {}, "usage": usage, "error": str(exc)}

    return {"output": {}, "usage": usage, "error": "max_turns"}


def run_grok(model: str, prompt: str, tools: list[str], sb: Sandbox, max_turns: int = 10) -> dict:
    """xAI Grok — OpenAI-compatible Chat Completions at api.x.ai."""
    key = os.environ.get("XAI_API_KEY")
    if not key:
        return {"output": {}, "usage": {}, "error": "XAI_API_KEY missing"}
    return run_openai_compatible(
        model,
        prompt,
        tools,
        sb,
        api_key=key,
        base_url="https://api.x.ai/v1",
        max_turns=max_turns,
    )


def run_anthropic(model: str, prompt: str, tools: list[str], sb: Sandbox, max_turns: int = 10) -> dict:
    import anthropic

    client = anthropic.Anthropic()
    tool_defs = [
        {
            "name": n,
            "description": n,
            "input_schema": {
                "type": "object",
                "properties": {},
                "additionalProperties": True,
            },
        }
        for n in tools
    ]
    messages: list[dict] = [{"role": "user", "content": prompt}]
    usage = {"input_tokens": 0, "output_tokens": 0}
    for _ in range(max_turns):
        try:
            resp = client.messages.create(
                model=model,
                max_tokens=2048,
                system="Use tools as needed. When done, reply with a single JSON object only.",
                tools=tool_defs,
                messages=messages,
            )
        except Exception as exc:  # noqa: BLE001
            return {"output": {}, "usage": usage, "error": str(exc)}
        usage["input_tokens"] += getattr(resp.usage, "input_tokens", 0) or 0
        usage["output_tokens"] += getattr(resp.usage, "output_tokens", 0) or 0
        tool_uses = [b for b in resp.content if getattr(b, "type", None) == "tool_use"]
        texts = [b.text for b in resp.content if getattr(b, "type", None) == "text"]
        if tool_uses:
            messages.append({"role": "assistant", "content": resp.content})
            results = []
            for b in tool_uses:
                result = sb.call(b.name, dict(b.input or {}))
                results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": b.id,
                        "content": json.dumps(result),
                    }
                )
            messages.append({"role": "user", "content": results})
            continue
        return {"output": _parse_json_object("\n".join(texts)), "usage": usage, "error": None}
    return {"output": {}, "usage": usage, "error": "max_turns"}


def run_gemini(model: str, prompt: str, tools: list[str], sb: Sandbox, max_turns: int = 10) -> dict:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
    # Simple multi-turn: concatenate tool results into the prompt (minimal, shared conditions).
    transcript = prompt
    usage = {"input_tokens": 0, "output_tokens": 0}
    decls = [
        types.FunctionDeclaration(
            name=n,
            description=n,
            parameters={"type": "object", "properties": {}},
        )
        for n in tools
    ]
    for _ in range(max_turns):
        resp = None
        last_err = None
        for attempt in range(6):
            try:
                resp = client.models.generate_content(
                    model=model,
                    contents=transcript + "\nWhen finished, return JSON only.",
                    config=types.GenerateContentConfig(
                        temperature=0,
                        tools=[types.Tool(function_declarations=decls)],
                    ),
                )
                last_err = None
                break
            except Exception as exc:  # noqa: BLE001
                msg = str(exc)
                last_err = msg
                if "429" in msg or "RESOURCE_EXHAUSTED" in msg:
                    # Free tier is ~15 RPM; wait and retry.
                    wait = 40 + attempt * 10
                    print(f"    rate-limited; sleeping {wait}s (attempt {attempt+1}/6)")
                    time.sleep(wait)
                    continue
                return {"output": {}, "usage": usage, "error": msg}
        if last_err:
            return {"output": {}, "usage": usage, "error": last_err}
        um = getattr(resp, "usage_metadata", None)
        if um:
            usage["input_tokens"] += getattr(um, "prompt_token_count", 0) or 0
            usage["output_tokens"] += getattr(um, "candidates_token_count", 0) or 0
        fcalls = []
        for cand in getattr(resp, "candidates", []) or []:
            for part in getattr(getattr(cand, "content", None), "parts", []) or []:
                fc = getattr(part, "function_call", None)
                if fc:
                    fcalls.append(fc)
        if fcalls:
            for fc in fcalls:
                result = sb.call(fc.name, dict(fc.args or {}))
                transcript += f"\nTOOL {fc.name} => {json.dumps(result)}"
            # Small pace between tool-loop turns on free tier
            time.sleep(5)
            continue
        text = getattr(resp, "text", None) or ""
        return {"output": _parse_json_object(text), "usage": usage, "error": None}
    return {"output": {}, "usage": usage, "error": "max_turns"}


def estimate_cost(provider: str, model: str, usage: dict) -> dict:
    # Partial known rates from docs (2026-10-03). Unknown => null (not zero).
    rates = {
        ("anthropic", "claude-sonnet-5"): (2.0, 10.0),
        ("anthropic", "claude-haiku-4-5-20251001"): (1.0, 5.0),
        # xAI docs 2026-10-03: grok-4.7 $2 / $6 per MTok in/out
        ("grok", "grok-4.7"): (2.0, 6.0),
    }
    pair = rates.get((provider, model))
    if not pair:
        return {
            "gross_usd_estimate": None,
            "pricing_status": "unknown_do_not_invent",
            "input_tokens": usage.get("input_tokens"),
            "output_tokens": usage.get("output_tokens"),
        }
    inn, out = pair
    cost = (usage.get("input_tokens", 0) / 1e6) * inn + (usage.get("output_tokens", 0) / 1e6) * out
    return {
        "gross_usd_estimate": round(cost, 6),
        "pricing_status": "documented_estimate",
        "input_tokens": usage.get("input_tokens"),
        "output_tokens": usage.get("output_tokens"),
        "rates_per_mtok": {"input": inn, "output": out},
    }


def run_reference_check() -> int:
    print("REFERENCE CHECK ONLY — validates fixtures/graders; not a model comparison.\n")
    rows = []
    for task_id in TASKS:
        sb = Sandbox()
        t0 = time.perf_counter()
        out = reference_solver(task_id, sb)
        g = grade(task_id, out, sb)
        elapsed = time.perf_counter() - t0
        rows.append((task_id, g["success"], g["passed"], g["total"], elapsed))
        status = "PASS" if g["success"] else "FAIL"
        print(f"  {task_id}: {status} ({g['passed']}/{g['total']}) {elapsed*1000:.1f}ms")
    ok = all(r[1] for r in rows)
    print("\nAll reference checks passed." if ok else "\nReference checks failed.")
    return 0 if ok else 1


def main() -> int:
    p = argparse.ArgumentParser(description="Minimal LLM comparison runner (T1–T9)")
    p.add_argument("--reference-check", action="store_true", help="Validate fixtures/graders only")
    p.add_argument("--provider", choices=["openai", "anthropic", "gemini", "grok"])
    p.add_argument("--model", help="Exact model ID (defaults per provider)")
    p.add_argument("--trials", type=int, default=3)
    p.add_argument("--tasks", nargs="*", default=list(TASKS.keys()))
    p.add_argument(
        "--pace-seconds",
        type=float,
        default=0,
        help="Sleep between trials (use ~20 on Gemini free tier to stay under 15 RPM).",
    )
    args = p.parse_args()

    if args.reference_check:
        return run_reference_check()

    if not args.provider:
        print("Provide --provider or --reference-check.", file=sys.stderr)
        print("\nCredentials required for live runs:")
        for prov, env in CREDENTIALS.items():
            present = "set" if os.getenv(env) else "MISSING"
            print(f"  {prov}: {env} ({present})")
        return 2

    env = CREDENTIALS[args.provider]
    if not os.getenv(env):
        print(f"Missing credential: {env}. Refusing to fabricate results.", file=sys.stderr)
        return 2

    model = args.model or DEFAULT_MODELS[args.provider]
    run_id = f"live_{args.provider}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_{uuid.uuid4().hex[:6]}"
    out_dir = ROOT / "outputs" / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    runners = {
        "openai": run_openai,
        "anthropic": run_anthropic,
        "gemini": run_gemini,
        "grok": run_grok,
    }
    runner = runners[args.provider]

    records = []
    print(f"Live run {run_id}")
    print(f"Provider={args.provider} model={model} trials={args.trials}")
    print("Shared conditions: temperature=0, same task prompts/tools, sandbox fixtures.\n")

    for task_id in args.tasks:
        meta = TASKS[task_id]
        for trial in range(1, args.trials + 1):
            sb = Sandbox()
            t0 = time.perf_counter()
            failure = None
            try:
                result = runner(
                    model,
                    meta["prompt"],
                    meta["tools"],
                    sb,
                    max_turns=int(meta.get("max_turns") or 10),
                )
                output = result["output"]
                usage = result["usage"]
                if result.get("error"):
                    failure = result["error"]
            except Exception as exc:  # noqa: BLE001
                output, usage, failure = {}, {"input_tokens": 0, "output_tokens": 0}, str(exc)
            elapsed = time.perf_counter() - t0
            if failure == "unsupported_capability" or (
                meta["vision"] and "vision" in str(failure or "").lower()
            ):
                g = {
                    "success": False,
                    "checks": [],
                    "passed": 0,
                    "total": 0,
                    "coverage_exclusion": "unsupported_capability",
                }
            else:
                g = grade(task_id, output, sb)
            rec = {
                "run_id": run_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "task_id": task_id,
                "trial": trial,
                "provider": args.provider,
                "model_id": model,
                "settings": {
                    "api": "responses",
                    "reasoning_effort": "medium",
                }
                if args.provider == "openai"
                else {"temperature": 0},
                "role": "runtime_model_under_test",
                "output": output,
                "tool_calls": sb.calls,
                "success": g.get("success"),
                "grade": g,
                "failure": failure,
                "elapsed_seconds": elapsed,
                "cost": estimate_cost(args.provider, model, usage),
                "measured": True,
            }
            records.append(rec)
            flag = "PASS" if rec["success"] else "FAIL"
            print(f"  {task_id} trial {trial}: {flag} {elapsed:.2f}s failure={failure}")
            if args.pace_seconds > 0:
                time.sleep(args.pace_seconds)

    jsonl = out_dir / "trials.jsonl"
    with jsonl.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")

    # Summary counts — measured only
    by_task = {}
    for r in records:
        by_task.setdefault(r["task_id"], {"pass": 0, "n": 0})
        by_task[r["task_id"]]["n"] += 1
        if r["success"]:
            by_task[r["task_id"]]["pass"] += 1
    summary = {
        "run_id": run_id,
        "provider": args.provider,
        "model_id": model,
        "trials_per_task": args.trials,
        "task_success_rates": {
            k: {"passes": v["pass"], "trials": v["n"], "rate": v["pass"] / v["n"] if v["n"] else None}
            for k, v in by_task.items()
        },
        "n_records": len(records),
        "note": "Measured live outputs. Do not mix with documented-capability tables.",
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"\nWrote {jsonl}")
    print(f"Wrote {out_dir / 'summary.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
