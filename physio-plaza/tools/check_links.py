#!/usr/bin/env python3
"""
Prüft die fertige Website auf kaputte interne Verweise – vor jedem Upload ausführen:

    python3 tools/check_links.py

Geprüft wird in allen HTML-Dateien unter public/:
  - Links auf andere Seiten            (z. B. /dry-needling/)
  - Sprungziele                        (z. B. /#termin  -> gibt es id="termin"?)
  - Bilder, Schriften, CSS, JavaScript (auch alle Grössen in srcset)
  - Icons                              (<use href="#i-phone"> braucht <symbol id="i-phone">)
  - FAQ: sichtbarer Text und Google-Strukturdaten müssen wortgleich sein

Externe Links (https://…, mailto:, tel:) werden nicht aufgerufen.
Das Skript ändert nichts; es meldet nur. Ende mit Fehlercode 1, wenn etwas nicht stimmt.
"""
import json
import re
import sys
from pathlib import Path

PUBLIC = Path(__file__).resolve().parent.parent / "public"


def target_file(path: str) -> Path:
    path = path.split("?")[0]
    if path.endswith("/"):
        return PUBLIC / path.lstrip("/") / "index.html"
    return PUBLIC / path.lstrip("/")


def strip_tags(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text).replace("&nbsp;", " ").replace("&amp;", "&")


def main() -> int:
    pages = sorted(PUBLIC.rglob("*.html"))
    ids = {p: set(re.findall(r'\bid="([^"]+)"', p.read_text(encoding="utf-8"))) for p in pages}
    problems = []
    checked = 0

    for page in pages:
        html = page.read_text(encoding="utf-8")
        name = str(page.relative_to(PUBLIC))

        refs = set(re.findall(r'<a\b[^>]*?\bhref="([^"]+)"', html))
        refs |= set(re.findall(r'\b(?:src|href)="(/[^"#?]+)"', html))
        refs |= set(re.findall(r'data-full="([^"]+)"', html))
        for srcset in re.findall(r'srcset="([^"]+)"', html):
            refs |= {part.strip().split(" ")[0] for part in srcset.split(",")}

        for ref in sorted(refs):
            if ref.startswith(("http://", "https://", "mailto:", "tel:", "data:")):
                continue
            checked += 1
            path, _, fragment = ref.partition("#")
            if path == "":
                target = page                      # Sprungziel auf derselben Seite
            elif path.startswith("/?"):
                target = PUBLIC / "index.html"     # Startseite mit Parameter
            else:
                target = target_file(path)
            if not target.exists():
                problems.append(f"{name}: Ziel fehlt -> {ref}")
            elif fragment and target.suffix == ".html" and fragment not in ids.get(target, set()):
                problems.append(f"{name}: Sprungziel fehlt -> {ref}")

        # Icons
        symbols = set(re.findall(r'<symbol id="([^"]+)"', html))
        for used in sorted(set(re.findall(r'<use href="([^"]+)"', html))):
            checked += 1
            if not used.startswith("#"):
                problems.append(f"{name}: Icon-Verweis muss mit # beginnen -> {used}")
            elif used[1:] not in symbols:
                problems.append(f"{name}: Icon fehlt -> {used}")

        # FAQ: sichtbar == Strukturdaten
        block = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
        if block:
            try:
                data = json.loads(block.group(1))
            except json.JSONDecodeError as err:
                problems.append(f"{name}: Strukturdaten sind kein gültiges JSON ({err})")
                continue
            for node in data.get("@graph", []):
                if node.get("@type") != "FAQPage":
                    continue
                structured = [(q["name"], q["acceptedAnswer"]["text"]) for q in node["mainEntity"]]
                visible = [
                    (strip_tags(q), strip_tags(a))
                    for q, a in re.findall(r'<summary>(.*?)</summary>\s*<div class="faq__answer"><p>(.*?)</p>', html, re.S)
                ]
                checked += len(structured)
                if structured != visible:
                    problems.append(f"{name}: FAQ-Text und Strukturdaten sind nicht wortgleich")

    for line in problems:
        print("FEHLER  " + line)
    print(f"{checked} Verweise auf {len(pages)} Seiten geprüft – {len(problems)} Probleme")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
