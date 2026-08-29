# ADEMI – Website

Website für ADEMI, Maler-, Gipser- und Reinigungsbetrieb in Biel-Bienne.
Statische Seite ohne Framework und ohne Build-Schritt: HTML und CSS in einer
Datei, dazu ein Ordner mit Bildern.

```
index.html              die komplette Seite (Struktur, Gestaltung, Formular)
netlify.toml            Netlify-Konfiguration
assets/
  logo.png              Logo freigestellt, transparenter Hintergrund
  logo-weiss.png        gleiche Marke für dunklen Untergrund (Footer)
  projekte/             die sechs Bilder der Oberflächen-Galerie
FOTOS.md                wie eigene Fotos eingesetzt werden
```

---

## Lokal ansehen

`index.html` doppelklicken. Für ein Verhalten wie im Netz:

```bash
npx http-server . -p 8000
```

Dann `http://localhost:8000` öffnen.

---

## Veröffentlichen (Netlify)

Netlify hostet die Seite kostenlos, inklusive HTTPS.

**Variante 1 – Ordner hochladen.** Auf [app.netlify.com/drop](https://app.netlify.com/drop)
den Projektordner ins Browserfenster ziehen. Die Seite ist sofort erreichbar.

**Variante 2 – mit GitHub verbinden** (empfohlen, weil jede Änderung automatisch
live geht). In Netlify „Add new site" → „Import an existing project" → dieses
Repository wählen. Einstellungen:

| Feld | Wert |
| --- | --- |
| Build command | leer lassen |
| Publish directory | `.` |

**Variante 3 – Kommandozeile.**

```bash
npm install -g netlify-cli
netlify login
netlify deploy --prod
```

---

## Vor dem Live-Gang zu erledigen

Diese Punkte müssen stimmen, bevor die Seite öffentlich ist:

1. **Eigene Fotos einsetzen.** Die sechs Bilder in `assets/projekte/` sind
   erzeugte Materialaufnahmen, keine Fotos echter Aufträge. Siehe `FOTOS.md`.
2. **Angaben prüfen.** Telefon, E-Mail, Adresse und Erreichbarkeit stehen im
   Abschnitt „Kontakt" sowie in der Kopf- und Fusszeile.
3. **Einsatzgebiet prüfen.** Aktuell genannt: Biel-Bienne, Nidau, Brügg, Lyss,
   Region Seeland. Anpassen, falls das nicht passt.
4. **Sprachen prüfen.** Im Abschnitt „Über uns" stehen Deutsch, Albanisch und
   Französisch.
5. **`canonical`-Adresse setzen.** In `index.html` ganz oben steht
   `https://ademi-maler-gipser.ch/` als Platzhalter. Auf die echte Adresse
   ändern, sobald die Domain feststeht.
6. **Impressum ergänzen.** Für einen Schweizer Geschäftsauftritt gehört ein
   Impressum mit Firmenname, Adresse und Kontakt dazu. Bei Bedarf eine
   `impressum.html` anlegen und in der Fusszeile verlinken.

---

## Kontaktformular

Das Formular läuft über Netlify Forms. Es funktioniert erst, wenn die Seite bei
Netlify liegt — lokal geöffnet passiert beim Absenden nichts.

Nach dem Veröffentlichen: In Netlify die Seite öffnen → „Forms" → dort stehen
die Anfragen. Unter „Forms" → „Form notifications" eine E-Mail-Benachrichtigung
an `ademi.maler.gipser@gmail.com` einrichten, sonst muss man selbst nachschauen.

Gegen Spam ist ein verstecktes Feld eingebaut (`netlify-honeypot="firma"`), das
Menschen nie ausfüllen, automatische Skripte aber schon. Solche Einsendungen
verwirft Netlify.

---

## Eigene Domain

1. Domain kaufen, zum Beispiel bei Infomaniak oder Hostpoint (beide Schweiz).
2. In Netlify: „Domain settings" → „Add a domain".
3. Die DNS-Einträge beim Anbieter so setzen, wie Netlify sie anzeigt.
4. Bis zu 48 Stunden warten. Das HTTPS-Zertifikat stellt Netlify selbst aus.

---

## Texte ändern

Alles steht in `index.html`. Die Farben stehen gesammelt oben im
`<style>`-Block:

```css
--brand:#d6392c;   /* Rot aus dem Logo */
--ink:#161616;     /* Schwarz aus dem Logo */
```

Wird eine Farbe dort geändert, zieht die ganze Seite mit.

---

## Getestet

Geprüft mit Chromium bei 1440 px und 390 px Breite: alle Bilder laden, kein
seitliches Scrollen, das Mobilmenü öffnet und schliesst, Schrift auf farbigen
Flächen erfüllt die Kontrastvorgaben (WCAG AA).
