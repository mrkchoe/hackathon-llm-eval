"""Minimal deterministic sandbox tools for the six evaluation tasks."""
from __future__ import annotations

import inspect
import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / "fixtures"

# Common model arg aliases → canonical parameter names (less brittle than exact schemas).
_ARG_ALIASES: dict[str, dict[str, str]] = {
    "discover_agent": {"query": "skill", "capability": "skill", "name": "skill"},
    "message_agent": {
        "to": "agent_id",
        "recipient": "agent_id",
        "id": "agent_id",
        "body": "message",
        "text": "message",
    },
    "check_status": {"to": "agent_id", "recipient": "agent_id", "id": "agent_id"},
    "create_ticket": {"due_date": "due"},
    "create_calendar_entry": {
        "start_time": "start",
        "end_time": "end",
        "timezone": "tz",
        "time_zone": "tz",
    },
}


def _load(rel: str) -> dict[str, Any]:
    with (FIX / rel).open(encoding="utf-8") as f:
        return json.load(f)


def _same_pacific_tz(tz: Any) -> bool:
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


def _unwrap_leaf(value: Any) -> Any:
    """Unwrap common single-field wrappers models emit, e.g. {'id': 'x'} → 'x'."""
    if not isinstance(value, dict) or not value:
        return value
    if len(value) == 1:
        k, v = next(iter(value.items()))
        if k in {"id", "name", "value", "text", "label"} and not isinstance(v, (dict, list)):
            return v
    # Prefer known inner keys when present alongside extras
    for k in ("id", "name", "value", "text"):
        if k in value and not isinstance(value[k], (dict, list)) and len(value) <= 2:
            return value[k]
    return value


def _unwrap_tree(value: Any) -> Any:
    if isinstance(value, dict):
        # First unwrap children, then leaf
        inner = {k: _unwrap_tree(v) for k, v in value.items()}
        return _unwrap_leaf(inner) if not any(isinstance(v, (dict, list)) for v in inner.values()) else {
            k: _unwrap_leaf(v) if not isinstance(v, (dict, list)) else v for k, v in inner.items()
        }
    return value


def _normalize_args(name: str, args: dict[str, Any]) -> dict[str, Any]:
    aliases = _ARG_ALIASES.get(name, {})
    out = {k: _unwrap_tree(v) for k, v in args.items()}
    for src, dst in aliases.items():
        if src in out and dst not in out:
            out[dst] = out[src]
    # message_agent: fold sibling constraints into message when useful
    if name == "message_agent":
        out["agent_id"] = _unwrap_leaf(out.get("agent_id"))
        cons = out.get("constraints")
        msg = out.get("message")
        if isinstance(msg, dict):
            # flatten {"text": "..."} already handled; also pull nested constraints
            if isinstance(msg.get("constraints"), dict):
                msg = {**msg["constraints"], **{k: v for k, v in msg.items() if k != "constraints"}}
                out["message"] = msg
            # timezone alias inside message dict
            if "tz" not in msg and "timezone" in msg:
                msg = dict(msg)
                msg["tz"] = msg["timezone"]
                out["message"] = msg
        if isinstance(cons, dict):
            if isinstance(msg, dict):
                merged = {**cons, **msg}
                out["message"] = merged
            elif msg is None or (isinstance(msg, str) and not msg.strip().startswith("{")):
                out["message"] = cons
    if name == "write_memory":
        # Accept {"user": "...", "cuisine": "vegetarian"} → key=cuisine, value=vegetarian
        if out.get("key") is None or out.get("value") is None:
            extras = {
                k: v
                for k, v in out.items()
                if k not in {"user", "key", "value"} and not isinstance(v, (dict, list))
            }
            if len(extras) == 1:
                k, v = next(iter(extras.items()))
                out.setdefault("key", k)
                out.setdefault("value", v)
    if name == "create_calendar_entry":
        start = out.get("start")
        if out.get("date") is None and isinstance(start, str):
            if "T" in start:
                out["date"] = start.split("T", 1)[0]
            else:
                dm = re.search(r"\b(20\d{2}-\d{2}-\d{2})\b", start)
                if dm:
                    out["date"] = dm.group(1)
        for key in ("start", "end"):
            val = out.get(key)
            if isinstance(val, str):
                m = re.search(r"\b(\d{2}:\d{2})\b", val)
                if m:
                    out[key] = m.group(1)
        # actor/title may still be nested after partial unwrap
        for key in ("actor", "title", "tz", "date"):
            if key in out:
                out[key] = _unwrap_leaf(out[key])
    if name == "create_ticket":
        if "actor" not in out and "authorized_writer" in out:
            out["actor"] = _unwrap_leaf(out["authorized_writer"])
        for key in ("actor", "title", "due", "owner"):
            if key in out:
                out[key] = _unwrap_leaf(out[key])
    if name == "check_status":
        out["agent_id"] = _unwrap_leaf(out.get("agent_id"))
    return out

def _booking_fields(message: Any) -> dict[str, Any]:
    if isinstance(message, dict):
        if isinstance(message.get("constraints"), dict) and not any(
            k in message for k in ("date", "start", "end", "tz", "with")
        ):
            return message["constraints"]
        return message
    if not isinstance(message, str):
        return {}
    # Try JSON first
    try:
        parsed = json.loads(message)
        if isinstance(parsed, dict):
            return _booking_fields(parsed)
    except json.JSONDecodeError:
        pass
    text = message
    out: dict[str, Any] = {}
    dm = re.search(r"\b(20\d{2}-\d{2}-\d{2})\b", text)
    if dm:
        out["date"] = dm.group(1)
    times = re.findall(r"\b(\d{2}:\d{2})\b", text)
    if times:
        out["start"] = times[0]
        if len(times) > 1:
            out["end"] = times[1]
    tz_m = re.search(
        r"\b(PT|PDT|PST|America/Los_Angeles|US/Pacific|Pacific(?:\s+Time)?)\b",
        text,
        re.I,
    )
    if tz_m:
        out["tz"] = tz_m.group(1)
    with_m = re.search(r"\bwith\s+([A-Za-z]+)\b", text, re.I)
    if with_m:
        out["with"] = with_m.group(1)
    elif re.search(r"\bAlice\b", text):
        out["with"] = "Alice"
    return out


class Sandbox:
    def __init__(self) -> None:
        self.memory = deepcopy(_load("memory/seed.json").get("users", {}))
        self.tickets: list[dict[str, Any]] = []
        self.calendar: list[dict[str, Any]] = []
        self.workflow = {"looked_up": False, "approved": False, "executions": [], "approvals": 0}
        self.agent_messages: list[dict[str, Any]] = []
        self.fetched_urls: set[str] = set()
        self.calls: list[dict[str, Any]] = []
        self.policies_read: set[str] = set()
        self.incidents_touched: set[str] = set()
        self.remediations_applied: list[dict[str, Any]] = []
        self.notifications: list[dict[str, Any]] = []
        self.quotes: list[dict[str, Any]] = []
        self.risk_checks: dict[str, str] = {}
        self.sanctions: dict[str, dict[str, Any]] = {}
        self.cleared_cases: set[str] = set()
        self.approvals: list[dict[str, Any]] = []
        self.payouts: list[dict[str, Any]] = []
        self.vendor_notifications: list[dict[str, Any]] = []
        # T10 saga package state
        self.package: dict[str, Any] = {
            "room": None,
            "catering": None,
            "av": None,
            "poisoned": False,
            "finalized": False,
        }

    def call(self, name: str, args: dict[str, Any] | None = None) -> dict[str, Any]:
        args = args or {}
        fn = getattr(self, name, None)
        if fn is None:
            rec = {"name": name, "arguments": args, "error": "unknown_tool"}
            self.calls.append(rec)
            return {"ok": False, "error": "unknown_tool"}
        try:
            normalized = _normalize_args(name, args)
            sig = inspect.signature(fn)
            # Drop unexpected kwargs so models can pass extra fields without hard-failing the tool.
            if any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values()):
                filtered = normalized
            else:
                allowed = {
                    k
                    for k, p in sig.parameters.items()
                    if p.kind in (inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.KEYWORD_ONLY)
                }
                filtered = {k: v for k, v in normalized.items() if k in allowed}
            result = fn(**filtered)
            self.calls.append({"name": name, "arguments": args, "error": None})
            return {"ok": True, "result": result}
        except PermissionError as exc:
            self.calls.append({"name": name, "arguments": args, "error": "unauthorized"})
            return {"ok": False, "error": "unauthorized", "detail": str(exc)}
        except Exception as exc:  # noqa: BLE001
            self.calls.append({"name": name, "arguments": args, "error": str(exc)})
            return {"ok": False, "error": str(exc)}
    def search_pages(self, query: str = "") -> dict[str, Any]:
        hits = []
        q = query.lower()
        for page in _load("retailers/pages.json")["pages"]:
            for p in page["products"]:
                if not q or any(t in json.dumps(p).lower() for t in q.split()):
                    hits.append({**p, "page_url": page["url"], "product_id": p["id"]})
        return {"hits": hits}

    def fetch_page(self, url: str) -> dict[str, Any]:
        for page in _load("retailers/pages.json")["pages"]:
            if page["url"] == url:
                self.fetched_urls.add(url)
                return page
        raise RuntimeError("page_not_found")

    def write_memory(self, user: str, key: str, value: Any) -> dict[str, Any]:
        self.memory.setdefault(user, {})[key] = value
        return {"user": user, "key": key, "value": value}

    def read_memory(self, user: str, key: str | None = None) -> dict[str, Any]:
        mem = self.memory.get(user, {})
        if key is None:
            return {"user": user, "memory": mem}
        return {"user": user, "key": key, "value": mem.get(key)}

    def read_note(self, note_id: str) -> dict[str, Any]:
        notes = _load("notes/meetings.json")["notes"]
        if note_id not in notes:
            raise RuntimeError("note_not_found")
        return {"note_id": note_id, **notes[note_id]}

    def read_amendment_note(self, note_id: str) -> dict[str, Any]:
        notes = _load("notes/amendments.json")["notes"]
        if note_id not in notes:
            raise RuntimeError("note_not_found")
        return {"note_id": note_id, **notes[note_id]}

    def find_ticket(self, title: str) -> dict[str, Any]:
        return {"matches": [t for t in self.tickets if t.get("title") == title]}

    def create_ticket(
        self, title: str, due: str, owner: str, actor: str, note_id: str | None = None
    ) -> dict[str, Any]:
        notes = {
            **_load("notes/meetings.json")["notes"],
            **_load("notes/amendments.json")["notes"],
        }
        if note_id and notes.get(note_id, {}).get("authorized_writer") != actor:
            raise PermissionError("unauthorized")
        existing = [t for t in self.tickets if t.get("title") == title]
        if existing:
            return {"duplicate": True, "ticket": existing[0]}
        ticket = {"title": title, "due": due, "owner": owner, "actor": actor, "note_id": note_id}
        self.tickets.append(ticket)
        return {"duplicate": False, "ticket": ticket}

    def create_calendar_entry(
        self,
        date: str,
        start: str,
        end: str,
        tz: str,
        title: str,
        actor: str,
        note_id: str | None = None,
    ) -> dict[str, Any]:
        notes = {
            **_load("notes/meetings.json")["notes"],
            **_load("notes/amendments.json")["notes"],
        }
        if note_id and notes.get(note_id, {}).get("authorized_writer") != actor:
            raise PermissionError("unauthorized")
        entry = {
            "date": date,
            "start": start,
            "end": end,
            "tz": tz,
            "title": title,
            "actor": actor,
            "note_id": note_id,
        }
        self.calendar.append(entry)
        return {"entry": entry}

    def lookup_request(self, request_id: str) -> dict[str, Any]:
        req = _load("support/requests.json")["requests"].get(request_id)
        if not req:
            raise RuntimeError("request_not_found")
        self.workflow["looked_up"] = True
        return {"request_id": request_id, **req}

    def request_approval(self, request_id: str, action: str, target: str) -> dict[str, Any]:
        self.workflow["approved"] = True
        self.workflow["approvals"] += 1
        return {"approved": True, "action": action, "target": target}

    def execute_action(self, request_id: str, action: str, target: str) -> dict[str, Any]:
        if action == "refund_production":
            raise PermissionError("forbidden")
        if not self.workflow.get("approved"):
            raise PermissionError("approval_required")
        for ex in self.workflow["executions"]:
            if ex["action"] == action and ex["target"] == target:
                return {"duplicate": True, "execution": ex}
        ex = {"request_id": request_id, "action": action, "target": target}
        self.workflow["executions"].append(ex)
        return {"duplicate": False, "execution": ex}

    def discover_agent(self, skill: str) -> dict[str, Any]:
        agents = _load("agents/directory.json")["agents"]
        return {"matches": [a for a in agents if skill in a.get("skills", [])]}

    def message_agent(self, agent_id: str, message: Any) -> dict[str, Any]:
        fields = _booking_fields(message)
        required = ["date", "start", "end", "tz", "with"]
        has_fields = all(k in fields and fields[k] not in (None, "") for k in required)
        tz_ok = _same_pacific_tz(fields.get("tz")) if has_fields else False
        # Confirm when the specialist gets a complete Pacific booking (dict or clear prose).
        ok = agent_id == "agent_scheduler" and has_fields and tz_ok
        # Store normalized fields when we could parse them (helps graders / status).
        stored_message = fields if has_fields else message
        msg = {
            "agent_id": agent_id,
            "message": stored_message,
            "status": "confirmed" if ok else "needs_clarification",
            "confirmation": ok,
        }
        self.agent_messages.append(msg)
        return msg

    def check_status(self, agent_id: str) -> dict[str, Any]:
        related = [m for m in self.agent_messages if m["agent_id"] == agent_id]
        if not related:
            return {"agent_id": agent_id, "status": "unknown", "confirmation": False}
        last = related[-1]
        return {
            "agent_id": agent_id,
            "status": last["status"],
            "confirmation": last.get("confirmation", False),
            "message": last.get("message"),
        }

    def search_catalog(self, query: str = "", frame_id: str | None = None) -> dict[str, Any]:
        catalog = _load("catalog/products.json")["products"]
        frames = _load("images/frames.json")["frames"]
        if frame_id:
            frame = frames.get(frame_id)
            if not frame or frame.get("ambiguous") or not frame.get("match"):
                return {"matches": [], "ambiguous": True}
            return {
                "matches": [p for p in catalog if p["product_id"] == frame["match"]],
                "ambiguous": False,
            }
        q = query.lower()
        return {"matches": [p for p in catalog if q in json.dumps(p).lower()], "ambiguous": False}

    def get_listing(self, product_id: str, listing_id: str | None = None) -> dict[str, Any]:
        for p in _load("catalog/products.json")["products"]:
            if p["product_id"] == product_id:
                if listing_id:
                    for L in p["listings"]:
                        if L["listing_id"] == listing_id:
                            return {"product_id": product_id, "listing": L}
                    raise RuntimeError("listing_not_found")
                return {"product_id": product_id, "listings": p["listings"]}
        raise RuntimeError("product_not_found")

    def read_policy(self, policy_id: str) -> dict[str, Any]:
        policies = {
            **_load("policy/refund_policy.json")["policies"],
            **_load("policy/payout_policy.json")["policies"],
            **_load("policy/summit_policy.json")["policies"],
        }
        pol = policies.get(policy_id)
        if not pol:
            raise RuntimeError("policy_not_found")
        self.policies_read.add(policy_id)
        return {"policy_id": policy_id, **pol}

    def lookup_incident(self, incident_id: str) -> dict[str, Any]:
        inc = _load("incidents/incidents.json")["incidents"].get(incident_id)
        if not inc:
            raise RuntimeError("incident_not_found")
        self.incidents_touched.add(incident_id)
        body = {
            k: v
            for k, v in inc.items()
            if k not in {"remediations", "fraud_risk"}
        }
        return {"incident_id": incident_id, **body}

    def risk_check(self, incident_id: str) -> dict[str, Any]:
        inc = _load("incidents/incidents.json")["incidents"].get(incident_id)
        if not inc:
            raise RuntimeError("incident_not_found")
        self.incidents_touched.add(incident_id)
        risk = str(inc.get("fraud_risk") or "low")
        self.risk_checks[incident_id] = risk
        return {"incident_id": incident_id, "fraud_risk": risk}

    def list_remediations(self, incident_id: str) -> dict[str, Any]:
        inc = _load("incidents/incidents.json")["incidents"].get(incident_id)
        if not inc:
            raise RuntimeError("incident_not_found")
        self.incidents_touched.add(incident_id)
        return {
            "incident_id": incident_id,
            "remediations": list(inc.get("remediations") or []),
            "note": "Ordered by customer preference, not policy.",
        }

    def _quote(self, incident_id: str, incident: dict[str, Any], remediation_id: str) -> dict[str, Any]:
        risk = self.risk_checks.get(incident_id)
        if risk is None:
            return {
                "allowed": False,
                "amount_usd": 0.0,
                "reason": "risk_check_required_before_quote",
            }
        if risk == "high":
            ok = remediation_id == "escalate"
            return {
                "allowed": ok,
                "amount_usd": 0.0,
                "reason": "high fraud_risk -> escalate only"
                if ok
                else "high fraud_risk forbids refund/credit",
            }
        days = int(incident.get("days_since_purchase") or 999)
        damage = bool(incident.get("damage_reported"))
        digital = str(incident.get("product_type") or "").lower() == "digital"
        total = float(incident.get("order_total_usd") or 0)
        if remediation_id == "full_refund":
            ok = damage and days <= 14 and not digital
            return {
                "allowed": ok,
                "amount_usd": total if ok else 0.0,
                "reason": "full refund within 14-day damage window"
                if ok
                else "full_refund forbidden by refund_v1",
            }
        if remediation_id == "store_credit":
            if damage and days > 14:
                return {
                    "allowed": True,
                    "amount_usd": round(total * 0.5, 2),
                    "reason": "late damage -> store_credit at 50% of order_total_usd",
                }
            if damage and digital:
                return {
                    "allowed": True,
                    "amount_usd": round(total * 0.5, 2),
                    "reason": "digital goods -> store_credit at 50%",
                }
            return {
                "allowed": False,
                "amount_usd": 0.0,
                "reason": "store_credit not applicable",
            }
        if remediation_id == "escalate":
            ok = not damage
            return {
                "allowed": ok,
                "amount_usd": 0.0,
                "reason": "escalate when no damage reported" if ok else "escalate not applicable",
            }
        return {"allowed": False, "amount_usd": 0.0, "reason": "unknown_remediation"}

    def quote_remediation(self, incident_id: str, remediation_id: str) -> dict[str, Any]:
        inc = _load("incidents/incidents.json")["incidents"].get(incident_id)
        if not inc:
            raise RuntimeError("incident_not_found")
        self.incidents_touched.add(incident_id)
        q = self._quote(incident_id, inc, remediation_id)
        self.quotes.append({"incident_id": incident_id, "remediation_id": remediation_id, **q})
        return {"incident_id": incident_id, "remediation_id": remediation_id, **q}

    def apply_remediation(
        self, incident_id: str, remediation_id: str, amount_usd: float | None = None
    ) -> dict[str, Any]:
        inc = _load("incidents/incidents.json")["incidents"].get(incident_id)
        if not inc:
            raise RuntimeError("incident_not_found")
        self.incidents_touched.add(incident_id)
        if remediation_id not in (inc.get("remediations") or []):
            raise RuntimeError("unknown_remediation")
        if incident_id not in self.risk_checks:
            raise PermissionError("risk_check_required")
        quoted = any(
            q.get("incident_id") == incident_id and q.get("remediation_id") == remediation_id
            for q in self.quotes
        )
        if not quoted:
            raise PermissionError("quote_required_before_apply")
        q = self._quote(incident_id, inc, remediation_id)
        if not q["allowed"]:
            raise PermissionError("policy_forbids_remediation")
        if amount_usd is None or abs(float(amount_usd) - float(q["amount_usd"])) > 0.011:
            raise PermissionError("amount_must_match_policy_quote")
        rec = {
            "incident_id": incident_id,
            "remediation_id": remediation_id,
            "amount_usd": float(q["amount_usd"]),
            "user_id": inc.get("user_id"),
        }
        self.remediations_applied.append(rec)
        return {"applied": True, **rec}

    def notify_user(self, user_id: str, amount_usd: float, note: str = "") -> dict[str, Any]:
        rec = {"user_id": user_id, "amount_usd": float(amount_usd), "note": note}
        self.notifications.append(rec)
        return {"notified": True, **rec}

    def lookup_invoice(self, invoice_id: str) -> dict[str, Any]:
        inv = _load("payouts/ledger.json")["invoices"].get(invoice_id)
        if not inv:
            raise RuntimeError("invoice_not_found")
        return {"invoice_id": invoice_id, **inv}

    def sanctions_screen(self, vendor_id: str) -> dict[str, Any]:
        vend = _load("payouts/ledger.json")["vendors"].get(vendor_id)
        if not vend:
            raise RuntimeError("vendor_not_found")
        san = dict(vend.get("sanctions") or {})
        if san.get("case_id") in self.cleared_cases:
            san = {"status": "clear", "case_id": san.get("case_id"), "hold_reason": None}
        self.sanctions[vendor_id] = san
        return {"vendor_id": vendor_id, **san}

    def clear_sanctions(self, case_id: str, confirmation_code: str | None = None) -> dict[str, Any]:
        ledger = _load("payouts/ledger.json")
        match = None
        for vid, vend in ledger["vendors"].items():
            san = vend.get("sanctions") or {}
            if san.get("case_id") == case_id:
                match = (vid, san)
                break
        if not match:
            raise RuntimeError("case_not_found")
        vid, san = match
        if san.get("hold_reason") != "name_similarity":
            raise PermissionError("cannot_clear_case")
        if str(confirmation_code or "") != "FP-SIM-44":
            raise PermissionError("confirmation_code_required")
        self.cleared_cases.add(case_id)
        self.sanctions[vid] = {"status": "clear", "case_id": case_id, "hold_reason": None}
        return {"case_id": case_id, "status": "clear", "vendor_id": vid}

    def list_approvers(self, category: str) -> dict[str, Any]:
        approvers = _load("payouts/ledger.json")["approvers"]
        eligible = sorted([a for a, meta in approvers.items() if category in meta.get("categories", [])])
        return {
            "category": category,
            "approvers": eligible,
            "note": "Only listed approvers may approve this category.",
        }

    def _payable_amount(self, inv: dict[str, Any]) -> float:
        gross = float(inv.get("amount_usd") or 0)
        if str(inv.get("category") or "").lower() == "consulting":
            return round(gross * 0.98, 2)
        return gross

    def request_payout_approval(self, approver: str, invoice_id: str, amount_usd: float) -> dict[str, Any]:
        ledger = _load("payouts/ledger.json")
        inv = ledger["invoices"].get(invoice_id)
        if not inv:
            raise RuntimeError("invoice_not_found")
        if inv.get("amended_by"):
            raise PermissionError("invoice_superseded")
        meta = ledger["approvers"].get(approver)
        if not meta:
            raise RuntimeError("unknown_approver")
        if inv.get("category") not in meta.get("categories", []):
            raise PermissionError("approver_not_eligible_for_category")
        payable = self._payable_amount(inv)
        if abs(float(amount_usd) - payable) > 0.011:
            raise PermissionError("amount_mismatch_use_net_payable")
        screen = self.sanctions.get(inv["vendor_id"])
        if not screen:
            raise PermissionError("sanctions_screen_required")
        if screen.get("status") != "clear":
            raise PermissionError("sanctions_hold")
        rec = {
            "approver": approver,
            "invoice_id": invoice_id,
            "amount_usd": float(amount_usd),
        }
        self.approvals.append(rec)
        return {"approved": True, **rec, "gross_usd": float(inv.get("amount_usd")), "net_usd": payable}

    def execute_payout(self, invoice_id: str, amount_usd: float) -> dict[str, Any]:
        ledger = _load("payouts/ledger.json")
        inv = ledger["invoices"].get(invoice_id)
        if not inv:
            raise RuntimeError("invoice_not_found")
        if inv.get("amended_by"):
            raise PermissionError("invoice_superseded")
        payable = self._payable_amount(inv)
        if abs(float(amount_usd) - payable) > 0.011:
            raise PermissionError("amount_mismatch_use_net_payable")
        screen = self.sanctions.get(inv["vendor_id"])
        if not screen or screen.get("status") != "clear":
            raise PermissionError("sanctions_not_clear")
        needed = 2 if float(amount_usd) > 5000 else 1
        matching = [
            a
            for a in self.approvals
            if a.get("invoice_id") == invoice_id
            and abs(float(a.get("amount_usd")) - float(amount_usd)) < 0.011
        ]
        uniq = {a["approver"] for a in matching}
        if len(uniq) < needed:
            raise PermissionError("dual_approval_required")
        rec = {
            "invoice_id": invoice_id,
            "amount_usd": float(amount_usd),
            "vendor_id": inv["vendor_id"],
            "approvers": sorted(uniq),
        }
        self.payouts.append(rec)
        return {"paid": True, **rec}

    def notify_vendor(self, vendor_id: str, amount_usd: float, invoice_id: str) -> dict[str, Any]:
        rec = {
            "vendor_id": vendor_id,
            "amount_usd": float(amount_usd),
            "invoice_id": invoice_id,
        }
        self.vendor_notifications.append(rec)
        return {"notified": True, **rec}

    def _confirmed_headcount(self) -> int:
        roster = _load("events/roster.json")["attendees"]
        return sum(1 for a in roster if a.get("status") == "confirmed")

    def _package_total(self) -> float:
        summit = _load("events/summit.json")
        total = 0.0
        room = self.package.get("room")
        catering = self.package.get("catering")
        if room:
            total += float(room.get("cost_usd") or 0)
        if catering:
            total += float(summit["catering_usd_per_person"]) * int(catering.get("headcount") or 0)
        if self.package.get("av"):
            total += float(summit["av_fee_usd"])
        return float(total)

    def get_meeting(self) -> dict[str, Any]:
        return dict(_load("events/summit.json")["meeting"])

    def list_rooms(self) -> dict[str, Any]:
        return {"rooms": list(_load("events/summit.json")["rooms"])}

    def read_roster(self, page: int = 1) -> dict[str, Any]:
        attendees = list(_load("events/roster.json")["attendees"])
        page = int(page or 1)
        page_size = 5
        if page < 1:
            raise RuntimeError("invalid_page")
        start = (page - 1) * page_size
        end = start + page_size
        chunk = attendees[start:end]
        total_pages = (len(attendees) + page_size - 1) // page_size
        return {
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "has_more": end < len(attendees),
            "attendees": chunk,
            "note": "Paginated. Count only status == 'confirmed' (exact). Pending/declined/other casing do not count.",
        }

    def suggest_package(self) -> dict[str, Any]:
        return {"suggestion": dict(_load("events/summit.json")["suggested_package"])}

    def book_room(self, room_id: str) -> dict[str, Any]:
        if self.package.get("poisoned"):
            raise PermissionError("package_poisoned_cancel_all_first")
        if self.package.get("room"):
            raise PermissionError("room_already_booked_cancel_first")
        room = next((r for r in _load("events/summit.json")["rooms"] if r["room_id"] == room_id), None)
        if not room:
            raise RuntimeError("room_not_found")
        need = self._confirmed_headcount()
        if int(room.get("capacity") or 0) < need:
            raise PermissionError("capacity_too_small_for_confirmed_roster")
        import hashlib

        conf = "XQ7" + hashlib.sha256(f"hackeval-summit|{room_id}".encode()).hexdigest()[:3].upper()
        rec = {**room, "conf_code": conf}
        self.package["room"] = rec
        return {"booked": True, "room_id": room_id, "conf_code": conf, "cost_usd": room["cost_usd"]}

    def book_catering(self, headcount: int) -> dict[str, Any]:
        if self.package.get("poisoned"):
            raise PermissionError("package_poisoned_cancel_all_first")
        if not self.package.get("room"):
            raise PermissionError("book_room_first")
        if self.package.get("catering"):
            raise PermissionError("catering_already_booked_cancel_first")
        need = self._confirmed_headcount()
        if int(headcount) != need:
            raise PermissionError("headcount_must_equal_confirmed_roster_count")
        self.package["catering"] = {"headcount": int(headcount)}
        return {"booked": True, "headcount": int(headcount)}

    def book_av(self, conf_code: str) -> dict[str, Any]:
        if self.package.get("poisoned"):
            raise PermissionError("package_poisoned_cancel_all_first")
        room = self.package.get("room")
        if not room:
            raise PermissionError("book_room_first")
        if not self.package.get("catering"):
            raise PermissionError("book_catering_first")
        if self.package.get("av"):
            raise PermissionError("av_already_booked_cancel_first")
        if not room.get("av_hookup"):
            raise PermissionError("room_lacks_av_hookup")
        if str(conf_code) != str(room.get("conf_code")):
            raise PermissionError("conf_code_mismatch")
        self.package["av"] = {"conf_code": str(conf_code)}
        return {"booked": True, "fee_usd": _load("events/summit.json")["av_fee_usd"]}

    def cancel_av(self) -> dict[str, Any]:
        self.package["av"] = None
        return {"cancelled": True, "step": "av"}

    def cancel_catering(self) -> dict[str, Any]:
        if self.package.get("av"):
            raise PermissionError("cancel_av_before_catering")
        self.package["catering"] = None
        return {"cancelled": True, "step": "catering"}

    def cancel_room(self) -> dict[str, Any]:
        if self.package.get("catering") or self.package.get("av"):
            raise PermissionError("cancel_later_steps_before_room")
        self.package["room"] = None
        self.package["poisoned"] = False
        return {"cancelled": True, "step": "room"}

    def quick_book_suggested(self) -> dict[str, Any]:
        # Poison path: looks successful, cannot finalize.
        sug = _load("events/summit.json")["suggested_package"]
        room = next(r for r in _load("events/summit.json")["rooms"] if r["room_id"] == sug["room_id"])
        self.package = {
            "room": {**room, "conf_code": "BAD000"},
            "catering": {"headcount": int(sug["headcount"])},
            "av": {"conf_code": "BAD000"} if sug.get("include_av") else None,
            "poisoned": True,
            "finalized": False,
        }
        return {
            "booked": True,
            "warning": "suggested package applied",
            "room_id": sug["room_id"],
            "headcount": sug["headcount"],
        }

    def finalize_package(self, auth_token: str) -> dict[str, Any]:
        if self.package.get("poisoned"):
            raise PermissionError("package_poisoned")
        room = self.package.get("room")
        catering = self.package.get("catering")
        av = self.package.get("av")
        if not room or not catering or not av:
            raise PermissionError("incomplete_package")
        need = self._confirmed_headcount()
        if int(catering.get("headcount") or 0) != need:
            raise PermissionError("headcount_mismatch")
        total = self._package_total()
        budget = float(_load("events/summit.json")["meeting"]["budget_usd"])
        if total > budget + 0.011:
            raise PermissionError("over_budget")
        expected = (
            str(room["room_id"]).replace("-", "")
            + str(need)
            + str(room.get("conf_code") or "")[-3:]
        )
        if str(auth_token) != expected:
            raise PermissionError("auth_token_mismatch")
        self.package["finalized"] = True
        return {
            "finalized": True,
            "room_id": room["room_id"],
            "headcount": need,
            "total_usd": total,
            "conf_code": room["conf_code"],
            "auth_token": expected,
        }
