"""PC-Steuerung: Apps, Links und Dateien öffnen, mit deinen gespeicherten Logins.

Links öffnen sich in deinem normalen Standard-Browser, also mit allen
gespeicherten Logins. Für Klicken/Tippen auf Webseiten gibt es den Connector
``browser`` (Playwright im Extension-Modus, nutzt deinen echten Chrome), für
beliebige Desktop-Apps den Connector ``desktop`` (Windows-MCP bzw. AppleScript).
"""

from __future__ import annotations

import os
import platform
import re
import shutil
import subprocess
import urllib.parse
from pathlib import Path

ALLOWED_SCHEMES = {"http", "https", "mailto", "tel", "sms", "whatsapp", "spotify", "zoommtg", "msteams"}
APP_NAME = re.compile(r"^[\w .+&()'-]{1,80}$", re.UNICODE)

# Häufige Apps → wie das Betriebssystem sie kennt
ALIASES = {
    "windows": {
        "chrome": "chrome", "edge": "msedge", "spotify": "spotify:", "whatsapp": "whatsapp:",
        "outlook": "outlook", "word": "winword", "excel": "excel", "powerpoint": "powerpnt",
        "explorer": "explorer", "rechner": "calc", "notizen": "notepad", "teams": "msteams:",
        "vscode": "code", "vs code": "code", "terminal": "wt", "einstellungen": "ms-settings:",
    },
    "darwin": {
        "chrome": "Google Chrome", "vscode": "Visual Studio Code", "vs code": "Visual Studio Code",
        "rechner": "Calculator", "notizen": "Notes", "kalender": "Calendar", "mail": "Mail",
        "finder": "Finder", "einstellungen": "System Settings", "nachrichten": "Messages",
        "terminal": "Terminal", "musik": "Music", "fotos": "Photos",
    },
}


def _system() -> str:
    return platform.system().lower()


def _launch(argv: list[str]) -> None:
    kwargs: dict = {"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}
    if _system() == "windows":
        kwargs["creationflags"] = 0x00000008  # DETACHED_PROCESS
    else:
        kwargs["start_new_session"] = True
    subprocess.Popen(argv, **kwargs)  # noqa: S603 - argv-Liste, keine Shell


def open_url(url: str) -> str:
    """Link im Standard-Browser öffnen (gespeicherte Logins inklusive)."""
    url = url.strip()
    if not re.match(r"^[a-z][a-z0-9+.-]*:", url, re.I):
        url = "https://" + url
    scheme = urllib.parse.urlparse(url).scheme.lower()
    if scheme not in ALLOWED_SCHEMES:
        raise ValueError(f"Link-Typ '{scheme}' ist nicht erlaubt.")
    system = _system()
    if system == "windows":
        os.startfile(url)  # type: ignore[attr-defined]  # noqa: S606
    elif system == "darwin":
        _launch(["open", url])
    else:
        _launch(["xdg-open", url])
    return f"Geöffnet: {url}"


def open_app(name: str) -> str:
    """App starten, z.B. 'Spotify', 'Excel', 'Visual Studio Code'."""
    name = name.strip()
    if not APP_NAME.match(name):
        raise ValueError("Ungültiger App-Name.")
    system = _system()
    target = ALIASES.get(system, {}).get(name.lower(), name)
    if system == "windows":
        if target.endswith(":"):
            os.startfile(target)  # type: ignore[attr-defined]  # noqa: S606
        else:
            # "start" findet registrierte Apps (App Paths) wie Explorer-Ausführen
            _launch(["cmd", "/c", "start", "", target])
    elif system == "darwin":
        result = subprocess.run(["open", "-a", target], capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"App '{name}' nicht gefunden.")
    else:
        exe = shutil.which(target.lower().replace(" ", "-")) or shutil.which(target.lower())
        if not exe:
            raise RuntimeError(f"App '{name}' nicht gefunden.")
        _launch([exe])
    return f"Gestartet: {name}"


def open_path(path: str) -> str:
    """Datei oder Ordner mit der passenden App öffnen."""
    p = Path(path).expanduser()
    if not p.exists():
        raise FileNotFoundError(f"Gibt es nicht: {p}")
    system = _system()
    if system == "windows":
        os.startfile(str(p))  # type: ignore[attr-defined]  # noqa: S606
    elif system == "darwin":
        _launch(["open", str(p)])
    else:
        _launch(["xdg-open", str(p)])
    return f"Geöffnet: {p}"


def browser_for_app_window() -> list[str] | None:
    """Chrome/Edge/Chromium finden, um das HUD als eigenes App-Fenster zu öffnen."""
    system = _system()
    candidates: list[str] = []
    if system == "windows":
        for base in (os.environ.get("PROGRAMFILES", ""), os.environ.get("PROGRAMFILES(X86)", ""),
                     os.environ.get("LOCALAPPDATA", "")):
            candidates += [
                os.path.join(base, "Google", "Chrome", "Application", "chrome.exe"),
                os.path.join(base, "Microsoft", "Edge", "Application", "msedge.exe"),
            ]
    elif system == "darwin":
        candidates += [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
            "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
        ]
    else:
        candidates += [shutil.which(n) or "" for n in ("google-chrome", "chromium", "chromium-browser", "microsoft-edge")]
    for c in candidates:
        if c and os.path.exists(c):
            return [c]
    return None


def open_hud_window(url: str) -> str:
    browser = browser_for_app_window()
    if browser:
        _launch([*browser, f"--app={url}", "--start-maximized"])
        return f"HUD-Fenster geöffnet: {url}"
    return open_url(url)
