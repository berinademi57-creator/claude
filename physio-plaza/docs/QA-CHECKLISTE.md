# ADEMI Website-QA – Physiotherapie Central Plaza

Stand: 13. November 2026 · geprüft lokal mit Netlify-ähnlichem Testserver (Header, Weiterleitungen, Brotli)
Umfang: 9 Seiten – Startseite, 4 Leistungsseiten, Impressum, Datenschutz, Danke-Seite, Fehlerseite

## Top 3 Prioritäten (offen)
1. **Netlify richtig einschalten: Projekt öffentlich, Formular-Erkennung an, Benachrichtigung an – und Hasan klickt in der Bestätigungs-Mail auf «Confirm».**
   *Warum:* Ohne Formular-Erkennung zeigt das Formular eine Fehlermeldung. Ohne bestätigte Benachrichtigung bleiben
   Anfragen ungelesen im Netlify-Konto liegen. Das Formular ist das wichtigste Werkzeug, um neue Patienten zu gewinnen.
2. **Hasan gibt die Inhalte frei** – medizinische Texte der vier Leistungsseiten, Dry-Needling-Zertifikat, Titel,
   Parkplan, Bildrechte der Gerätefotos.
   *Warum:* Falsche Fachaussagen, unzutreffende Titel oder fremde Fotos ohne Erlaubnis sind die realistischsten Gründe
   für eine Abmahnung oder eine Beschwerde (UWG, GesBG, Urheberrecht). Eine kurze schriftliche Freigabe per E-Mail genügt.
3. **Domain umziehen, HTTPS prüfen, Google-Unternehmensprofil + Search Console verknüpfen.**
   *Warum:* Erst mit der alten Domain übernimmt die neue Seite das Google-Ranking; das Unternehmensprofil bringt bei
   lokalen Suchen die meisten Klicks.

## Checkliste

| # | Bereich | Punkt | Status |
|---|---|---|---|
| 1 | Layout & Responsive | 320 / 375 / 768 / 1280+ px geprüft, kein horizontales Scrollen (5 Geräte emuliert) | ✅ Bestanden |
| 1 | Layout & Responsive | Texte nicht abgeschnitten, Buttons ≥ 48 px (Hauptbuttons 56 px) | ✅ Bestanden |
| 1 | Layout & Responsive | Sprunglinks landen exakt (auch von Unterseiten und alten Wix-Adressen), Galerie verschiebt nichts | ✅ Bestanden |
| 2 | Design-System | Kundenmarke umgesetzt: Weiss, Praxis-Blau, Seidenwellen; Schrift Jost (wie Visitenkarte). ADEMI-Farben gelten nur für ADEMI-Eigenmaterial | ✅ Bestanden |
| 2 | Design-System | Einheitliche Abstände/Typo über Design-Tokens in `main.css`; Leistungsseiten erben Kopf- und Fusszeile automatisch von der Startseite | ✅ Bestanden |
| 3 | Performance | Bilder als AVIF + WebP in passenden Grössen, Lazy-Loading, keine Fremd-Skripte | ✅ Bestanden |
| 3 | Performance | Lighthouse PC 100 · Handy 96 (Startseite), 99 (Leistungsseiten), 100 (Rechtliches) | ✅ Bestanden |
| 4 | SEO | Jede Seite: eigener Title, Meta-Description, genau 1 H1 (mit Ort), sinnvolle H2/H3, Canonical | ✅ Bestanden |
| 4 | SEO | Alt-Texte, sitemap.xml (7 Adressen), robots.txt, Open Graph, Schema.org (Physiotherapy, Service, FAQ, Breadcrumb) | ✅ Bestanden |
| 4 | SEO | Eigene Seiten für Neurorehabilitation, Dry Needling, Stosswellentherapie, Massage – intern verlinkt | ✅ Bestanden |
| 4 | SEO | 301-Weiterleitungen aller Adressen aus der alten Wix-Sitemap | ✅ Bestanden |
| 4 | SEO | Google-Unternehmensprofil verknüpft (`sameAs`) | ⏳ Offen – *warum:* Google ordnet Website und Profil sicherer einander zu |
| 5 | Barrierefreiheit | Kontrast ≥ 4.5:1, sichtbarer Fokus, Formular-Labels, Alt-Texte | ✅ Bestanden |
| 5 | Barrierefreiheit | axe-core WCAG 2.1 AA: 0 Verstösse auf 9 Seiten; Tastatur, „Bewegung reduzieren", ohne JS | ✅ Bestanden |
| 6 | Formulare & Recht | Kontaktformular lokal getestet inkl. Spam-Schutz (Honeypot, Zeitsperre) und Vorauswahl des Anliegens | ✅ Bestanden |
| 6 | Formulare & Recht | Formular live auf Netlify getestet (E-Mail kommt bei Hasan an) | ⏳ Offen – *warum:* Netlify verarbeitet das Formular erst nach dem Einschalten; lokal lässt sich das nicht prüfen |
| 6 | Formulare & Recht | Datenschutzerklärung, Impressum (mit UID), kein Cookie-Banner nötig | ✅ Bestanden |
| 6 | Formulare & Recht | Medizinische Texte sachlich, ohne Heilversprechen, mit Hinweis „ersetzt keine Abklärung" | ✅ Bestanden |
| 6 | Formulare & Recht | Inhalte/Titel/Bildrechte vom Kunden bestätigt | ⏳ Offen – *warum:* Nur Hasan kann Fachinhalte, Zertifikate und Bildrechte verbindlich bestätigen |
| 6 | Formulare & Recht | Vertrag zur Auftragsbearbeitung Praxis ↔ ADEMI DIGITAL (falls die Seite in deinem Netlify-Konto läuft) | ⏳ Offen – *warum:* Wer das Konto verwaltet, kann Patientenanfragen lesen; das DSG verlangt dafür eine Vereinbarung |
| 7 | Deployment | Netlify-Konfiguration, `_headers`, `_redirects`, 404, Favicon | ✅ Bestanden |
| 7 | Deployment | Projekt auf «öffentlich», «Powered by Netlify»-Abzeichen aus | ⏳ Offen (nach Upload) – *warum:* Neue Projekte können privat starten; das Abzeichen passt nicht zu einer Kundenseite |
| 7 | Deployment | Domain/DNS, HTTPS-Zertifikat | ⏳ Offen (nach Upload) – *warum:* Geht erst, wenn die Seite auf Netlify liegt |
| 7 | Deployment | Deploy nur mit ausdrücklichem OK von Berin | ✅ (nicht deployt) |

## Automatische Prüfungen vor jedem Upload
```bash
python3 tools/build_leistungen.py   # nur nötig, wenn Texte oder Kopf-/Fusszeile geändert wurden
python3 tools/check_links.py        # muss „0 Probleme" melden
```

## Deine Aufgaben, Berin (Lernmodus)
Bitte selbst umsetzen, danach lese ich gegen:

1. **Netlify Forms einrichten** (Schritte 3–6 im README, Abschnitt 2): Formular-Erkennung einschalten, nochmals
   hochladen, Benachrichtigung an `info@physio-plaza.ch`, Hasan bestätigt, Testanfrage senden.
   → Schick mir einen Screenshot der eingegangenen Anfrage.
   *Was du dabei lernst:* Eine statische Seite hat keinen eigenen Server – Netlify „liest" das Formular beim
   Veröffentlichen aus dem HTML und nimmt die Anfragen stellvertretend entgegen.
2. **Konsole prüfen:** Auf der Live-Seite `F12` drücken → Reiter **Console**. Dort darf nichts Rotes stehen.
   Siehst du „Refused to execute inline script … Content Security Policy", ist das «Powered by Netlify»-Abzeichen
   noch an → ausschalten (README, Abschnitt 2, Schritt 2) und neu laden.
   *Was du dabei lernst:* Die Content-Security-Policy erlaubt nur Skripte aus unseren eigenen Dateien. Alles, was
   jemand von aussen einschleust – hier harmlos durch Netlify selbst –, blockiert der Browser.
3. **`sameAs` ergänzen**, sobald das Google-Unternehmensprofil live ist: In `public/index.html` im JSON-LD
   beim Block `"@type": "Physiotherapy"` die Zeile
   `"sameAs": ["https://maps.google.com/?cid=DEINE-ID"],` hinzufügen (Komma beachten!).
   → Danach `python3 tools/check_links.py` ausführen (prüft auch, ob das JSON noch gültig ist) und mit dem
   Google-Test für Rich-Suchergebnisse kontrollieren.
