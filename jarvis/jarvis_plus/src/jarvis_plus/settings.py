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
        return self.get("JARVIS_USER_NAME", "Boss")


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
