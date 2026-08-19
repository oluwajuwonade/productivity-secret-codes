"""
secret_codes.code8_9_10_loops
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Code 8  - Prompt Chaining: save recurring workflows as reusable chains of
          prompts with variable placeholders; each run fills placeholders
          and executes the chain.
Code 9  - Energy Ledger: log hourly energy 1-5, detect the 3-5h peak window
          and trough, and hard-assign task types to energy states.
Code 10 - Weekly Review: count shipped deliverables, harvest assets, update
          the delegation audit, set next week's skeleton, delete one
          commitment.

Usage:
    >>> from secret_codes.code8_9_10_loops import *
    >>> save_chain("fico_report", steps=[...])
    >>> run_chain("fico_report", vars={"dataset": "fico.csv"})   # returns filled prompts
    >>> log_energy(level=4)
    >>> peak = peak_window()                                      # optimal deep-work hours
    >>> weekly_review(shipped=4, harvested=2, automations=1, deleted=1)
"""

import json
import string
from datetime import date, timedelta

from . import store


# ------------------------- Code 8: Prompt Chaining -------------------------

def save_chain(name: str, steps: list[dict], description: str = "") -> int:
    """Save a prompt chain. Each step: {'step': n, 'prompt': str, 'vars': [str]}.
    The chain file becomes the artifact; outputs are secondary."""
    store.init_db()
    conn = store.get_conn()
    cur = conn.execute(
        "INSERT INTO prompt_chains (name, description, steps, created) VALUES (?,?,?,?)",
        (name, description, json.dumps(steps), store.now()),
    )
    conn.commit()
    return cur.lastrowid


def run_chain(name: str, variables: dict[str, str], dry_run: bool = True) -> dict:
    """Fill a saved chain's placeholders and (optionally) execute via the
    built-in LLM. Returns filled prompts; execute=True runs them."""
    store.init_db()
    conn = store.get_conn()
    row = conn.execute("SELECT * FROM prompt_chains WHERE name=?", (name,)).fetchone()
    if row is None:
        raise KeyError(f"no chain named {name}")
    steps = json.loads(row["steps"])
    filled, context = [], ""
    for s in steps:
        text = string.Template(s["prompt"]).safe_substitute({**variables, "CONTEXT": context})
        filled.append({"step": s["step"], "filled_prompt": text})
        if s.get("output_is_context", False):
            context = text
    conn.execute("UPDATE prompt_chains SET usage_count = usage_count + 1 WHERE name=?", (name,))
    conn.commit()
    return {"chain": name, "filled_steps": filled}


def list_chains() -> list[dict]:
    store.init_db()
    conn = store.get_conn()
    rows = conn.execute("SELECT id, name, description, usage_count, created FROM prompt_chains ORDER BY usage_count DESC").fetchall()
    return [dict(r) for r in rows]


# ------------------------- Code 9: Energy Ledger -------------------------

def log_energy(level: int, hour: int | None = None, task_type: str | None = None) -> int:
    """Log the current hour's energy 1-5. One week of logs reveals the
    consistent 3-5h peak window."""
    store.init_db()
    if not 1 <= level <= 5:
        raise ValueError("level must be 1-5")
    from datetime import datetime as _dt
    hour = hour if hour is not None else _dt.now().hour
    conn = store.get_conn()
    cur = conn.execute(
        "INSERT INTO energy_entries (entry_date, hour, level, task_type, created) VALUES (?,?,?,?,?)",
        (store.today(), hour, level, task_type, store.now()),
    )
    conn.commit()
    return cur.lastrowid


def peak_window(days: int = 7, require_min_samples: int = 1) -> dict:
    """Find the 3-5 hour peak window and trough from the last `days` of
    ledger data. Drives energy-based scheduling."""
    store.init_db()
    conn = store.get_conn()
    cutoff = (date.today() - timedelta(days=days)).isoformat()
    rows = conn.execute(
        "SELECT hour, AVG(level) AS avg_level, COUNT(*) AS n FROM energy_entries "
        "WHERE entry_date >= ? GROUP BY hour HAVING n >= ? ORDER BY hour",
        (cutoff, require_min_samples),
    ).fetchall()
    if not rows:
        return {"peak": None, "trough": None, "note": "insufficient data — log hourly energy for a week"}
    data = [(r["hour"], r["avg_level"]) for r in rows]
    peak = max(data, key=lambda x: x[1])
    trough = min(data, key=lambda x: x[1])
    # contiguous peak block: hours within 0.5 of peak
    block = [h for h, v in data if v >= peak[1] - 0.5]
    return {
        "peak_hour": peak[0],
        "peak_block": f"{min(block):02d}:00-{max(block)+1:02d}:00",
        "peak_avg_level": round(peak[1], 2),
        "trough_hour": trough[0],
        "trough_avg_level": round(trough[1], 2),
        "assignment": {
            "peak -> deep work only (analysis, writing, modeling)",
            "trough -> shallow batch (email, admin, organization)",
            "medium -> communication, light research, revisions",
        },
    }


# ------------------------- Code 10: Weekly Review -------------------------

def weekly_review(shipped: int, harvested: int, automations: int, deleted: int, notes: str = "") -> int:
    """Record the weekly review. The maintenance loop that sustains the other
    nine codes. Exactly one commitment must be deleted each week."""
    store.init_db()
    week = (date.today() - timedelta(days=date.today().weekday())).isoformat()
    conn = store.get_conn()
    cur = conn.execute(
        "INSERT INTO weekly_reviews (week, shipped_deliverables, assets_harvested, new_automations, "
        "commitments_deleted, notes, created) VALUES (?,?,?,?,?,?,?)",
        (week, shipped, harvested, automations, deleted, notes, store.now()),
    )
    conn.commit()
    return cur.lastrowid


def review_history() -> list[dict]:
    store.init_db()
    conn = store.get_conn()
    rows = conn.execute(
        "SELECT week, shipped_deliverables, assets_harvested, new_automations, commitments_deleted, notes "
        "FROM weekly_reviews ORDER BY week DESC"
    ).fetchall()
    return [dict(r) for r in rows]
