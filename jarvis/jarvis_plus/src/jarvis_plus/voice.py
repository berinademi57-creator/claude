"""Stimme: Text→Sprache und Sprache→Text über ElevenLabs.

Für das HUD (MP3) und für Telegram-Sprachnachrichten (OGG/Opus).
Der ElevenLabs-Key braucht die Rechte „Text to Speech“ und „Speech to Text“.
"""

from __future__ import annotations

import json
import urllib.request
import uuid

from .settings import Settings

API = "https://api.elevenlabs.io/v1"
DEFAULT_VOICE = "onwK4e9ZLuTAKqWW03F9"  # „Daniel“: tiefe, ruhige Erzähler-Stimme


def available(settings: Settings) -> bool:
    return bool(settings.get("ELEVENLABS_API_KEY"))


def tts(settings: Settings, text: str, fmt: str = "mp3_44100_128") -> bytes:
    """Text sprechen. fmt: mp3_44100_128 (HUD) oder opus_48000_64 (Telegram)."""
    voice = settings.get("ELEVENLABS_VOICE_ID", DEFAULT_VOICE)
    body = json.dumps({
        "text": text[:2000],
        "model_id": settings.get("ELEVENLABS_MODEL", "eleven_flash_v2_5"),
        "language_code": "de",
        "voice_settings": {"stability": 0.45, "similarity_boost": 0.8, "style": 0.35},
    }).encode()
    req = urllib.request.Request(
        f"{API}/text-to-speech/{voice}?output_format={fmt}",
        data=body,
        headers={"xi-api-key": settings.require("ELEVENLABS_API_KEY"), "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def multipart(fields: dict[str, str], files: dict[str, tuple[str, bytes, str]]) -> tuple[bytes, str]:
    """multipart/form-data bauen (ohne Zusatzpakete)."""
    boundary = uuid.uuid4().hex
    parts: list[bytes] = []
    for name, value in fields.items():
        parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode())
    for name, (filename, data, ctype) in files.items():
        parts.append(
            f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"; filename="{filename}"\r\n'
            f"Content-Type: {ctype}\r\n\r\n".encode() + data + b"\r\n"
        )
    parts.append(f"--{boundary}--\r\n".encode())
    return b"".join(parts), f"multipart/form-data; boundary={boundary}"


def stt(settings: Settings, audio: bytes, filename: str = "voice.ogg") -> str:
    """Sprachnachricht in Text umwandeln (ElevenLabs Scribe)."""
    body, ctype = multipart(
        {"model_id": settings.get("ELEVENLABS_STT_MODEL", "scribe_v1"), "language_code": "deu"},
        {"file": (filename, audio, "audio/ogg")},
    )
    req = urllib.request.Request(
        f"{API}/speech-to-text", data=body,
        headers={"xi-api-key": settings.require("ELEVENLABS_API_KEY"), "Content-Type": ctype},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return (json.loads(resp.read().decode()).get("text") or "").strip()
