"""Mini-CRM für deine Kunden (lokale SQLite-Datei, nichts in der Cloud)."""

from __future__ import annotations

import sqlite3
from datetime import date, datetime
from pathlib import Path
from typing import Any

from .settings import data_path

SCHEMA = """
CREATE TABLE IF NOT EXISTS kunden (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE COLLATE NOCASE,
    kontakt TEXT DEFAULT '',
    status TEXT DEFAULT 'lead',
    naechster_schritt TEXT DEFAULT '',
    faellig_am TEXT DEFAULT '',
    aktualisiert TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS notizen (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kunde_id INTEGER NOT NULL REFERENCES kunden(id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    erstellt TEXT NOT NULL
);
"""

STATUSES = ("lead", "angebot", "kunde", "stammkunde", "pausiert", "verloren")


def _connect(db_path: Path | None = None) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path or data_path("kunden.db"))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    return conn


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def save(
    name: str,
    kontakt: str | None = None,
    status: str | None = None,
    naechster_schritt: str | None = None,
    faellig_am: str | None = None,
    *,
    db_path: Path | None = None,
) -> dict[str, Any]:
    if not name.strip():
        raise ValueError("Name fehlt.")
    if status and status not in STATUSES:
        raise ValueError(f"Status muss einer von {', '.join(STATUSES)} sein.")
    if faellig_am:
        date.fromisoformat(faellig_am)  # validiert JJJJ-MM-TT
    with _connect(db_path) as conn:
        row = conn.execute("SELECT * FROM kunden WHERE name = ?", (name.strip(),)).fetchone()
        if row is None:
            conn.execute(
                "INSERT INTO kunden (name, kontakt, status, naechster_schritt, faellig_am,"
                " aktualisiert) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    name.strip(),
                    kontakt or "",
                    status or "lead",
                    naechster_schritt or "",
                    faellig_am or "",
                    _now(),
                ),
            )
        else:
            conn.execute(
                "UPDATE kunden SET kontakt = ?, status = ?, naechster_schritt = ?,"
                " faellig_am = ?, aktualisiert = ? WHERE id = ?",
                (
                    kontakt if kontakt is not None else row["kontakt"],
                    status or row["status"],
                    naechster_schritt if naechster_schritt is not None
                    else row["naechster_schritt"],
                    faellig_am if faellig_am is not None else row["faellig_am"],
                    _now(),
                    row["id"],
                ),
            )
    return get(name, db_path=db_path)


def add_note(name: str, text: str, *, db_path: Path | None = None) -> dict[str, Any]:
    with _connect(db_path) as conn:
        row = conn.execute("SELECT id FROM kunden WHERE name = ?", (name.strip(),)).fetchone()
        if row is None:
            raise ValueError(f"Kunde '{name}' gibt es nicht. Erst speichern.")
        conn.execute(
            "INSERT INTO notizen (kunde_id, text, erstellt) VALUES (?, ?, ?)",
            (row["id"], text.strip(), _now()),
        )
        conn.execute("UPDATE kunden SET aktualisiert = ? WHERE id = ?", (_now(), row["id"]))
    return get(name, db_path=db_path)


def get(name: str, *, db_path: Path | None = None) -> dict[str, Any]:
    with _connect(db_path) as conn:
        row = conn.execute("SELECT * FROM kunden WHERE name = ?", (name.strip(),)).fetchone()
        if row is None:
            raise ValueError(f"Kunde '{name}' nicht gefunden.")
        notes = conn.execute(
            "SELECT text, erstellt FROM notizen WHERE kunde_id = ? ORDER BY id DESC LIMIT 20",
            (row["id"],),
        ).fetchall()
    return {**dict(row), "notizen": [dict(n) for n in notes]}


def list_all(status: str | None = None, *, db_path: Path | None = None) -> list[dict[str, Any]]:
    with _connect(db_path) as conn:
        if status:
            rows = conn.execute(
                "SELECT * FROM kunden WHERE status = ? ORDER BY aktualisiert DESC", (status,)
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM kunden ORDER BY aktualisiert DESC").fetchall()
    return [dict(r) for r in rows]


def due(today: str | None = None, *, db_path: Path | None = None) -> list[dict[str, Any]]:
    day = today or date.today().isoformat()
    with _connect(db_path) as conn:
        rows = conn.execute(
            "SELECT * FROM kunden WHERE faellig_am != '' AND faellig_am <= ?"
            " ORDER BY faellig_am",
            (day,),
        ).fetchall()
    return [dict(r) for r in rows]
