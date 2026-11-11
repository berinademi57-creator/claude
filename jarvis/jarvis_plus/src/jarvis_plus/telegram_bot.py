"""Telegram mit Sprache: Text UND Sprachnachrichten in beide Richtungen.

- Du schreibst oder schickst eine Sprachnachricht → Jarvis antwortet
  (auf Sprachnachrichten mit einer Sprachnachricht in seiner Stimme).
- Nur dein Chat (TELEGRAM_CHAT_ID) wird beantwortet.
Läuft im HUD-Prozess mit (Autostart). Ersetzt den Telegram-Kanal von OpenJarvis.
"""

from __future__ import annotations

import json
import time
import urllib.request
from typing import Any

from . import activity, voice
from .settings import Settings, load_settings

API = "https://api.telegram.org"


def _call(token: str, method: str, params: dict[str, Any] | None = None, timeout: int = 70) -> Any:
    data = json.dumps(params or {}).encode()
    req = urllib.request.Request(f"{API}/bot{token}/{method}", data=data,
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode()).get("result")


def _download(token: str, file_id: str) -> bytes:
    info = _call(token, "getFile", {"file_id": file_id}, timeout=30)
    with urllib.request.urlopen(f"{API}/file/bot{token}/{info['file_path']}", timeout=60) as resp:
        return resp.read()


def send_voice(settings: Settings, chat_id: str, text: str, caption: str = "") -> None:
    audio = voice.tts(settings, text, fmt="opus_48000_64")
    body, ctype = voice.multipart(
        {"chat_id": chat_id, "caption": caption[:1000]},
        {"voice": ("jarvis.ogg", audio, "audio/ogg")},
    )
    req = urllib.request.Request(f"{API}/bot{settings.require('TELEGRAM_BOT_TOKEN')}/sendVoice",
                                 data=body, headers={"Content-Type": ctype}, method="POST")
    urllib.request.urlopen(req, timeout=60).read()


def _answer(settings: Settings, text: str, history: list[dict[str, str]], spoken: bool) -> str:
    from .hud_server import _ask_openjarvis, choose_model, trim_history
    from .phone_line import CALL_HINT

    model, text = choose_model(text, settings)
    prompt = (CALL_HINT + text) if spoken else text
    data = _ask_openjarvis(settings, model, trim_history(history) + [{"role": "user", "content": prompt}])
    return data["choices"][0]["message"]["content"] or "…"


def run_forever() -> None:
    offset = 0
    history: list[dict[str, str]] = []
    while True:
        settings = load_settings()
        token, me = settings.get("TELEGRAM_BOT_TOKEN"), settings.get("TELEGRAM_CHAT_ID")
        if not token or not me:
            time.sleep(60)
            continue
        try:
            updates = _call(token, "getUpdates", {"offset": offset, "timeout": 50}) or []
        except Exception:  # noqa: BLE001
            time.sleep(5)
            continue
        for upd in updates:
            offset = upd["update_id"] + 1
            msg = upd.get("message") or {}
            chat_id = str((msg.get("chat") or {}).get("id", ""))
            if chat_id != str(me):
                continue  # nur Boss Ademi
            spoken = bool(msg.get("voice") or msg.get("audio"))
            try:
                _call(token, "sendChatAction", {"chat_id": chat_id, "action": "record_voice" if spoken else "typing"}, 10)
                if spoken:
                    media = msg.get("voice") or msg.get("audio")
                    text = voice.stt(settings, _download(token, media["file_id"]))
                    activity.log("telegram", "Sprachnachricht", status="start", detail=text[:120])
                else:
                    text = (msg.get("text") or "").strip()
                    activity.log("telegram", "Nachricht", status="start", detail=text[:120])
                if not text:
                    continue
                reply = _answer(settings, text, history, spoken)
                history += [{"role": "user", "content": text}, {"role": "assistant", "content": reply}]
                history[:] = history[-20:]
                if spoken and voice.available(settings):
                    from .phone_line import speakable

                    send_voice(settings, chat_id, speakable(reply), caption=reply if len(reply) > 300 else "")
                else:
                    _call(token, "sendMessage", {"chat_id": chat_id, "text": reply[:4000]}, 30)
                activity.log("telegram", "Antwort gesendet", status="ok")
            except Exception as exc:  # noqa: BLE001
                activity.log("telegram", "Telegram-Fehler", status="error", detail=str(exc)[:200])
                try:
                    _call(token, "sendMessage", {"chat_id": chat_id,
                                                 "text": f"⚠️ Da hat etwas nicht geklappt: {str(exc)[:300]}"}, 30)
                except Exception:  # noqa: BLE001
                    pass
