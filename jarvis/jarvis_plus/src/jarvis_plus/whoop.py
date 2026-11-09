"""Whoop-Anbindung (offizielle Developer API v2, OAuth2).

Einmalig ``jarvis-plus whoop-login`` ausführen: Browser öffnet sich, du
erlaubst den Zugriff, der Token wird lokal gespeichert und danach automatisch
erneuert (Scope ``offline``).
"""

from __future__ import annotations

import json
import secrets
import time
import urllib.parse
import webbrowser
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any

from . import http
from .settings import Settings, data_path, write_private

AUTH_URL = "https://api.prod.whoop.com/oauth/oauth2/auth"
TOKEN_URL = "https://api.prod.whoop.com/oauth/oauth2/token"
API = "https://api.prod.whoop.com/developer/v2"
SCOPES = (
    "offline read:recovery read:cycles read:sleep read:workout "
    "read:profile read:body_measurement"
)


def _token_file():
    return data_path("whoop-token.json")


# --------------------------------------------------------------------------
# OAuth
# --------------------------------------------------------------------------


def _save_token(payload: dict[str, Any]) -> dict[str, Any]:
    token = {
        "access_token": payload["access_token"],
        "refresh_token": payload.get("refresh_token", ""),
        "expires_at": time.time() + int(payload.get("expires_in", 3600)) - 60,
    }
    write_private(_token_file(), json.dumps(token))
    return token


def login(settings: Settings) -> None:
    """Interaktiver OAuth-Login über einen lokalen Callback-Server."""
    client_id = settings.require("WHOOP_CLIENT_ID")
    client_secret = settings.require("WHOOP_CLIENT_SECRET")
    redirect_uri = settings.get("WHOOP_REDIRECT_URI", "http://localhost:8080/callback")
    parsed = urllib.parse.urlparse(redirect_uri)
    if parsed.hostname not in ("localhost", "127.0.0.1"):
        raise RuntimeError(
            "Für den Login muss WHOOP_REDIRECT_URI auf localhost zeigen, "
            "z.B. http://localhost:8080/callback"
        )
    state = secrets.token_urlsafe(16)
    result: dict[str, str] = {}

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            result.update({k: v[0] for k, v in query.items()})
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(
                "<h2>Whoop verbunden. Du kannst dieses Fenster schließen.</h2>".encode()
            )

        def log_message(self, *args: Any) -> None:
            pass

    url = AUTH_URL + "?" + urllib.parse.urlencode(
        {
            "response_type": "code",
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": SCOPES,
            "state": state,
        }
    )
    server = HTTPServer((parsed.hostname, parsed.port or 80), Handler)
    print("Öffne im Browser (falls es nicht automatisch passiert):\n" + url)
    webbrowser.open(url)
    while "code" not in result and "error" not in result:
        server.handle_request()
    server.server_close()

    if result.get("state") != state:
        raise RuntimeError("Whoop-Login abgebrochen: state passt nicht.")
    if "error" in result:
        raise RuntimeError(f"Whoop-Login fehlgeschlagen: {result['error']}")

    payload = http.post(
        TOKEN_URL,
        form={
            "grant_type": "authorization_code",
            "code": result["code"],
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
        },
    )
    _save_token(payload)
    print("✅ Whoop verbunden.")


def _access_token(settings: Settings) -> str:
    path = _token_file()
    if not path.exists():
        raise RuntimeError("Whoop ist nicht verbunden. Führe `jarvis-plus whoop-login` aus.")
    token = json.loads(path.read_text(encoding="utf-8"))
    if time.time() < token.get("expires_at", 0):
        return token["access_token"]
    if not token.get("refresh_token"):
        raise RuntimeError("Whoop-Token abgelaufen. Führe `jarvis-plus whoop-login` aus.")
    payload = http.post(
        TOKEN_URL,
        form={
            "grant_type": "refresh_token",
            "refresh_token": token["refresh_token"],
            "client_id": settings.require("WHOOP_CLIENT_ID"),
            "client_secret": settings.require("WHOOP_CLIENT_SECRET"),
            "scope": "offline",
        },
    )
    return _save_token(payload)["access_token"]


def _get(settings: Settings, path: str, **params: Any) -> Any:
    return http.get(f"{API}{path}", params=params, bearer=_access_token(settings))


def _records(settings: Settings, path: str, days: int) -> list[dict[str, Any]]:
    start = (datetime.now(timezone.utc) - timedelta(days=days)).strftime(
        "%Y-%m-%dT%H:%M:%S.000Z"
    )
    data = _get(settings, path, limit=25, start=start)
    return data.get("records", []) if isinstance(data, dict) else []


# --------------------------------------------------------------------------
# Daten aufbereiten (pure Funktionen, testbar)
# --------------------------------------------------------------------------


def _hours(milli: float | None) -> float | None:
    return round(milli / 3_600_000, 2) if milli else None


def summarize_recovery(rec: dict[str, Any]) -> dict[str, Any]:
    score = rec.get("score") or {}
    return {
        "datum": rec.get("created_at", "")[:10],
        "recovery_prozent": score.get("recovery_score"),
        "hrv_ms": round(score["hrv_rmssd_milli"], 1)
        if score.get("hrv_rmssd_milli") is not None
        else None,
        "ruhepuls": score.get("resting_heart_rate"),
        "spo2": score.get("spo2_percentage"),
        "hauttemperatur_c": score.get("skin_temp_celsius"),
    }


def summarize_sleep(sleep: dict[str, Any]) -> dict[str, Any]:
    score = sleep.get("score") or {}
    stages = score.get("stage_summary") or {}
    in_bed = stages.get("total_in_bed_time_milli") or 0
    awake = stages.get("total_awake_time_milli") or 0
    return {
        "ende": sleep.get("end", ""),
        "nap": sleep.get("nap", False),
        "schlaf_stunden": _hours(in_bed - awake) if in_bed else None,
        "tiefschlaf_stunden": _hours(stages.get("total_slow_wave_sleep_time_milli")),
        "rem_stunden": _hours(stages.get("total_rem_sleep_time_milli")),
        "schlaf_performance_prozent": score.get("sleep_performance_percentage"),
        "effizienz_prozent": score.get("sleep_efficiency_percentage"),
        "atemfrequenz": score.get("respiratory_rate"),
    }


def summarize_cycle(cycle: dict[str, Any]) -> dict[str, Any]:
    score = cycle.get("score") or {}
    kj = score.get("kilojoule")
    return {
        "start": cycle.get("start", ""),
        "strain": round(score["strain"], 1) if score.get("strain") is not None else None,
        "kcal": round(kj / 4.184) if kj else None,
        "durchschnittspuls": score.get("average_heart_rate"),
        "maxpuls": score.get("max_heart_rate"),
    }


def baseline(recoveries: list[dict[str, Any]]) -> dict[str, float | None]:
    """Durchschnitt von HRV und Ruhepuls über die übergebenen Tage."""
    hrv = [r["hrv_ms"] for r in recoveries if r.get("hrv_ms")]
    rhr = [r["ruhepuls"] for r in recoveries if r.get("ruhepuls")]
    return {
        "hrv_ms": round(sum(hrv) / len(hrv), 1) if hrv else None,
        "ruhepuls": round(sum(rhr) / len(rhr), 1) if rhr else None,
    }


# --------------------------------------------------------------------------
# Öffentliche Funktionen für die Tools
# --------------------------------------------------------------------------


def overview(settings: Settings, days: int = 7) -> dict[str, Any]:
    """Recovery, Schlaf, Strain und Workouts der letzten Tage."""
    recoveries = [summarize_recovery(r) for r in _records(settings, "/recovery", days)]
    sleeps = [
        summarize_sleep(s)
        for s in _records(settings, "/activity/sleep", days)
        if not s.get("nap")
    ]
    cycles = [summarize_cycle(c) for c in _records(settings, "/cycle", days)]
    workouts = [
        {
            "sport": w.get("sport_name") or w.get("sport_id"),
            "start": w.get("start", ""),
            "strain": (w.get("score") or {}).get("strain"),
            "durchschnittspuls": (w.get("score") or {}).get("average_heart_rate"),
        }
        for w in _records(settings, "/activity/workout", days)
    ]
    return {
        "heute": {
            "recovery": recoveries[0] if recoveries else None,
            "schlaf": sleeps[0] if sleeps else None,
            "zyklus": cycles[0] if cycles else None,
        },
        "baseline": baseline(recoveries[1:] or recoveries),
        "verlauf_recovery": recoveries,
        "verlauf_schlaf": sleeps,
        "verlauf_strain": cycles,
        "workouts": workouts,
    }
