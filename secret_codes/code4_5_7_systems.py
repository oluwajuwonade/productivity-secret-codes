"""
secret_codes.code4_5_7_systems
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Code 4 - AI Delegation Audit: triage every recurring task with two questions
         ("rule-based enough?" / "error cost tolerable?") and log decisions.
Code 5 - Asset Conversion / Harvest Ritual: end-of-project 10-minute harvest
         that converts work into templates, prompts, product ideas, content.
Code 7 - The 3-Task Day: enforce exactly three daily tasks — one deliverable,
         one progress, one compounding — with shipped-deliverable tracking.

Usage:
    >>> from secret_codes.code4_5_7_systems import *
    >>> audit("Transcribe meeting recordings weekly", rule_based=1, error_tolerable=1)
    >>> audit_report()
    >>> set_daily_three([("Finish FICO report", 'deliverable'), ("Read X", 'progress'), ("Template Y", 'compounding')])
    >>> harvest("FICO segmentation project", asset_type='template', name='credit_risk_template')
"""

from datetime import date

from . import store


# ------------------------- Code 4: AI Delegation Audit -------------------------

def audit(task_description: str, rule_based: bool, error_tolerable: bool,
          hours_saved_per_week: float = 0.0) -> dict:
    """Apply the two-question triage and log the decision."""
    store.init_db()
    conn = store.get_conn()
    rb, et = int(rule_based), int(error_tolerable)
    if rb and et:
        decision = "automate"
    elif rb:
        decision = "delegate"   # human review stays in the loop
    else:
        decision = "keep"
    cur = conn.execute(
        "INSERT INTO delegations (task_description, rule_based, error_tolerable, decision, "
        "hours_saved_per_week, reviewed) VALUES (?,?,?,?,?,?)",
        (task_description, rb, et, decision, hours_saved_per_week, store.today()),
    )
    conn.commit()
    return {"description": task_description, "rule_based": rb, "error_tolerable": et, "decision": decision, "row_id": cur.lastrowid}


def audit_report() -> dict:
    """Monthly delegation audit summary. Target: 70%+ of weekly hours on
    judgment-only tasks."""
    store.init_db()
    conn = store.get_conn()
    totals = conn.execute(
        "SELECT decision, COUNT(*) AS n, COALESCE(SUM(hours_saved_per_week),0) AS hrs "
        "FROM delegations GROUP BY decision"
    ).fetchall()
    all_tasks = conn.execute("SELECT COUNT(*) AS n, COALESCE(SUM(hours_saved_per_week),0) AS hrs FROM delegations").fetchone()
    judgment_rows = conn.execute(
        "SELECT COALESCE(SUM(hours_spent),0) AS jh, COUNT(*) AS jc FROM tasks WHERE judgment_only=1 AND status='done'"
    ).fetchone()
    total_task_hours = conn.execute("SELECT COALESCE(SUM(hours_spent),0) AS th FROM tasks WHERE status='done'").fetchone()
    jh = judgment_rows["jh"]; th = total_task_hours["th"]
    return {
        "by_decision": {r["decision"]: {"count": r["n"], "hours_saved_per_week": r["hrs"]} for r in totals},
        "total_reviewed": all_tasks["n"],
        "total_hours_automatable_per_week": all_tasks["hrs"],
        "judgment_only_fraction": round(jh / th, 2) if th else None,
        "target": 0.70,
    }


# ------------------------- Code 5: Asset Harvest Ritual -------------------------

HARVEST_QUESTIONS = [
    "What template can I extract from this?",
    "What prompt or script made this faster?",
    "Who else would pay for this result?",
    "What did I learn that is worth a post or article?",
]


def harvest(project: str, asset_type: str, name: str, description: str = "", file_path: str | None = None) -> int:
    """10-minute end-of-project harvest. Each project must leave at least one
    reusable asset — the bridge from hourly effort to scalable income."""
    store.init_db()
    conn = store.get_conn()
    cur = conn.execute(
        "INSERT INTO assets (name, asset_type, description, project, file_path, created) VALUES (?,?,?,?,?,?)",
        (name, asset_type, description, project, file_path, store.now()),
    )
    conn.commit()
    return cur.lastrowid


def asset_inventory() -> list[dict]:
    store.init_db()
    conn = store.get_conn()
    rows = conn.execute(
        "SELECT asset_type, COUNT(*) AS n FROM assets GROUP BY asset_type ORDER BY n DESC"
    ).fetchall()
    all_rows = conn.execute("SELECT id, name, asset_type, project, created FROM assets ORDER BY created DESC").fetchall()
    return {"by_type": {r["asset_type"]: r["n"] for r in rows}, "assets": [dict(r) for r in all_rows]}


# ------------------------- Code 7: The 3-Task Day -------------------------

def set_daily_three(tasks: list[tuple[str, str]]) -> dict:
    """Define exactly three tasks for today: one deliverable, one progress,
    one compounding. Constraint forces prioritization at planning time."""
    store.init_db()
    conn = store.get_conn()
    kinds = [t[1] for t in tasks]
    if len(tasks) != 3:
        raise ValueError(f"3-Task Day requires exactly 3 tasks, got {len(tasks)}")
    if sorted(kinds) != ["compounding", "deliverable", "progress"]:
        raise ValueError("Tasks must be exactly one each of: deliverable, progress, compounding")
    conn.execute("UPDATE tasks SET status='open' WHERE kind IN ('deliverable','progress','compounding') AND created >= ?", (store.today(),))
    created = []
    for title, kind in tasks:
        cur = conn.execute(
            "INSERT INTO tasks (title, context, kind, status, created) VALUES (?,?,?,'open',?)",
            (title, "deep" if kind == "deliverable" else ("shallow" if kind == "progress" else "learning"), kind, store.now()),
        )
        created.append({"title": title, "kind": kind, "id": cur.lastrowid})
    conn.commit()
    return {"date": store.today(), "tasks": created}


def daily_status() -> dict:
    """End-of-day metric: shipped deliverables, not hours worked."""
    store.init_db()
    conn = store.get_conn()
    today_str = store.today()
    today_rows = conn.execute(
        "SELECT kind, status, COALESCE(SUM(verify_tags),0) AS open_verify, COALESCE(SUM(verified),0) AS closed_verify "
        "FROM tasks WHERE created >= ? GROUP BY kind, status", (today_str,)
    ).fetchall()
    matrix = {}
    for r in today_rows:
        matrix.setdefault(r["kind"], {})[r["status"]] = {
            "count": r["kind"], "open_verify": r["open_verify"], "closed_verify": r["closed_verify"],
        }
    # count today's three
    rows = conn.execute(
        "SELECT title, kind, status FROM tasks WHERE created >= ? ORDER BY kind", (today_str,)
    ).fetchall()
    return {
        "date": today_str,
        "tasks": [dict(r) for r in rows],
        "shipped_deliverables": sum(1 for r in rows if r["kind"] == "deliverable" and r["status"] == "done"),
    }
