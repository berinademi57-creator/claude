"""Externe Connectoren (MCP-Server) für Jarvis an- und abmelden.

Die meisten Dienste (Higgsfield, Canva, Notion …) bieten einen offiziellen
Remote-MCP-Server mit Login (OAuth). Wir binden sie über ``mcp-remote`` ein:
das öffnet beim ersten Mal den Browser zum Einloggen und merkt sich den Login.
Braucht Node.js (npx).
"""

from __future__ import annotations

import json
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any

from .settings import HOME, Settings, load_settings, write_private

# Lokale Connectoren (laufen auf deinem PC, kein Login nötig)
LOCAL: dict[str, dict[str, Any]] = {
    "browser": {
        "titel": "Browser mit deinen Logins (Playwright, Extension-Modus)",
        "command": "npx",
        # Token aus der Chrome-Erweiterung → credentials.toml [browser], damit nicht
        # jedes Mal bestätigt werden muss (PLAYWRIGHT_MCP_EXTENSION_TOKEN).
        "args": ["-y", "@playwright/mcp@latest", "--extension"],
    },
    "desktop": {
        "titel": "Desktop-Steuerung (Windows-MCP bzw. AppleScript auf dem Mac)",
    },
}

CATALOG: dict[str, dict[str, Any]] = {
    "higgsfield": {
        "titel": "Higgsfield (Bilder & Videos, braucht Abo, kostet Credits)",
        "url": "https://mcp.higgsfield.ai/mcp",
    },
    "canva": {"titel": "Canva (Designs erstellen/exportieren)", "url": "https://mcp.canva.com/mcp"},
    "notion": {"titel": "Notion (Notizen, Datenbanken, Memory)", "url": "https://mcp.notion.com/mcp"},
    "figma": {"titel": "Figma (Designs lesen)", "url": "https://mcp.figma.com/mcp"},
    "21st": {
        "titel": "21st.dev (fertige UI-Komponenten für Websites)",
        "url": "https://21st.dev/api/mcp",
        "header": "x-api-key:{key}",
        "env": "TWENTYFIRST_API_KEY",
    },
}


def servers_file() -> Path:
    return HOME / "mcp-servers.json"


def _load() -> list[dict[str, Any]]:
    try:
        data = json.loads(servers_file().read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    return data if isinstance(data, list) else [data]


def _save(servers: list[dict[str, Any]]) -> None:
    write_private(servers_file(), json.dumps(servers, indent=2))


def local_entry(name: str, system: str | None = None) -> dict[str, Any]:
    import platform

    system = (system or platform.system()).lower()
    if name == "desktop":
        if system == "windows":
            return {"name": "desktop", "command": shutil.which("uvx") or "uvx", "args": ["windows-mcp"]}
        if system == "darwin":
            return {"name": "desktop", "command": shutil.which("npx") or "npx",
                    "args": ["-y", "@steipete/macos-automator-mcp@latest"]}
        raise RuntimeError("Desktop-Steuerung gibt es für Windows und macOS.")
    item = LOCAL[name]
    return {"name": name, "command": shutil.which(item["command"]) or item["command"], "args": list(item["args"])}


def entry_for(name: str, settings: Settings | None = None) -> dict[str, Any]:
    if name in LOCAL:
        return local_entry(name)
    item = CATALOG[name]
    args = ["-y", "mcp-remote@latest", item["url"]]
    if item.get("header"):
        key = (settings or load_settings()).require(item["env"])
        args += ["--header", item["header"].format(key=key)]
    return {"name": name, "command": shutil.which("npx") or "npx", "args": args}


def add(name: str, settings: Settings | None = None) -> dict[str, Any]:
    if name not in CATALOG and name not in LOCAL:
        raise ValueError(f"Unbekannt: {name}. Verfügbar: {', '.join([*LOCAL, *CATALOG])}")
    servers = [s for s in _load() if s.get("name") != name]
    entry = entry_for(name, settings)
    servers.append(entry)
    _save(servers)
    return entry


def register_self() -> dict[str, Any]:
    """jarvis-plus selbst eintragen/aktualisieren, andere Connectoren bleiben erhalten."""
    exe = shutil.which("jarvis-plus")
    if not exe:
        raise RuntimeError("jarvis-plus ist nicht im PATH.")
    entry = {"name": "jarvis-plus", "command": exe, "args": ["serve"]}
    servers = [s for s in _load() if s.get("name") != "jarvis-plus"]
    _save([entry, *servers])
    return entry


def remove(name: str) -> None:
    _save([s for s in _load() if s.get("name") != name])


def listing() -> list[dict[str, Any]]:
    active = {s.get("name") for s in _load()}
    return [{"name": k, "titel": v["titel"], "aktiv": k in active} for k, v in {**LOCAL, **CATALOG}.items()]


def login(name: str, settings: Settings, timeout: int = 180) -> str:
    """Einmal mcp-remote starten, damit der Browser-Login passiert."""
    if name in LOCAL:
        return f"✅ {name} eingetragen (läuft lokal, kein Login nötig)."
    if not shutil.which("npx"):
        raise RuntimeError("Node.js fehlt (npx nicht gefunden). Installiere Node.js 22 von nodejs.org.")
    entry = entry_for(name, settings)
    print(f"Öffne Login für {name} … (Browser bestätigen)")
    proc = subprocess.Popen(
        [shutil.which("npx") or "npx", *entry["args"]],
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )
    deadline = time.time() + timeout
    ok = False
    assert proc.stderr is not None
    while time.time() < deadline:
        line = proc.stderr.readline()
        if not line:
            break
        if "Connected to remote server" in line or "Proxy established" in line:
            ok = True
            break
    proc.terminate()
    return f"✅ {name} verbunden." if ok else (
        f"⚠️ {name}: Login nicht bestätigt. Jarvis versucht es beim nächsten Start erneut."
    )
