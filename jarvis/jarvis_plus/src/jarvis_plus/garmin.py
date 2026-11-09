"""Garmin-Anbindung.

Garmin bietet Privatpersonen keine offizielle API (die Health-API ist nur für
Firmen). Wir nutzen deshalb die verbreitete inoffizielle Bibliothek
``garminconnect``. Einmalig ``jarvis-plus garmin-login`` ausführen, danach
werden die Login-Tokens lokal wiederverwendet.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from .settings import Settings, data_path


def _tokenstore() -> str:
    path = data_path("garmin-tokens", "x").parent
    path.mkdir(parents=True, exist_ok=True)
    return str(path)


def _client(settings: Settings, *, interactive: bool = False) -> Any:
    try:
        from garminconnect import Garmin
    except ImportError as exc:  # pragma: no cover - abhängig von Installation
        raise RuntimeError(
            "Paket fehlt: pip install 'jarvis-plus[garmin]' (bzw. garminconnect)"
        ) from exc

    store = _tokenstore()
    if not interactive:
        client = Garmin()
        try:
            client.login(store)
            return client
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError(
                "Garmin ist nicht verbunden. Führe `jarvis-plus garmin-login` aus."
            ) from exc

    email = settings.require("GARMIN_EMAIL")
    password = settings.require("GARMIN_PASSWORD")
    client = Garmin(
        email=email,
        password=password,
        prompt_mfa=lambda: input("Garmin MFA-Code: "),
    )
    client.login()
    client.garth.dump(store)
    return client


def login(settings: Settings) -> None:
    _client(settings, interactive=True)
    print("✅ Garmin verbunden. (Passwort kannst du jetzt aus der .env löschen.)")


def summarize_stats(stats: dict[str, Any]) -> dict[str, Any]:
    """Wichtige Werte aus ``get_stats`` (pure Funktion, testbar)."""
    return {
        "schritte": stats.get("totalSteps"),
        "kcal_gesamt": stats.get("totalKilocalories"),
        "ruhepuls": stats.get("restingHeartRate"),
        "stress_durchschnitt": stats.get("averageStressLevel"),
        "stress_max": stats.get("maxStressLevel"),
        "stress_aktuell": stats.get("stressQualifier"),
        "body_battery_aktuell": stats.get("bodyBatteryMostRecentValue"),
        "body_battery_hoch": stats.get("bodyBatteryHighestValue"),
        "body_battery_tief": stats.get("bodyBatteryLowestValue"),
        "intensitaetsminuten": (stats.get("moderateIntensityMinutes") or 0)
        + 2 * (stats.get("vigorousIntensityMinutes") or 0),
    }


def summarize_sleep(sleep: dict[str, Any]) -> dict[str, Any]:
    dto = sleep.get("dailySleepDTO") or {}
    secs = dto.get("sleepTimeSeconds")
    scores = (dto.get("sleepScores") or {}).get("overall") or {}
    return {
        "schlaf_stunden": round(secs / 3600, 2) if secs else None,
        "tiefschlaf_stunden": round((dto.get("deepSleepSeconds") or 0) / 3600, 2),
        "rem_stunden": round((dto.get("remSleepSeconds") or 0) / 3600, 2),
        "schlaf_score": scores.get("value"),
        "hrv_nacht": sleep.get("avgOvernightHrv"),
    }


def overview(settings: Settings, day: str | None = None) -> dict[str, Any]:
    client = _client(settings)
    d = day or date.today().isoformat()
    result: dict[str, Any] = {"datum": d}
    try:
        result["tag"] = summarize_stats(client.get_stats(d))
    except Exception as exc:  # noqa: BLE001
        result["tag_fehler"] = str(exc)
    try:
        result["schlaf"] = summarize_sleep(client.get_sleep_data(d))
    except Exception as exc:  # noqa: BLE001
        result["schlaf_fehler"] = str(exc)
    try:
        yesterday = (date.fromisoformat(d) - timedelta(days=1)).isoformat()
        result["stress_gestern"] = summarize_stats(client.get_stats(yesterday)).get(
            "stress_durchschnitt"
        )
    except Exception:  # noqa: BLE001
        pass
    return result
