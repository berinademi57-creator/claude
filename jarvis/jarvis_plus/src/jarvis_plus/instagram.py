"""Instagram über die offizielle Instagram-API (Business-/Creator-Account).

Was die offizielle API erlaubt: eigene Posts + Kommentare lesen, auf
Kommentare antworten, Fotos veröffentlichen, Statistiken abrufen.
DMs lesen/senden braucht eine geprüfte Meta-App und ist hier nicht drin.
Feed scrollen, liken, folgen usw. ist über die API nicht möglich (und per
Bot gegen die Instagram-Regeln, dein Account könnte gesperrt werden).
"""

from __future__ import annotations

import time
from typing import Any

from . import http
from .settings import Settings


def _base(settings: Settings) -> str:
    version = settings.get("INSTAGRAM_API_VERSION", "v23.0")
    return f"https://graph.instagram.com/{version}"


def _token(settings: Settings) -> str:
    return settings.require("INSTAGRAM_ACCESS_TOKEN")


def account(settings: Settings) -> dict[str, Any]:
    return http.get(
        f"{_base(settings)}/me",
        params={
            "fields": "user_id,username,name,followers_count,follows_count,media_count",
            "access_token": _token(settings),
        },
    )


def recent_posts(settings: Settings, limit: int = 10) -> list[dict[str, Any]]:
    data = http.get(
        f"{_base(settings)}/me/media",
        params={
            "fields": "id,caption,media_type,permalink,timestamp,like_count,comments_count",
            "limit": max(1, min(limit, 50)),
            "access_token": _token(settings),
        },
    )
    return data.get("data", [])


def comments(settings: Settings, media_id: str) -> list[dict[str, Any]]:
    data = http.get(
        f"{_base(settings)}/{media_id}/comments",
        params={
            "fields": "id,text,username,timestamp",
            "access_token": _token(settings),
        },
    )
    return data.get("data", [])


def reply_to_comment(settings: Settings, comment_id: str, message: str) -> str:
    resp = http.post(
        f"{_base(settings)}/{comment_id}/replies",
        form={"message": message, "access_token": _token(settings)},
    )
    return f"Antwort gepostet (ID {resp.get('id', '?')})."


def publish_photo(settings: Settings, image_url: str, caption: str) -> str:
    """Foto posten. image_url muss eine öffentlich erreichbare JPEG-URL sein."""
    user_id = account(settings).get("user_id") or "me"
    container = http.post(
        f"{_base(settings)}/{user_id}/media",
        form={
            "image_url": image_url,
            "caption": caption,
            "access_token": _token(settings),
        },
    )
    creation_id = container["id"]
    for _ in range(10):  # warten, bis Instagram das Bild verarbeitet hat
        status = http.get(
            f"{_base(settings)}/{creation_id}",
            params={"fields": "status_code", "access_token": _token(settings)},
        )
        if status.get("status_code") in ("FINISHED", None):
            break
        if status.get("status_code") == "ERROR":
            raise RuntimeError("Instagram konnte das Bild nicht verarbeiten.")
        time.sleep(3)
    resp = http.post(
        f"{_base(settings)}/{user_id}/media_publish",
        form={"creation_id": creation_id, "access_token": _token(settings)},
    )
    return f"Gepostet (Media-ID {resp.get('id', '?')})."


def insights(settings: Settings, metrics: str = "reach,views,profile_views") -> Any:
    return http.get(
        f"{_base(settings)}/me/insights",
        params={
            "metric": metrics,
            "period": "day",
            "metric_type": "total_value",
            "access_token": _token(settings),
        },
    )
