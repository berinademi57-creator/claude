"""Design-Recherche über die Datenbank von UI/UX Pro Max (MIT-Lizenz).

192 Farbpaletten, 74 Schrift-Kombinationen, 80 Stile, 120 UX-Regeln, GSAP-Presets.
Der Installer lädt das Projekt nach ``~/.openjarvis/vendor/ui-ux-pro-max``.
Hier wird nur dessen reines Python-Suchskript aufgerufen (ohne Shell).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from .settings import HOME

REPO = "https://github.com/nextlevelbuilder/ui-ux-pro-max-skill"
DOMAINS = {"style", "color", "chart", "landing", "product", "ux", "typography", "icons", "gsap",
           "react", "web", "google-fonts"}


def script_path() -> Path:
    return HOME / "vendor" / "ui-ux-pro-max" / ".claude" / "skills" / "ui-ux-pro-max" / "scripts" / "search.py"


def build_args(anfrage: str, bereich: str = "", projekt: str = "", bewegung: int = 0) -> list[str]:
    anfrage = anfrage.strip()
    if not anfrage or len(anfrage) > 200:
        raise ValueError("Anfrage leer oder zu lang (max. 200 Zeichen).")
    args = [anfrage]
    if bereich:
        bereich = bereich.strip().lower()
        if bereich not in DOMAINS:
            raise ValueError(f"Bereich muss einer von {', '.join(sorted(DOMAINS))} sein.")
        args += ["--domain", bereich]
    else:
        args += ["--design-system", "--format", "markdown"]
        if projekt.strip():
            args += ["-p", projekt.strip()[:60]]
        if 1 <= bewegung <= 10:
            args += ["--motion", str(bewegung)]
    return args


def search(anfrage: str, bereich: str = "", projekt: str = "", bewegung: int = 0) -> str:
    script = script_path()
    if not script.exists():
        raise RuntimeError(
            "Design-Datenbank fehlt. Installer erneut ausführen oder: "
            f"git clone --depth 1 {REPO} ~/.openjarvis/vendor/ui-ux-pro-max"
        )
    result = subprocess.run(
        [sys.executable, str(script), *build_args(anfrage, bereich, projekt, bewegung)],
        capture_output=True, text=True, timeout=60, cwd=str(script.parent),
    )
    out = (result.stdout or "").strip()
    if result.returncode != 0 and not out:
        raise RuntimeError((result.stderr or "Suche fehlgeschlagen")[-500:])
    return out[:12000] or "Keine Treffer. Mit anderen Begriffen nochmal versuchen."
