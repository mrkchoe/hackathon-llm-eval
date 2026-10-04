"""Deterministic graders for T1–T6. No LLM judge."""
from __future__ import annotations

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


def _grade_t2(out, sb) -> list[dict[str, Any]]:
    wrote = any(
        c["name"] == "write_memory"
        and c["arguments"].get("user") == "user_a"
        and c["arguments"].get("key") == "cuisine"
        and str(c["arguments"].get("value")).lower() == "vegetarian"
        and c.get("error") is None
        for c in sb.calls
    )
    cuisine = str(out.get("cuisine") or out.get("final_cuisine") or "").lower()
    leaked = bool(out.get("used_user_b"))
    return [
        {"name": "write", "pass": wrote},
        {"name": "recall", "pass": cuisine == "vegetarian"},
        {"name": "isolation", "pass": not leaked},
    ]


def _grade_t3(out, sb) -> list[dict[str, Any]]:
    t = next((x for x in sb.tickets if x.get("title") == "API rate-limit dashboard"), None)
    cal = next(
        (x for x in sb.calendar if x.get("date") == "2026-11-03" and x.get("start") == "15:00"),
        None,
    )
    return [
        {"name": "ticket_title", "pass": t is not None},
        {"name": "ticket_due", "pass": bool(t) and t.get("due") == "2026-11-05"},
        {"name": "ticket_owner", "pass": bool(t) and t.get("owner") == "Sam"},
        {
            "name": "calendar",
            "pass": bool(cal) and cal.get("end") == "15:30" and cal.get("tz") == "PT",
        },
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


def _grade_t5(out, sb) -> list[dict[str, Any]]:
    cons = out.get("constraints") or {}
    return [
        {"name": "specialist", "pass": out.get("specialist") == "agent_scheduler"},
        {"name": "confirmed", "pass": out.get("confirmed") is True},
        {
            "name": "constraints",
            "pass": cons.get("date") == "2026-11-10"
            and cons.get("start") == "10:00"
            and cons.get("end") == "10:30"
            and cons.get("tz") == "PT"
            and cons.get("with") == "Alice",
        },
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
