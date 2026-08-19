"""
secret_codes.cli
~~~~~~~~~~~~~~~~
Command-line interface for the Productivity Secret Codes system.

Usage:
    python -m secret_codes.cli capture "Call client about Q3 numbers"
    python -m secret_codes.cli process          # daily inbox processing window (16:45)
    python -m secret_codes.cli three "Finish FICO report|deliverable" "Read prompt eng paper|progress" "Extract template|compounding"
    python -m secret_codes.cli done 1           # mark task done (hours optional: --hours 2.5 --judgment)
    python -m secret_codes.cli audit "Transcribe meetings weekly" --rule-based --tolerable --hours 3
    python -m secret_codes.cli energy 4         # log current hour's energy level
    python -m secret_codes.cli harvest "FICO project" --type template --name fico_report_template
    python -m secret_codes.cli schedule         # build today's blocked schedule
    python -m secret_codes.cli peak             # show energy peak window (Code 9)
    python -m secret_codes.cli review --shipped 4 --harvested 2 --automations 1 --deleted 1
    python -m secret_codes.cli status           # daily dashboard
"""

import argparse
import json
import sys

from . import store
from .code1_2_skeleton import WorkingDraftTimer, parse_skeleton, verify_progress
from .code3_6_context import build_day_schedule, capture, context_counts, process_inbox
from .code4_5_7_systems import audit, audit_report, daily_status, harvest, set_daily_three
from .code8_9_10_loops import list_chains, log_energy, peak_window, review_history, weekly_review


def _out(obj: object) -> None:
    print(json.dumps(obj, indent=2, default=str))


def main() -> None:
    p = argparse.ArgumentParser(prog="secret-codes", description="Productivity Secret Codes CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    # Code 6: capture
    c = sub.add_parser("capture", help="2-minute inbox capture (Code 6)")
    c.add_argument("text")

    # Code 6: process inbox
    sub.add_parser("process", help="Process inbox in the daily window (Code 6)")

    # Code 7: 3-task day
    t = sub.add_parser("three", help="Set exactly 3 tasks: title|kind x3 (Code 7)")
    t.add_argument("tasks", nargs=3, help="title|deliverable|progress|compounding")

    # mark done
    d = sub.add_parser("done", help="Mark task done")
    d.add_argument("task_id", type=int)
    d.add_argument("--hours", type=float, default=0.0)
    d.add_argument("--judgment", action="store_true", help="this was judgment-only work (Code 4 metric)")

    # Code 4: delegation audit
    a = sub.add_parser("audit", help="AI delegation triage (Code 4)")
    a.add_argument("description")
    a.add_argument("--rule-based", action="store_true")
    a.add_argument("--tolerable", action="store_true", help="error cost tolerable")
    a.add_argument("--hours", type=float, default=0.0, help="hours/week this task consumes")
    a.add_argument("--report", action="store_true", help="show monthly audit report")

    # Code 9: energy
    e = sub.add_parser("energy", help="Log energy level 1-5 for current hour (Code 9)")
    e.add_argument("level", type=int, choices=range(1, 6))
    subp = sub.add_parser("peak", help="Show energy peak window (Code 9)")

    # Code 5: harvest
    h = sub.add_parser("harvest", help="End-of-project asset harvest (Code 5)")
    h.add_argument("project")
    h.add_argument("--type", required=True, choices=["template", "prompt", "product_idea", "content_idea", "script"])
    h.add_argument("--name", required=True)
    h.add_argument("--description", default="")

    # Code 3: schedule
    sub.add_parser("schedule", help="Build today's context-blocked schedule (Code 3)")
    sub.add_parser("contexts", help="Open task counts by context (Code 3)")

    # Code 1: skeleton + verify
    s = sub.add_parser("skeleton", help="Parse [VERIFY] tags from a skeleton file (Code 1)")
    s.add_argument("file")
    s.add_argument("task_id", type=int)
    v = sub.add_parser("verify", help="Close a [VERIFY] claim (Code 1)")
    v.add_argument("task_id", type=int)
    v.add_argument("claim_id", type=int)
    v.add_argument("--wrong", action="store_true")
    v.add_argument("--progress", action="store_true", help="show verify progress")

    # Code 2: draft timer
    sub.add_parser("draft", help="Start the 15-minute working draft timer (Code 2)")

    # Code 10: weekly review
    r = sub.add_parser("review", help="Log weekly review (Code 10)")
    r.add_argument("--shipped", type=int, default=0)
    r.add_argument("--harvested", type=int, default=0)
    r.add_argument("--automations", type=int, default=0)
    r.add_argument("--deleted", type=int, default=1, help="delete one commitment every week")
    r.add_argument("--notes", default="")
    r.add_argument("--history", action="store_true", help="show review history")

    # dashboard
    sub.add_parser("status", help="Daily dashboard: all codes at a glance")

    # chains
    l = sub.add_parser("chains", help="List saved prompt chains (Code 8)")

    args = p.parse_args()

    try:
        if args.cmd == "capture":
            _out({"captured": capture(args.text)})
        elif args.cmd == "process":
            _out(process_inbox())
        elif args.cmd == "three":
            parsed = []
            for spec in args.tasks:
                title, kind = spec.rsplit("|", 1)
                parsed.append((title, kind))
            _out(set_daily_three(parsed))
        elif args.cmd == "done":
            store.init_db()
            conn = store.get_conn()
            conn.execute(
                "UPDATE tasks SET status='done', done_at=?, hours_spent=?, judgment_only=? WHERE id=?",
                (store.now(), args.hours, int(args.judgment), args.task_id),
            )
            conn.commit()
            _out({"task_id": args.task_id, "status": "done"})
        elif args.cmd == "audit":
            if args.report:
                _out(audit_report())
            else:
                _out(audit(args.description, args.rule_based, args.tolerable, args.hours))
        elif args.cmd == "energy":
            _out({"logged": log_energy(args.level)})
        elif args.cmd == "peak":
            _out(peak_window())
        elif args.cmd == "harvest":
            _out({"asset_id": harvest(args.project, args.type, args.name, args.description)})
        elif args.cmd == "schedule":
            _out(build_day_schedule())
        elif args.cmd == "contexts":
            _out(context_counts())
        elif args.cmd == "skeleton":
            _out({"claims": parse_skeleton(args.file, args.task_id)})
        elif args.cmd == "verify":
            if args.progress:
                _out(verify_progress(args.task_id))
            else:
                _out({"claim_id": args.claim_id, **verify_progress(args.task_id)})
        elif args.cmd == "draft":
            _out({"message": "15-minute working draft timer started. Draft and accept with code: "
                             "from secret_codes.code1_2_skeleton import WorkingDraftTimer; "
                             "WorkingDraftTimer().draft_accepted('path')",
                  "rules": ["15 min max", "no editing while drafting", "structure first", "define done first"]})
        elif args.cmd == "review":
            if args.history:
                _out(review_history())
            else:
                _out({"review_id": weekly_review(args.shipped, args.harvested, args.automations, args.deleted, args.notes)})
        elif args.cmd == "status":
            from .dashboard import daily_dashboard
            _out(daily_dashboard())
        elif args.cmd == "chains":
            _out(list_chains())
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
