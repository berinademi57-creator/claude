#!/usr/bin/env python3
"""
Erzeugt die Leistungsseiten (z. B. /dry-needling/) als fertige HTML-Dateien.

Warum ein Skript?
  Alle Leistungsseiten haben denselben Aufbau. Kopfzeile, Menü, Icons und Fusszeile
  werden automatisch aus public/index.html übernommen. So gibt es nur EINE Stelle,
  an der man sie ändert – und die Unterseiten können nie davon abweichen.

So änderst du Inhalte:
  1. Texte unten in PAGES anpassen (oder eine neue Seite ergänzen).
  2. Im Projektordner ausführen:   python3 tools/build_leistungen.py
  3. Die erzeugten Dateien public/<slug>/index.html NICHT von Hand ändern –
     sie werden beim nächsten Lauf überschrieben.

Das Skript schreibt ausserdem public/sitemap.xml neu (alle Seiten für Google).
Es braucht nur Python 3, keine Zusatzpakete.

WICHTIG (Gesundheitswerbung, GesBG Art. 16): Texte sachlich halten – keine
Heilversprechen, keine Superlative. Formulierungen wie "kann unterstützen" verwenden.
Medizinische Inhalte vor der Veröffentlichung von Hasan prüfen lassen.
"""
import html
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "public"
SITE = "https://www.physio-plaza.com"
PRACTICE = "Physiotherapie Central Plaza"
PHONE_SHOWN = "041 554 55 41"
PHONE_LINK = "+41415545541"

# Angaben für die Karte "Auf einen Blick" (gleiche Daten wie auf der Startseite!)
OPENING_MAIN = "Mo–Fr 08:00–21:00 Uhr"
OPENING_SUB = "Sa 07:00–19:00 Uhr"
PHONE_HOURS = "Di–Fr, 13:00–14:00 Uhr"

KK_FRAGE = "Übernimmt die Krankenkasse die Kosten?"
KK_ANTWORT = (
    "Ob und in welchem Umfang Ihre Krankenkasse die Kosten übernimmt, hängt von Ihrer "
    "Versicherung und davon ab, ob eine ärztliche Verordnung vorliegt. Wir beraten Sie gerne persönlich."
)

# ---------------------------------------------------------------------------
#  INHALTE
#  Bausteine ("blocks"):  ("h2", Text) · ("p", Text) · ("check", [Punkte]) ·
#                         ("flow", [(Titel, Text)]) · ("defs", [(Titel, Text)]) · ("note", Text)
# ---------------------------------------------------------------------------
PAGES = [
    {
        "slug": "neurorehabilitation",
        "label": "Neurorehabilitation",
        "eyebrow": "Unser Schwerpunkt",
        "title": "Neurorehabilitation in Emmenbrücke | Physiotherapie Central Plaza",
        "description": "Neurologische Physiotherapie in Emmenbrücke bei Luzern: individuelle Neurorehabilitation "
                       "bei Hasan Zećiri, M.Sc. Neurorehabilitation. Jetzt Termin anfragen.",
        "h1": "Neurorehabilitation in Emmenbrücke",
        "lead": "Neurologische Physiotherapie – präzise, individuell und auf wissenschaftlicher Basis. "
                "Der Schwerpunkt unserer Praxis.",
        "teaser": "Neurologische Physiotherapie – der Schwerpunkt unserer Praxis.",
        "image": {"base": "praxis-raum-1-wand", "widths": [480, 800, 1200], "w": 800, "h": 1067, "device": False,
                  "alt": "Behandlungsraum mit anatomischen Lehrtafeln zu Muskulatur und Skelett"},
        "blocks": [
            ("h2", "Was ist Neurorehabilitation?"),
            ("p", "Die Neurorehabilitation ist ein Fachgebiet der Physiotherapie für Menschen mit Erkrankungen oder "
                  "Verletzungen des Nervensystems. Ziel ist es, Bewegungen und Fähigkeiten wieder zu erlernen, zu "
                  "erhalten oder Einschränkungen im Alltag so gut wie möglich auszugleichen."),
            ("p", "Hasan Zećiri hat sich mit einem Masterabschluss (M.Sc.) auf die Neurorehabilitation spezialisiert "
                  "und begleitet seit über 15 Jahren Patientinnen und Patienten."),
            ("h2", "Für wen ist die Therapie gedacht?"),
            ("p", "Neurologische Physiotherapie richtet sich unter anderem an Menschen"),
            ("check", [
                "nach einem Schlaganfall",
                "mit Multipler Sklerose (MS)",
                "mit Morbus Parkinson",
                "nach Verletzungen von Gehirn oder Rückenmark",
                "mit Erkrankungen oder Verletzungen einzelner Nerven",
            ]),
            ("p", "Ob und wie wir Sie unterstützen können, klären wir in einem ersten Gespräch und einer gründlichen "
                  "Untersuchung."),
            ("h2", "Woran wir gemeinsam arbeiten"),
            ("p", "Die Therapie richtet sich nach Ihren persönlichen Zielen. Typische Schwerpunkte sind:"),
            ("check", [
                "Gleichgewicht und sicheres Gehen",
                "Kraft, Beweglichkeit und Koordination",
                "Alltagsbewegungen wie Aufstehen, Treppensteigen oder Greifen",
                "Übungen, die Sie zu Hause selbstständig weiterführen können",
            ]),
            ("h2", "So läuft die Behandlung ab"),
            ("flow", [
                ("Gespräch und Befund", "Wir nehmen uns Zeit für Ihre Vorgeschichte, untersuchen unter anderem "
                                        "Beweglichkeit, Kraft und Gleichgewicht und besprechen, was Sie im Alltag "
                                        "erreichen möchten."),
                ("Individueller Therapieplan", "Auf dieser Grundlage stellen wir einen Therapieplan zusammen, der zu "
                                               "Ihren Zielen und Ihrem Alltag passt."),
                ("Therapie und Verlauf", "Wir üben gezielt und überprüfen die Fortschritte regelmässig. So können wir "
                                         "die Therapie laufend anpassen."),
            ]),
            ("note", "Bitte bringen Sie zum ersten Termin, falls vorhanden, Ihre ärztliche Verordnung sowie Berichte "
                     "aus Spital oder Rehabilitation mit."),
        ],
        "faq": [
            ("Wie lange dauert eine Neurorehabilitation?",
             "Das ist sehr unterschiedlich und hängt von der Erkrankung, Ihren Zielen und dem Verlauf ab. Nach dem "
             "Befund besprechen wir mit Ihnen einen realistischen Plan."),
            (KK_FRAGE, KK_ANTWORT),
            ("Wo kann ich parkieren?",
             "Für unsere Patientinnen und Patienten stehen hinter dem Tramhüsli eigene Parkplätze zur Verfügung."),
        ],
        "cta": "Fragen zur Neurorehabilitation?",
    },
    {
        "slug": "dry-needling",
        "label": "Dry Needling",
        "eyebrow": "Leistung",
        "title": "Dry Needling in Emmenbrücke | Physiotherapie Central Plaza",
        "description": "Dry Needling in Emmenbrücke bei Luzern: gezielte Behandlung von Triggerpunkten mit feinen "
                       "Nadeln bei muskulären Verspannungen. Jetzt Termin anfragen.",
        "h1": "Dry Needling in Emmenbrücke",
        "lead": "Mit feinen Nadeln werden gezielt Triggerpunkte behandelt – mit dem Ziel, Verspannungen zu lösen "
                "und Beschwerden zu verringern.",
        "teaser": "Feine Nadeln gezielt an Triggerpunkten – bei muskulären Verspannungen.",
        "image": {"base": "dry-needling", "widths": [480, 800], "w": 800, "h": 800, "device": False,
                  "alt": "Therapeut mit Handschuhen setzt eine feine Nadel für das Dry Needling"},
        "blocks": [
            ("h2", "Was ist Dry Needling?"),
            ("p", "Dry Needling ist eine Behandlungstechnik der Physiotherapie. Dabei wird eine sehr dünne, sterile "
                  "Einwegnadel gezielt in einen sogenannten Triggerpunkt gesetzt – eine verhärtete, oft "
                  "druckempfindliche Stelle in der Muskulatur."),
            ("p", "«Dry» (trocken) heisst die Methode, weil kein Medikament gespritzt wird. Verwendet werden ähnliche "
                  "Nadeln wie in der Akupunktur; das Konzept ist jedoch ein anderes: Dry Needling orientiert sich an "
                  "der Anatomie und an den Triggerpunkten der Muskulatur."),
            ("h2", "Wann wird Dry Needling eingesetzt?"),
            ("p", "Dry Needling wird unter anderem bei muskulären Verspannungen und schmerzhaften Triggerpunkten "
                  "eingesetzt. Meist ist es ein Baustein innerhalb der Physiotherapie."),
            ("check", [
                "Sehr dünne, sterile Einwegnadeln",
                "Kein Medikament – daher «dry» (trocken)",
                "Meist kombiniert mit manueller Therapie und aktiven Übungen",
            ]),
            ("h2", "So läuft die Behandlung ab"),
            ("flow", [
                ("Befund", "Wir untersuchen die betroffene Muskulatur und klären im Gespräch, ob Dry Needling für Sie "
                           "geeignet ist."),
                ("Behandlung", "Die Nadel wird gezielt in den Triggerpunkt gesetzt. Dabei kann der Muskel kurz zucken "
                               "– das ist eine normale Reaktion."),
                ("Danach", "In den ein bis zwei Tagen nach der Behandlung ist ein Gefühl wie Muskelkater möglich. Wir "
                           "zeigen Ihnen passende Übungen für zu Hause."),
            ]),
            ("note", "Bitte informieren Sie uns vor der Behandlung, wenn Sie schwanger sind, blutverdünnende "
                     "Medikamente einnehmen oder Angst vor Nadeln haben."),
        ],
        "faq": [
            ("Tut Dry Needling weh?",
             "Den Einstich spüren viele Menschen kaum. Trifft die Nadel den Triggerpunkt, kann der Muskel kurz zucken; "
             "das wird oft als kurzes, dumpfes Ziehen beschrieben. Danach ist ein Gefühl wie Muskelkater möglich."),
            ("Ist Dry Needling dasselbe wie Akupunktur?",
             "Nein. Es werden zwar ähnliche Nadeln verwendet, Dry Needling orientiert sich aber an der Anatomie und an "
             "den Triggerpunkten der Muskulatur und ist eine Technik der Physiotherapie."),
            (KK_FRAGE, KK_ANTWORT),
        ],
        "cta": "Fragen zum Dry Needling?",
    },
    {
        "slug": "stosswellentherapie",
        "label": "Stosswellentherapie",
        "eyebrow": "Leistung",
        "title": "Stosswellentherapie in Emmenbrücke | Physiotherapie Central Plaza",
        "description": "Stosswellentherapie in Emmenbrücke bei Luzern: eingesetzt unter anderem bei hartnäckigen "
                       "Sehnen- und Weichteilbeschwerden wie Fersensporn. Jetzt Termin anfragen.",
        "h1": "Stosswellentherapie in Emmenbrücke",
        "lead": "Wird unter anderem bei hartnäckigen Sehnen- und Weichteilbeschwerden eingesetzt – "
                "beispielsweise bei Fersensporn.",
        "teaser": "Druckwellen von aussen – unter anderem bei hartnäckigen Sehnenbeschwerden wie Fersensporn.",
        "image": {"base": "geraet-stosswelle", "widths": [400, 800], "w": 800, "h": 600, "device": True,
                  "alt": "Stosswellentherapie-Gerät mit Handstück"},
        "blocks": [
            ("h2", "Was ist die Stosswellentherapie?"),
            ("p", "Bei der Stosswellentherapie werden kurze, energiereiche Druckwellen über ein Handstück von aussen "
                  "auf das betroffene Gewebe übertragen – ohne Nadeln und ohne Medikamente."),
            ("p", "Ziel ist es, Durchblutung und Stoffwechsel im behandelten Gewebe anzuregen und so die "
                  "körpereigenen Heilungsprozesse zu unterstützen."),
            ("h2", "Wann wird sie eingesetzt?"),
            ("p", "Die Stosswellentherapie wird unter anderem bei hartnäckigen Sehnen- und Weichteilbeschwerden "
                  "eingesetzt. Typische Beispiele sind:"),
            ("check", [
                "Fersensporn und Beschwerden der Fusssohle",
                "Beschwerden der Achillessehne",
                "Tennis- oder Golferellenbogen",
                "Sehnenbeschwerden an der Schulter",
            ]),
            ("p", "Ob die Stosswellentherapie in Ihrem Fall sinnvoll ist, beurteilen wir nach einer gründlichen "
                  "Untersuchung."),
            ("h2", "So läuft die Behandlung ab"),
            ("flow", [
                ("Befund", "Wir untersuchen die betroffene Stelle und besprechen mit Ihnen, ob die "
                           "Stosswellentherapie zu Ihren Beschwerden passt."),
                ("Behandlung", "Nach dem Auftragen eines Kontaktgels wird das Handstück auf die betroffene Stelle "
                               "aufgesetzt. Die eigentliche Behandlung dauert in der Regel nur wenige Minuten."),
                ("Verlauf", "Häufig werden mehrere Sitzungen durchgeführt. Wie viele sinnvoll sind, besprechen wir "
                            "individuell."),
            ]),
            ("note", "Bitte informieren Sie uns vor der Behandlung, wenn Sie schwanger sind, blutverdünnende "
                     "Medikamente einnehmen oder einen Herzschrittmacher tragen."),
        ],
        "faq": [
            ("Ist die Behandlung schmerzhaft?",
             "Die Stosswellen können an der behandelten Stelle unangenehm sein. Die Intensität passen wir laufend an "
             "Ihr Empfinden an. Nach der Behandlung sind vorübergehend eine Rötung oder ein leichter Druckschmerz "
             "möglich."),
            ("Wie viele Sitzungen brauche ich?",
             "Das hängt von Ihren Beschwerden und vom Verlauf ab. Nach dem Befund besprechen wir mit Ihnen ein "
             "sinnvolles Vorgehen."),
            (KK_FRAGE,
             "Die Kostenübernahme ist je nach Versicherung unterschiedlich. Wir informieren Sie gerne vor der "
             "Behandlung über die Kosten."),
        ],
        "cta": "Fragen zur Stosswellentherapie?",
    },
    {
        "slug": "massage",
        "label": "Massage & Lymphdrainage",
        "eyebrow": "Leistung",
        "title": "Massage & Lymphdrainage Emmenbrücke | Physiotherapie Central Plaza",
        "description": "Medizinische Massage, Sportmassage, Schwangerschaftsmassage, Gesichtsmassage und "
                       "Lymphdrainage in Emmenbrücke bei Luzern. Jetzt Termin anfragen.",
        "h1": "Massage & Lymphdrainage in Emmenbrücke",
        "lead": "Ergänzend zur manuellen Therapie bieten wir medizinische Massage, Sportmassage, "
                "Schwangerschaftsmassage, Gesichtsmassage und Lymphdrainage an.",
        "teaser": "Medizinische Massage, Sportmassage, Schwangerschafts- und Gesichtsmassage sowie Lymphdrainage.",
        "image": {"base": "praxis-raum-4", "widths": [480, 800, 1200], "w": 800, "h": 1067, "device": False,
                  "alt": "Behandlungsraum mit blauen Therapieliegen vor einer Holzlamellenwand"},
        "blocks": [
            ("h2", "Unsere Massagen im Überblick"),
            ("defs", [
                ("Medizinische Massage", "Gezielte Grifftechniken, um verspannte Muskulatur zu lockern – häufig als "
                                         "Teil der physiotherapeutischen Behandlung."),
                ("Sportmassage", "Für sportlich Aktive: zur Lockerung der Muskulatur, zum Beispiel nach Training oder "
                                 "Wettkampf."),
                ("Schwangerschaftsmassage", "Sanfte Massage in bequemer Lagerung, abgestimmt auf die Bedürfnisse in "
                                            "der Schwangerschaft."),
                ("Gesichtsmassage", "Sanfte Massage von Gesicht und Kopf zur Entspannung."),
                ("Lymphdrainage", "Sanfte, rhythmische Grifftechnik, die den Abfluss von Gewebeflüssigkeit "
                                  "unterstützen kann – zum Beispiel bei Schwellungen."),
            ]),
            ("h2", "Manuelle Therapie"),
            ("p", "Gezielte Handgriffe können die Beweglichkeit fördern und Schmerzen lindern. Die manuelle Therapie "
                  "ist ein fester Bestandteil der Physiotherapie und wird häufig mit Massage und aktiven Übungen "
                  "kombiniert."),
            ("h2", "So läuft die Behandlung ab"),
            ("flow", [
                ("Ihr Anliegen", "Schildern Sie uns Ihre Beschwerden und Wünsche – wir empfehlen Ihnen die passende "
                                 "Behandlung."),
                ("Behandlung", "Die Massage wird auf Sie abgestimmt: Technik, Intensität und Lagerung richten sich "
                               "nach Ihrem Befinden."),
                ("Empfehlungen", "Auf Wunsch geben wir Ihnen Tipps und einfache Übungen für den Alltag mit."),
            ]),
            ("note", "Bitte informieren Sie uns vor der Behandlung über eine Schwangerschaft, frische Verletzungen "
                     "oder bestehende Erkrankungen."),
        ],
        "faq": [
            ("Welche Massage passt zu mir?",
             "Das hängt von Ihren Beschwerden und Zielen ab. Schildern Sie uns Ihr Anliegen – wir empfehlen Ihnen die "
             "passende Behandlung."),
            ("Brauche ich eine ärztliche Verordnung?",
             "Ob eine Verordnung nötig ist und ob Ihre Versicherung die Kosten übernimmt, hängt von der Art der "
             "Behandlung und Ihrer Versicherung ab. Wir beraten Sie gerne persönlich."),
        ],
        "cta": "Fragen zu Massage oder Lymphdrainage?",
    },
]

# Welche Icons aus der Startseite die Unterseiten brauchen
ICONS = ["i-phone", "i-calendar", "i-chevron-right", "i-check", "i-arrow-right", "i-pin", "i-clock", "i-info",
         "i-cap", "i-car", "i-bus", "logo"]


# ---------------------------------------------------------------------------
#  Hilfsfunktionen
# ---------------------------------------------------------------------------
def esc(text: str) -> str:
    """Text sicher für HTML machen und Telefonnummer/Abkürzungen zusammenhalten."""
    out = html.escape(text, quote=False)
    out = out.replace(PHONE_SHOWN, PHONE_SHOWN.replace(" ", "&nbsp;"))
    return out.replace("z. B.", "z.&nbsp;B.")


def attr(text: str) -> str:
    return html.escape(text, quote=True)


def between(source: str, start: str, end: str, include_end: bool = False) -> str:
    """Schneidet den Abschnitt zwischen zwei eindeutigen Markern aus der Startseite."""
    if source.count(start) != 1:
        sys.exit(f"FEHLER: Marker nicht eindeutig gefunden: {start!r}")
    i = source.index(start)
    j = source.find(end, i)
    if j < 0:
        sys.exit(f"FEHLER: Ende-Marker fehlt: {end!r}")
    return source[i:j + (len(end) if include_end else 0)].strip()


def icon(name: str) -> str:
    return f'<svg class="icon" aria-hidden="true"><use href="#{name}"/></svg>'


def picture(img: dict) -> str:
    sizes = "(max-width: 1024px) 92vw, 520px"

    def srcset(ext: str) -> str:
        return ", ".join(f"/assets/img/{img['base']}-{w}.{ext} {w}w" for w in img["widths"])

    for w in img["widths"]:
        for ext in ("avif", "webp"):
            f = PUBLIC / "assets" / "img" / f"{img['base']}-{w}.{ext}"
            if not f.exists():
                sys.exit(f"FEHLER: Bild fehlt: {f}")
    mid = img["widths"][min(1, len(img["widths"]) - 1)]
    return (
        f'<picture><source type="image/avif" srcset="{srcset("avif")}" sizes="{sizes}">'
        f'<img src="/assets/img/{img["base"]}-{mid}.webp" srcset="{srcset("webp")}" sizes="{sizes}" '
        f'width="{img["w"]}" height="{img["h"]}" fetchpriority="high" decoding="async" alt="{attr(img["alt"])}"></picture>'
    )


def render_blocks(blocks) -> str:
    out = []
    for kind, value in blocks:
        if kind == "h2":
            out.append(f"          <h2>{esc(value)}</h2>")
        elif kind == "p":
            out.append(f"          <p>{esc(value)}</p>")
        elif kind == "check":
            items = "".join(
                f'\n            <li><span class="check">{icon("i-check")}</span><span>{esc(i)}</span></li>' for i in value
            )
            out.append(f'          <ul class="checklist">{items}\n          </ul>')
        elif kind == "flow":
            items = "".join(f"\n            <li><h3>{esc(t)}</h3><p>{esc(x)}</p></li>" for t, x in value)
            out.append(f'          <ol class="flow">{items}\n          </ol>')
        elif kind == "defs":
            items = "".join(f"\n            <li><h3>{esc(t)}</h3><p>{esc(x)}</p></li>" for t, x in value)
            out.append(f'          <ul class="deflist">{items}\n          </ul>')
        elif kind == "note":
            out.append(f'          <p class="note">{icon("i-info")}<span>{esc(value)}</span></p>')
        else:
            sys.exit(f"FEHLER: unbekannter Baustein {kind!r}")
    return "\n".join(out)


def json_ld(page: dict, url: str) -> str:
    data = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebPage",
                "@id": url + "#webpage",
                "url": url,
                "name": page["title"],
                "description": page["description"],
                "inLanguage": "de-CH",
                "isPartOf": {"@id": SITE + "/#website"},
                "about": {"@id": url + "#leistung"},
                "breadcrumb": {"@id": url + "#breadcrumb"},
            },
            {
                "@type": "BreadcrumbList",
                "@id": url + "#breadcrumb",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Startseite", "item": SITE + "/"},
                    {"@type": "ListItem", "position": 2, "name": page["label"], "item": url},
                ],
            },
            {
                "@type": "Service",
                "@id": url + "#leistung",
                "name": page["label"],
                "serviceType": page["label"],
                "description": page["lead"],
                "url": url,
                "provider": {"@id": SITE + "/#praxis"},
                "areaServed": [{"@type": "City", "name": n} for n in ("Emmenbrücke", "Emmen", "Luzern")],
            },
            {
                "@type": "FAQPage",
                "mainEntity": [
                    {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                    for q, a in page["faq"]
                ],
            },
        ],
    }
    # "</" entschärfen, damit der Datenblock das <script>-Element nie vorzeitig beenden kann
    return json.dumps(data, ensure_ascii=False, indent=2).replace("</", "<\\/")


# ---------------------------------------------------------------------------
#  Seite zusammensetzen
# ---------------------------------------------------------------------------
def render(page: dict, shared: dict) -> str:
    url = f"{SITE}/{page['slug']}/"
    termin = f"/?anliegen={page['slug']}#termin"

    def localize(fragment: str) -> str:
        """Sprunglinks der Startseite (#x) zeigen von der Unterseite aus auf /#x.

        Wichtig: nur echte Links (<a href="#...">) umschreiben – NICHT die Icon-Verweise
        (<use href="#i-phone"/>), sonst findet der Browser die Symbole nicht mehr.
        """
        fragment = re.sub(r'(<a\b[^>]*?\bhref=")#', r"\1/#", fragment)
        # "Zum Inhalt springen" bleibt auf der eigenen Seite
        fragment = fragment.replace('href="/#main"', 'href="#main"')
        return fragment.replace('href="/#termin"', f'href="{termin}"')

    header = localize(shared["header"]).replace(
        '<a class="nav__link" href="/#leistungen">', '<a class="nav__link" href="/#leistungen" aria-current="true">'
    )
    footer = localize(shared["footer"])
    action_bar = localize(shared["action_bar"])

    faq = "".join(
        f"\n          <details>\n            <summary>{esc(q)}</summary>\n"
        f'            <div class="faq__answer"><p>{esc(a)}</p></div>\n          </details>'
        for q, a in page["faq"]
    )
    others = "".join(
        f'\n          <li><a class="link-card" href="/{o["slug"]}/">'
        f'<span class="link-card__title">{esc(o["label"])}</span>'
        f'<span class="link-card__text">{esc(o["teaser"])}</span>'
        f'<span class="link-card__more">Mehr erfahren {icon("i-arrow-right")}</span></a></li>'
        for o in PAGES if o["slug"] != page["slug"]
    )
    media_class = "page-hero__media page-hero__media--device" if page["image"]["device"] else "page-hero__media"
    phone_html = PHONE_SHOWN.replace(" ", "&nbsp;")

    return f"""<!DOCTYPE html>
<html lang="de-CH">
<head>
  <!-- Erzeugt von tools/build_leistungen.py – Texte dort ändern und das Skript neu ausführen. -->
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>{esc(page["title"])}</title>
  <meta name="description" content="{attr(page["description"])}">
  <link rel="canonical" href="{url}">
  <meta name="robots" content="index, follow, max-image-preview:large">
  <meta name="theme-color" content="#ffffff">
  <meta name="format-detection" content="telephone=no">

  <meta property="og:type" content="website">
  <meta property="og:locale" content="de_CH">
  <meta property="og:site_name" content="Physiotherapie Central Plaza GmbH">
  <meta property="og:title" content="{attr(page["title"])}">
  <meta property="og:description" content="{attr(page["description"])}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{SITE}/assets/img/og-image.jpg">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="Physiotherapie Central Plaza GmbH in Emmenbrücke – Physiotherapie, die bewegt.">
  <meta name="twitter:card" content="summary_large_image">

  <link rel="icon" href="/favicon.ico" sizes="32x32">
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png">
  <link rel="manifest" href="/site.webmanifest">

  <link rel="preload" href="/assets/fonts/jost-latin.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="/assets/css/main.css">
  <script src="/assets/js/main.js" defer></script>

  <script type="application/ld+json">
{json_ld(page, url)}
  </script>
</head>
<body>
  {shared["sprite"]}

  {header}
  <main id="main">
    <section class="page-hero page-hero--service" aria-labelledby="seitentitel">
      <div class="container page-hero__grid">
        <div>
          <nav class="breadcrumb" aria-label="Sie sind hier">
            <ol>
              <li><a href="/">Startseite</a></li>
              <li><a href="/#leistungen">Leistungen</a></li>
              <li><span aria-current="page">{esc(page["label"])}</span></li>
            </ol>
          </nav>
          <p class="eyebrow">{esc(page["eyebrow"])}</p>
          <h1 id="seitentitel">{esc(page["h1"])}</h1>
          <p>{esc(page["lead"])}</p>
          <div class="btn-row">
            <a class="btn btn--primary" href="{termin}">{icon("i-calendar")}Termin anfragen</a>
            <a class="btn btn--light" href="tel:{PHONE_LINK}">{icon("i-phone")}{phone_html}</a>
          </div>
          <p class="page-hero__hint">Telefon: {esc(PHONE_HOURS)} · Anfragen per Formular jederzeit</p>
        </div>
        <div class="{media_class}">
          {picture(page["image"])}
        </div>
      </div>
    </section>

    <section class="section">
      <div class="container article">
        <div class="article__main">
{render_blocks(page["blocks"])}
          <p class="article__disclaimer">Diese Informationen dienen der allgemeinen Orientierung und ersetzen keine individuelle ärztliche oder physiotherapeutische Abklärung.</p>
        </div>

        <aside class="article__aside" aria-label="Praxis auf einen Blick">
          <div class="aside-card">
            <h2>Auf einen Blick</h2>
            <ul class="aside-list">
              <li><span class="chip__icon">{icon("i-cap")}</span><span><strong>Hasan Zećiri</strong>Physiotherapeut (B.Sc.), M.Sc. Neurorehabilitation</span></li>
              <li><span class="chip__icon">{icon("i-pin")}</span><span><strong>Gerliswilstrasse 30</strong>6020 Emmenbrücke</span></li>
              <li><span class="chip__icon">{icon("i-clock")}</span><span><strong>{esc(OPENING_MAIN)}</strong>{esc(OPENING_SUB)}</span></li>
              <li><span class="chip__icon">{icon("i-car")}</span><span><strong>Eigene Patientenparkplätze</strong>hinter dem Tramhüsli</span></li>
              <li><span class="chip__icon">{icon("i-bus")}</span><span><strong>Bus bis «Viscosistadt»</strong>Linien 2 und 46, rund eine Gehminute</span></li>
              <li><span class="chip__icon">{icon("i-phone")}</span><span><strong><a href="tel:{PHONE_LINK}">{phone_html}</a></strong>{esc(PHONE_HOURS)}</span></li>
            </ul>
            <p class="open-status" id="open-status" hidden><span class="status-dot" data-open-dot></span><span data-open-text></span></p>
            <a class="btn btn--primary btn--block" href="{termin}">{icon("i-calendar")}Termin anfragen</a>
          </div>
        </aside>
      </div>
    </section>

    <section class="section section--ice" aria-labelledby="faq-titel">
      <div class="container">
        <div class="section-head section-head--center">
          <p class="eyebrow">Gut zu wissen</p>
          <h2 class="h2" id="faq-titel">Häufige <em>Fragen</em></h2>
        </div>
        <div class="faq">{faq}
        </div>
      </div>
    </section>

    <section class="section section--flush-bottom" aria-labelledby="weitere-titel">
      <div class="container">
        <div class="section-head">
          <p class="eyebrow">Leistungen</p>
          <h2 class="h2" id="weitere-titel">Weitere <em>Schwerpunkte</em></h2>
        </div>
        <ul class="link-cards">{others}
        </ul>
        <p class="more-link"><a href="/#leistungen">Alle Leistungen ansehen</a></p>
      </div>
    </section>

    <section class="section section--cta" aria-labelledby="cta-titel">
      <div class="container">
        <div class="cta-band">
          <h2 id="cta-titel">{esc(page["cta"])}</h2>
          <p>Wir beraten Sie gerne persönlich und nehmen uns Zeit für Ihr Anliegen.</p>
          <div class="btn-row">
            <a class="btn btn--white" href="{termin}">{icon("i-calendar")}Termin anfragen</a>
            <a class="btn btn--outline-white" href="tel:{PHONE_LINK}">{icon("i-phone")}{phone_html}</a>
          </div>
        </div>
      </div>
    </section>
  </main>

  {footer}

  {action_bar}
</body>
</html>
"""


def read_shared() -> dict:
    """Kopfzeile, Menü, Icons und Fusszeile aus der Startseite holen."""
    home = (PUBLIC / "index.html").read_text(encoding="utf-8")
    sprite_all = between(home, '<svg class="sr-only"', "</svg>", include_end=True)
    symbols = {m.group(1): m.group(0) for m in re.finditer(r'(?s)<symbol id="([^"]+)".*?</symbol>', sprite_all)}
    missing = [i for i in ICONS if i not in symbols]
    if missing:
        sys.exit(f"FEHLER: Icons fehlen in index.html: {missing}")
    sprite = (
        '<svg class="sr-only" aria-hidden="true" focusable="false" xmlns="http://www.w3.org/2000/svg">\n    '
        + "\n    ".join(symbols[i] for i in ICONS)
        + "\n  </svg>"
    )
    return {
        "sprite": sprite,
        "header": between(home, '<a class="skip-link"', '<main id="main">'),
        "footer": between(home, '<footer class="site-footer">', "</footer>", include_end=True),
        "action_bar": between(home, '<aside class="action-bar"', "</aside>", include_end=True),
    }


def write_sitemap() -> None:
    today = date.today().isoformat()
    entries = [("/", "1.0", "monthly")]
    entries += [(f"/{p['slug']}/", "0.8", "monthly") for p in PAGES]
    entries += [("/impressum/", "0.3", "yearly"), ("/datenschutz/", "0.3", "yearly")]
    body = "".join(
        f"  <url>\n    <loc>{SITE}{path}</loc>\n    <lastmod>{today}</lastmod>\n"
        f"    <changefreq>{freq}</changefreq>\n    <priority>{prio}</priority>\n  </url>\n"
        for path, prio, freq in entries
    )
    (PUBLIC / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + body + "</urlset>\n",
        encoding="utf-8",
    )


def main() -> None:
    shared = read_shared()
    for page in PAGES:
        # einfache Qualitätsprüfungen, damit SEO-Angaben nicht versehentlich zu lang werden
        if len(page["title"]) > 70:
            sys.exit(f"FEHLER: Titel zu lang ({len(page['title'])} Zeichen): {page['title']}")
        if not 110 <= len(page["description"]) <= 170:
            sys.exit(f"FEHLER: Beschreibung sollte 110–170 Zeichen haben ({len(page['description'])}): {page['slug']}")
        target = PUBLIC / page["slug"] / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render(page, shared), encoding="utf-8")
        print(f"geschrieben: public/{page['slug']}/index.html  (Titel {len(page['title'])} Z., "
              f"Beschreibung {len(page['description'])} Z.)")
    write_sitemap()
    print("geschrieben: public/sitemap.xml")


if __name__ == "__main__":
    main()
