"""Kommandozeile: ``jarvis-plus <befehl>``."""

from __future__ import annotations

import argparse
import json
import sys

from .settings import ENV_FILE, load_settings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="jarvis-plus", description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("serve", help="MCP-Server starten (macht OpenJarvis automatisch)")
    sub.add_parser("whoop-login", help="Whoop einmalig verbinden")
    sub.add_parser("garmin-login", help="Garmin einmalig verbinden")
    sub.add_parser("check", help="Stress-Check jetzt ausführen und anzeigen")
    watch = sub.add_parser("watch", help="Wächter dauerhaft laufen lassen")
    watch.add_argument("--minutes", type=int, default=None)
    call = sub.add_parser("test-call", help="Testanruf auf dein Handy")
    call.add_argument("text", nargs="?", default="Hallo, hier ist Jarvis. Der Testanruf funktioniert.")
    tg = sub.add_parser("test-telegram", help="Test-Nachricht über Telegram")
    tg.add_argument("text", nargs="?", default="Jarvis ist online ✅")
    sub.add_parser("where", help="Zeigt, wo die Einstellungen liegen")
    hud = sub.add_parser("hud", help="Jarvis-Oberfläche starten (http://localhost:8765)")
    hud.add_argument("--host", default=None)
    hud.add_argument("--port", type=int, default=None)
    hud.add_argument("--demo", action="store_true", help="Beispiel-Gesundheitsdaten anzeigen")
    auto = sub.add_parser("autostart", help="Jarvis immer im Hintergrund laufen lassen")
    auto.add_argument("aktion", choices=["an", "aus"], nargs="?", default="an")
    con = sub.add_parser("connect", help="Connector verbinden (browser, desktop, higgsfield, canva, notion, figma, 21st)")
    con.add_argument("name")
    dis = sub.add_parser("disconnect", help="Connector entfernen")
    dis.add_argument("name")
    sub.add_parser("connectors", help="Verfügbare Connectoren anzeigen")
    sub.add_parser("status", help="Welche Zugänge fehlen noch?")
    sub.add_parser("register", help="jarvis-plus in OpenJarvis eintragen (macht der Installer)")
    sub.add_parser("telefon-einrichten", help="Echte Telefonate mit Jarvis einrichten (Twilio + Tailscale)")
    sub.add_parser("open", help="HUD als eigenes App-Fenster öffnen")
    merge = sub.add_parser("env-merge", help="Leere Einstellungen aus einer Datei ergänzen (Installer)")
    merge.add_argument("datei")

    args = parser.parse_args(argv)
    settings = load_settings()

    try:
        if args.cmd == "serve":
            from .server import main as serve

            serve()
        elif args.cmd == "whoop-login":
            from . import whoop

            whoop.login(settings)
        elif args.cmd == "garmin-login":
            from . import garmin

            garmin.login(settings)
        elif args.cmd == "check":
            from .server import _collect_health

            print(json.dumps(_collect_health(), ensure_ascii=False, indent=2, default=str))
        elif args.cmd == "watch":
            from .watcher import run_forever

            run_forever(args.minutes)
        elif args.cmd == "test-call":
            from .phone import call_me

            print(call_me(settings, args.text))
        elif args.cmd == "test-telegram":
            from .phone import telegram_me

            print(telegram_me(settings, args.text))
        elif args.cmd == "where":
            print(f"Einstellungen: {ENV_FILE}")
        elif args.cmd == "hud":
            import os

            from .hud_server import run

            if args.demo:
                os.environ["JARVIS_DEMO"] = "1"
            run(args.host, args.port)
        elif args.cmd == "autostart":
            from .autostart import apply

            print("\n".join(apply(install=args.aktion == "an")))
        elif args.cmd == "connect":
            from . import connectors

            connectors.add(args.name, settings)
            print(connectors.login(args.name, settings))
            print("Neu starten, damit Jarvis ihn nutzt: jarvis restart")
        elif args.cmd == "disconnect":
            from . import connectors

            connectors.remove(args.name)
            print(f"{args.name} entfernt.")
        elif args.cmd == "connectors":
            from . import connectors

            for c in connectors.listing():
                print(f"{'✅' if c['aktiv'] else '○ '} {c['name']:<11} {c['titel']}")
        elif args.cmd == "telefon-einrichten":
            from .phone_line import setup

            print("\n".join(setup(settings)))
            print("Neu starten, damit die Leitung aktiv wird: jarvis-plus autostart")
        elif args.cmd == "env-merge":
            from pathlib import Path

            from .settings import merge_env

            keys = merge_env(Path(args.datei))
            print(f"Übernommen: {', '.join(keys) if keys else 'nichts Neues'}")
        elif args.cmd == "open":
            from .pc import open_hud_window

            print(open_hud_window(f"http://localhost:{settings.get_int('HUD_PORT', 8765)}"))
        elif args.cmd == "register":
            from . import connectors

            print("Eingetragen:", connectors.register_self()["command"])
        elif args.cmd == "status":
            from .access import status

            for row in status(settings):
                mark = "✅" if row["verbunden"] else "❌"
                print(f"{mark} {row['name']:<28} {row['so_gehts']}")
    except KeyboardInterrupt:
        return 130
    except Exception as exc:  # noqa: BLE001
        print(f"❌ {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
