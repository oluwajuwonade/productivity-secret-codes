<!-- PORTFOLIO-CONTEXT
Oluwajuwon Adediji | Data & Quantitative Analyst | Decision Intelligence | AI-Powered Analytics
Portfolio: https://oluwajuwonade.github.io
-->

> **Portfolio case study:** Workflow automation and analyst productivity engineering using a reproducible Python system.

# Productivity Secret Codes

An executable implementation of the ten productivity codes from the *Productivity Secret Codes* playbook. Each code is a real Python module callable from the command line or as a library, backed by a SQLite database that persists across sessions in `~/.productivity_codes/`. The system has **zero external dependencies** — it runs on the Python standard library alone.

## The Ten Codes

| # | Code | Module | CLI | Principle |
|---|---|---|---|---|
| 1 | Reverse Drafting | `code1_2_skeleton` | `skeleton`, `verify` | Write the output skeleton first, track `[VERIFY]` claims to closure |
| 2 | 15-Minute Working Draft | `code1_2_skeleton` | `draft` | Timebox the zero-to-one step; draft and edit are separate modes |
| 3 | Context Batching | `code3_6_context` | `schedule`, `contexts` | Block the day by context type; detect interleaving leaks |
| 4 | AI Delegation Audit | `code4_5_7_systems` | `audit` | Delegate rule-based, tolerable-error tasks; target 70% judgment-only hours |
| 5 | Asset Harvest | `code4_5_7_systems` | `harvest` | Every project leaves behind a template, prompt, or product idea |
| 6 | Capture Loop | `code3_6_context` | `capture`, `process` | Two-minute inbox capture; one daily processing window |
| 7 | 3-Task Day | `code4_5_7_systems` | `three`, `done` | Exactly three tasks: one deliverable, one progress, one compounding |
| 8 | Prompt Chaining | `code8_9_10_loops` | `chains` | Save recurring workflows as reusable prompt chains with variables |
| 9 | Energy Ledger | `code8_9_10_loops` | `energy`, `peak` | Log hourly energy; schedule deep work into the detected peak window |
| 10 | Weekly Review | `code8_9_10_loops` | `review` | Count shipped deliverables, harvest assets, delete one commitment |

## Quick Start

```bash
# Run the full end-to-end demo exercising all ten codes
python3 test_codes.py

# Daily dashboard aggregating all codes
python3 -m secret_codes.cli status

# Capture a thought in two minutes
python3 -m secret_codes.cli capture "Email client about revised timeline"

# Process the inbox in the fixed daily window (16:45)
python3 -m secret_codes.cli process

# Set today's three tasks
python3 -m secret_codes.cli three "Finish report|deliverable" "Read paper|progress" "Extract template|compounding"

# Mark a task done (log hours and whether it was judgment-only)
python3 -m secret_codes.cli done 1 --hours 2.5 --judgment

# Log this hour's energy level (1-5)
python3 -m secret_codes.cli energy 4

# Find your peak deep-work window from the ledger
python3 -m secret_codes.cli peak

# End-of-project harvest
python3 -m secret_codes.cli harvest "Project Name" --type template --name report_skeleton --description "..."

# AI delegation triage
python3 -m secret_codes.cli audit "Transcribe call recordings" --rule-based --tolerable --hours 3
python3 -m secret_codes.cli audit --report   # monthly audit vs 70% target

# Log the weekly review (default: delete one commitment)
python3 -m secret_codes.cli review --shipped 4 --harvested 2 --automations 1

# Extract [VERIFY] tags from a skeleton file (task_id = created task)
python3 -m secret_codes.cli skeleton demo_skeleton.md 1
python3 -m secret_codes.cli verify 1 3       # close claim 3
python3 -m secret_codes.cli verify 1 --progress   # completion rate
```

## Python API

```python
from secret_codes.code3_6_context import capture, build_day_schedule
from secret_codes.code4_5_7_systems import set_daily_three, harvest
from secret_codes.code8_9_10_loops import log_energy, peak_window, save_chain, run_chain

set_daily_three([
    ("Finish FICO segmentation report", "deliverable"),
    ("Read evaluation framework paper", "progress"),
    ("Extract report template", "compounding"),
])

capture("Email client about revised timeline")
log_energy(4)
harvest("FICO project", "template", "risk_report_skeleton")
print(peak_window())

save_chain("report", steps=[
    {"step": 1, "prompt": "Load dataset $dataset and compute stats.",
     "vars": ["dataset"], "output_is_context": True},
    {"step": 2, "prompt": "Given this context: $CONTEXT — write a client memo.",
     "vars": []},
])
print(run_chain("report", {"dataset": "data.csv"}))
```

## Recommended Daily Operating Sequence

| Time | Command | Code |
|---|---|---|
| First 15 min | Write skeleton, run `skeleton` to extract claims | 1 |
| Morning | `three` then execute the deep block | 7, 3 |
| Hourly | `energy <level>` | 9 |
| 16:45 | `process` — inbox sweep | 6 |
| End of project | `harvest` | 5 |
| Weekly | `review --shipped ... --deleted 1` | 10 |
| Anytime | `status` for the full dashboard | all |

## Architecture

All state persists in `~/.productivity_codes/productivity.db` (SQLite, WAL mode), so the system survives across sessions and composes naturally with cron or scheduled agents — e.g., a scheduled agent that runs `process` at 16:45 daily and `review` every Friday. Each code embeds its playbook metric as a real function: `verify_progress()` reports `[VERIFY]` completion rate, `audit_report()` computes the judgment-only fraction against the 0.70 target, `daily_status()` counts shipped deliverables, and `interleaving_leak()` quantifies context switching.

```
secret_codes/
├── __init__.py
├── store.py              # SQLite schema + persistence
├── code1_2_skeleton.py   # Codes 1–2: reverse drafting, working draft timer
├── code3_6_context.py    # Codes 3, 6: context batching, capture loop
├── code4_5_7_systems.py  # Codes 4–5, 7: delegation audit, harvest, 3-task day
├── code8_9_10_loops.py   # Codes 8–10: prompt chains, energy ledger, weekly review
├── cli.py                # Command-line interface
└── dashboard.py          # Daily aggregated dashboard
```

## Requirements

Python 3.11+ (standard library only). No pip packages needed.
