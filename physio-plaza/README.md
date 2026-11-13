# Physiotherapie Central Plaza – Website

Neue Website für **Physiotherapie Central Plaza GmbH**, Gerliswilstrasse 30, 6020 Emmenbrücke
(Ersatz für den bisherigen Wix-Auftritt physio-plaza.com).

- Reines HTML/CSS/JavaScript – **keine Abhängigkeiten, keine Datenbank, kein Login**
- Für den Upload ist **kein Build nötig**: Die fertigen Dateien liegen in `public/`
- Eigene 3D-Seidenwelle (WebGL) im Design von Visitenkarte & Praxisschild
- 9 Seiten: Startseite, 4 Leistungsseiten, Impressum, Datenschutz, Danke-Seite, Fehlerseite
- Läuft auf Netlify (kostenloser Plan reicht)

---

## 1. So lädst du die Website auf Netlify hoch

> Die Menünamen unten entsprechen der Netlify-Dokumentation vom November 2026. Netlify benennt Menüs
> gelegentlich um – wenn etwas anders heisst, hilft die Suche oben im Netlify-Dashboard.

### Variante A – Drag & Drop (am einfachsten)
1. Die ZIP-Datei **zuerst entpacken**. Netlify nimmt beim Hineinziehen einen **Ordner**, keine ZIP-Datei.
2. Auf <https://app.netlify.com> einloggen und die Seite **Projects** öffnen. Ganz unten ist das Feld zum Hineinziehen.
3. Den entpackten Ordner **`physio-plaza-website`** hineinziehen.
   (Wer aus dem Repository arbeitet: Das ist der Ordner `physio-plaza/public` – nicht der ganze Projektordner!)
4. Projektnamen ändern, z. B. `physio-plaza` → Adresse `physio-plaza.netlify.app`.

> `_headers` und `_redirects` liegen im Ordner und werden automatisch mitgenommen.

**Später aktualisieren:** Projekt öffnen → **Deploys** → den neuen Ordner ins Feld ganz unten ziehen.

### Variante B – über GitHub (Updates gehen dann automatisch live)
1. **Add new project → Import an existing project → GitHub** → dieses Repository wählen.
2. Branch: `claude/physiotherapist-website-klnmf0` (oder nach dem Mergen `main`).
3. **Base directory:** `physio-plaza` · **Build command:** leer lassen · **Publish directory:** `physio-plaza/public`.

### ⚠️ Drei Dinge, die man bei Netlify wissen muss
| Thema | Was gilt (Netlify-Doku, Nov. 2026) | Was du tust |
|-------|------------------------------------|-------------|
| **Kontingent** | Im Free-Plan gibt es 300 Credits pro Monat. **Jede Veröffentlichung kostet 15 Credits**, dazu kommen Datenverkehr (20 Credits pro GB) und Seitenaufrufe (2 Credits pro 10 000 Anfragen). Formulare sind gratis. | Nicht «zum Ausprobieren» zwanzigmal hochladen – erst lokal prüfen, dann hochladen. |
| **Pause bei 0 Credits** | Ist das Kontingent aufgebraucht, werden **alle Projekte im Konto pausiert** (Besucher sehen «Site not available», Formulare gehen nicht mehr) – bis zum nächsten Monat oder bis zu einem bezahlten Plan. | Für eine Praxis-Website am besten ein **eigenes Netlify-Konto der Praxis** (nicht zusammen mit anderen Kundenprojekten). Die Warn-Mails von Netlify (50/75/90 %) ernst nehmen. |
| **Wem gehört das Konto?** | Wer das Konto verwaltet, kann die Formular-Anfragen der Patientinnen und Patienten lesen. | Läuft die Seite in **deinem** Konto, braucht es einen kurzen schriftlichen Auftragsbearbeitungsvertrag zwischen Praxis und ADEMI DIGITAL (siehe `docs/RECHT-CHECK.md`). Sauberer: Konto gehört der Praxis. |

> Ältere Netlify-Konten (erstellt vor dem 4. September 2025) haben noch das alte Preismodell ohne Credits,
> dafür mit einer Obergrenze für Formular-Anfragen pro Monat. Welches Modell gilt, steht im Dashboard unter
> **Usage & billing**.

---

## 2. Nach dem ersten Upload – Checkliste (wichtig!)

| # | Was | Wo in Netlify | Warum |
|---|-----|---------------|-------|
| 1 | **Projekt öffentlich schalten** | Knopf **Make public** (oder Project configuration → General → Visitor access → Project visibility) | Neue Projekte können als «privat» starten – dann sieht nur das Netlify-Team die Seite, Besucher nicht. |
| 2 | **«Powered by Netlify»-Abzeichen ausschalten** | Project configuration → General → Powered by Netlify badge → aus | Auf neuen Free-Projekten blendet Netlify unten rechts ein eigenes Abzeichen ein. Unsere Sicherheitsrichtlinie (CSP) blockiert es zwar – aber der blockierte Versuch erzeugt eine Fehlermeldung im Browser. Ausschalten = sauber. |
| 3 | **Formular-Erkennung einschalten** | Forms → *Enable form detection*, danach **nochmals hochladen** (die Erkennung greift erst ab der nächsten Veröffentlichung) | Sonst kommen keine Anfragen an – das Formular zeigt dann eine Fehlermeldung. |
| 4 | **E-Mail-Benachrichtigung** an `info@physio-plaza.ch` | Forms → Submission notifications → E-Mail hinzufügen (Formular „kontakt") | Hasan bekommt jede Anfrage sofort per Mail. |
| 5 | **Hasan bestätigt die Benachrichtigung** | Netlify schickt an `info@physio-plaza.ch` eine Bestätigungs-Mail → **Confirm** anklicken | Adressen ausserhalb des Netlify-Teams bekommen erst nach dieser Bestätigung Mails; bis dahin steht «pending confirmation». Lehnt Netlify die Adresse ganz ab («must be the email of a team member»), ist die Bestätigung für das Konto noch nicht freigeschaltet → Konto der Praxis verwenden oder vorerst die eigene Adresse eintragen und weiterleiten. |
| 6 | **Test-Anfrage senden** | auf der Live-Seite | Prüfen, ob die Mail ankommt (auch im Spam-Ordner schauen). Antworten gehen direkt an die Patientin/den Patienten, wenn eine E-Mail-Adresse angegeben wurde. |
| 7 | **Domain verbinden** | Domain management → Domain hinzufügen → `www.physio-plaza.com` als *Primary* | Neue Seite unter der alten Adresse – Google-Ranking bleibt. |
| 8 | DNS beim Domain-Anbieter umstellen | gemäss Anleitung von Netlify | Erst danach zeigt die Domain auf die neue Seite. |
| 9 | **HTTPS** prüfen (Let's Encrypt) | Domain management → HTTPS | Wird automatisch aktiviert; muss „Certificate active" zeigen. |
| 10 | **Wix erst kündigen, wenn die Domain auf Netlify zeigt** | – | Sonst ist die Praxis offline. Domain ggf. von Wix wegtransferieren. |
| 11 | Sicherheits-Test | <https://securityheaders.com> und <https://developer.mozilla.org/en-US/observatory> | Ziel: Note **A+**. |
| 12 | Google Search Console | Property anlegen → `sitemap.xml` einreichen | Google findet die neue Seite schneller. |
| 13 | Google-Unternehmensprofil | Website-Link & Öffnungszeiten prüfen | Lokales SEO („Physiotherapie Emmenbrücke"). |
| 14 | Netlify **Data Processing Agreement** | im Netlify-Konto/Trust Center (DPA) herunterladen & ablegen | Wird in der Datenschutzerklärung erwähnt. |
| 15 | Formular-Anfragen regelmässig löschen | Forms → Submissions | Datenschutzerklärung verspricht Löschung spätestens nach 12 Monaten. |

---

## 3. Wo ändere ich was?

| Inhalt | Datei |
|--------|-------|
| Alle Texte der Startseite | `public/index.html` |
| **Leistungsseiten** (Neurorehabilitation, Dry Needling, Stosswellentherapie, Massage) | `tools/build_leistungen.py` (Abschnitt `PAGES`) – danach das Skript ausführen, siehe unten |
| Farben, Abstände, Schrift | `public/assets/css/main.css` (oben bei „Design-Tokens") |
| Impressum / Datenschutz | `public/impressum/index.html`, `public/datenschutz/index.html` |
| Sicherheits-Header | `public/_headers` |
| Weiterleitungen alter Adressen | `public/_redirects` |

### Leistungsseiten ändern oder eine neue anlegen
Die vier Leistungsseiten werden von einem kleinen Skript erzeugt. Kopfzeile, Menü, Icons und
Fusszeile übernimmt es automatisch aus der Startseite – so können die Seiten nie voneinander abweichen.
```bash
# 1. Texte in tools/build_leistungen.py anpassen (oder einen neuen Block in PAGES kopieren)
python3 tools/build_leistungen.py     # 2. Seiten + sitemap.xml neu erzeugen
python3 tools/check_links.py          # 3. prüfen, ob alle Links, Bilder und Icons stimmen
```
Die Dateien `public/<leistung>/index.html` **nicht von Hand ändern** – sie werden überschrieben.
Auch nach Änderungen an Kopf- oder Fusszeile der Startseite das Skript einmal laufen lassen.
(Impressum und Datenschutz haben eine eigene, einfachere Kopf- und Fusszeile direkt in der Datei.)

### Vor jedem Upload
```bash
python3 tools/check_links.py
```
Meldet kaputte Links, fehlende Bilder/Icons und FAQ-Texte, die nicht mehr zu den Google-Daten passen.

### ⚠️ Öffnungs- und Telefonzeiten stehen an mehreren Stellen – immer alle anpassen
1. `public/index.html` → Tabelle `id="hours"` (Kontaktbereich)
2. `public/index.html` → Footer „Öffnungszeiten"
3. `public/index.html` → FAQ „Kann ich auch abends oder am Samstag kommen?"
4. `public/index.html` → JSON-LD oben (`openingHoursSpecification` **und** die gleiche FAQ-Antwort, für Google)
5. `public/index.html` → Hero-Liste „Mo–Sa geöffnet, auch abends" und die Telefonzeit-Hinweise
6. `public/assets/js/main.js` → `var HOURS = { … }` und `var PHONE_HOURS = { … }` (Live-Anzeigen „Jetzt geöffnet" / „Jetzt telefonisch erreichbar")
7. `tools/build_leistungen.py` → `OPENING_MAIN`, `OPENING_SUB`, `PHONE_HOURS` (Infokarte der Leistungsseiten) – danach Skript ausführen

Tipp: `grep -rn "21:00\|21 Uhr\|19:00\|13:00" public tools` zeigt alle Fundstellen.

### FAQ ändern
Jede Frage der Startseite steht **zweimal** in `index.html`: sichtbar (`<details>`) und im JSON-LD (`FAQPage`).
Beide müssen wortgleich sein, sonst ignoriert Google die FAQ – `tools/check_links.py` prüft das.
Bei den Leistungsseiten erledigt das Skript beides automatisch.

### Anfahrt aktuell halten
Buslinien (2 und 46 an der Haltestelle «Emmenbrücke, Viscosistadt») stammen aus den offiziellen
Fahrplandaten vom November 2026. Nach dem Fahrplanwechsel im Dezember kurz auf sbb.ch prüfen.
Die Bildunterschrift beim Parkplan gibt die Datumsangaben aus dem Plan wieder (Feld 276 ab 1. Dezember 2026,
Feld 275 ab 1. Februar 2027). Ab Februar 2027 vereinfachen – am besten mit einem neuen Plan ohne Datum von Hasan.

### Andere Domain als www.physio-plaza.com?
Die Adresse steht in `index.html`, `impressum/index.html`, `datenschutz/index.html`, `robots.txt`,
`.well-known/security.txt` und als `SITE` in `tools/build_leistungen.py`. Einmal alles ersetzen, z. B.:
```bash
grep -rl "www.physio-plaza.com" public tools | xargs sed -i 's#https://www.physio-plaza.com#https://www.NEUE-DOMAIN.ch#g'
python3 tools/build_leistungen.py
```

### Neue Fotos einbauen
```bash
python3 tools/optimize_images.py <ordner-mit-originalfotos>   # erzeugt AVIF + WebP in mehreren Grössen
python3 tools/make_silk_svg.py                                  # Wellenmuster neu erzeugen
```
Das Skript entfernt automatisch **alle Metadaten** (z. B. GPS-Standort aus Handyfotos).

---

## 4. Sicherheit – was eingebaut ist und warum (Lernmodus)

| Massnahme | Was sie verhindert |
|-----------|--------------------|
| **Statische Seite** ohne CMS, Datenbank oder Login | Es gibt nichts, was man „hacken" kann: keine SQL-Injection, keine geklauten Admin-Passwörter, keine veralteten Plugins (Hauptgrund für gehackte WordPress-Seiten). |
| **Content-Security-Policy** (`default-src 'none'`, nur eigene Dateien, kein `unsafe-inline`) | Selbst wenn jemand Code einschleusen könnte, würde der Browser ihn nicht ausführen (XSS-Schutz). |
| **Trusted Types** (`require-trusted-types-for 'script'`) | Der Browser blockiert gefährliche DOM-Zuweisungen wie `innerHTML` mit Text komplett. Unser JavaScript nutzt nur `textContent`. |
| **HSTS** (2 Jahre) | Verbindung immer verschlüsselt, kein Abfangen über unsicheres WLAN. |
| **X-Frame-Options / frame-ancestors** | Niemand kann die Seite unsichtbar in eine Betrugsseite einbetten (Clickjacking). |
| **Permissions-Policy** | Kamera, Mikrofon, Standort, Zahlungen usw. sind gesperrt. |
| **COOP / CORP / Origin-Agent-Cluster** | Isoliert die Seite von fremden Fenstern und Seiten. |
| **Keine externen Dienste** (kein Google Fonts, kein Maps-Embed, kein Tracking) | Keine Daten an Dritte → kein Cookie-Banner nötig, keine Abmahnung wegen Google Fonts. |
| **Formular**: Honeypot-Feld, Zeitsperre (Bots sind zu schnell), Mehrfachversand-Sperre, Längenbegrenzungen, Netlify-Spamfilter | Spam-Schutz ohne reCAPTCHA (das wäre wieder Google). |
| **Keine Gesundheitsdaten im Formular** (Hinweis im Formular) | Gesundheitsdaten sind besonders schützenswert (DSG). |
| **security.txt** | Seriöse Sicherheitsforscher wissen, wo sie Lücken melden können. |
| **DDoS / Firewall** | Übernimmt Netlify automatisch (globales CDN). |

---

## 5. Recht (Schweiz) – Stand der Umsetzung

- ✅ Impressum mit Firma, Adresse, E-Mail, Geschäftsführer, **UID CHE-149.883.560** (aus Zefix geprüft)
- ✅ Datenschutzerklärung nach revDSG (inkl. DSGVO-Hinweisen), Netlify als Hosting (USA, Swiss-U.S. Data Privacy Framework zertifiziert – geprüft)
- ✅ Kein Cookie-Banner nötig: keine Cookies, kein Tracking
- ✅ Schriften lokal (kein Google-Fonts-Risiko)
- ✅ Gesundheitswerbung **sachlich** formuliert (GesBG Art. 16: Werbung muss objektiv, nicht irreführend und nicht aufdringlich sein): keine Heilversprechen, keine Superlative wie „beste" oder „modernste", Wirkungen mit „kann … unterstützen"
- ✅ Leistungsseiten mit Hinweis „ersetzt keine individuelle Abklärung" und mit Hinweisen, wann man die Praxis vor der Behandlung informieren soll (z. B. Schwangerschaft, Blutverdünner)
- ⚠️ **Vom Kunden bestätigen lassen:** siehe Abschnitt 6 – vor allem die medizinischen Texte der vier Leistungsseiten

---

## 6. Offene Punkte – bitte mit Hasan klären

**Vor dem Livegang (wichtig):**

1. **Medizinische Texte der vier Leistungsseiten** (`/neurorehabilitation/`, `/dry-needling/`, `/stosswellentherapie/`, `/massage/`): Hasan liest sie fachlich gegen – Anwendungsgebiete, Ablauf, Hinweise vor der Behandlung, FAQ. Die Texte sind bewusst vorsichtig formuliert, stammen aber nicht von ihm. Dasselbe gilt für den Neuro-Text auf der Startseite.
2. **Dry Needling**: Physioswiss verlangt dafür SRK-Anerkennung **und** eine standardisierte Dry-Needling-Ausbildung. Zertifikat vorhanden? Sonst Karte **und** Seite `/dry-needling/` entfernen: Block in `tools/build_leistungen.py` löschen, Ordner `public/dry-needling/` löschen, Skript ausführen – `python3 tools/check_links.py` zeigt danach alle Stellen, die noch auf die Seite verweisen.
3. **Titel & Abschlüsse**: gemäss Praxis-Broschüre umgesetzt – Physiotherapeut (B.Sc.), M.Sc. Neurorehabilitation, **Ultraschalldiagnostik (MSc) in Ausbildung**, über 15 Jahre Erfahrung, seit 2018 in der Schweiz, Praxis seit 2023. Sobald der Ultraschall-Master abgeschlossen ist: Text im Profil und Zeitstrahl anpassen.
4. **Parkplan**: Im Plan sind die Felder 271–274 rot markiert; bei den grauen Feldern steht „Parkplatz ab 01.12.26" (276) und „ab 01.02.27" (275). Stimmt die Lesart „rot = heute gültig, grau = kommt dazu"? Am besten liefert Hasan einen aktuellen Plan ohne Datum.
5. **Bildrechte**: Gerätefotos stammen von Herstellern, das Dry-Needling-Bild von der alten Wix-Seite – dürfen sie verwendet werden? (Im Zweifel durch eigene Fotos ersetzen.)
6. **FAQ-Antworten** (Verordnung, Versichertenkarte, Krankenkasse) – passen sie zur Praxis?

**Kann nach dem Livegang folgen:**

7. **Barrierefreier Zugang**: Ist die Praxis stufenlos bzw. mit Lift erreichbar? Für Neuro-Patientinnen und -Patienten eine der ersten Fragen – wenn ja, gehört das auf die Seite (Anfahrt + Neurorehabilitation).
8. **Preise für Selbstzahler** (Massagen): nennen oder nicht? Falls ja: Preisbekanntgabeverordnung beachten (Endpreise in CHF).
9. **Mobilnummer** (076 271 22 76, steht auf dem Praxisschild) zusätzlich auf der Website zeigen? Aktuell nur Festnetz.
10. **Logo**: nach der Broschüre zweifarbig als Vektor nachgezeichnet (`brand/logo-mark.svg`). Falls die Original-Logodatei (SVG/PDF) existiert → austauschen.
11. **Domain**: bleibt es `www.physio-plaza.com`? (E-Mail läuft über `physio-plaza.ch`.)
12. **Online-Buchung**: Wix-Buchung war leer. Später z. B. OneDoc o. Ä. einbinden? (Dann CSP + Datenschutz anpassen.)
13. **Echte Behandlungsfotos** (Hasan bei der Arbeit, mit Einwilligung der abgebildeten Person) – das stärkste Vertrauenssignal, das der Seite noch fehlt.

---

## 7. Qualitäts-Ergebnisse (lokal gemessen)

Gemessen am 13. November 2026 mit einem lokalen Testserver, der Netlify nachbildet (Header, Weiterleitungen,
Komprimierung). Werte in der Reihenfolge Leistung · Barrierefreiheit · Best Practices · SEO.

| Test | Ergebnis |
|------|----------|
| Lighthouse PC – Startseite, 4 Leistungsseiten, Impressum, Datenschutz | 100 · 100 · 100 · 100 |
| Lighthouse Handy – Startseite | 96 · 100 · 100 · 100 (fünf Läufe, jedes Mal 96) |
| Lighthouse Handy – Leistungsseiten | 99 · 100 · 100 · 100 |
| Lighthouse Handy – Impressum / Datenschutz | 100 · 100 · 100 · 100 |
| Lighthouse Danke-Seite | 100 · 100 · 100 · 63 – der SEO-Wert ist Absicht: Die Seite ist für Google gesperrt (`noindex`) |
| Fehlerseite (404) | mit Lighthouse nicht messbar, weil sie korrekt den Status 404 liefert; mit axe-core und HTML-Validierung geprüft |
| Sicherheits-Review (Code) | keine Schwachstellen gefunden; kein Inline-Code, keine fremden Skripte, kein `innerHTML` |
| axe-core (WCAG 2.1 AA) | 0 Verstösse auf allen 9 Seiten (PC & Handy) |
| HTML-Validierung (html-validate) | 0 Fehler auf allen 9 Seiten |
| Link-Prüfer (`tools/check_links.py`) | 381 Verweise auf 9 Seiten, 0 Probleme |
| Kontrast | alle Texte ≥ 4.5:1 (grosse Überschriften ≥ 3:1) |
| Responsive | 320 / 375 / 768 / 1280+ px, kein horizontales Scrollen |
| Geräte-Emulation | iPhone SE, iPhone 13, Pixel 7, Galaxy S9+, iPad Mini – exakte Breite, kein seitliches Wischen |
| Funktionstests (automatisiert) | Menü, Formular (Fehler/Erfolg/Honeypot/Vorauswahl), Galerie, Grossansicht, Filter, Einblendungen, Zeitstrahl, Sprunglinks, alte Wix-Adressen, Telefon- und Öffnungszeiten-Anzeige, ohne JavaScript, „Bewegung reduzieren" |

> Die Handy-Werte entstehen mit künstlich gedrosseltem Prozessor und langsamem Mobilfunk. Je nach Testrechner
> schwanken sie um ein bis zwei Punkte – auf der echten Netlify-Adresse nochmals mit
> <https://pagespeed.web.dev> messen.

---

## Projektstruktur
```
physio-plaza/
├── netlify.toml            Netlify-Einstellungen (für Variante B)
├── public/                 ← DAS wird veröffentlicht
│   ├── index.html          Startseite (von Hand gepflegt – Vorlage für Kopf- und Fusszeile)
│   ├── neurorehabilitation/ dry-needling/ stosswellentherapie/ massage/
│   │                       Leistungsseiten (vom Skript erzeugt – nicht von Hand ändern)
│   ├── impressum/ datenschutz/ danke/   Unterseiten
│   ├── 404.html            Fehlerseite
│   ├── _headers            Sicherheits-Header
│   ├── _redirects          Weiterleitungen alter Wix-Adressen
│   ├── robots.txt sitemap.xml site.webmanifest
│   ├── .well-known/security.txt
│   └── assets/ (css, js, fonts, img)
├── brand/                  Logo als SVG (blau & weiss) für Drucksachen/Social Media
├── docs/
│   ├── QA-CHECKLISTE.md    ADEMI-QA: Bestanden/Offen + deine Aufgaben
│   ├── RECHT-CHECK.md      Compliance-Check (DSG, UWG, GesBG, Bildrechte)
│   ├── SEO-AUDIT.md        lokales SEO-Audit mit Keywords & Aktionsplan
│   └── DESIGN-CRITIQUE.md  Design-Kritik: Befunde und was umgesetzt wurde
└── tools/
    ├── build_leistungen.py erzeugt die Leistungsseiten und die sitemap.xml
    ├── check_links.py      prüft Links, Bilder, Icons und FAQ – vor jedem Upload ausführen
    ├── optimize_images.py  Fotos verkleinern (AVIF/WebP), Metadaten entfernen
    └── make_silk_svg.py    Wellenmuster erzeugen
```
