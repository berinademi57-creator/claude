"""Aktivitäts-Protokoll: alles, was Jarvis tut, landet hier und im HUD.

Eine JSON-Zeile pro Ereignis in ``~/.openjarvis/jarvis-plus/activity.jsonl``.
Der MCP-Server (von OpenJarvis gestartet) und das HUD sind getrennte Prozesse;
die Datei ist die gemeinsame „Leitung“ zwischen beiden.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from .settings import data_path

MAX_BYTES = 2_000_000  # danach wird die Datei rotiert


def log_file() -> Path:
    return data_path("activity.jsonl")


def log(kind: str, title: str, *, status: str = "info", detail: str = "", **extra: Any) -> dict:
    """Ereignis schreiben. kind z.B. 'tool', 'chat', 'alarm', 'website'."""
    event = {
        "ts": time.time(),
        "kind": kind,
        "title": title,
        "status": status,  # start | ok | error | info
        "detail": detail[:500],
        **extra,
    }
    path = log_file()
    try:
        if path.exists() and path.stat().st_size > MAX_BYTES:
            path.replace(path.with_suffix(".old.jsonl"))
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(event, ensure_ascii=False, default=str) + "\n")
    except OSError:
        pass  # Protokoll darf nie die eigentliche Arbeit stoppen
    return event


def read_from(offset: int) -> tuple[list[dict], int]:
    """Neue Ereignisse ab Byte-Offset lesen. Gibt (events, neuer_offset) zurück."""
    path = log_file()
    if not path.exists():
        return [], 0
    size = path.stat().st_size
    if offset > size:  # Datei wurde rotiert
        offset = 0
    events: list[dict] = []
    with path.open("rb") as fh:
        fh.seek(offset)
        chunk = fh.read()
    # Nur vollständige Zeilen verarbeiten
    end = chunk.rfind(b"\n") + 1
    for line in chunk[:end].splitlines():
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return events, offset + end


def recent(limit: int = 50) -> list[dict]:
    path = log_file()
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()[-limit:]
    out = []
    for line in lines:
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out
