# Eigene Fotos einsetzen

## Was aktuell drin ist

Die sechs Bilder in `assets/projekte/` sind **gezeichnete Motive**, keine Fotos.
Sie zeigen die Gewerke erkennbar (Raum mit Farbroller, Fassade mit Gerüst, Kelle
im Verputz, Farbdose, Fensterabzieher) und halten das Layout, bis eigene Fotos
da sind.

**Keine Bilder aus der Google-Bildersuche nehmen.** Fast alles dort ist
geschützt. Auf einer Firmenwebsite ist das ein echtes Risiko — Forderungen
liegen schnell im vierstelligen Bereich. Frei auffindbar heisst nicht frei
verwendbar.

Saubere Quellen:

1. **Eigene Fotos** — für einen Handwerksbetrieb mit Abstand am besten.
2. **Lizenzfrei** von [unsplash.com](https://unsplash.com),
   [pexels.com](https://pexels.com) oder [pixabay.com](https://pixabay.com).
   Suchbegriffe: `painter wall`, `plastering`, `house painting`, `renovation`.

---

## Austauschen

Die Dateinamen stehen fest im HTML. Gleicher Name = nichts weiter zu ändern.

| Datei | Motiv | Wird verwendet |
| --- | --- | --- |
| `01-innenanstrich.jpg` | Innenanstrich | Hintergrund oben, Karte Malerarbeiten, Galerie |
| `02-fassade.jpg` | Fassade | Galerie |
| `03-gipserarbeiten.jpg` | Verputz | Karte Gipserarbeiten, Galerie |
| `04-feinputz.jpg` | Feine Oberfläche | Galerie, Bild bei „Über uns" |
| `05-farbberatung.jpg` | Farbe, Muster | Galerie |
| `06-reinigung.jpg` | Reinigung | Karte Reinigung, Galerie |

Foto umbenennen, Datei in `assets/projekte/` überschreiben, Seite neu laden.

`01-innenanstrich.jpg` und `04-feinputz.jpg` werden gross dargestellt — dafür
die besten Aufnahmen nehmen.

**Anforderungen:** JPG, quer, mindestens 1600 × 1200 Pixel, höchstens etwa
300 KB. Verkleinern kostenlos auf [squoosh.app](https://squoosh.app) oder
[tinyjpg.com](https://tinyjpg.com).

---

## Gut fotografieren

- Tageslicht, kein Blitz.
- Vorher und nachher von derselben Stelle aus.
- Vor dem Auslösen aufräumen: Eimer, Kabel, Folie aus dem Bild.
- Quer halten. Hochkant wird beschnitten.
- Kanten parallel zum Bildrand, sonst kippt die Wand.
- Auch Details: eine saubere Kante zeigt Handwerk oft besser als ein ganzer Raum.

Wo Personen erkennbar sind oder fremde Wohnungen zu sehen sind: vorher die
Erlaubnis der Kundschaft einholen.

---

## Beschriftungen anpassen

Sobald echte Aufträge abgebildet sind, kann die Galerie konkreter werden. In
`index.html` im Abschnitt `id="arbeiten"`:

```html
<figcaption>Innenanstrich</figcaption>
```

wird zum Beispiel zu:

```html
<figcaption>Innenanstrich, 3-Zimmer-Wohnung Biel</figcaption>
```

Dann darf die Rubrik auch „Referenzen" heissen. Solange dort Platzhalter
stehen, sollte dieses Wort nicht verwendet werden — es verspricht
abgeschlossene Kundenaufträge.

Ebenfalls anpassen: der `alt`-Text jedes Bildes. Er beschreibt das Bild für
Suchmaschinen und für Menschen, die die Seite vorlesen lassen.

---

## Danach veröffentlichen

```bash
git add assets/projekte/
git commit -m "Eigene Projektfotos eingesetzt"
git push
```

Netlify baut von selbst neu. Ohne GitHub: Ordner erneut auf
[app.netlify.com/drop](https://app.netlify.com/drop) ziehen.
