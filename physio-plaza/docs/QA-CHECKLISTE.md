# ADEMI Website-QA – Physiotherapie Central Plaza

Stand: November 2026 · geprüft lokal mit Netlify-ähnlichem Testserver (Header, Weiterleitungen, Brotli)

## Top 3 Prioritäten (offen)
1. **Netlify Forms aktivieren + Benachrichtigung + Live-Test.**
   *Warum:* Ohne aktivierte Formular-Erkennung landen Patientenanfragen im Nichts – das Formular ist das wichtigste Werkzeug, um neue Patienten zu gewinnen.
2. **Kundenbestätigung einholen** (Titel/Abschlüsse, Dry-Needling-Zertifikat, FAQ-Texte, Bildrechte Gerätefotos).
   *Warum:* Falsche Titel oder fremde Fotos ohne Erlaubnis sind die realistischsten Abmahn-Gründe für eine Praxis-Website (UWG, Urheberrecht).
3. **Domain umziehen, HTTPS prüfen, Google-Unternehmensprofil + Search Console verknüpfen.**
   *Warum:* Erst mit der alten Domain übernimmt die neue Seite das Google-Ranking; das Unternehmensprofil bringt bei lokalen Suchen die meisten Klicks.

## Checkliste

| # | Bereich | Punkt | Status |
|---|---|---|---|
| 1 | Layout & Responsive | 375 / 768 / 1280+ px geprüft, kein horizontales Scrollen | ✅ Bestanden |
| 1 | Layout & Responsive | Texte nicht abgeschnitten, Buttons ≥ 48 px (Hauptbuttons 56 px) | ✅ Bestanden |
| 2 | Design-System | Kundenmarke umgesetzt: Weiss, Praxis-Blau, Seidenwellen; Schrift Jost (wie Visitenkarte). ADEMI-Farben gelten nur für ADEMI-Eigenmaterial | ✅ Bestanden |
| 2 | Design-System | Einheitliche Abstände/Typo über Design-Tokens in `main.css` | ✅ Bestanden |
| 3 | Performance | Bilder als AVIF + WebP in passenden Grössen, Lazy-Loading, keine Fremd-Skripte | ✅ Bestanden |
| 3 | Performance | Lighthouse Desktop 100 · Handy 97–98 | ✅ Bestanden |
| 4 | SEO | Title, Meta-Description, genau 1 H1 (mit Ort), sinnvolle H2/H3 | ✅ Bestanden |
| 4 | SEO | Alt-Texte, sitemap.xml, robots.txt, Open Graph, Schema.org (Physiotherapy, FAQ) | ✅ Bestanden |
| 4 | SEO | Google-Unternehmensprofil verknüpft (`sameAs`) | ⏳ Offen |
| 5 | Barrierefreiheit | Kontrast ≥ 4.5:1, sichtbarer Fokus, Formular-Labels, Alt-Texte | ✅ Bestanden |
| 5 | Barrierefreiheit | axe-core WCAG 2.1 AA: 0 Verstösse; Tastatur, „Bewegung reduzieren", ohne JS | ✅ Bestanden |
| 6 | Formulare & Recht | Kontaktformular lokal getestet inkl. Spam-Schutz (Honeypot, Zeitsperre) | ✅ Bestanden |
| 6 | Formulare & Recht | Formular live auf Netlify getestet (E-Mail kommt an) | ⏳ Offen |
| 6 | Formulare & Recht | Datenschutzerklärung, Impressum (mit UID), kein Cookie-Banner nötig | ✅ Bestanden |
| 6 | Formulare & Recht | Inhalte/Titel/Bildrechte vom Kunden bestätigt | ⏳ Offen |
| 7 | Deployment | Netlify-Konfiguration, `_headers`, `_redirects`, 404, Favicon | ✅ Bestanden |
| 7 | Deployment | Domain/DNS, HTTPS-Zertifikat | ⏳ Offen (nach Upload) |
| 7 | Deployment | Deploy nur mit ausdrücklichem OK von Berin | ✅ (nicht deployt) |

## Deine Aufgaben, Berin (Lernmodus)
Bitte selbst umsetzen, danach lese ich gegen:

1. **Netlify Forms einrichten**: Formular-Erkennung aktivieren, neu deployen, E-Mail-Benachrichtigung an
   `info@physio-plaza.ch`, Testanfrage senden. → Schick mir einen Screenshot der eingegangenen Anfrage.
2. **`sameAs` ergänzen**, sobald das Google-Unternehmensprofil live ist: In `public/index.html` im JSON-LD
   beim Block `"@type": "Physiotherapy"` die Zeile
   `"sameAs": ["https://maps.google.com/?cid=DEINE-ID"],` hinzufügen (Komma beachten!).
   → Danach prüfen mit dem Google-Test für Rich-Suchergebnisse.
