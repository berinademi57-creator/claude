"""Einstellungen laden.

Alle Secrets liegen in ``~/.openjarvis/jarvis-plus.env`` (oder in echten
Umgebungsvariablen, die haben Vorrang). Nichts davon gehört in Git.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

def _openjarvis_home() -> Path:
    """Gleiche Reihenfolge wie OpenJarvis selbst (core/paths.py)."""
    if os.environ.get("OPENJARVIS_HOME"):
        return Path(os.environ["OPENJARVIS_HOME"]).expanduser()
    if os.environ.get("XDG_DATA_HOME"):
        return Path(os.environ["XDG_DATA_HOME"]).expanduser() / "openjarvis"
    return Path.home() / ".openjarvis"


HOME = _openjarvis_home()
ENV_FILE = Path(os.environ.get("JARVIS_PLUS_ENV", HOME / "jarvis-plus.env")).expanduser()
DATA_DIR = HOME / "jarvis-plus"


def _parse_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        values[key.strip()] = value
    return values


@dataclass
class Settings:
    values: dict[str, str]

    def get(self, key: str, default: str = "") -> str:
        return os.environ.get(key) or self.values.get(key) or default

    def require(self, key: str) -> str:
        value = self.get(key)
        if not value:
            raise RuntimeError(
                f"{key} fehlt. Trag es in {ENV_FILE} ein (siehe .env.example)."
            )
        return value

    def get_int(self, key: str, default: int) -> int:
        try:
            return int(self.get(key, str(default)))
        except ValueError:
            return default

    @property
    def timezone(self) -> str:
        return self.get("JARVIS_TIMEZONE", "Europe/Berlin")

    @property
    def name(self) -> str:
        """So spricht Jarvis dich an (Begrüssung, Telefon, Alarme)."""
        return self.get("JARVIS_ANREDE", "Boss Ademi")


def load_settings() -> Settings:
    return Settings(_parse_env_file(ENV_FILE))


def data_path(*parts: str) -> Path:
    path = DATA_DIR.joinpath(*parts)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def write_private(path: Path, text: str) -> None:
    """Datei schreiben, die nur der eigene Benutzer lesen darf (Tokens)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    try:
        path.chmod(0o600)
    except OSError:  # Windows
        pass


def set_value(key: str, value: str, path: Path | None = None) -> None:
    """Einen Wert in jarvis-plus.env setzen (Zeile ersetzen oder anhängen)."""
    path = path or ENV_FILE
    lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    out, done = [], False
    for line in lines:
        if line.split("=", 1)[0].strip() == key and not line.lstrip().startswith("#"):
            out.append(f"{key}={value}")
            done = True
        else:
            out.append(line)
    if not done:
        out.append(f"{key}={value}")
    write_private(path, "\n".join(out) + "\n")


def merge_env(source: Path, target: Path | None = None) -> list[str]:
    """Werte aus source übernehmen, aber nur wo target leer ist. Gibt geänderte Keys zurück."""
    target = target or ENV_FILE
    current = _parse_env_file(target)
    changed = []
    for key, value in _parse_env_file(source).items():
        if value and not current.get(key):
            set_value(key, value, target)
            changed.append(key)
    return changed


def fix_brain_config(path: Path | None = None, model: str = "claude-haiku-5-5") -> list[str]:
    """[engine] und [intelligence] in config.toml auf Claude stellen, alles andere behalten."""
    path = path or (HOME / "config.toml")
    want = {
        "engine": {"default": '"cloud"'},
        "intelligence": {"default_model": f'"{model}"', "provider": '"anthropic"'},
    }
    lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    out: list[str] = []
    section = None
    done: dict[str, set[str]] = {k: set() for k in want}
    seen_sections: set[str] = set()
    changes: list[str] = []

    def flush(sec: str | None) -> None:
        if sec in want:
            for key, val in want[sec].items():
                if key not in done[sec]:
                    out.append(f"{key} = {val}")
                    done[sec].add(key)
                    changes.append(f"{sec}.{key} ergänzt")

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]") and not stripped.startswith("[["):
            flush(section)
            section = stripped[1:-1].strip()
            if section in want and section in seen_sections:
                section = "__dup__" + section  # doppelte Sektion: Inhalte auskommentieren
                out.append("# " + line + "   (doppelt, von jarvis-plus deaktiviert)")
                continue
            seen_sections.add(section)
            out.append(line)
            continue
        if section and section.startswith("__dup__"):
            out.append(("# " + line) if stripped and not stripped.startswith("#") else line)
            continue
        if section in want and "=" in stripped and not stripped.startswith("#"):
            key = stripped.split("=", 1)[0].strip()
            if key in want[section]:
                new = f"{key} = {want[section][key]}"
                if stripped != new:
                    changes.append(f"{section}.{key}: {stripped.split('=', 1)[1].strip()} → {want[section][key]}")
                out.append(new)
                done[section].add(key)
                continue
        out.append(line)
    flush(section)
    for sec in want:
        if sec not in seen_sections:
            out += ["", f"[{sec}]"]
            for key, val in want[sec].items():
                out.append(f"{key} = {val}")
            changes.append(f"[{sec}] angelegt")
    path.write_text("\n".join(out) + "\n", encoding="utf-8")
    return changes
