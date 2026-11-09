"""Welche Zugänge hat Jarvis, welche fehlen noch, und wie bekommst du sie?

Wird vom Tool ``zugriffe_status`` und vom HUD (Panel „Zugriffe“) benutzt,
damit Jarvis dir immer konkret sagt, was er noch braucht.
"""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from typing import Callable

from .settings import HOME, Settings, data_path


@dataclass
class Integration:
    key: str
    name: str
    bereich: str
    check: Callable[[Settings], bool]
    wie: str  # Anleitung, falls es fehlt


def _has(*keys: str) -> Callable[[Settings], bool]:
    return lambda s: all(s.get(k) for k in keys)


def _file(name: str) -> Callable[[Settings], bool]:
    return lambda s: data_path(name).exists()


def _openjarvis_cred(key: str) -> Callable[[Settings], bool]:
    def check(s: Settings) -> bool:
        if s.get(key):
            return True
        path = HOME / "credentials.toml"
        if not path.exists():
            return False
        text = path.read_text(encoding="utf-8")
        return any(
            line.split("=", 1)[0].strip() == key and len(line.split("=", 1)[1].strip()) > 2
            for line in text.splitlines()
            if "=" in line and not line.strip().startswith("#")
        )

    return check


def _mcp(name: str) -> Callable[[Settings], bool]:
    def check(_: Settings) -> bool:
        path = HOME / "mcp-servers.json"
        try:
            servers = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return False
        return any(s.get("name") == name for s in servers)

    return check


def _garmin(_: Settings) -> bool:
    folder = data_path("garmin-tokens", "x").parent
    return folder.exists() and any(folder.iterdir())


INTEGRATIONS: list[Integration] = [
    Integration("claude", "Claude (Gehirn)", "Kern", _openjarvis_cred("ANTHROPIC_API_KEY"),
                "API-Key auf console.anthropic.com erstellen → ~/.openjarvis/credentials.toml"),
    Integration("telegram", "Telegram", "Kontakt", _has("TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"),
                "@BotFather → /newbot; Chat-ID über @userinfobot → jarvis-plus.env"),
    Integration("stimme", "Film-Stimme (ElevenLabs)", "Stimme", _has("ELEVENLABS_API_KEY"),
                "elevenlabs.io (gratis) → API Keys → ELEVENLABS_API_KEY in jarvis-plus.env"),
    Integration("twilio", "Anrufe & SMS", "Kontakt",
                _has("TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_FROM_NUMBER", "MY_PHONE_NUMBER"),
                "twilio.com Konto + Nummer kaufen → SID, Token, Nummern in jarvis-plus.env"),
    Integration("whoop", "Whoop", "Gesundheit", _file("whoop-token.json"),
                "WHOOP_CLIENT_SECRET in jarvis-plus.env, dann `jarvis-plus whoop-login`"),
    Integration("garmin", "Garmin", "Gesundheit", _garmin,
                "GARMIN_EMAIL/PASSWORD in jarvis-plus.env, dann `jarvis-plus garmin-login`"),
    Integration("instagram", "Instagram", "Business", _has("INSTAGRAM_ACCESS_TOKEN"),
                "Business-Account + Meta-App → Token in jarvis-plus.env"),
    Integration("netlify", "Websites veröffentlichen", "Business", _has("NETLIFY_AUTH_TOKEN"),
                "app.netlify.com → User settings → Applications → Personal access token"),
    Integration("higgsfield", "Higgsfield", "Connector", _mcp("higgsfield"),
                "`jarvis-plus connect higgsfield` (Higgsfield-Abo nötig)"),
    Integration("canva", "Canva", "Connector", _mcp("canva"), "`jarvis-plus connect canva`"),
    Integration("notion", "Notion", "Connector", _mcp("notion"), "`jarvis-plus connect notion`"),
    Integration("21st", "21st.dev (UI-Komponenten)", "Connector", _mcp("21st"),
                "Key auf 21st.dev/mcp → TWENTYFIRST_API_KEY, dann `jarvis-plus connect 21st`"),
    Integration("node", "Node.js (für Connectoren)", "System", lambda s: bool(shutil.which("npx")),
                "Node.js 22 installieren: nodejs.org (Windows: winget install OpenJS.NodeJS.LTS)"),
    Integration("browser", "Browser mit deinen Logins", "PC", _mcp("browser"),
                "Chrome-Erweiterung „Playwright MCP Bridge“ installieren, dann `jarvis-plus connect browser`"),
    Integration("desktop", "Desktop-Apps steuern", "PC", _mcp("desktop"),
                "`jarvis-plus connect desktop` (Mac: danach Bedienungshilfen-Zugriff erlauben)"),
    Integration("tailscale", "Tailscale (Handy-Zugang)", "System", lambda s: bool(shutil.which("tailscale")),
                "tailscale.com installieren (PC + Handy), gleiches Konto"),
    Integration("telefon", "Telefon-Leitung (mit Jarvis telefonieren)", "Kontakt",
                lambda s: all(s.get(k) for k in ("PHONE_SECRET", "PHONE_PUBLIC_URL", "TWILIO_AUTH_TOKEN")),
                "Twilio eintragen, Tailscale installieren, dann `jarvis-plus telefon-einrichten`"),
    Integration("design-db", "Design-Datenbank (UI/UX Pro Max)", "Websites",
                lambda s: (HOME / "vendor" / "ui-ux-pro-max").exists(),
                "Installer erneut ausführen (lädt sie automatisch)"),
]


def status(settings: Settings) -> list[dict]:
    rows = []
    for item in INTEGRATIONS:
        try:
            ok = bool(item.check(settings))
        except Exception:  # noqa: BLE001
            ok = False
        rows.append(
            {
                "key": item.key,
                "name": item.name,
                "bereich": item.bereich,
                "verbunden": ok,
                "so_gehts": "" if ok else item.wie,
            }
        )
    return rows


def missing_summary(settings: Settings) -> str:
    missing = [r for r in status(settings) if not r["verbunden"]]
    if not missing:
        return "Alle Zugänge sind eingerichtet."
    return "Mir fehlen noch diese Zugänge:\n" + "\n".join(
        f"• {r['name']}: {r['so_gehts']}" for r in missing
    )
