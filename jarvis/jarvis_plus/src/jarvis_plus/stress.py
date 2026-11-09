"""Stress-/Belastungs-Einschätzung aus Whoop- und Garmin-Daten.

Bewusst einfache, nachvollziehbare Regeln statt Blackbox. Das ist eine
Orientierung, keine medizinische Diagnose.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class StressResult:
    level: str  # "niedrig" | "mittel" | "hoch" | "unbekannt"
    punkte: int
    gruende: list[str] = field(default_factory=list)
    tipps: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "level": self.level,
            "punkte": self.punkte,
            "gruende": self.gruende,
            "tipps": self.tipps,
        }


def assess(
    whoop: dict[str, Any] | None = None, garmin: dict[str, Any] | None = None
) -> StressResult:
    points = 0
    reasons: list[str] = []
    signals = 0

    if whoop:
        today = (whoop.get("heute") or {})
        rec = today.get("recovery") or {}
        sleep = today.get("schlaf") or {}
        base = whoop.get("baseline") or {}

        recovery = rec.get("recovery_prozent")
        if recovery is not None:
            signals += 1
            if recovery < 34:
                points += 2
                reasons.append(f"Whoop-Recovery nur {recovery:.0f} % (rot)")
            elif recovery < 67:
                points += 1
                reasons.append(f"Whoop-Recovery {recovery:.0f} % (gelb)")

        hrv, hrv_base = rec.get("hrv_ms"), base.get("hrv_ms")
        if hrv and hrv_base:
            signals += 1
            ratio = hrv / hrv_base
            if ratio < 0.8:
                points += 2
                reasons.append(f"HRV {hrv:.0f} ms, deutlich unter deinem Schnitt ({hrv_base:.0f})")
            elif ratio < 0.9:
                points += 1
                reasons.append(f"HRV {hrv:.0f} ms, leicht unter deinem Schnitt ({hrv_base:.0f})")

        rhr, rhr_base = rec.get("ruhepuls"), base.get("ruhepuls")
        if rhr and rhr_base:
            signals += 1
            if rhr - rhr_base >= 5:
                points += 1
                reasons.append(f"Ruhepuls {rhr:.0f}, {rhr - rhr_base:.0f} über normal")

        hours = sleep.get("schlaf_stunden")
        if hours is not None:
            signals += 1
            if hours < 6:
                points += 1
                reasons.append(f"Nur {hours:.1f} h Schlaf")

    if garmin:
        day = garmin.get("tag") or {}
        stress = day.get("stress_durchschnitt")
        if stress is not None and stress >= 0:
            signals += 1
            if stress >= 50:
                points += 2
                reasons.append(f"Garmin-Stress im Schnitt {stress} (hoch)")
            elif stress >= 35:
                points += 1
                reasons.append(f"Garmin-Stress im Schnitt {stress} (erhöht)")

        battery = day.get("body_battery_aktuell")
        if battery is not None:
            signals += 1
            if battery < 25:
                points += 1
                reasons.append(f"Body Battery nur noch {battery}")

        g_sleep = (garmin.get("schlaf") or {}).get("schlaf_stunden")
        if g_sleep is not None and not (whoop and (whoop.get("heute") or {}).get("schlaf")):
            signals += 1
            if g_sleep < 6:
                points += 1
                reasons.append(f"Nur {g_sleep:.1f} h Schlaf (Garmin)")

    if signals == 0:
        return StressResult("unbekannt", 0, ["Keine Gesundheitsdaten verfügbar"], [])

    if points >= 4:
        level = "hoch"
        tips = [
            "5 Minuten Box-Breathing: 4 s ein, 4 s halten, 4 s aus, 4 s halten",
            "Heute kein hartes Training, lieber Spaziergang oder Mobility",
            "Wichtigste Aufgabe des Tages auswählen, Rest verschieben",
            "Früher ins Bett, Handy 1 h vorher weg",
        ]
    elif points >= 2:
        level = "mittel"
        tips = [
            "Kurze Pause und Wasser trinken",
            "Moderates Training ist ok, auf den Körper hören",
            "Abends 15 Minuten ohne Bildschirm runterfahren",
        ]
    else:
        level = "niedrig"
        tips = ["Gute Werte, guter Tag für Fokus-Arbeit oder intensives Training"]
    return StressResult(level, points, reasons or ["Alle Werte im normalen Bereich"], tips)
