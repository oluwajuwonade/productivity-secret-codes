"""
secret_codes.code1_2_skeleton
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Code 1 - Reverse Drafting: write the output skeleton first, extract [VERIFY]
         claims, then track verification progress as the analysis fills gaps.
Code 2 - 15-Minute Working Draft: timebox the zero-to-one step and enforce
         a strict draft-vs-edit separation.

Usage:
    >>> from secret_codes.code1_2_skeleton import *
    >>> parse_skeleton("report_skeleton.md", task_id=1)   # extracts [VERIFY] tags
    >>> close_verify_task(task_id=1, claim_id=3)          # mark a claim verified
    >>> stats = verify_progress(task_id=1)                # open vs closed ratio
"""

import re
from pathlib import Path

from . import store

VERIFY_PATTERN = re.compile(r"\[VERIFY\]\s*:?\s*(.+?)(?:\s*\[(?:VERIFY|DONE|WRONG)\])?\s*$", re.IGNORECASE)
VERIFY_MARKER = "[VERIFY]"


def parse_skeleton(filepath: str, task_id: int) -> list[dict]:
    """Extract every [VERIFY] claim from a pre-written skeleton file and store
    them as verification tasks attached to `task_id`.

    Returns the list of stored claims (each with id, claim text).
    """
    store.init_db()
    text = Path(filepath).read_text(encoding="utf-8")

    claims = []
    for lineno, line in enumerate(text.splitlines(), 1):
        m = VERIFY_PATTERN.search(line)
        if m:
            claim = m.group(1).strip()
            claims.append({"task_id": task_id, "claim": claim, "line": lineno})

    conn = store.get_conn()
    created = store.now()
    for c in claims:
        conn.execute(
            "INSERT INTO verify_claims (task_id, claim, status, created) VALUES (?, ?, 'open', ?)",
            (c["task_id"], c["claim"], created),
        )
    # update the task's open verify count
    conn.execute(
        "UPDATE tasks SET verify_tags = (SELECT COUNT(*) FROM verify_claims WHERE task_id=? AND status='open') WHERE id=?",
        (task_id, task_id),
    )
    conn.commit()
    return claims


def close_verify_task(task_id: int, claim_id: int, wrong: bool = False) -> dict:
    """Close a [VERIFY] claim. If the placeholder turned out wrong, mark
    'wrong' — that is a hypothesis that accelerated understanding (Code 1)."""
    store.init_db()
    conn = store.get_conn()
    status = "wrong" if wrong else "closed"
    conn.execute(
        "UPDATE verify_claims SET status=?, closed_at=? WHERE id=? AND task_id=?",
        (status, store.now(), claim_id, task_id),
    )
    conn.execute(
        "UPDATE tasks SET verified = (SELECT COUNT(*) FROM verify_claims WHERE task_id=? AND status IN ('closed','wrong')), "
        "verify_tags = (SELECT COUNT(*) FROM verify_claims WHERE task_id=? AND status='open') WHERE id=?",
        (task_id, task_id, task_id),
    )
    conn.commit()
    return {"claim_id": claim_id, "status": status}


def verify_progress(task_id: int) -> dict:
    """Completion rate of a skeleton-driven session. Target: close VERIFY
    items at 3-5x the rate of exploratory work (Code 1 metric)."""
    store.init_db()
    conn = store.get_conn()
    row = conn.execute(
        "SELECT COUNT(*) AS total, "
        "SUM(CASE WHEN status='open' THEN 1 ELSE 0 END) AS open_, "
        "SUM(CASE WHEN status='closed' THEN 1 ELSE 0 END) AS closed_, "
        "SUM(CASE WHEN status='wrong' THEN 1 ELSE 0 END) AS wrong_ "
        "FROM verify_claims WHERE task_id=?",
        (task_id,),
    ).fetchone()
    total = row["total"] or 0
    pct = (row["closed_"] + row["wrong_"]) / total * 100 if total else 0.0
    return {
        "task_id": task_id,
        "total_claims": total,
        "open": row["open_"],
        "closed": row["closed_"],
        "wrong_hypotheses": row["wrong_"],
        "completion_pct": round(pct, 1),
    }


# ------------------------- Code 2: 15-Minute Working Draft -------------------------

class WorkingDraftTimer:
    """Enforce the 15-minute rough-draft rule. Start immediately on task
    start; stop the moment the draft exists — no editing yet."""

    WINDOW_MINUTES = 15

    def __init__(self) -> None:
        import time
        self._start = time.time()

    def elapsed_minutes(self) -> float:
        import time
        return (time.time() - self._start) / 60.0

    def is_within_window(self) -> bool:
        return self.elapsed_minutes() < self.WINDOW_MINUTES

    def remaining_seconds(self) -> int:
        return max(0, int((self.WINDOW_MINUTES * 60) - self.elapsed_minutes() * 60))

    def draft_accepted(self, draft_path: str) -> dict:
        """Accept a rough draft. Validates the core rule: draft must exist
        and be non-trivial (>= 50 chars) before the window closes."""
        p = Path(draft_path)
        size = p.stat().st_size if p.exists() else 0
        within = self.is_within_window()
        return {
            "draft_file": str(p),
            "chars": size,
            "accepted": p.exists() and size >= 50,
            "within_15_minutes": within,
            "rule_violated": not within and size > 0,
            "elapsed_minutes": round(self.elapsed_minutes(), 1),
        }


DRAFT_RULES = {
    "1": "Draft must exist within 15 minutes of starting, even if ugly",
    "2": "Never edit while drafting — drafting and editing are separate modes",
    "3": "First iteration targets structure (skeleton), not prose",
    "4": "Define 'done' before starting: 'Finished when X exists'",
}
