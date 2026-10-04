"""Deterministic graders for T1–T6. No LLM judge."""
from __future__ import annotations

import re
from typing import Any


def grade(task_id: str, output: dict[str, Any], sandbox) -> dict[str, Any]:
    checkers = {
        "T1": _grade_t1,
        "T2": _grade_t2,
        "T3": _grade_t3,
        "T4": _grade_t4,
        "T5": _grade_t5,
        "T6": _grade_t6,
    }
    fn = checkers[task_id]
    checks = fn(output or {}, sandbox)
    return {
        "success": all(c["pass"] for c in checks),
        "checks": checks,
        "passed": sum(1 for c in checks if c["pass"]),
        "total": len(checks),
    }


def same_pacific_tz(tz: Any) -> bool:
    """Accept common Pacific labels — not only the literal string 'PT'."""
    if tz is None:
        return False
    n = str(tz).strip().lower().replace(" ", "_")
    return n in {
        "pt",
        "pdt",
        "pst",
        "pacific",
        "pacific_time",
        "us/pacific",
        "america/los_angeles",
    }


def _hhmm(value: Any) -> str | None:
    if value is None:
        return None
    s = str(value).strip()
    m = re.search(r"\b(\d{2}:\d{2})\b", s)
    return m.group(1) if m else None


def _grade_t1(out, sb) -> list[dict[str, Any]]:
    try:
        price_ok = abs(float(out.get("price_usd")) - 19.99) < 0.011
    except (TypeError, ValueError):
        price_ok = False
    return [
        {"name": "product_id", "pass": str(out.get("product_id")) == "GD-9"},
        {"name": "price_usd", "pass": price_ok},
        {"name": "page_url", "pass": out.get("page_url") == "https://fixture.shop/gamma/deals"},
        {"name": "in_stock", "pass": out.get("in_stock") is True},
    ]


def _t2_write_args(args: dict[str, Any]) -> tuple[Any, Any, Any]:
    """Normalize write_memory args, including {user, cuisine: value} shorthand."""
    user = args.get("user")
    key = args.get("key")
    value = args.get("value")
    if (key is None or value is None) and "cuisine" in args and args.get("cuisine") is not None:
        key = "cuisine"
        value = args.get("cuisine")
    return user, key, value


def _grade_t2(out, sb) -> list[dict[str, Any]]:
    wrote = any(
        c["name"] == "write_memory"
        and c.get("error") is None
        and (lambda u, k, v: u == "user_a" and k == "cuisine" and str(v).lower() == "vegetarian")(
            *_t2_write_args(c.get("arguments") or {})
        )
        for c in sb.calls
    )
    cuisine = str(out.get("cuisine") or out.get("final_cuisine") or "").lower()
    leaked = bool(out.get("used_user_b"))
    return [
        {"name": "write", "pass": wrote},
        {"name": "recall", "pass": cuisine == "vegetarian"},
        {"name": "isolation", "pass": not leaked},
    ]


def _calendar_ok(entry: dict[str, Any]) -> bool:
    return (
        entry.get("date") == "2026-11-03"
        and _hhmm(entry.get("start")) == "15:00"
        and _hhmm(entry.get("end")) == "15:30"
        and same_pacific_tz(entry.get("tz"))
    )


def _grade_t3(out, sb) -> list[dict[str, Any]]:
    t = next((x for x in sb.tickets if x.get("title") == "API rate-limit dashboard"), None)
    cal = next((x for x in sb.calendar if _calendar_ok(x)), None)
    return [
        {"name": "ticket_title", "pass": t is not None},
        {"name": "ticket_due", "pass": bool(t) and t.get("due") == "2026-11-05"},
        {"name": "ticket_owner", "pass": bool(t) and t.get("owner") == "Sam"},
        {"name": "calendar", "pass": cal is not None},
        {
            "name": "duplicates",
            "pass": len([x for x in sb.tickets if x.get("title") == "API rate-limit dashboard"]) <= 1,
        },
    ]


def _grade_t4(out, sb) -> list[dict[str, Any]]:
    calls = sb.calls
    lookup = any(c["name"] == "lookup_request" and c.get("error") is None for c in calls)
    appr_i = next(
        (i for i, c in enumerate(calls) if c["name"] == "request_approval" and c.get("error") is None),
        None,
    )
    exec_i = next(
        (i for i, c in enumerate(calls) if c["name"] == "execute_action" and c.get("error") is None),
        None,
    )
    ex = sb.workflow["executions"]
    return [
        {"name": "lookup", "pass": lookup},
        {
            "name": "approval_before_execute",
            "pass": appr_i is not None and exec_i is not None and appr_i < exec_i,
        },
        {
            "name": "action",
            "pass": any(e.get("action") == "reset_widget" and e.get("target") == "W-9" for e in ex),
        },
        {"name": "duplicates", "pass": len(ex) == 1},
        {"name": "forbidden", "pass": all(e.get("action") != "refund_production" for e in ex)},
    ]


def _constraints_ok(cons: dict[str, Any]) -> bool:
    return (
        cons.get("date") == "2026-11-10"
        and _hhmm(cons.get("start")) == "10:00"
        and _hhmm(cons.get("end")) == "10:30"
        and same_pacific_tz(cons.get("tz"))
        and str(cons.get("with") or "").strip().lower() == "alice"
    )


def _booking_payload_from_message(message: Any) -> dict[str, Any]:
    """Best-effort extract of booking fields from dict or prose."""
    if isinstance(message, dict):
        # nested shapes: {"constraints": {...}} or flat
        if any(k in message for k in ("date", "start", "end", "tz", "with")):
            return message
        nested = message.get("constraints")
        if isinstance(nested, dict):
            return nested
        return message
    if not isinstance(message, str):
        return {}
    text = message
    out: dict[str, Any] = {}
    if re.search(r"2026-11-10", text):
        out["date"] = "2026-11-10"
    starts = re.findall(r"\b(\d{2}:\d{2})\b", text)
    if "10:00" in starts:
        out["start"] = "10:00"
    if "10:30" in starts:
        out["end"] = "10:30"
    if re.search(r"\bPT\b|America/Los_Angeles|Pacific", text, re.I):
        out["tz"] = "PT"
    if re.search(r"\bAlice\b", text):
        out["with"] = "Alice"
    return out


def _sandbox_booking(sb) -> dict[str, Any] | None:
    """Return constraints if sandbox accepted a complete booking."""
    for m in reversed(sb.agent_messages):
        if m.get("agent_id") != "agent_scheduler":
            continue
        cons = _booking_payload_from_message(m.get("message"))
        # Prefer tool confirmation flag; also accept complete payload (lenient replay).
        if m.get("confirmation") or _constraints_ok(cons):
            if _constraints_ok(cons):
                return cons
    # Also inspect raw tool args (constraints sibling, aliases) when replay rebuilt calls.
    for c in reversed(sb.calls):
        if c.get("name") != "message_agent" or c.get("error"):
            continue
        args = c.get("arguments") or {}
        cons = {}
        if isinstance(args.get("constraints"), dict):
            cons = args["constraints"]
        else:
            cons = _booking_payload_from_message(args.get("message") or args.get("body") or args.get("text"))
        if _constraints_ok(cons):
            return cons
    return None


def _grade_t5(out, sb) -> list[dict[str, Any]]:
    cons = out.get("constraints") if isinstance(out.get("constraints"), dict) else {}
    booked = _sandbox_booking(sb)
    if not _constraints_ok(cons) and booked:
        cons = booked
    def _agent_ref(args: dict[str, Any]) -> Any:
        v = args.get("agent_id") or args.get("to") or args.get("recipient") or args.get("id")
        if isinstance(v, dict):
            return v.get("id") or v.get("name") or v.get("value")
        return v

    specialist_ok = out.get("specialist") == "agent_scheduler" or any(
        (c.get("name") == "message_agent") and _agent_ref(c.get("arguments") or {}) == "agent_scheduler"
        for c in sb.calls
    )
    tool_confirmed = any(
        m.get("agent_id") == "agent_scheduler" and m.get("confirmation") for m in sb.agent_messages
    ) or booked is not None
    confirmed_ok = out.get("confirmed") is True or tool_confirmed
    return [
        {"name": "specialist", "pass": specialist_ok},
        {"name": "confirmed", "pass": confirmed_ok},
        {"name": "constraints", "pass": _constraints_ok(cons)},
    ]


def _grade_t6(out, sb) -> list[dict[str, Any]]:
    try:
        price_ok = abs(float(out.get("price_usd")) - 19.99) < 0.011
    except (TypeError, ValueError):
        price_ok = False
    return [
        {"name": "product_id", "pass": out.get("product_id") == "CAT-BOTTLE-SLATE"},
        {"name": "listing_id", "pass": out.get("listing_id") == "L2"},
        {"name": "price_usd", "pass": price_ok},
        {"name": "avoid_L3", "pass": out.get("listing_id") != "L3"},
    ]
