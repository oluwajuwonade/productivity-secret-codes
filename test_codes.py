"""
test_codes.py — End-to-end demonstration of all ten Productivity Secret Codes.

Run:  python test_codes.py
This exercises every code as real executable software and prints results.
"""

import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from secret_codes import store
from secret_codes.code1_2_skeleton import WorkingDraftTimer, parse_skeleton
from secret_codes.code3_6_context import build_day_schedule, capture, interleaving_leak, process_inbox
from secret_codes.code4_5_7_systems import audit, audit_report, asset_inventory, daily_status, harvest, set_daily_three
from secret_codes.code8_9_10_loops import list_chains, log_energy, peak_window, run_chain, save_chain, weekly_review
from secret_codes.dashboard import text_dashboard

STORE = os.path.expanduser("~/.productivity_codes")
if os.path.exists(STORE):
    shutil.rmtree(STORE)
os.makedirs(STORE)

print("#" * 60)
print(" PRODUCTIVITY SECRET CODES — FULL SYSTEM TEST")
print("#" * 60)

# ---- Code 6: capture ----
print("\n[Code 6] Two-Minute Capture Loop")
ids = [capture("Email vendor about API pricing"),
       capture("Analysis: segment new customer cohort by region"),
       capture("delete: old draft v1 — superseded")]
print(f"  captured {len(ids)} items into inbox")

# ---- Code 6: process ----
print("\n[Code 6] Inbox processing window")
print(f"  {process_inbox()}")

# ---- Code 1: reverse draft ----
print("\n[Code 1] Reverse Drafting — parse skeleton [VERIFY] tags")
task_id = 1
claims = parse_skeleton("demo_skeleton.md", task_id)
print(f"  extracted {len(claims)} [VERIFY] claims")

# ---- Code 2: working draft ----
print("\n[Code 2] 15-Minute Working Draft")
from pathlib import Path
draft_path = "/tmp/draft.md"
Path(draft_path).write_text("# Rough draft\n- structure only, not prose\n- [placeholder section 2]\n" * 5)
timer = WorkingDraftTimer()
res = timer.draft_accepted(draft_path)
print(f"  {res}")

# ---- Code 7: 3-task day ----
print("\n[Code 7] The 3-Task Day")
print(set_daily_three([
    ("Finish FICO segmentation report — main deliverable", "deliverable"),
    ("Read prompt engineering evaluation paper", "progress"),
    ("Extract reusable credit-risk template", "compounding"),
]))
print(f"  {daily_status()}")

# ---- Code 4: delegation audit ----
print("\n[Code 4] AI Delegation Audit")
audit("Transcribe client call recordings weekly", rule_based=True, error_tolerable=True, hours_saved_per_week=3.0)
audit("Format weekly client newsletter", rule_based=True, error_tolerable=False, hours_saved_per_week=1.5)
audit("Write quarterly strategy memo", rule_based=False, error_tolerable=False)
print(f"  {audit_report()}")

# ---- Code 5: harvest ----
print("\n[Code 5] Asset Harvest Ritual")
harvest("FICO segmentation", "template", "credit_risk_report_template", "Skeleton + verify-tag workflow")
harvest("FICO segmentation", "prompt", "segmentation_analysis_chain", "dataset -> clusters -> memo chain")
harvest("FICO segmentation", "product_idea", "risk_segmentation_scorecard", "Gumroad digital product candidate")
print(f"  {asset_inventory()['by_type']}")

# ---- Code 8: prompt chaining ----
print("\n[Code 8] Prompt Chaining")
save_chain("segmentation_report", description="dataset in -> memo out", steps=[
    {"step": 1, "prompt": "Load dataset $dataset and compute basic stats.", "vars": ["dataset"], "output_is_context": True},
    {"step": 2, "prompt": "Given this context: $CONTEXT — cluster into 3 risk tiers.", "vars": [], "output_is_context": True},
    {"step": 3, "prompt": "Given this context: $CONTEXT — write a 200-word client memo.", "vars": []},
])
filled = run_chain("segmentation_report", {"dataset": "fico_data.csv"})
print(f"  chain usage after run: {list_chains()[0]['usage_count']}")
print(f"  filled step 1: {filled['filled_steps'][0]['filled_prompt'][:60]}...")

# ---- Code 9: energy ledger ----
print("\n[Code 9] Energy Ledger")
import random
random.seed(42)
for hour in range(7, 21):
    level = 5 if 9 <= hour <= 11 else (2 if 13 <= hour <= 14 else random.choice([3, 4]))
    log_energy(level, hour=hour)
print(f"  {peak_window()}")

# ---- Code 3: schedule ----
print("\n[Code 3] Context-Batched Day Schedule")
sched = build_day_schedule()
for block in sched["blocks"]:
    print(f"  {block['time']} [{block['context']}] {block['open_tasks']} tasks")

# ---- Code 10: weekly review ----
print("\n[Code 10] Weekly Review")
weekly_review(shipped=4, harvested=3, automations=1, deleted=1, notes="Week 1 baseline")
print("  weekly review logged (shipped=4, harvested=3, automations=1, deleted=1)")

print("\n" + text_dashboard())
print("\nAll ten codes executed successfully.")
