<!-- PORTFOLIO-CONTEXT
Oluwajuwon Adediji | Data & Quantitative Analyst | Automation Engineering
Portfolio: https://oluwajuwonade.github.io
-->

# Productivity Systems Automation Engine

> **Engineering problem:** How can repeatable personal-workflow rules become executable, persistent software systems?

An executable implementation of ten productivity rules as modular Python components backed by SQLite persistence and a command-line interface.

## What it demonstrates

- Modular Python architecture
- Command-line interface design
- SQLite persistence
- Reusable functions
- Workflow automation
- State management
- Simple reporting logic
- Zero external Python dependencies

## System architecture

`CLI → Workflow modules → SQLite store → Reports / dashboards`

The system persists state in `~/.productivity_codes/productivity.db` and exposes the workflow through both CLI commands and a Python API.

## Included systems

1. Reverse drafting
2. Working-draft timeboxing
3. Context batching
4. AI delegation audit
5. Asset harvesting
6. Capture loop
7. Three-task day
8. Prompt chaining
9. Energy ledger
10. Weekly review

## Quick start

```bash
python3 test_codes.py
python3 -m secret_codes.cli status
```

Additional CLI examples and the Python API are documented in the source tree.

## Portfolio role

**Tier 3 — Automation & Systems Engineering**

This is a supporting engineering project rather than a primary analytics case study. Its value is demonstrating the ability to turn a workflow framework into executable, persistent software.

## Author

**Oluwajuwon Adediji**  
Data & Quantitative Analyst | Automation & Analytical Systems
