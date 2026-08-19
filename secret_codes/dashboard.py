"""
secret_codes.dashboard
~~~~~~~~~~~~~~~~~~~~~~
Daily dashboard aggregating all ten codes into a single status view.

Usage:
    >>> from secret_codes.dashboard import daily_dashboard, text_dashboard
    >>> print(text_dashboard())
"""

from . import store
from .code3_6_context import context_counts, inbox_items
from .code4_5_7_systems import asset_inventory, audit_report, daily_status
from .code8_9_10_loops import peak_window


def daily_dashboard() -> dict:
    """Aggregate view across all ten codes for today."""
    store.init_db()
    ds = daily_status()
    return {
        "code_1_2_reverse_draft": {
            "tasks_today": ds["tasks"],
            "shipped_deliverables": ds["shipped_deliverables"],
        },
        "code_3_context_batching": context_counts(),
        "code_4_delegation_audit": audit_report(),
        "code_5_asset_harvest": asset_inventory(),
        "code_6_inbox": {"open_items": len(inbox_items()), "items": inbox_items()[:10]},
        "code_7_three_task_day": ds,
        "code_9_energy": peak_window(),
    }


def text_dashboard() -> str:
    """Plain-text dashboard for terminal use."""
    d = daily_dashboard()
    lines = ["=" * 60, " PRODUCTIVITY SECRET CODES - DAILY DASHBOARD", "=" * 60]
    t = d["code_1_2_reverse_draft"]
    lines.append(f"\n[Code 1/2/7] Today: {len(t['tasks_today'])} tasks | {t['shipped_deliverables']} shipped deliverables")
    for tk in t["tasks_today"]:
        mark = "x" if tk["status"] == "done" else " "
        lines.append(f"   [{mark}] ({tk['kind']}) {tk['title']}")
    lines.append(f"\n[Code 3] Open tasks by context: {d['code_3_context_batching']}")
    i = d["code_6_inbox"]
    lines.append(f"\n[Code 6] Inbox: {i['open_items']} open item(s)")
    ar = d["code_4_delegation_audit"]
    lines.append(f"\n[Code 4] Delegation audit: {ar['total_reviewed']} tasks reviewed | "
                 f"{ar['total_hours_automatable_per_week']} hrs/wk automatable | "
                 f"judgment-only fraction: {ar['judgment_only_fraction']} (target >= 0.70)")
    inv = d["code_5_asset_harvest"]
    lines.append(f"\n[Code 5] Asset inventory: {inv['by_type']}")
    en = d["code_9_energy"]
    lines.append(f"\n[Code 9] Peak window: {en.get('peak_block')} (avg {en.get('peak_avg_level')}) | "
                 f"trough hour: {en.get('trough_hour')}")
    lines.append("\n" + "=" * 60)
    return "\n".join(lines)


if __name__ == "__main__":
    print(text_dashboard())
