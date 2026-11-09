"""Echte Telefonate mit Jarvis (Twilio ConversationRelay).

Du rufst deine Twilio-Nummer an (oder Jarvis ruft dich an) und redest ganz
normal. Twilio wandelt Sprache in Text um, Jarvis antwortet, Twilio liest vor.

Sicherheit (der Endpunkt ist öffentlich erreichbar, über Tailscale Funnel):
- geheimer Pfad (PHONE_SECRET) in jeder URL
- Twilio-Signatur wird geprüft (mit TWILIO_AUTH_TOKEN)
- nur Anrufe von DEINER Nummer (MY_PHONE_NUMBER) werden angenommen
- der Sprach-Kanal akzeptiert nur Anrufe, die vorher geprüft wurden
- läuft auf eigenem Port (8766), das HUD ist darüber NICHT erreichbar
"""

from __future__ import annotations

import asyncio
import base64
import hashlib
import hmac
import json
import secrets
import shutil
import subprocess
import time
import urllib.parse
from typing import Any
from xml.sax.saxutils import quoteattr

from . import activity
from . import net as http
from .settings import Settings, data_path, load_settings, set_value, write_private

TWILIO_API = "https://api.twilio.com/2010-04-01/Accounts"
CALL_TTL = 3 * 3600
CALL_HINT = (
    "[Telefonat: antworte wie am Telefon, kurz in 1–3 Sätzen, ohne Listen, Links, "
    "Emojis oder Markdown] "
)


# ------------------------------------------------------------------ Hilfen


def speakable(text: str) -> str:
    """Markdown, Links und Emojis entfernen, damit es am Telefon natürlich klingt."""
    import re

    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)      # [Text](link) → Text
    text = re.sub(r"https?://\S+", "Link per Telegram", text)
    text = re.sub(r"[*_`#>|]+", "", text)
    text = re.sub(r"^\s*[-•]\s+", "", text, flags=re.M)
    text = re.sub(r"[\U0001F000-\U0001FAFF\u2600-\u27BF]", "", text)
    return re.sub(r"\s+", " ", text).strip()[:1500]


def twilio_signature(auth_token: str, url: str, params: dict[str, str]) -> str:
    """Signatur wie Twilio sie berechnet: HMAC-SHA1(URL + sortierte Parameter)."""
    payload = url + "".join(k + params[k] for k in sorted(params))
    digest = hmac.new(auth_token.encode(), payload.encode(), hashlib.sha1).digest()
    return base64.b64encode(digest).decode()


def public_base(settings: Settings) -> str:
    base = settings.require("PHONE_PUBLIC_URL").rstrip("/")
    if not base.startswith("https://"):
        raise RuntimeError("PHONE_PUBLIC_URL muss mit https:// beginnen.")
    return base


def voice_url(settings: Settings) -> str:
    return f"{public_base(settings)}/twilio/voice/{settings.require('PHONE_SECRET')}"


def relay_url(settings: Settings) -> str:
    base = public_base(settings).replace("https://", "wss://", 1)
    return f"{base}/twilio/relay/{settings.require('PHONE_SECRET')}"


def relay_twiml(settings: Settings, greeting: str) -> str:
    attrs = {
        "url": relay_url(settings),
        "welcomeGreeting": greeting[:300],
        "language": settings.get("PHONE_LANGUAGE", "de-DE"),
    }
    if settings.get("PHONE_TTS_PROVIDER"):
        attrs["ttsProvider"] = settings.get("PHONE_TTS_PROVIDER")
    if settings.get("PHONE_VOICE"):
        attrs["voice"] = settings.get("PHONE_VOICE")
    attr_text = " ".join(f"{k}={quoteattr(v)}" for k, v in attrs.items())
    return f"<Response><Connect><ConversationRelay {attr_text}/></Connect></Response>"


def _calls_file():
    return data_path("phone-calls.json")


def allow_call(call_sid: str) -> None:
    path = _calls_file()
    try:
        calls = json.loads(path.read_text()) if path.exists() else {}
    except json.JSONDecodeError:
        calls = {}
    now = time.time()
    calls = {k: v for k, v in calls.items() if now - v < CALL_TTL}
    calls[call_sid] = now
    write_private(path, json.dumps(calls))


def is_allowed(call_sid: str) -> bool:
    try:
        calls = json.loads(_calls_file().read_text())
    except (OSError, json.JSONDecodeError):
        return False
    ts = calls.get(call_sid)
    return bool(ts) and time.time() - ts < CALL_TTL


def _same_number(a: str, b: str) -> bool:
    norm = lambda n: "".join(c for c in n if c.isdigit())  # noqa: E731
    return bool(a) and norm(a) == norm(b)


# ------------------------------------------------------------------ Anruf starten


def call_me_conversation(settings: Settings, greeting: str) -> str:
    """Jarvis ruft dich an und ihr könnt richtig miteinander reden."""
    sid = settings.require("TWILIO_ACCOUNT_SID")
    token = settings.require("TWILIO_AUTH_TOKEN")
    resp = http.post(
        f"{TWILIO_API}/{sid}/Calls.json",
        form={
            "To": settings.require("MY_PHONE_NUMBER"),
            "From": settings.require("TWILIO_FROM_NUMBER"),
            "Twiml": relay_twiml(settings, greeting or f"Hey {settings.name}, hier ist Jarvis."),
        },
        basic_auth=(sid, token),
    )
    call_sid = resp.get("sid", "")
    if call_sid:
        allow_call(call_sid)
    activity.log("telefon", "Ich rufe dich an", status="info", detail=greeting[:120])
    return f"Anruf gestartet (ID {call_sid or '?'}). Du kannst direkt mit mir reden."


# ------------------------------------------------------------------ Server


def create_app():
    from starlette.applications import Starlette
    from starlette.requests import Request
    from starlette.responses import PlainTextResponse, Response
    from starlette.routing import Route, WebSocketRoute
    from starlette.websockets import WebSocket, WebSocketDisconnect

    from .hud_server import _ask_openjarvis, trim_history

    histories: dict[str, list[dict[str, str]]] = {}

    def secret_ok(settings: Settings, given: str) -> bool:
        expected = settings.get("PHONE_SECRET")
        return bool(expected) and secrets.compare_digest(given, expected)

    async def voice(request: Request) -> Response:
        settings = load_settings()
        if not secret_ok(settings, request.path_params["secret"]):
            return Response(status_code=404)
        params = dict(urllib.parse.parse_qsl((await request.body()).decode()))
        token = settings.get("TWILIO_AUTH_TOKEN")
        url = f"{public_base(settings)}{request.url.path}"
        if request.url.query:
            url += "?" + request.url.query
        given = request.headers.get("x-twilio-signature", "")
        if not token or not secrets.compare_digest(given, twilio_signature(token, url, params)):
            activity.log("telefon", "Anruf abgelehnt", status="error", detail="Signatur ungültig")
            return Response(status_code=403)
        caller = params.get("From", "")
        if params.get("Direction", "inbound") == "inbound" and not _same_number(
            caller, settings.get("MY_PHONE_NUMBER")
        ):
            activity.log("telefon", "Fremder Anruf abgelehnt", status="error", detail=caller[-4:].rjust(8, "•"))
            return Response("<Response><Reject/></Response>", media_type="text/xml")
        allow_call(params.get("CallSid", ""))
        activity.log("telefon", "Du rufst an", status="info")
        greeting = settings.get("PHONE_GREETING", f"Hey {settings.name}, was gibt's?")
        return Response(relay_twiml(settings, greeting), media_type="text/xml")

    async def relay(websocket: WebSocket) -> None:
        settings = load_settings()
        if not secret_ok(settings, websocket.path_params["secret"]):
            await websocket.close(code=1008)
            return
        await websocket.accept()
        call_sid = ""
        try:
            while True:
                msg = await websocket.receive_json()
                kind = msg.get("type")
                if kind == "setup":
                    call_sid = msg.get("callSid", "")
                    if not is_allowed(call_sid):
                        activity.log("telefon", "Sprach-Kanal abgelehnt", status="error")
                        await websocket.close(code=1008)
                        return
                    histories.setdefault(call_sid, [])
                elif kind == "prompt" and call_sid and msg.get("last", True):
                    text = str(msg.get("voicePrompt", "")).strip()
                    if not text:
                        continue
                    activity.log("telefon", "Telefon", status="start", detail=text[:120])
                    history = histories[call_sid]
                    messages = trim_history(history, keep=8) + [
                        {"role": "user", "content": CALL_HINT + text}
                    ]
                    model = settings.get("JARVIS_MODEL_FAST", "claude-haiku-5-5")
                    try:
                        data = await asyncio.to_thread(_ask_openjarvis, settings, model, messages)
                        reply = data["choices"][0]["message"]["content"] or "Hm, da fehlt mir gerade die Antwort."
                    except Exception:  # noqa: BLE001
                        reply = "Sorry, ich erreiche gerade mein Gehirn nicht. Versuch es gleich nochmal."
                    history += [{"role": "user", "content": text}, {"role": "assistant", "content": reply}]
                    await websocket.send_json({"type": "text", "token": speakable(reply), "last": True})
                    activity.log("telefon", "Telefon", status="ok", detail=reply[:120])
                elif kind == "error":
                    activity.log("telefon", "Telefon-Fehler", status="error", detail=str(msg.get("description", ""))[:200])
        except WebSocketDisconnect:
            pass
        finally:
            histories.pop(call_sid, None)
            if call_sid:
                activity.log("telefon", "Anruf beendet", status="info")

    async def health(_request: Request) -> Response:
        return PlainTextResponse("ok")

    return Starlette(
        routes=[
            Route("/twilio/voice/{secret}", voice, methods=["POST"]),
            WebSocketRoute("/twilio/relay/{secret}", relay),
            Route("/twilio/health", health),
        ]
    )


def enabled(settings: Settings) -> bool:
    return all(settings.get(k) for k in ("PHONE_SECRET", "PHONE_PUBLIC_URL", "TWILIO_AUTH_TOKEN"))


# ------------------------------------------------------------------ Einrichtung


def _tailscale_funnel(port: int, https_port: int) -> str | None:
    exe = shutil.which("tailscale")
    if not exe:
        return None
    subprocess.run([exe, "funnel", "--bg", f"--https={https_port}", str(port)], check=False)
    out = subprocess.run([exe, "status", "--json"], capture_output=True, text=True)
    try:
        dns = json.loads(out.stdout)["Self"]["DNSName"].rstrip(".")
    except (json.JSONDecodeError, KeyError):
        return None
    return f"https://{dns}:{https_port}" if https_port != 443 else f"https://{dns}"


def setup(settings: Settings) -> list[str]:
    """Alles für echte Telefonate einrichten. Gibt eine Liste von Schritten zurück."""
    log: list[str] = []
    if not settings.get("PHONE_SECRET"):
        set_value("PHONE_SECRET", secrets.token_urlsafe(24))
        log.append("✅ Geheimer Telefon-Schlüssel erzeugt")
    settings = load_settings()

    port = settings.get_int("PHONE_PORT", 8766)
    if not settings.get("PHONE_PUBLIC_URL"):
        url = _tailscale_funnel(port, 8443)
        if not url:
            raise RuntimeError(
                "Öffentliche Adresse fehlt. Installiere Tailscale, melde dich an und führe "
                "den Befehl erneut aus (oder setze PHONE_PUBLIC_URL selbst)."
            )
        set_value("PHONE_PUBLIC_URL", url)
        log.append(f"✅ Öffentliche Adresse über Tailscale Funnel: {url}")
        settings = load_settings()

    sid = settings.require("TWILIO_ACCOUNT_SID")
    token = settings.require("TWILIO_AUTH_TOKEN")
    number = settings.require("TWILIO_FROM_NUMBER")
    found = http.get(
        f"{TWILIO_API}/{sid}/IncomingPhoneNumbers.json",
        params={"PhoneNumber": number},
        basic_auth=(sid, token),
    )
    numbers = found.get("incoming_phone_numbers", []) if isinstance(found, dict) else []
    if not numbers:
        raise RuntimeError(f"Die Nummer {number} gehört nicht zu diesem Twilio-Konto.")
    http.post(
        f"{TWILIO_API}/{sid}/IncomingPhoneNumbers/{numbers[0]['sid']}.json",
        form={"VoiceUrl": voice_url(settings), "VoiceMethod": "POST"},
        basic_auth=(sid, token),
    )
    log.append(f"✅ Twilio-Nummer {number} leitet Anrufe an Jarvis")
    log.append("📞 Ruf jetzt deine Twilio-Nummer an. Jarvis muss laufen (jarvis-plus autostart).")
    return log


def describe(settings: Settings) -> dict[str, Any]:
    return {"aktiv": enabled(settings), "nummer": settings.get("TWILIO_FROM_NUMBER")}
