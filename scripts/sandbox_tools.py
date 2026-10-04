"""Minimal deterministic sandbox tools for the six evaluation tasks."""
from __future__ import annotations

import inspect
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / "fixtures"


def _load(rel: str) -> dict[str, Any]:
    with (FIX / rel).open(encoding="utf-8") as f:
        return json.load(f)


class Sandbox:
    def __init__(self) -> None:
        self.memory = deepcopy(_load("memory/seed.json").get("users", {}))
        self.tickets: list[dict[str, Any]] = []
        self.calendar: list[dict[str, Any]] = []
        self.workflow = {"looked_up": False, "approved": False, "executions": [], "approvals": 0}
        self.agent_messages: list[dict[str, Any]] = []
        self.fetched_urls: set[str] = set()
        self.calls: list[dict[str, Any]] = []

    def call(self, name: str, args: dict[str, Any] | None = None) -> dict[str, Any]:
        args = args or {}
        fn = getattr(self, name, None)
        if fn is None:
            rec = {"name": name, "arguments": args, "error": "unknown_tool"}
            self.calls.append(rec)
            return {"ok": False, "error": "unknown_tool"}
        try:
            sig = inspect.signature(fn)
            # Drop unexpected kwargs so models can pass extra fields without hard-failing the tool.
            if any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values()):
                filtered = args
            else:
                allowed = {
                    k
                    for k, p in sig.parameters.items()
                    if p.kind in (inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.KEYWORD_ONLY)
                }
                filtered = {k: v for k, v in args.items() if k in allowed}
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

    def find_ticket(self, title: str) -> dict[str, Any]:
        return {"matches": [t for t in self.tickets if t.get("title") == title]}

    def create_ticket(
        self, title: str, due: str, owner: str, actor: str, note_id: str | None = None
    ) -> dict[str, Any]:
        notes = _load("notes/meetings.json")["notes"]
        if note_id and notes.get(note_id, {}).get("authorized_writer") != actor:
            raise PermissionError("unauthorized")
        existing = [t for t in self.tickets if t.get("title") == title]
        if existing:
            return {"duplicate": True, "ticket": existing[0]}
        ticket = {"title": title, "due": due, "owner": owner, "actor": actor}
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
        notes = _load("notes/meetings.json")["notes"]
        if note_id and notes.get(note_id, {}).get("authorized_writer") != actor:
            raise PermissionError("unauthorized")
        entry = {"date": date, "start": start, "end": end, "tz": tz, "title": title, "actor": actor}
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

    def message_agent(self, agent_id: str, message: dict[str, Any]) -> dict[str, Any]:
        required = ["date", "start", "end", "tz", "with"]
        ok = agent_id == "agent_scheduler" and all(k in message for k in required)
        msg = {
            "agent_id": agent_id,
            "message": message,
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
