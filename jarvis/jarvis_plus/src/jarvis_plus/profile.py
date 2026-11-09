"""„Über mich“-Profil: eine Markdown-Datei, die Jarvis liest und ergänzt.

Liegt lokal in ``~/.openjarvis/ueber-mich.md``. Du kannst sie jederzeit selbst
öffnen, korrigieren oder Dinge löschen.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from .settings import HOME

PROFILE = HOME / "ueber-mich.md"


def read(path: Path = PROFILE) -> str:
    if not path.exists():
        return "(Noch kein Profil. Fülle ~/.openjarvis/ueber-mich.md aus.)"
    return path.read_text(encoding="utf-8")


def append(section: str, fact: str, path: Path = PROFILE) -> str:
    """Fakt unter einer Überschrift ergänzen (Überschrift wird angelegt)."""
    fact = fact.strip().replace("\n", " ")
    section = section.strip().lstrip("#").strip() or "Notizen"
    if not fact:
        raise ValueError("Leerer Eintrag.")
    text = path.read_text(encoding="utf-8") if path.exists() else "# Über mich\n"
    line = f"- {fact} _(gelernt {date.today().isoformat()})_"
    lines = text.rstrip("\n").split("\n")
    header = f"## {section}"
    if header in lines:
        idx = lines.index(header) + 1
        while idx < len(lines) and not lines[idx].startswith("## "):
            idx += 1
        while idx > 0 and not lines[idx - 1].strip():
            idx -= 1
        lines.insert(idx, line)
    else:
        lines += ["", header, line]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return f"Gespeichert unter '{section}': {fact}"
