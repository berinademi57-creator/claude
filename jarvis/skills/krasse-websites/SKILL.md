---
name: krasse-websites
description: >-
  Baut in Minuten auffällige, schnelle Websites und Landingpages (eine Datei, ohne Build),
  speichert sie mit website_speichern, zeigt sie live im HUD und veröffentlicht sie nach
  Bestätigung mit website_veroeffentlichen. Nutzen bei: Website, Landingpage, Onepager,
  Homepage, Shop-Seite, Portfolio, „bau mir eine Seite“.
---

# Krasse Websites

Ziel: Seiten, bei denen man stehen bleibt. Kino-Look, flüssige Animationen und trotzdem
schnell, mobil perfekt und verständlich. Kombiniere diesen Ablauf mit den installierten
Design-Skills `frontend-design`, `impeccable`, `design-taste-frontend` und
`web-design-guidelines`. Die liefern Geschmack und Qualitätsregeln, dieser Skill den Ablauf.

## Ablauf (immer so)
1. **Brief in einem Satz klären**: Wer, was, für wen, welche eine Aktion soll der Besucher
   machen? Fehlt etwas Wichtiges (Firmenname, Angebot, Kontakt), frag einmal kurz nach.
   Sonst triff sinnvolle Annahmen und sag welche.
2. **Konzept in 3 Zeilen** an den Nutzer: Stil, Farben, Wow-Moment. Nicht auf Antwort warten,
   ausser der Nutzer will mitreden.
3. **Bauen**: komplette `index.html` in **einem** Aufruf von `website_speichern`
   (spart Credits). CSS und JS inline.
4. Sag: „Steht, siehst du live im HUD.“ Frag nach Änderungen.
5. **Änderungen**: nur die betroffenen Abschnitte ändern, Datei neu speichern.
6. **Veröffentlichen** erst nach klarem „ja“ → `website_veroeffentlichen`, Live-Link nennen.
   Fehlt `NETLIFY_AUTH_TOKEN`, sag genau, wie man ihn bekommt (`zugriffe_status`).

## Technik
- Eine Datei, kein Build. Vanilla JS. Bibliotheken nur wenn nötig, von
  `https://cdnjs.cloudflare.com` mit fester Version (z.B. GSAP 3.12.5, three.js r128).
- Mobile first: 360 px bis 1920 px, keine horizontale Scrollbar, Touch-Ziele ≥ 44 px.
- Performance: Canvas-Effekte mit `requestAnimationFrame`, Partikelzahl auf dem Handy halbieren,
  `prefers-reduced-motion` respektieren, Bilder `loading="lazy"`.
- Barrierefreiheit: echte Überschriften-Hierarchie, Kontrast ≥ 4.5:1, `alt`-Texte, Fokus sichtbar.
- SEO-Basis: `<title>`, Meta-Description, Open-Graph-Tags, `lang="de"`.

## Stil-Rezepte (passend wählen, nicht alles auf einmal)
- **Neon-Noir** (Tech, Fitness, Drinks, Gaming): fast schwarzer Hintergrund, eine
  Akzentfarbe mit Glow, riesige fette Headline (clamp 48–140 px, enges Letter-Spacing),
  Partikel- oder Raster-Canvas im Hero, Zahlen-Counter, Marquee-Band.
- **Clean Premium** (Handwerk, Praxis, Beratung, KMU): viel Weissraum, ruhige Typo,
  eine Akzentfarbe, echte Fotos oder Platzhalter-Flächen, Vertrauen (Bewertungen, Ablauf in
  3 Schritten, Preise „ab …“).
- **Editorial** (Mode, Kunst, Food): grosse Serif-Headlines, asymmetrisches Raster,
  langsame Bild-Reveals.

## Wow-Momente (genau einen oder zwei pro Seite)
Partikel-Hero, der auf die Maus reagiert · Scroll-Reveal von Headlines Wort für Wort ·
Glücksrad oder Quiz als Lead-Magnet · Live-Counter · Vorher/Nachher-Slider ·
3D-Karten mit Tilt · Countdown für Angebot.

## Texte
Deutsch, Du-Form (ausser der Kunde will Sie), kurz und konkret. Headline = Nutzen, nicht
Firmenname. Ein klarer Call-to-Action, mehrfach wiederholt. Keine erfundenen Zahlen,
Bewertungen oder Kundennamen: Platzhalter klar als Platzhalter markieren.

## Bilder
Hat der Nutzer Higgsfield verbunden und will echte Bilder: dort erzeugen (kostet Credits,
vorher fragen). Sonst CSS/SVG-Grafik, Verläufe, Muster oder neutrale Platzhalterflächen.

## Vor dem Speichern prüfen
- [ ] Sieht bei 375 px Breite gut aus?
- [ ] Ein CTA klar sichtbar über dem Falz?
- [ ] Animationen ruckelfrei und nicht ablenkend?
- [ ] Keine Platzhalter vergessen, Kontaktdaten korrekt?
