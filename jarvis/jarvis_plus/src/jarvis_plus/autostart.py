"""Jarvis immer im Hintergrund: startet automatisch beim Hochfahren/Anmelden.

Drei Dienste:
  openjarvis   → ``jarvis serve``      (Gehirn, Telegram, API)
  jarvis-hud   → ``jarvis-plus hud``   (Oberfläche Port 8765, Telefon-Leitung Port 8766)
  jarvis-watch → ``jarvis-plus watch`` (Stress-/Kunden-Wächter)
Dazu beim Anmelden einmal: ``jarvis-plus open`` → HUD als eigenes App-Fenster
(abschaltbar mit JARVIS_OPEN_ON_LOGIN=false).

macOS: LaunchAgents · Linux: systemd --user · Windows: Aufgabenplanung
"""

from __future__ import annotations

import platform
import shutil
import subprocess
import sys
from pathlib import Path

SERVICES = {
    "openjarvis": ["jarvis", "serve"],
    "jarvis-hud": ["jarvis-plus", "hud"],
    "jarvis-watch": ["jarvis-plus", "watch"],
}
LABEL_PREFIX = "ch.ademidigital."
WINDOW = ("jarvis-window", ["jarvis-plus", "open"])


def _open_on_login() -> bool:
    from .settings import load_settings

    return load_settings().get("JARVIS_OPEN_ON_LOGIN", "true").lower() != "false"


def _resolve(cmd: list[str]) -> list[str]:
    exe = shutil.which(cmd[0])
    if not exe:
        raise RuntimeError(f"'{cmd[0]}' nicht gefunden. Ist es installiert und im PATH?")
    return [exe, *cmd[1:]]


def _log_dir() -> Path:
    from .settings import HOME

    path = HOME / "logs"
    path.mkdir(parents=True, exist_ok=True)
    return path


# ------------------------------------------------------------------ macOS


def launchd_plist(name: str, argv: list[str], log_dir: Path, keep_alive: bool = True) -> str:
    args = "\n".join(f"    <string>{a}</string>" for a in argv)
    keep = "<true/>" if keep_alive else "<false/>"
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>{LABEL_PREFIX}{name}</string>
  <key>ProgramArguments</key>
  <array>
{args}
  </array>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key>{keep}
  <key>ThrottleInterval</key><integer>20</integer>
  <key>EnvironmentVariables</key>
  <dict><key>PATH</key><string>{Path(argv[0]).parent}:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string></dict>
  <key>StandardOutPath</key><string>{log_dir / (name + '.log')}</string>
  <key>StandardErrorPath</key><string>{log_dir / (name + '.log')}</string>
</dict>
</plist>
"""


def _mac(install: bool) -> list[str]:
    agents = Path.home() / "Library" / "LaunchAgents"
    agents.mkdir(parents=True, exist_ok=True)
    out = []
    for name, cmd in SERVICES.items():
        plist = agents / f"{LABEL_PREFIX}{name}.plist"
        subprocess.run(["launchctl", "unload", str(plist)], capture_output=True)
        if install:
            plist.write_text(launchd_plist(name, _resolve(cmd), _log_dir()))
            subprocess.run(["launchctl", "load", "-w", str(plist)], check=True)
            out.append(f"✅ {name} läuft (LaunchAgent)")
        elif plist.exists():
            plist.unlink()
            out.append(f"🗑  {name} entfernt")
    name, cmd = WINDOW
    plist = agents / f"{LABEL_PREFIX}{name}.plist"
    subprocess.run(["launchctl", "unload", str(plist)], capture_output=True)
    if install and _open_on_login():
        plist.write_text(launchd_plist(name, _resolve(cmd), _log_dir(), keep_alive=False))
        subprocess.run(["launchctl", "load", "-w", str(plist)], check=False)
        out.append("✅ HUD-Fenster öffnet sich beim Anmelden")
    elif plist.exists():
        plist.unlink()
    return out


# ------------------------------------------------------------------ Linux


def systemd_unit(name: str, argv: list[str]) -> str:
    after = "" if name == "openjarvis" else "After=openjarvis.service\n"
    exec_line = " ".join(f'"{a}"' if " " in a else a for a in argv)
    return f"""[Unit]
Description=Jarvis {name}
{after}
[Service]
ExecStart={exec_line}
Restart=always
RestartSec=10
Environment=PATH={Path(argv[0]).parent}:/usr/local/bin:/usr/bin:/bin

[Install]
WantedBy=default.target
"""


def _linux(install: bool) -> list[str]:
    units = Path.home() / ".config" / "systemd" / "user"
    units.mkdir(parents=True, exist_ok=True)
    out = []
    for name, cmd in SERVICES.items():
        unit = units / f"{name}.service"
        if install:
            unit.write_text(systemd_unit(name, _resolve(cmd)))
        else:
            subprocess.run(["systemctl", "--user", "disable", "--now", f"{name}.service"],
                           capture_output=True)
            unit.unlink(missing_ok=True)
            out.append(f"🗑  {name} entfernt")
    subprocess.run(["systemctl", "--user", "daemon-reload"], check=False)
    if install:
        for name in SERVICES:
            subprocess.run(["systemctl", "--user", "enable", "--now", f"{name}.service"], check=True)
            out.append(f"✅ {name} läuft (systemd)")
        # auch ohne Anmeldung weiterlaufen lassen
        subprocess.run(["loginctl", "enable-linger"], capture_output=True)
    desktop = Path.home() / ".config" / "autostart" / "jarvis-window.desktop"
    if install and _open_on_login():
        desktop.parent.mkdir(parents=True, exist_ok=True)
        desktop.write_text(xdg_desktop_entry(_resolve(WINDOW[1])))
        out.append("✅ HUD-Fenster öffnet sich beim Anmelden")
    else:
        desktop.unlink(missing_ok=True)
    return out


def xdg_desktop_entry(argv: list[str]) -> str:
    return (
        "[Desktop Entry]\nType=Application\nName=Jarvis\n"
        f"Exec=sh -c 'sleep 15; {argv[0]} {' '.join(argv[1:])}'\n"
        "X-GNOME-Autostart-enabled=true\n"
    )


# ------------------------------------------------------------------ Windows


def windows_command(argv: list[str]) -> str:
    inner = " ".join(f"'{a}'" if i == 0 else a for i, a in enumerate(argv))
    return f'powershell.exe -NoProfile -WindowStyle Hidden -Command "& {inner}"'


def windows_vbs(cmds: list[list[str]], delay_s: int = 0) -> str:
    """VBScript, das Programme unsichtbar startet (kein schwarzes Fenster)."""
    lines = ['Set sh = CreateObject("WScript.Shell")']
    if delay_s:
        lines.append(f"WScript.Sleep {delay_s * 1000}")
    for argv in cmds:
        quoted = " ".join(f'""{a}""' if " " in a or i == 0 else a for i, a in enumerate(argv))
        lines.append(f'sh.Run "{quoted}", 0, False')
    return "\r\n".join(lines) + "\r\n"


def _startup_dir() -> Path:
    import os

    return Path(os.environ.get("APPDATA", str(Path.home()))) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"


def _windows(install: bool) -> list[str]:
    """Autostart-Ordner statt Aufgabenplanung: braucht keine Admin-Rechte."""
    out = []
    # alte Aufgaben (falls vorhanden) entfernen
    for name in [*SERVICES, "window"]:
        subprocess.run(["schtasks", "/Delete", "/TN", f"Jarvis-{name}", "/F"], capture_output=True)
    folder = _startup_dir()
    services = folder / "Jarvis.vbs"
    window = folder / "Jarvis-Fenster.vbs"
    if not install:
        services.unlink(missing_ok=True)
        window.unlink(missing_ok=True)
        return ["🗑  Jarvis aus dem Autostart entfernt"]
    folder.mkdir(parents=True, exist_ok=True)
    cmds = [_resolve(cmd) for cmd in SERVICES.values()]
    services.write_text(windows_vbs(cmds), encoding="utf-8")
    subprocess.run(["wscript", str(services)], check=False)  # jetzt gleich starten
    out += [f"✅ {name} läuft (startet bei jeder Anmeldung)" for name in SERVICES]
    if _open_on_login():
        window.write_text(windows_vbs([_resolve(WINDOW[1])], delay_s=20), encoding="utf-8")
        out.append("✅ HUD-Fenster öffnet sich beim Anmelden")
    else:
        window.unlink(missing_ok=True)
    return out


def apply(install: bool = True) -> list[str]:
    system = platform.system()
    if system == "Darwin":
        return _mac(install)
    if system == "Linux":
        return _linux(install)
    if system == "Windows":
        return _windows(install)
    raise RuntimeError(f"Betriebssystem nicht unterstützt: {system} ({sys.platform})")
