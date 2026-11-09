"""Hintergrund-Wächter: prüft regelmäßig deine Werte und meldet sich von selbst.

- Stress hoch  -> Telegram-Nachricht mit Tipps (optional Anruf).
- Kunden fällig -> einmal am Tag Telegram-Erinnerung.
- Ruhezeiten (Standard 22–7 Uhr): keine Meldungen.
"""

from __future__ import annotations

import json
import time
from datetime import datetime
from zoneinfo import ZoneInfo

from . import customers, garmin, phone, stress, whoop
from .settings import Settings, data_path, load_settings, write_private


def _state() -> dict:
    path = data_path("watcher-state.json")
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def _save_state(state: dict) -> None:
    write_private(data_path("watcher-state.json"), json.dumps(state))


def in_quiet_hours(now: datetime, start: int, end: int) -> bool:
    if start == end:
        return False
    if start > end:  # z.B. 22 -> 7 über Mitternacht
        return now.hour >= start or now.hour < end
    return start <= now.hour < end


def check_once(settings: Settings, now: datetime | None = None) -> list[str]:
    tz = ZoneInfo(settings.timezone)
    now = now or datetime.now(tz)
    log: list[str] = []
    if in_quiet_hours(
        now,
        settings.get_int("WATCH_QUIET_START", 22),
        settings.get_int("WATCH_QUIET_END", 7),
    ):
        return ["Ruhezeit, keine Meldungen."]

    state = _state()

    # ---- Stress
    w = g = None
    try:
        w = whoop.overview(settings, days=7)
    except Exception as exc:  # noqa: BLE001
        log.append(f"Whoop: {exc}")
    try:
        g = garmin.overview(settings)
    except Exception as exc:  # noqa: BLE001
        log.append(f"Garmin: {exc}")
    result = stress.assess(w, g)
    log.append(f"Stress: {result.level} ({result.punkte} Punkte)")

    cooldown = settings.get_int("WATCH_ALERT_COOLDOWN_HOURS", 4) * 3600
    if result.level == "hoch" and time.time() - state.get("last_stress_alert", 0) > cooldown:
        text = (
            f"Hey {settings.name}, deine Werte zeigen gerade viel Stress.\n"
            + "\n".join(f"• {r}" for r in result.gruende)
            + "\n\nVorschlag:\n"
            + "\n".join(f"→ {t}" for t in result.tipps[:3])
        )
        call = settings.get("WATCH_CALL_ON_HIGH_STRESS", "false").lower() == "true"
        log += phone.notify(settings, text, call=call)
        state["last_stress_alert"] = time.time()

    # ---- Kunden einmal pro Tag
    today = now.date().isoformat()
    if state.get("last_customer_digest") != today and now.hour >= 9:
        due = customers.due(today)
        if due:
            text = "📋 Heute fällig bei Kunden:\n" + "\n".join(
                f"• {c['name']}: {c['naechster_schritt'] or 'nachfassen'} ({c['faellig_am']})"
                for c in due
            )
            log += phone.notify(settings, text)
        state["last_customer_digest"] = today

    _save_state(state)
    return log


def run_forever(interval_minutes: int | None = None) -> None:
    settings = load_settings()
    minutes = interval_minutes or settings.get_int("WATCH_INTERVAL_MINUTES", 30)
    print(f"Wächter läuft, prüft alle {minutes} Minuten. Strg+C zum Beenden.")
    while True:
        try:
            for line in check_once(load_settings()):
                print(datetime.now().strftime("%H:%M"), line)
        except Exception as exc:  # noqa: BLE001
            print("Fehler:", exc)
        time.sleep(minutes * 60)
