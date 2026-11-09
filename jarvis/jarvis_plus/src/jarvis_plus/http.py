"""Kleiner HTTP-Helfer auf Basis der Standardbibliothek (keine Extra-Pakete)."""

from __future__ import annotations

import base64
import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Mapping

TIMEOUT = 30


class HttpError(RuntimeError):
    def __init__(self, status: int, body: str, url: str) -> None:
        super().__init__(f"HTTP {status} bei {url}: {body[:500]}")
        self.status = status
        self.body = body


def request(
    method: str,
    url: str,
    *,
    params: Mapping[str, Any] | None = None,
    form: Mapping[str, Any] | None = None,
    headers: Mapping[str, str] | None = None,
    basic_auth: tuple[str, str] | None = None,
    bearer: str | None = None,
) -> Any:
    """HTTP-Request senden und JSON (oder Text) zurückgeben."""
    if params:
        clean = {k: v for k, v in params.items() if v is not None}
        url = f"{url}?{urllib.parse.urlencode(clean)}"
    data = None
    hdrs = {"Accept": "application/json", "User-Agent": "jarvis-plus/0.1"}
    if headers:
        hdrs.update(headers)
    if form is not None:
        data = urllib.parse.urlencode(
            {k: v for k, v in form.items() if v is not None}
        ).encode()
        hdrs["Content-Type"] = "application/x-www-form-urlencoded"
    if basic_auth:
        token = base64.b64encode(f"{basic_auth[0]}:{basic_auth[1]}".encode()).decode()
        hdrs["Authorization"] = f"Basic {token}"
    if bearer:
        hdrs["Authorization"] = f"Bearer {bearer}"

    req = urllib.request.Request(url, data=data, headers=hdrs, method=method)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            body = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise HttpError(exc.code, body, url.split("?")[0]) from None
    if not body:
        return {}
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return body


def get(url: str, **kwargs: Any) -> Any:
    return request("GET", url, **kwargs)


def post(url: str, **kwargs: Any) -> Any:
    return request("POST", url, **kwargs)
