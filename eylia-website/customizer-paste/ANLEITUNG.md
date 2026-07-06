# ELURA – Fertige Blöcke für "Anpassen" (Customizer)

Kein Code-Editor nötig! So geht's:

## Startseite (Sections 01–11)

1. Shopify-Admin → **Onlineshop → Themes** → bei deinem Theme auf **„Anpassen"**
2. Oben Seite auf **„Startseite"** stellen
3. **„Abschnitt hinzufügen"** → **„Individuelles Liquid"** (Custom Liquid) wählen
4. Datei öffnen, **alles kopieren**, ins Textfeld einfügen → **Speichern**
5. Für jede Datei 01–11 wiederholen (jedes Mal ein NEUES „Individuelles Liquid" hinzufügen)
6. Am Ende per Drag & Drop in der Reihenfolge 01 → 11 anordnen

## Produktseite (Section 12)

1. Oben im Customizer die Seite auf **irgendein Produkt** stellen (Dropdown „Startseite" → „Produkte" → ein Produkt wählen)
2. Falls dein Theme bereits eine Standard-Produktinfo-Section zeigt (Bild, Preis, Warenkorb-Button): diese Section **ausblenden oder entfernen**, damit nichts doppelt erscheint (Klick auf die Section → Augen-Symbol zum Ausblenden, oder Papierkorb zum Entfernen)
3. **„Abschnitt hinzufügen"** → **„Individuelles Liquid"** → Inhalt von `12-produktseite.liquid` einfügen → Speichern
4. Das gilt automatisch für ALLE Produkte — nicht pro Produkt wiederholen

## Was ist neu/dynamisch (überlebt Katalog-Änderungen)

- **Bestseller (04)**: zieht automatisch alle Produkte mit Tag „Bestseller" — bei neuen Produkten einfach den Tag setzen, die Website aktualisiert sich von selbst.
- **Kategorien (05)**: Bild & Anzahl kommen automatisch aus den Collections `armbander`, `halsketten`, `ringe`.
- **Editorial (06)**: zeigt automatisch das erste Produkt der Collection `glucksbringer`.
- **Instagram-Galerie (09)**: zieht automatisch aus der Collection `gold-momente`.
- **Produktseite (12)**: funktioniert für jedes Produkt automatisch — Bilder, Varianten, Preis, Beschreibung, „Das könnte dir gefallen".

Nur die Sections 01, 02, 03, 07, 08, 10, 11 haben feste Texte (Ankündigung, Hero, Trust-Icons, Reviews, Gold-Momente-Countdown, FAQ, Newsletter) — die kannst du direkt im eingefügten Text anpassen.

## Design-System (V3 — redaktionell statt generisch)
- Schwarz `#0d0d0d` / Papier `#f4f2ec` / Gold `#a9832f`–`#c9a24a`, Serifen-Überschriften (Georgia) + klare Sans für Fließtext
- Keine Emoji-Icons mehr — stattdessen nummerierte Abschnitte „(01)", „(02)" … und feine Trennlinien
- Laufschrift-Banner statt statischer Ankündigung, asymmetrisches Bestseller-Raster mit Hover-Quick-Add, großes Zitat bei den Kundenstimmen, Vollbild-Hintergrund bei „Gold-Momente"

## Wichtig
- Keine Lieferzeit-Angaben mehr im Text (wie gewünscht).
- Header & Footer liefert dein Theme — nicht doppelt einbauen.
