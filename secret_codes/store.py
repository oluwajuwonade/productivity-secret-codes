"""
secret_codes.store
~~~~~~~~~~~~~~~~~~
Persistent storage layer for the Productivity Secret Codes system.

All data lives under ~/.productivity_codes/ as SQLite + JSON so the system
survives across sessions and requires zero external dependencies beyond
the Python standard library.

Entities:
  - tasks          : inbox items and the daily 3-task plan (Codes 6, 7)
  - verify_claims  : [VERIFY] claims from reverse-draft skeletons (Code 1)
  - assets         : harvested reusable assets (Code 5)
  - energy_entries : hourly energy ledger (Code 9)
  - delegations    : AI delegation audit log (Code 4)
  - prompt_chains  : saved prompt chains (Code 8)
  - weekly_reviews : weekly review records (Code 10)
"""

import json
import sqlite3
import threading
from datetime import date, datetime
from pathlib import Path

DB_DIR = Path.home() / ".productivity_codes"
DB_DIR.mkdir(exist_ok=True)
DB_PATH = DB_DIR / "productivity.db"

_local = threading.local()


def get_conn() -> sqlite3.Connection:
    conn = getattr(_local, "conn", None)
    if conn is None:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        _local.conn = conn
    return conn


SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    context TEXT NOT NULL CHECK (context IN ('deep','shallow','communication','learning')),
    kind TEXT CHECK (kind IN ('deliverable','progress','compounding','inbox')),
    status TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open','done')),
    verify_tags INTEGER NOT NULL DEFAULT 0,      -- open [VERIFY] tags (Code 1)
    verified INTEGER NOT NULL DEFAULT 0,         -- closed [VERIFY] tags
    hours_spent REAL NOT NULL DEFAULT 0,
    judgment_only INTEGER NOT NULL DEFAULT 0,    -- was this judgment-only work?
    created TEXT NOT NULL,
    done_at TEXT
);

CREATE TABLE IF NOT EXISTS verify_claims (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER REFERENCES tasks(id),
    claim TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open','closed','wrong')),
    created TEXT NOT NULL,
    closed_at TEXT
);

CREATE TABLE IF NOT EXISTS assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    asset_type TEXT NOT NULL CHECK (asset_type IN ('template','prompt','product_idea','content_idea','script')),
    description TEXT NOT NULL DEFAULT '',
    project TEXT NOT NULL DEFAULT '',
    file_path TEXT,
    created TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS energy_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_date TEXT NOT NULL,
    hour INTEGER NOT NULL,
    level INTEGER NOT NULL CHECK (level BETWEEN 1 AND 5),
    task_type TEXT,
    created TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS delegations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_description TEXT NOT NULL,
    rule_based INTEGER NOT NULL,          -- 0/1
    error_tolerable INTEGER NOT NULL,     -- 0/1
    decision TEXT NOT NULL CHECK (decision IN ('delegate','keep','automate')),
    status TEXT NOT NULL DEFAULT 'manual' CHECK (status IN ('manual','delegated','automated')),
    hours_saved_per_week REAL DEFAULT 0,
    reviewed TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS prompt_chains (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    steps TEXT NOT NULL,                  -- JSON array of {step, prompt, vars[]}
    usage_count INTEGER NOT NULL DEFAULT 0,
    created TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS weekly_reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    week TEXT NOT NULL,
    shipped_deliverables INTEGER NOT NULL DEFAULT 0,
    assets_harvested INTEGER NOT NULL DEFAULT 0,
    new_automations INTEGER NOT NULL DEFAULT 0,
    commitments_deleted INTEGER NOT NULL DEFAULT 0,
    notes TEXT NOT NULL DEFAULT '',
    created TEXT NOT NULL
);
"""


def init_db() -> None:
    conn = get_conn()
    conn.executescript(SCHEMA)
    conn.commit()


def today() -> str:
    return date.today().isoformat()


def now() -> str:
    return datetime.now().isoformat(timespec="seconds")
