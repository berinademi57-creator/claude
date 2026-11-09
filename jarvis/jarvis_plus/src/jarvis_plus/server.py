"""MCP-Server: macht alle jarvis-plus Funktionen für OpenJarvis nutzbar.

OpenJarvis startet ihn automatisch (siehe config/mcp-servers.json). Er
funktioniert auch mit jedem anderen MCP-Client (z.B. Claude Desktop).
"""

from __future__ import annotations

import json
from typing import Any, Callable

from . import customers, garmin, instagram, phone, profile, stress, whoop
from .settings import load_settings

try:  # mcp >= 2
    from mcp.server import MCPServer as _Server
except ImportError:  # mcp 1.x
    from mcp.server.fastmcp import FastMCP as _Server

INSTRUCTIONS = (
    "Persönliche Werkzeuge: Gesundheit (Whoop, Garmin, Stress), Anrufe/SMS/"
    "Telegram an den Nutzer, Instagram, Kunden-CRM und das Profil 'über mich'. "
    "Vor Instagram-Posts und Kommentar-Antworten immer erst den Text zeigen und "
    "die Bestätigung des Nutzers abwarten."
)

mcp = _Server("jarvis-plus", instructions=INSTRUCTIONS)


def _run(fn: Callable[[], Any]) -> str:
    """Ergebnis als JSON-Text; Fehler als verständliche Meldung statt Absturz."""
    try:
        result = fn()
    except Exception as exc:  # noqa: BLE001
        return f"FEHLER: {exc}"
    if isinstance(result, str):
        return result
    return json.dumps(result, ensure_ascii=False, indent=1, default=str)


# ---------------------------------------------------------------- Gesundheit


@mcp.tool()
def whoop_daten(tage: int = 7) -> str:
    """Whoop: Recovery, HRV, Ruhepuls, Schlaf, Strain und Workouts der letzten Tage."""
    return _run(lambda: whoop.overview(load_settings(), days=max(1, min(tage, 30))))


@mcp.tool()
def garmin_daten(datum: str = "") -> str:
    """Garmin: Stress, Body Battery, Schritte, Ruhepuls, Schlaf. datum = JJJJ-MM-TT (leer = heute)."""
    return _run(lambda: garmin.overview(load_settings(), datum or None))


def _collect_health() -> dict[str, Any]:
    settings = load_settings()
    data: dict[str, Any] = {}
    try:
        data["whoop"] = whoop.overview(settings, days=7)
    except Exception as exc:  # noqa: BLE001
        data["whoop_fehler"] = str(exc)
    try:
        data["garmin"] = garmin.overview(settings)
    except Exception as exc:  # noqa: BLE001
        data["garmin_fehler"] = str(exc)
    data["stress"] = stress.assess(data.get("whoop"), data.get("garmin")).as_dict()
    return data


@mcp.tool()
def stress_check() -> str:
    """Wie gestresst/belastet bin ich gerade? Kombiniert Whoop + Garmin und gibt Level, Gründe und Tipps."""
    return _run(_collect_health)


# ---------------------------------------------------------------- Kontakt zu mir


@mcp.tool()
def mich_anrufen(nachricht: str) -> str:
    """Ruft MEIN Handy an und liest die Nachricht vor (z.B. Erinnerung, Weckruf, Alarm)."""
    return _run(lambda: phone.call_me(load_settings(), nachricht))


@mcp.tool()
def mir_sms_schicken(nachricht: str) -> str:
    """Schickt mir eine SMS auf mein Handy."""
    return _run(lambda: phone.sms_me(load_settings(), nachricht))


@mcp.tool()
def mir_telegram_schicken(nachricht: str) -> str:
    """Schickt mir eine Telegram-Nachricht (Push aufs Handy und PC)."""
    return _run(lambda: phone.telegram_me(load_settings(), nachricht))


# ---------------------------------------------------------------- Über mich


@mcp.tool()
def ueber_mich_lesen() -> str:
    """Liest mein Profil: Ziele, Gewohnheiten, Business, Vorlieben, Personen. Vor persönlichen Antworten nutzen."""
    return _run(profile.read)


@mcp.tool()
def ueber_mich_merken(bereich: str, fakt: str) -> str:
    """Speichert etwas Neues über mich dauerhaft, z.B. bereich='Ziele', fakt='Will bis Juni 75 kg wiegen'."""
    return _run(lambda: profile.append(bereich, fakt))


# ---------------------------------------------------------------- Kunden


@mcp.tool()
def kunde_speichern(
    name: str,
    kontakt: str = "",
    status: str = "",
    naechster_schritt: str = "",
    faellig_am: str = "",
) -> str:
    """Kunde anlegen/aktualisieren. status: lead|angebot|kunde|stammkunde|pausiert|verloren. faellig_am: JJJJ-MM-TT."""
    return _run(
        lambda: customers.save(
            name,
            kontakt or None,
            status or None,
            naechster_schritt or None,
            faellig_am or None,
        )
    )


@mcp.tool()
def kunde_notiz(name: str, notiz: str) -> str:
    """Notiz zu einem Kunden speichern (Gespräch, Wunsch, Preis, ...)."""
    return _run(lambda: customers.add_note(name, notiz))


@mcp.tool()
def kunde_anzeigen(name: str) -> str:
    """Alle Infos + letzte Notizen zu einem Kunden."""
    return _run(lambda: customers.get(name))


@mcp.tool()
def kunden_liste(status: str = "") -> str:
    """Alle Kunden, optional nach Status gefiltert."""
    return _run(lambda: customers.list_all(status or None))


@mcp.tool()
def kunden_faellig() -> str:
    """Kunden, bei denen heute (oder überfällig) etwas zu tun ist."""
    return _run(customers.due)


# ---------------------------------------------------------------- Instagram


@mcp.tool()
def instagram_konto() -> str:
    """Mein Instagram-Konto: Follower, Anzahl Posts usw."""
    return _run(lambda: instagram.account(load_settings()))


@mcp.tool()
def instagram_posts(anzahl: int = 10) -> str:
    """Meine letzten Instagram-Posts mit Likes und Kommentar-Anzahl."""
    return _run(lambda: instagram.recent_posts(load_settings(), anzahl))


@mcp.tool()
def instagram_kommentare(media_id: str) -> str:
    """Kommentare unter einem meiner Posts."""
    return _run(lambda: instagram.comments(load_settings(), media_id))


@mcp.tool()
def instagram_kommentar_antworten(kommentar_id: str, text: str) -> str:
    """Antwortet auf einen Kommentar. NUR nach ausdrücklicher Bestätigung des Nutzers aufrufen."""
    return _run(lambda: instagram.reply_to_comment(load_settings(), kommentar_id, text))


@mcp.tool()
def instagram_foto_posten(bild_url: str, caption: str) -> str:
    """Postet ein Foto (öffentliche JPEG-URL). NUR nach ausdrücklicher Bestätigung des Nutzers aufrufen."""
    return _run(lambda: instagram.publish_photo(load_settings(), bild_url, caption))


@mcp.tool()
def instagram_statistiken() -> str:
    """Reichweite, Aufrufe und Profilbesuche von heute."""
    return _run(lambda: instagram.insights(load_settings()))


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
