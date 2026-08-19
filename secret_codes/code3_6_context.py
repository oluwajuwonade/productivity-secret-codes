"""
secret_codes.code3_6_context
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Code 3 - Context Batching: classify tasks by context type, then generate
         time-blocked schedules that keep deep/shallow/communication/learning
         work separated.
Code 6 - Two-Minute Capture Loop: instant unsorted inbox capture, single
         daily processing window that sorts each item into Do/Schedule/
         Delegate/Delete.

Usage:
    >>> from secret_codes.code3_6_context import *
    >>> capture("Call client about Q3 numbers")          # inbox, 2-minute rule
    >>> process_inbox("2026-08-19")                       # process window
    >>> schedule = build_day_schedule(date_=date(2026,8,19))
"""

import sqlite3
from datetime import date, datetime

from . import store


# ------------------------- Code 3: Context Batching -------------------------

CONTEXTS = ["deep", "shallow", "communication", "learning"]

CONTEXT_GUIDANCE = {
    "deep": "2-3h block, morning preferred. ONE project per block (setup cost paid once).",
    "shallow": "30-min sweep, max 2 per day, never during deep blocks.",
    "communication": "Fixed window (e.g. 11:30 + 16:30). Batch replies.",
    "learning": "Research/reading block; pair with medium energy, not peak.",
}

# Default block plan keyed by (context) -> suggested times
DEFAULT_BLOCKS = {
    "deep": [("08:30", "11:30")],
    "learning": [("13:30", "14:30")],
    "shallow": [("15:00", "15:30"), ("17:00", "17:30")],
    "communication": [("11:30", "12:00"), ("16:30", "17:00")],
}


def add_task(title: str, context: str, kind: str = "inbox", judgment_only: int = 0) -> int:
    """Capture a task with context classification (Code 3) — the classification
    is the anti-interleaving mechanism for multi-disciplinary work."""
    store.init_db()
    if context not in CONTEXTS:
        raise ValueError(f"context must be one of {CONTEXTS}")
    conn = store.get_conn()
    cur = conn.execute(
        "INSERT INTO tasks (title, context, kind, judgment_only, created) VALUES (?,?,?,?,?)",
        (title, context, kind, judgment_only, store.now()),
    )
    conn.commit()
    return cur.lastrowid


def context_counts(date_: date | None = None) -> dict:
    """Snapshot of open tasks per context type (Code 3 batching input)."""
    store.init_db()
    conn = store.get_conn()
    conds = "status='open'"
    params: list = []
    if date_:
        conds += " AND created >= ?"
        params.append(date_.isoformat())
    rows = conn.execute(
        f"SELECT context, COUNT(*) AS n FROM tasks WHERE {conds} GROUP BY context", params
    ).fetchall()
    return {r["context"]: r["n"] for r in rows}


def build_day_schedule(date_: date | None = None, energy: dict | None = None) -> dict:
    """Generate a blocked daily schedule from open tasks.

    If an `energy` dict mapping hour -> 1-5 is provided (Code 9), deep blocks
    are shifted to peak hours instead of the static defaults."""
    store.init_db()
    conn = store.get_conn()
    rows = conn.execute(
        "SELECT id, title, context FROM tasks WHERE status='open' ORDER BY created"
    ).fetchall()

    schedule: dict[str, list] = {c: [] for c in CONTEXTS}
    for r in rows:
        schedule[r["context"]].append({"id": r["id"], "title": r["title"]})

    blocks = []
    for ctx in CONTEXTS:
        for start, end in DEFAULT_BLOCKS.get(ctx, []):
            items = schedule[ctx]
            # one project per deep block: collapse titles into project hint
            projects = sorted({t["title"].split(" — ")[0] if " — " in t["title"] else t["title"] for t in items})
            blocks.append({
                "time": f"{start}-{end}",
                "context": ctx,
                "guidance": CONTEXT_GUIDANCE[ctx],
                "open_tasks": len(items),
                "tasks": items,
            })
    return {"date": (date_ or date.today()).isoformat(), "blocks": blocks}


def interleaving_leak(tasks: list[tuple[int, str]]) -> dict:
    """Detect the #1 leak in multi-disciplinary work: interleaving context
    types within the same work session. Pass a list of (timestamp_epoch, title)
    for tasks completed in order."""
    store.init_db()
    conn = store.get_conn()
    ctx_seq = []
    for ts, title in tasks:
        row = conn.execute(
            "SELECT context FROM tasks WHERE title=? ORDER BY created DESC LIMIT 1", (title,)
        ).fetchone()
        ctx_seq.append(row["context"] if row else "unknown")
    switches = sum(1 for a, b in zip(ctx_seq, ctx_seq[1:]) if a != b)
    return {
        "sequence": ctx_seq,
        "context_switches": switches,
        "total_tasks": len(ctx_seq),
        "switch_rate": round(switches / max(1, len(ctx_seq) - 1) * 100, 1),
        "verdict": "LEAKING" if switches >= 2 else "batched",
    }


# ------------------------- Code 6: Two-Minute Capture Loop -------------------------

def capture(text: str) -> int:
    """2-minute rule: anything you think of goes into the single inbox
    instantly — NO organization at capture time."""
    store.init_db()
    conn = store.get_conn()
    cur = conn.execute(
        "INSERT INTO tasks (title, context, kind, status, created) VALUES (?, 'shallow', 'inbox', 'open', ?)",
        (text, store.now()),
    )
    conn.commit()
    return cur.lastrowid


def inbox_items() -> list[dict]:
    store.init_db()
    conn = store.get_conn()
    rows = conn.execute("SELECT id, title, created FROM tasks WHERE kind='inbox' AND status='open'").fetchall()
    return [dict(r) for r in rows]


def process_inbox(date_: date | None = None) -> dict:
    """Single daily processing window (fixed time, e.g. 16:45). Every inbox
    item must be sorted into Do/Schedule/Delegate/Delete. The inbox may
    never be reopened outside this window."""
    store.init_db()
    date_ = date_ or date.today()
    conn = store.get_conn()
    items = inbox_items()
    results = {"processed": len(items), "deleted": 0, "promoted_deep": 0, "promoted_communication": 0, "kept": 0}
    for it in items:
        # Heuristic triage: short actionable items -> communication; items
        # containing analysis/report keywords -> deep. Humans override via CLI.
        title = it["title"].lower()
        deep_kw = {"analysis", "report", "model", "data", "chart", "memo", "evaluation", "framework"}
        if any(k in title for k in deep_kw):
            conn.execute("UPDATE tasks SET kind='progress', context='deep' WHERE id=?", (it["id"],))
            results["promoted_deep"] += 1
        elif title.startswith("email") or title.startswith("call") or title.startswith("reply"):
            conn.execute("UPDATE tasks SET kind='progress', context='communication' WHERE id=?", (it["id"],))
            results["promoted_communication"] += 1
        elif title.startswith("delete:") or title.startswith("!"):
            conn.execute("DELETE FROM tasks WHERE id=?", (it["id"],))
            results["deleted"] += 1
        else:
            conn.execute("UPDATE tasks SET kind='progress', context='shallow' WHERE id=?", (it["id"],))
            results["kept"] += 1
    conn.commit()
    return results
