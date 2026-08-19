"""
secret_codes - The Productivity Secret Codes system.

Ten codes from the playbook, each implemented as executable software:

  Code 1  : Reverse Drafting        -> code1_2_skeleton.parse_skeleton / verify_progress
  Code 2  : 15-Minute Working Draft -> code1_2_skeleton.WorkingDraftTimer
  Code 3  : Context Batching        -> code3_6_context.build_day_schedule / interleaving_leak
  Code 4  : AI Delegation Audit     -> code4_5_7_systems.audit / audit_report
  Code 5  : Asset Harvest           -> code4_5_7_systems.harvest / asset_inventory
  Code 6  : Capture Loop            -> code3_6_context.capture / process_inbox
  Code 7  : 3-Task Day              -> code4_5_7_systems.set_daily_three / daily_status
  Code 8  : Prompt Chaining         -> code8_9_10_loops.save_chain / run_chain
  Code 9  : Energy Ledger           -> code8_9_10_loops.log_energy / peak_window
  Code 10 : Weekly Review           -> code8_9_10_loops.weekly_review / review_history

CLI entry point: python -m secret_codes.cli
Dashboard:       python -m secret_codes.dashboard
"""

from . import store  # noqa: F401 - ensures schema is importable
