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
    except KeyboardInterrupt:
        return 130
    except Exception as exc:  # noqa: BLE001
        print(f"❌ {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
