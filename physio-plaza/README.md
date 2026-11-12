# Physiotherapie Central Plaza – Website

Neue Website für **Physiotherapie Central Plaza GmbH**, Gerliswilstrasse 30, 6020 Emmenbrücke
(Ersatz für den bisherigen Wix-Auftritt physio-plaza.com).

- Reines HTML/CSS/JavaScript – **kein Build, keine Abhängigkeiten, keine Datenbank, kein Login**
- Eigene 3D-Seidenwelle (WebGL) im Design von Visitenkarte & Praxisschild
- Läuft auf Netlify (kostenloser Plan reicht)

---

## 1. So lädst du die Website auf Netlify hoch

### Variante A – Drag & Drop (am einfachsten)
1. Auf <https://app.netlify.com> einloggen.
2. **Add new site → Deploy manually**.
3. Den Ordner **`physio-plaza/public`** (nicht den ganzen Projektordner!) ins Feld ziehen.
4. Unter **Site configuration → Change site name** z. B. `physio-plaza` eingeben → `physio-plaza.netlify.app`.

> `_headers` und `_redirects` liegen im Ordner `public` und werden automatisch mitgenommen.

### Variante B – über GitHub (Updates gehen dann automatisch live)
1. **Add new site → Import an existing project → GitHub** → dieses Repository wählen.
2. Branch: `claude/physiotherapist-website-klnmf0` (oder nach dem Mergen `main`).
3. **Base directory:** `physio-plaza` · **Build command:** leer lassen · **Publish directory:** `physio-plaza/public`.

---

## 2. Nach dem ersten Upload – Checkliste (wichtig!)

| # | Was | Wo in Netlify | Warum |
|---|-----|---------------|-------|
| 1 | **Formular-Erkennung einschalten** | Site configuration → Forms → *Enable form detection*, danach **neu deployen** | Sonst kommen keine Anfragen an. |
| 2 | **E-Mail-Benachrichtigung** an `info@physio-plaza.ch` | Forms → Form notifications → Email notification (Formular „kontakt") | Hasan bekommt jede Anfrage sofort per Mail. |
| 3 | **Test-Anfrage senden** | auf der Live-Seite | Prüfen, ob Mail ankommt (auch im Spam-Ordner schauen). |
| 4 | **Domain verbinden** | Domain management → Add a domain → `www.physio-plaza.com` als *Primary* | Neue Seite unter der alten Adresse – Google-Ranking bleibt. |
| 5 | DNS beim Domain-Anbieter umstellen | gemäss Anleitung von Netlify | Erst danach zeigt die Domain auf die neue Seite. |
| 6 | **HTTPS** prüfen (Let's Encrypt) | Domain management → HTTPS | Wird automatisch aktiviert; muss „Certificate active" zeigen. |
| 7 | **Wix erst kündigen, wenn die Domain auf Netlify zeigt** | – | Sonst ist die Praxis offline. Domain ggf. von Wix wegtransferieren. |
| 8 | Sicherheits-Test | <https://securityheaders.com> und <https://developer.mozilla.org/en-US/observatory> | Ziel: Note **A+**. |
| 9 | Google Search Console | Property anlegen → `sitemap.xml` einreichen | Google findet die neue Seite schneller. |
| 10 | Google-Unternehmensprofil | Website-Link & Öffnungszeiten prüfen | Lokales SEO („Physiotherapie Emmenbrücke"). |
| 11 | Netlify **Data Processing Agreement** | im Netlify-Konto/Trust Center (DPA) herunterladen & ablegen | Wird in der Datenschutzerklärung erwähnt. |
| 12 | Formular-Anfragen regelmässig löschen | Forms → Submissions | Datenschutzerklärung verspricht Löschung spätestens nach 12 Monaten. |

---

## 3. Wo ändere ich was?

| Inhalt | Datei |
|--------|-------|
| Alle Texte der Startseite | `public/index.html` |
| Farben, Abstände, Schrift | `public/assets/css/main.css` (oben bei „Design-Tokens") |
| Impressum / Datenschutz | `public/impressum/index.html`, `public/datenschutz/index.html` |
| Sicherheits-Header | `public/_headers` |
| Weiterleitungen alter Adressen | `public/_redirects` |

### ⚠️ Öffnungszeiten stehen an mehreren Stellen – immer alle anpassen
1. `public/index.html` → Tabelle `id="hours"` (Kontaktbereich)
2. `public/index.html` → Footer „Öffnungszeiten"
3. `public/index.html` → FAQ „Kann ich auch abends oder am Samstag kommen?"
4. `public/index.html` → JSON-LD oben (`openingHoursSpecification` **und** die gleiche FAQ-Antwort, für Google)
5. `public/index.html` → Hero-Liste „Mo–Sa geöffnet, auch abends"
6. `public/assets/js/main.js` → `var HOURS = { … }` (für die Live-Anzeige „Jetzt geöffnet")

Tipp: `grep -rn "21:00\|21 Uhr\|19:00" public` zeigt alle Fundstellen.

### FAQ ändern
Jede Frage steht **zweimal** in `index.html`: sichtbar (`<details>`) und im JSON-LD (`FAQPage`).
Beide müssen wortgleich sein, sonst ignoriert Google die FAQ.

### Andere Domain als www.physio-plaza.com?
Die Adresse steht in `index.html`, `impressum/index.html`, `datenschutz/index.html`, `sitemap.xml`,
`robots.txt` und `.well-known/security.txt`. Einmal alles ersetzen, z. B.:
```bash
grep -rl "www.physio-plaza.com" public | xargs sed -i 's#https://www.physio-plaza.com#https://www.NEUE-DOMAIN.ch#g'
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
- ⚠️ **Vom Kunden bestätigen lassen:** siehe Abschnitt 6

---

## 6. Offene Punkte – bitte mit Hasan klären

1. **Titel & Abschlüsse** exakt so korrekt? (Physiotherapeut B.Sc., M.Sc. Neurorehabilitation, Master Ultraschalldiagnostik, „über 15 Jahre Erfahrung", seit 2018 in der Schweiz)
1a. **Dry Needling**: Physioswiss verlangt dafür SRK-Anerkennung **und** eine standardisierte Dry-Needling-Ausbildung. Zertifikat vorhanden? Sonst die Karte entfernen.
2. **Text Neurorehabilitation** („begleite ich Menschen mit neurologisch bedingten Einschränkungen …") – inhaltlich ok?
3. **FAQ-Antworten** (Verordnung, Versichertenkarte, Krankenkasse) – passen sie zur Praxis?
4. **Bildrechte**: Gerätefotos stammen von Herstellern, das Dry-Needling-Bild von der alten Wix-Seite – dürfen sie verwendet werden? (Im Zweifel durch eigene Fotos ersetzen.)
5. **Mobilnummer** (076 271 22 76, steht auf dem Praxisschild) zusätzlich auf der Website zeigen? Aktuell nur Festnetz.
6. **Logo**: wurde als Vektor nachgezeichnet (`brand/logo-mark.svg`). Falls die Original-Logodatei existiert → austauschen.
7. **Domain**: bleibt es `www.physio-plaza.com`? (E-Mail läuft über `physio-plaza.ch`.)
8. **Online-Buchung**: Wix-Buchung war leer. Später z. B. OneDoc o. Ä. einbinden? (Dann CSP + Datenschutz anpassen.)

---

## 7. Qualitäts-Ergebnisse (lokal gemessen)

| Test | Ergebnis |
|------|----------|
| Lighthouse Desktop | Performance 100 · Barrierefreiheit 100 · Best Practices 100 · SEO 100 |
| Lighthouse Mobile | Performance 97–98 · Barrierefreiheit 100 · Best Practices 100 · SEO 100 |
| Lighthouse Impressum / Datenschutz | 100 · 100 · 100 · 100 |
| Sicherheits-Review (Code) | keine Schwachstellen gefunden |
| axe-core (WCAG 2.1 AA) | 0 Verstösse auf allen 5 Seiten (Desktop & Handy) |
| HTML-Validierung (html-validate) | 0 Fehler auf allen 5 Seiten |
| Kontrast | alle Texte ≥ 4.5:1 (grosse Überschriften ≥ 3:1) |
| Responsive | 320 / 375 / 768 / 1280+ px, kein horizontales Scrollen |
| Geräte-Emulation | iPhone SE, iPhone 13, Pixel 7, Galaxy S9+, iPad Mini – exakte Breite, kein seitliches Wischen |
| Funktionstests | Menü, Formular (Fehler/Erfolg/Honeypot), Galerie, Grossansicht, Filter, ohne JavaScript, „Bewegung reduzieren" |

---

## Projektstruktur
```
physio-plaza/
├── netlify.toml            Netlify-Einstellungen (für Variante B)
├── public/                 ← DAS wird veröffentlicht
│   ├── index.html          Startseite
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
│   └── SEO-AUDIT.md        lokales SEO-Audit mit Keywords & Aktionsplan
└── tools/                  Bild- und Muster-Generator (Python)
```
