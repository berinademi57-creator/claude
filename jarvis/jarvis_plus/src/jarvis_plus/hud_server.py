"""Jarvis HUD: die Oberfläche (PC + Handy) mit Orb, Stimme und Live-Aktivität.

Start: ``jarvis-plus hud`` → http://localhost:8765
Spricht mit OpenJarvis (``jarvis serve``, Port 8000) und zeigt alles live an,
was Jarvis gerade tut.
"""

from __future__ import annotations

import asyncio
import collections
import contextlib
import ipaddress
import json
import re
import secrets
import time
import urllib.error
import urllib.request
from importlib import resources
from pathlib import Path
from typing import Any

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import (
    FileResponse,
    HTMLResponse,
    JSONResponse,
    Response,
    StreamingResponse,
)
from starlette.routing import Route

from . import access, activity, websites
from .settings import Settings, load_settings

# --------------------------------------------------------------- Modellwahl
# Günstig + schnell für Alltag, stark nur wenn nötig (Websites, Code, Strategie).
SMART_PATTERN = re.compile(
    r"website|webseite|landing ?page|homepage|onlineshop|\bshop\b|seite (bauen|erstellen)|"
    r"bau (mir|eine?n?)|baue|programmier|\bcode\b|\bapp\b|skript|strategie|businessplan|"
    r"angebot (schreib|erstell)|offerte|analysier|konzept|design",
    re.IGNORECASE,
)


def choose_model(text: str, settings: Settings) -> tuple[str, str]:
    fast = settings.get("JARVIS_MODEL_FAST", "claude-haiku-5-5")
    smart = settings.get("JARVIS_MODEL_SMART", "claude-sonnet-5-5")
    stripped = text.strip().lower()
    if stripped.startswith("/smart"):
        return smart, text.strip()[6:].strip()
    if stripped.startswith("/schnell"):
        return fast, text.strip()[8:].strip()
    return (smart if SMART_PATTERN.search(text) else fast), text


def trim_history(history: list[dict[str, Any]], keep: int = 10) -> list[dict[str, str]]:
    """Nur die letzten Nachrichten mitschicken: spart Tokens = spart Geld."""
    out = []
    for msg in history[-keep:]:
        role = msg.get("role")
        content = str(msg.get("content", ""))
        if role in ("user", "assistant") and content:
            out.append({"role": role, "content": content[:4000]})
    return out


# --------------------------------------------------------------- OpenJarvis


def _openjarvis_url(settings: Settings) -> str:
    return settings.get("OPENJARVIS_URL", "http://127.0.0.1:8000").rstrip("/")


def _ask_openjarvis(settings: Settings, model: str, messages: list[dict[str, str]]) -> dict:
    body = json.dumps({"model": model, "messages": messages, "stream": False}).encode()
    headers = {"Content-Type": "application/json"}
    key = settings.get("OPENJARVIS_API_KEY")
    if key:
        headers["Authorization"] = f"Bearer {key}"
    req = urllib.request.Request(
        f"{_openjarvis_url(settings)}/v1/chat/completions", data=body, headers=headers, method="POST"
    )
    with urllib.request.urlopen(req, timeout=600) as resp:
        return json.loads(resp.read().decode())


# --------------------------------------------------------------- Stimme (ElevenLabs)
from . import voice as _voice


def _tts_provider(settings: Settings) -> str:
    return "elevenlabs" if _voice.available(settings) else "browser"


def _elevenlabs(settings: Settings, text: str) -> bytes:
    return _voice.tts(settings, text)


def _openjarvis_online(settings: Settings) -> bool:
    try:
        with urllib.request.urlopen(f"{_openjarvis_url(settings)}/health", timeout=2):
            return True
    except Exception:  # noqa: BLE001
        return False


# Live-Tool-Ereignisse aus OpenJarvis (eingebaute Tools wie web_search).
_bridge: collections.deque[tuple[int, dict]] = collections.deque(maxlen=200)
_bridge_seq = 0
JARVIS_PLUS_TOOLS: set[str] = set()


async def _openjarvis_event_bridge(settings: Settings) -> None:
    global _bridge_seq
    try:
        import websockets  # type: ignore[import-not-found]
    except ImportError:
        return
    url = _openjarvis_url(settings).replace("http", "ws", 1) + "/v1/agents/events"
    while True:
        try:
            headers = {}
            if settings.get("OPENJARVIS_API_KEY"):
                headers["Authorization"] = f"Bearer {settings.get('OPENJARVIS_API_KEY')}"
            async with websockets.connect(url, additional_headers=headers) as ws:
                async for raw in ws:
                    msg = json.loads(raw)
                    data = msg.get("data") or {}
                    tool = data.get("tool")
                    if not tool or tool in JARVIS_PLUS_TOOLS:
                        continue  # jarvis-plus Tools protokollieren sich selbst
                    kind = msg.get("type", "")
                    _bridge_seq += 1
                    _bridge.append(
                        (
                            _bridge_seq,
                            {
                                "ts": msg.get("timestamp") or time.time(),
                                "kind": "tool",
                                "title": tool,
                                "status": "start" if kind.endswith("start") else "ok",
                                "detail": "",
                            },
                        )
                    )
        except Exception:  # noqa: BLE001
            await asyncio.sleep(5)


# --------------------------------------------------------------- Zugriffsschutz


def _is_local(request: Request) -> bool:
    host = request.client.host if request.client else ""
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return host in ("localhost", "testclient")


def _authorized(request: Request, settings: Settings) -> bool:
    token = settings.get("HUD_TOKEN")
    if not token:
        return _is_local(request)
    given = (
        request.query_params.get("token")
        or request.cookies.get("jarvis_token")
        or request.headers.get("x-jarvis-token", "")
    )
    return secrets.compare_digest(given, token)


def _deny() -> Response:
    return HTMLResponse(
        "<body style='background:#000;color:#f33;font-family:monospace;padding:40px'>"
        "ZUGRIFF VERWEIGERT · öffne den Link mit ?token=… (HUD_TOKEN)</body>",
        status_code=401,
    )


# --------------------------------------------------------------- Routen

_health_cache: dict[str, Any] = {"ts": 0, "data": None}

DEMO_HEALTH = {
    "whoop": {
        "heute": {
            "recovery": {"recovery_prozent": 41, "hrv_ms": 48.2, "ruhepuls": 58},
            "schlaf": {"schlaf_stunden": 6.4},
            "zyklus": {"strain": 12.7},
        },
        "baseline": {"hrv_ms": 61.0, "ruhepuls": 54.0},
    },
    "garmin": {"tag": {"body_battery_aktuell": 34, "schritte": 8412, "stress_durchschnitt": 42}},
}


def _asset(name: str) -> Path:
    return Path(str(resources.files("jarvis_plus") / "hud" / name))


async def index(request: Request) -> Response:
    settings = load_settings()
    if not _authorized(request, settings):
        return _deny()
    resp = FileResponse(_asset("index.html"), media_type="text/html")
    if request.query_params.get("token"):
        resp.set_cookie("jarvis_token", request.query_params["token"], httponly=True,
                        samesite="strict", max_age=60 * 60 * 24 * 365)
    return resp


async def asset(request: Request) -> Response:
    name = request.path_params["name"]
    if name not in ("manifest.webmanifest", "icon.svg"):
        return Response(status_code=404)
    media = "application/manifest+json" if name.endswith("webmanifest") else "image/svg+xml"
    return FileResponse(_asset(name), media_type=media)


async def api_tts(request: Request) -> Response:
    settings = load_settings()
    if not _authorized(request, settings):
        return _deny()
    if _tts_provider(settings) != "elevenlabs":
        return JSONResponse({"error": "keine Premium-Stimme eingerichtet"}, status_code=404)
    text = str((await request.json()).get("text", "")).strip()
    if not text:
        return JSONResponse({"error": "leer"}, status_code=400)
    try:
        audio = await asyncio.to_thread(_elevenlabs, settings, text)
    except Exception as exc:  # noqa: BLE001
        activity.log("stimme", "ElevenLabs", status="error", detail=str(exc)[:200])
        return JSONResponse({"error": str(exc)[:200]}, status_code=502)
    return Response(audio, media_type="audio/mpeg")


async def api_status(request: Request) -> Response:
    settings = load_settings()
    if not _authorized(request, settings):
        return _deny()
    return JSONResponse(
        {
            "name": settings.name,
            "openjarvis": await asyncio.to_thread(_openjarvis_online, settings),
            "modelle": {
                "schnell": settings.get("JARVIS_MODEL_FAST", "claude-haiku-5-5"),
                "stark": settings.get("JARVIS_MODEL_SMART", "claude-sonnet-5-5"),
            },
            "zugriffe": access.status(settings),
            "websites": websites.list_sites(),
            "stimme": _tts_provider(settings),
        }
    )


async def api_health(request: Request) -> Response:
    settings = load_settings()
    if not _authorized(request, settings):
        return _deny()
    if settings.get("JARVIS_DEMO") == "1":
        from . import stress

        data = dict(DEMO_HEALTH)
        data["stress"] = stress.assess(data["whoop"], data["garmin"]).as_dict()
        return JSONResponse(data)
    fresh = request.query_params.get("refresh") == "1"
    if fresh or time.time() - _health_cache["ts"] > 600 or _health_cache["data"] is None:
        from .server import _collect_health

        _health_cache["data"] = await asyncio.to_thread(_collect_health)
        _health_cache["ts"] = time.time()
    return JSONResponse(_health_cache["data"])


async def api_chat(request: Request) -> Response:
    settings = load_settings()
    if not _authorized(request, settings):
        return _deny()
    body = await request.json()
    text = str(body.get("message", "")).strip()
    if not text:
        return JSONResponse({"error": "Leere Nachricht"}, status_code=400)
    model, text = choose_model(text, settings)
    prompt = text
    if body.get("mode") == "call":  # Anruf-Modus im HUD: kurze, gesprochene Antworten
        from .phone_line import CALL_HINT

        prompt = CALL_HINT + text
    messages = trim_history(body.get("history") or []) + [{"role": "user", "content": prompt}]
    started = time.time()
    activity.log("chat", "Auftrag", status="start", detail=text[:120], modell=model)
    try:
        data = await asyncio.to_thread(_ask_openjarvis, settings, model, messages)
        reply = data["choices"][0]["message"]["content"] or ""
    except urllib.error.URLError:
        reply = "OpenJarvis läuft gerade nicht. Starte es mit `jarvis start`."
        activity.log("chat", "Auftrag", status="error", detail="OpenJarvis nicht erreichbar")
        return JSONResponse({"reply": reply, "model": model, "error": True})
    except Exception as exc:  # noqa: BLE001
        activity.log("chat", "Auftrag", status="error", detail=str(exc))
        return JSONResponse({"reply": f"Fehler: {exc}", "model": model, "error": True})
    dauer = round(time.time() - started, 1)
    activity.log("chat", "Auftrag", status="ok", modell=model, dauer=dauer)
    return JSONResponse({"reply": reply, "model": model, "dauer": dauer})


async def api_events(request: Request) -> Response:
    settings = load_settings()
    if not _authorized(request, settings):
        return _deny()

    async def stream():
        events = activity.recent(30)
        for ev in events:
            ev["replay"] = True  # alte Ereignisse: nur anzeigen, nichts auslösen
            yield f"data: {json.dumps(ev, ensure_ascii=False)}\n\n"
        offset = activity.log_file().stat().st_size if activity.log_file().exists() else 0
        last_bridge = _bridge_seq
        idle = 0
        while not await request.is_disconnected():
            new, offset = activity.read_from(offset)
            for ev in new:
                yield f"data: {json.dumps(ev, ensure_ascii=False)}\n\n"
            for seq, ev in list(_bridge):
                if seq > last_bridge:
                    last_bridge = seq
                    yield f"data: {json.dumps(ev, ensure_ascii=False)}\n\n"
            idle += 1
            if idle >= 30:  # Keep-alive alle ~15 s
                idle = 0
                yield ": ping\n\n"
            await asyncio.sleep(0.5)

    return StreamingResponse(
        stream(), media_type="text/event-stream", headers={"Cache-Control": "no-cache"}
    )


async def site_file(request: Request) -> Response:
    settings = load_settings()
    if not _authorized(request, settings):
        return _deny()
    name = websites.slugify(request.path_params["name"])
    rel = request.path_params.get("path") or "index.html"
    site_dir = websites.sites_root() / name
    try:
        target = websites._safe_path(site_dir, rel)
    except ValueError:
        return Response(status_code=404)
    if target.is_dir():
        target = target / "index.html"
    if not target.is_file():
        return Response("Nicht gefunden", status_code=404)
    return FileResponse(target)


def create_app() -> Starlette:
    from . import server

    JARVIS_PLUS_TOOLS.update(
        name for name, obj in vars(server).items() if callable(obj) and getattr(obj, "__wrapped__", None)
    )
    settings = load_settings()

    @contextlib.asynccontextmanager
    async def lifespan(_app: Starlette):
        task = asyncio.get_running_loop().create_task(_openjarvis_event_bridge(settings))
        try:
            yield
        finally:
            task.cancel()

    return Starlette(
        routes=[
            Route("/", index),
            Route("/api/status", api_status),
            Route("/api/health", api_health),
            Route("/api/chat", api_chat, methods=["POST"]),
            Route("/api/tts", api_tts, methods=["POST"]),
            Route("/api/events", api_events),
            Route("/sites/{name}/", site_file),
            Route("/sites/{name}/{path:path}", site_file),
            Route("/{name}", asset),
        ],
        lifespan=lifespan,
    )


def run(host: str | None = None, port: int | None = None) -> None:
    import uvicorn

    settings = load_settings()
    host = host or settings.get("HUD_HOST", "127.0.0.1")
    port = port or settings.get_int("HUD_PORT", 8765)
    is_loopback = host in ("127.0.0.1", "localhost", "::1")
    if not is_loopback and not settings.get("HUD_TOKEN"):
        raise RuntimeError(
            "HUD im Netzwerk nur mit Passwort: setze HUD_TOKEN in jarvis-plus.env "
            "(oder nutze Tailscale: `tailscale serve --bg 8765`)."
        )
    print(f"Jarvis HUD läuft: http://{'localhost' if is_loopback else host}:{port}")
    servers = [uvicorn.Server(uvicorn.Config(create_app(), host=host, port=port, log_level="warning"))]

    from . import phone_line

    if phone_line.enabled(settings):
        phone_port = settings.get_int("PHONE_PORT", 8766)
        # Nur lokal; nach aussen geht nur dieser Port über Tailscale Funnel.
        servers.append(uvicorn.Server(uvicorn.Config(
            phone_line.create_app(), host="127.0.0.1", port=phone_port, log_level="warning")))
        print(f"Telefon-Leitung aktiv (Port {phone_port}, Nummer {settings.get('TWILIO_FROM_NUMBER')})")

    async def serve_all() -> None:
        import threading

        from . import telegram_bot

        # Telegram (Text + Sprachnachrichten) im Hintergrund mitlaufen lassen
        threading.Thread(target=telegram_bot.run_forever, daemon=True).start()
        await asyncio.gather(*(srv.serve() for srv in servers))

    asyncio.run(serve_all())
