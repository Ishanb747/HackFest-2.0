"""
db.py — Unified SQLite state persistent for RuleCheck.

Replaces the scattered JSON files. Contains tables for:
- rules
- violations
- explanations
- hitl_decisions
- audit_log
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

from config import SQLITE_DB_PATH

# Ensure data dir exists
SQLITE_DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(str(SQLITE_DB_PATH))
    conn.row_factory = sqlite3.Row
    
    # ── Schema Initialization ───────────────────────────────────────────────
    
    # Audit log (immutable)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            ts           TEXT    NOT NULL,
            phase        TEXT    NOT NULL,
            event_type   TEXT    NOT NULL,
            rule_id      TEXT,
            details_json TEXT
        )
    """)
    
    # Policy Rules
    conn.execute("""
        CREATE TABLE IF NOT EXISTS rules (
            id              TEXT PRIMARY KEY,
            rule_type       TEXT,
            description     TEXT,
            condition_field TEXT,
            operator        TEXT,
            threshold_value TEXT,
            sql_hint        TEXT,
            fingerprint     TEXT UNIQUE
        )
    """)
    
    # Violations (overwritten each Run)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS violations (
            rule_id          TEXT PRIMARY KEY,
            rule_description TEXT,
            sql              TEXT,
            violation_count  INTEGER,
            sample_json      TEXT,
            status           TEXT,
            reason           TEXT
        )
    """)
    
    # Violations (live run, overwritten each Run)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS violations_live (
            rule_id          TEXT PRIMARY KEY,
            rule_description TEXT,
            sql              TEXT,
            violation_count  INTEGER,
            sample_json      TEXT,
            status           TEXT,
            reason           TEXT
        )
    """)
    
    # Explanations (Phase 3)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS explanations (
            rule_id            TEXT PRIMARY KEY,
            alert_headline     TEXT,
            plain_english      TEXT,
            risk_level         TEXT,
            violation_count    INTEGER,
            recommended_action TEXT,
            policy_reference   TEXT,
            generated_by       TEXT
        )
    """)
    
    # HITL Decisions (Analyst approvals/dismissals)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS hitl_decisions (
            rule_id   TEXT PRIMARY KEY,
            action    TEXT NOT NULL,
            analyst   TEXT,
            notes     TEXT,
            timestamp TEXT NOT NULL
        )
    """)
    
    conn.commit()
    return conn


def _now() -> str:
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


# ════════════════════════════════════════════════════════════════════════════
# Audit Logging
# ════════════════════════════════════════════════════════════════════════════

def log_pipeline_run(phase: int, duration_s: float, stats: dict) -> None:
    conn = _connect()
    conn.execute(
        "INSERT INTO audit_log(ts, phase, event_type, rule_id, details_json) VALUES(?,?,?,?,?)",
        (_now(), f"Phase {phase}", "PIPELINE_RUN", None, json.dumps(stats)),
    )
    conn.commit()
    conn.close()


def log_hitl_decision(rule_id: str, action: str, analyst: str, notes: str) -> None:
    conn = _connect()
    conn.execute(
        "INSERT INTO audit_log(ts, phase, event_type, rule_id, details_json) VALUES(?,?,?,?,?)",
        (
            _now(),
            "Phase 3",
            f"HITL_{action}",
            rule_id,
            json.dumps({"analyst": analyst, "notes": notes, "action": action}),
        ),
    )
    conn.commit()
    conn.close()


def log_explanation_run(rule_count: int, duration_s: float) -> None:
    conn = _connect()
    conn.execute(
        "INSERT INTO audit_log(ts, phase, event_type, rule_id, details_json) VALUES(?,?,?,?,?)",
        (
            _now(), "Phase 3", "EXPLANATION_RUN", None,
            json.dumps({"rules_explained": rule_count, "duration_s": round(duration_s, 2)}),
        ),
    )
    conn.commit()
    conn.close()


def get_log(limit: int = 200) -> list[dict]:
    conn = _connect()
    rows = conn.execute("SELECT * FROM audit_log ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_stats() -> dict:
    conn = _connect()
    total     = conn.execute("SELECT COUNT(*) FROM audit_log").fetchone()[0]
    runs      = conn.execute("SELECT COUNT(*) FROM audit_log WHERE event_type='PIPELINE_RUN'").fetchone()[0]
    decisions = conn.execute("SELECT COUNT(*) FROM audit_log WHERE event_type LIKE 'HITL_%'").fetchone()[0]
    conn.close()
    return {"total_events": total, "pipeline_runs": runs, "hitl_decisions": decisions}


# ════════════════════════════════════════════════════════════════════════════
# State DB: Rules (Phase 1)
# ════════════════════════════════════════════════════════════════════════════

def save_rules(rules: list[dict]) -> tuple[int, int]:
    """Wipe old rules and insert new ones. Returns (added_count, skipped_count)."""
    conn = _connect()
    added = 0
    skipped = 0

    # Wipe existing rules so a new PDF completely replaces the old one
    conn.execute("DELETE FROM rules")
    
    for r in rules:
        try:
            conn.execute("""
                INSERT INTO rules (id, rule_type, description, condition_field, operator, threshold_value, sql_hint, fingerprint)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                r.get("id"),
                r.get("rule_type"),
                r.get("description"),
                r.get("condition_field"),
                r.get("operator"),
                str(r.get("threshold_value", "")),
                r.get("sql_hint"),
                r.get("_fingerprint")
            ))
            added += 1
        except sqlite3.IntegrityError:
            skipped += 1  # Duplicate fingerprint or ID
            
    conn.commit()
    conn.close()
    return added, skipped


def get_rules() -> list[dict]:
    conn = _connect()
    rows = conn.execute("SELECT * FROM rules").fetchall()
    conn.close()
    # Attempt to parse threshold_value back to original type if possible, or leave as string
    out = []
    for r in rows:
        d = dict(r)
        # Attempt to decode list thresholds
        tv = d["threshold_value"]
        if tv.startswith("[") and tv.endswith("]"):
            try: d["threshold_value"] = json.loads(tv)
            except: pass
        elif tv.isdigit():
            d["threshold_value"] = int(tv)
        out.append(d)
    return out


# ════════════════════════════════════════════════════════════════════════════
# State DB: Violations (Phase 2)
# ════════════════════════════════════════════════════════════════════════════

def save_violations(report: list[dict], live: bool = False) -> None:
    """Clear old violations and save physical run results."""
    table = "violations_live" if live else "violations"
    conn = _connect()
    conn.execute(f"DELETE FROM {table}")
    for v in report:
        conn.execute(f"""
            INSERT INTO {table} (rule_id, rule_description, sql, violation_count, sample_json, status, reason)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            v.get("rule_id"),
            v.get("rule_description"),
            v.get("sql"),
            v.get("violation_count", 0),
            json.dumps(v.get("sample_violations", [])),
            v.get("status"),
            v.get("reason"),
        ))
    conn.commit()
    conn.close()


def get_violations(live: bool = False) -> list[dict]:
    table = "violations_live" if live else "violations"
    conn = _connect()
    rows = conn.execute(f"SELECT * FROM {table}").fetchall()
    conn.close()
    out = []
    for r in rows:
        d = dict(r)
        d["sample_violations"] = json.loads(d.pop("sample_json", "[]"))
        out.append(d)
    return out


# ════════════════════════════════════════════════════════════════════════════
# State DB: Explanations (Phase 3)
# ════════════════════════════════════════════════════════════════════════════

def save_explanations(explanations: list[dict]) -> None:
    conn = _connect()
    conn.execute("DELETE FROM explanations")
    for e in explanations:
        conn.execute("""
            INSERT INTO explanations (rule_id, alert_headline, plain_english, risk_level, violation_count, recommended_action, policy_reference, generated_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            e.get("rule_id"),
            e.get("alert_headline"),
            e.get("plain_english"),
            e.get("risk_level"),
            e.get("violation_count"),
            e.get("recommended_action"),
            e.get("policy_reference"),
            e.get("generated_by"),
        ))
    conn.commit()
    conn.close()

def get_explanations() -> list[dict]:
    conn = _connect()
    rows = conn.execute("SELECT * FROM explanations").fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ════════════════════════════════════════════════════════════════════════════
# State DB: HITL Decisions
# ════════════════════════════════════════════════════════════════════════════

def save_decision(rule_id: str, action: str, analyst: str = "analyst", notes: str = "") -> dict:
    conn = _connect()
    ts = _now()
    conn.execute("""
        INSERT INTO hitl_decisions (rule_id, action, analyst, notes, timestamp)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(rule_id) DO UPDATE SET
            action=excluded.action,
            analyst=excluded.analyst,
            notes=excluded.notes,
            timestamp=excluded.timestamp
    """, (rule_id, action, analyst, notes, ts))
    conn.commit()
    conn.close()
    
    # Also log to audit
    log_hitl_decision(rule_id, action, analyst, notes)
    
    return {"rule_id": rule_id, "action": action, "analyst": analyst, "notes": notes, "timestamp": ts}


def get_decisions() -> dict[str, dict]:
    conn = _connect()
    rows = conn.execute("SELECT * FROM hitl_decisions").fetchall()
    conn.close()
    return {r["rule_id"]: dict(r) for r in rows}


def get_decision(rule_id: str) -> dict | None:
    conn = _connect()
    row = conn.execute("SELECT * FROM hitl_decisions WHERE rule_id = ?", (rule_id,)).fetchone()
    conn.close()
    return dict(row) if row else None
