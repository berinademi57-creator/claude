"""Anrufe, SMS und Push-Nachrichten an DICH.

- Anruf + SMS über Twilio (Jarvis ruft deine eigene Nummer an und spricht).
- Push über Telegram (kostenlos, auf Handy + PC).

Absichtlich nur an deine eigene Nummer / deinen eigenen Chat, damit Jarvis
niemals fremde Leute anruft oder zuspammt.
"""

from __future__ import annotations

from xml.sax.saxutils import escape

from . import http
from .settings import Settings

TWILIO_API = "https://api.twilio.com/2010-04-01/Accounts"
MAX_SAY_CHARS = 1500


def _twilio(settings: Settings) -> tuple[str, str, str, str]:
    return (
        settings.require("TWILIO_ACCOUNT_SID"),
        settings.require("TWILIO_AUTH_TOKEN"),
        settings.require("TWILIO_FROM_NUMBER"),
        settings.require("MY_PHONE_NUMBER"),
    )


def build_twiml(message: str, voice: str, language: str, repeat: bool = True) -> str:
    text = escape(message.strip()[:MAX_SAY_CHARS])
    say = f'<Say voice="{escape(voice)}" language="{escape(language)}">{text}</Say>'
    parts = [say]
    if repeat:
        parts.append('<Pause length="1"/>')
        parts.append(
            f'<Say voice="{escape(voice)}" language="{escape(language)}">'
            "Ich wiederhole.</Say>"
        )
        parts.append(say)
    return "<Response>" + "".join(parts) + "</Response>"


def call_me(settings: Settings, message: str) -> str:
    """Ruft deine Nummer an und liest die Nachricht vor."""
    if not message.strip():
        raise ValueError("Nachricht ist leer.")
    sid, token, from_nr, to_nr = _twilio(settings)
    twiml = build_twiml(
        message,
        voice=settings.get("TWILIO_VOICE", "Polly.Daniel-Neural"),
        language=settings.get("TWILIO_LANGUAGE", "de-DE"),
    )
    resp = http.post(
        f"{TWILIO_API}/{sid}/Calls.json",
        form={"To": to_nr, "From": from_nr, "Twiml": twiml},
        basic_auth=(sid, token),
    )
    return f"Anruf gestartet (ID {resp.get('sid', '?')})."


def sms_me(settings: Settings, message: str) -> str:
    sid, token, from_nr, to_nr = _twilio(settings)
    resp = http.post(
        f"{TWILIO_API}/{sid}/Messages.json",
        form={"To": to_nr, "From": from_nr, "Body": message[:1500]},
        basic_auth=(sid, token),
    )
    return f"SMS gesendet (ID {resp.get('sid', '?')})."


def telegram_me(settings: Settings, message: str) -> str:
    token = settings.require("TELEGRAM_BOT_TOKEN")
    chat_id = settings.require("TELEGRAM_CHAT_ID")
    http.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        form={"chat_id": chat_id, "text": message[:4000]},
    )
    return "Telegram-Nachricht gesendet."


def notify(settings: Settings, message: str, *, call: bool = False) -> list[str]:
    """Benachrichtigt über alle eingerichteten Wege; Fehler stoppen nichts."""
    results: list[str] = []
    if settings.get("TELEGRAM_BOT_TOKEN") and settings.get("TELEGRAM_CHAT_ID"):
        try:
            results.append(telegram_me(settings, message))
        except Exception as exc:  # noqa: BLE001
            results.append(f"Telegram-Fehler: {exc}")
    if call and settings.get("TWILIO_ACCOUNT_SID"):
        try:
            results.append(call_me(settings, message))
        except Exception as exc:  # noqa: BLE001
            results.append(f"Anruf-Fehler: {exc}")
    return results
