"""MCP-Server: macht alle jarvis-plus Funktionen für OpenJarvis nutzbar.

OpenJarvis startet ihn automatisch (siehe config/mcp-servers.json). Er
funktioniert auch mit jedem anderen MCP-Client (z.B. Claude Desktop).
"""

from __future__ import annotations

import functools
import json
import time
from typing import Any, Callable

from . import access, activity, customers, garmin, instagram, phone, profile, stress, websites, whoop
from .settings import load_settings

try:  # mcp >= 2
    from mcp.server import MCPServer as _Server
except ImportError:  # mcp 1.x
    from mcp.server.fastmcp import FastMCP as _Server

INSTRUCTIONS = (
    "Persönliche Werkzeuge: Gesundheit (Whoop, Garmin, Stress), Anrufe/SMS/"
    "Telegram an den Nutzer, Instagram, Kunden-CRM und das Profil 'über mich'. "
    "Vor Instagram-Posts, Kommentar-Antworten und dem Veröffentlichen von Websites "
    "immer erst zeigen, was passiert, und die Bestätigung des Nutzers abwarten. "
    "Fehlt ein Zugang, sag dem Nutzer genau, was er einrichten muss (zugriffe_status)."
)

_server = _Server("jarvis-plus", instructions=INSTRUCTIONS)


class _LoggedServer:
    """Wie der MCP-Server, aber jeder Tool-Aufruf landet im Aktivitäts-Protokoll."""

    def __init__(self, inner: Any) -> None:
        self._inner = inner

    def tool(self, *args: Any, **kwargs: Any) -> Callable:
        register = self._inner.tool(*args, **kwargs)

        def decorator(fn: Callable) -> Callable:
            @functools.wraps(fn)
            def wrapper(*a: Any, **kw: Any) -> Any:
                started = time.time()
                activity.log("tool", fn.__name__, status="start", detail=_short(kw))
                result = fn(*a, **kw)
                failed = isinstance(result, str) and result.startswith("FEHLER")
                activity.log(
                    "tool",
                    fn.__name__,
                    status="error" if failed else "ok",
                    detail=result[:300] if failed else "",
                    dauer=round(time.time() - started, 2),
                )
                return result

            return register(wrapper)

        return decorator

    def run(self, *args: Any, **kwargs: Any) -> None:
        self._inner.run(*args, **kwargs)


def _short(kwargs: dict[str, Any]) -> str:
    parts = []
    for key, value in kwargs.items():
        if "html" in key or "json" in key:
            continue  # grosse Inhalte nicht ins Protokoll
        text = str(value).replace("\n", " ")
        parts.append(f"{key}={text[:60]}{'…' if len(text) > 60 else ''}")
    return ", ".join(parts)


mcp = _LoggedServer(_server)


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


# ---------------------------------------------------------------- Websites


@mcp.tool()
def website_speichern(name: str, index_html: str, weitere_dateien_json: str = "") -> str:
    """Speichert eine Website (index.html + optional weitere Dateien als JSON {"pfad": "inhalt"}). Danach sofort live im HUD sichtbar."""

    def go() -> Any:
        files = {"index.html": index_html}
        if weitere_dateien_json.strip():
            files.update(json.loads(weitere_dateien_json))
        result = websites.save(name, files)
        activity.log("website", result["name"], status="ok", vorschau=result["vorschau"])
        return result

    return _run(go)


@mcp.tool()
def websites_liste() -> str:
    """Alle gebauten Websites mit Vorschau- und Live-Link."""
    return _run(websites.list_sites)


@mcp.tool()
def website_veroeffentlichen(name: str) -> str:
    """Stellt eine gespeicherte Website auf Netlify online. NUR nach ausdrücklicher Bestätigung des Nutzers aufrufen."""
    return _run(lambda: websites.publish(load_settings(), name))


# ---------------------------------------------------------------- Zugriffe


@mcp.tool()
def zugriffe_status() -> str:
    """Welche Zugänge (APIs, Connectoren) eingerichtet sind und was fehlt, mit Anleitung. Nutzen, wenn etwas nicht klappt."""
    return _run(lambda: access.missing_summary(load_settings()))


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
