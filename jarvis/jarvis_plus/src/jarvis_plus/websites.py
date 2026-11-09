"""Websites speichern, ansehen und veröffentlichen.

- Speichern: ``~/Jarvis-Websites/<name>/index.html`` (+ weitere Dateien)
- Vorschau: im HUD unter ``/sites/<name>/`` (live, auch auf dem Handy)
- Veröffentlichen: Netlify (kostenlos), braucht NETLIFY_AUTH_TOKEN
"""

from __future__ import annotations

import io
import json
import os
import re
import urllib.request
import zipfile
from pathlib import Path
from typing import Any

from . import net as http
from .settings import Settings

NETLIFY_API = "https://api.netlify.com/api/v1"
MAX_FILE_BYTES = 5_000_000


def sites_root() -> Path:
    root = Path(os.environ.get("JARVIS_SITES_DIR", Path.home() / "Jarvis-Websites")).expanduser()
    root.mkdir(parents=True, exist_ok=True)
    return root


def slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower().replace("ä", "ae").replace("ö", "oe")
                  .replace("ü", "ue").replace("ß", "ss")).strip("-")
    if not slug:
        raise ValueError("Ungültiger Website-Name.")
    return slug[:60]


def _safe_path(site_dir: Path, rel: str) -> Path:
    target = (site_dir / rel).resolve()
    if site_dir.resolve() not in target.parents and target != site_dir.resolve():
        raise ValueError(f"Ungültiger Dateipfad: {rel}")
    return target


def save(name: str, files: dict[str, str]) -> dict[str, Any]:
    """Dateien einer Website speichern. files = {"index.html": "...", "style.css": "..."}"""
    if "index.html" not in files:
        raise ValueError("index.html fehlt.")
    slug = slugify(name)
    site_dir = sites_root() / slug
    site_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for rel, content in files.items():
        if len(content.encode()) > MAX_FILE_BYTES:
            raise ValueError(f"{rel} ist zu gross.")
        path = _safe_path(site_dir, rel)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        written.append(rel)
    return {"name": slug, "ordner": str(site_dir), "dateien": written, "vorschau": f"/sites/{slug}/"}


def list_sites() -> list[dict[str, Any]]:
    out = []
    for d in sorted(sites_root().iterdir()):
        if (d / "index.html").exists():
            meta = d / ".jarvis.json"
            info = json.loads(meta.read_text()) if meta.exists() else {}
            out.append({"name": d.name, "vorschau": f"/sites/{d.name}/", "live_url": info.get("url", "")})
    return out


def _zip_site(site_dir: Path) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in site_dir.rglob("*"):
            if path.is_file() and not path.name.startswith(".jarvis"):
                zf.write(path, path.relative_to(site_dir).as_posix())
    return buf.getvalue()


def publish(settings: Settings, name: str) -> dict[str, Any]:
    """Website auf Netlify veröffentlichen (oder Update, wenn schon online)."""
    token = settings.require("NETLIFY_AUTH_TOKEN")
    slug = slugify(name)
    site_dir = sites_root() / slug
    if not (site_dir / "index.html").exists():
        raise ValueError(f"Website '{slug}' gibt es nicht.")
    meta_path = site_dir / ".jarvis.json"
    meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}

    if not meta.get("site_id"):
        site = http.post(f"{NETLIFY_API}/sites", json_body={}, bearer=token)
        meta = {"site_id": site["id"], "url": site.get("ssl_url") or site.get("url", "")}

    req = urllib.request.Request(
        f"{NETLIFY_API}/sites/{meta['site_id']}/deploys",
        data=_zip_site(site_dir),
        headers={"Content-Type": "application/zip", "Authorization": f"Bearer {token}"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        deploy = json.loads(resp.read().decode())
    meta["url"] = deploy.get("ssl_url") or meta.get("url", "")
    meta_path.write_text(json.dumps(meta))
    return {"name": slug, "live_url": meta["url"], "status": deploy.get("state", "uploaded")}
