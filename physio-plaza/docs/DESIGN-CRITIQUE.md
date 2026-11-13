# Design-Kritik: Website Physiotherapie Central Plaza

Stand: November 2026 · Grundlage: Screenshots PC (1440 px), Tablet (768 px), Handy (320–412 px)
Ziel der Seite: neue Patientinnen und Patienten gewinnen – sehr professionell, einfach für ältere
Menschen, handyfreundlich, mit Wow-Effekt am PC. Markenstil: Weiss, Praxis-Blau, Seidenwellen.

## Gesamteindruck
Die Seite wirkt ruhig, hochwertig und klar zur Marke gehörig (Wellen, Blau, Logo). Stärkster Moment ist
der Einstieg mit Porträt und 3D-Welle. Die grösste Chance lag beim **Weg zum Termin** und bei der
**Länge auf dem Handy** – beides ist jetzt verbessert.

## Bedienbarkeit

| Befund | Schwere | Empfehlung | Status |
|---|---|---|---|
| „Termin anfragen" sprang zum Anfang des Kontaktbereichs – auf dem Handy musste man danach noch an 4 Info-Karten vorbeiscrollen, bis das Formular kam | 🔴 Kritisch | Alle Termin-Buttons springen direkt ins Formular (`#termin`) | ✅ umgesetzt |
| Leistungen auf dem Handy sehr lang (11 Karten mit grossem Bild: 6580 px) | 🟡 Mittel | Kompakte Karten: kleines Bild links, Titel rechts, Text darunter – gleiche Schriftgrösse. Gemessen auf iPhone 13: 3800 px, also 42 % bzw. rund 4 Bildschirmhöhen weniger Scrollen | ✅ umgesetzt |
| Telefon nur Di–Fr 13–14 Uhr erreichbar, aber „Anrufen" ist immer sichtbar | 🟡 Mittel | Live-Hinweis „Jetzt telefonisch erreichbar" während der Telefonzeit; sonst Formular als Hauptweg | ✅ umgesetzt |
| Öffnungszeiten-Tabelle brach auf dem Handy mitten in der Uhrzeit um | 🟢 Klein | Uhrzeit bleibt auf einer Zeile | ✅ umgesetzt |
| Leistungen nur als kurze Karten – wer mehr wissen wollte, fand nichts | 🟡 Mittel | Eigene Seiten für die vier Schwerpunkte, mit «Auf einen Blick»-Karte und direktem Weg ins Formular (Anliegen ist dort schon ausgewählt) | ✅ umgesetzt |
| Anfahrt nur fürs Auto beschrieben; ältere Menschen kommen oft mit dem Bus | 🟡 Mittel | Haltestelle, Linien, Bahnhof und Gehzeiten nennen; zweiter Knopf «ÖV-Verbindung» | ✅ umgesetzt |
| Von einer anderen Seite ins Formular gesprungen, landete man am PC rund 200 px zu tief | 🟡 Mittel | Die 3D-Galerie reserviert ihre Höhe sofort, nichts rutscht mehr nach | ✅ umgesetzt |
| Parkplan enthält Datumsangaben, die nur im Bild standen | 🟢 Klein | Bildunterschrift nennt Feldnummern und Daten als Text (auch für Vorleseprogramme) | ✅ umgesetzt |
| Keine Online-Terminbuchung | 🟡 Mittel | Später z. B. OneDoc anbinden (siehe SEO-Audit) | ⏳ offen |

## Visuelle Hierarchie
- **Was zuerst auffällt:** die Überschrift „Physiotherapie, die bewegt." und das Porträt – richtig so,
  denn Vertrauen in die Person ist bei einer Einzelpraxis das wichtigste Argument.
- **Lesefluss:** Slogan → Ort → zwei klare Knöpfe → vier Vertrauenspunkte. Danach: Wer sind wir →
  Leistungen → Ablauf → Person → Räume → Kontakt. Das entspricht den Fragen, die neue Patienten stellen.
- **Betonung:** Es gibt genau eine Hauptaktion (blauer Knopf „Termin anfragen"). Anrufen ist bewusst
  die zweite Wahl (weiss), weil das Telefon nur eine Stunde pro Tag besetzt ist.

## Konsistenz

| Element | Problem | Lösung | Status |
|---|---|---|---|
| Kleine Abschnitts-Labels | An 4 Stellen grau/zu gross statt blau (CSS-Rangfolge: allgemeine Regel überschrieb die Klasse) | Regeln präzisiert | ✅ behoben |
| Label auf Leistungskarten | grau und grösser als geplant | blau, 14,4 px | ✅ behoben |
| Status „Jetzt geöffnet" | dunkler Text statt Grün | Grün auf hellgrün (Kontrast 4.8:1) | ✅ behoben |
| 404-Seite | grosse „404" wurde nur 18 px klein dargestellt | grosse Verlaufszahl | ✅ behoben |
| Impressum/Datenschutz | Seitenkopf und Text hatten unterschiedliche linke Kanten | gemeinsame Lesespalte | ✅ behoben |
| Formular-Einleitung | ohne Abstand zur Überschrift | 8 px Abstand, gedämpfte Farbe | ✅ behoben |

> **Lernpunkt (CSS-Spezifität):** Eine Regel wie `.karte p { … }` ist „stärker" als `.label { … }`,
> weil sie aus Klasse **und** Element besteht. Steht ein `<p class="label">` in der Karte, gewinnt
> die allgemeine Regel. Lösung: die spezielle Regel genauso stark machen (`.karte .label`) oder die
> allgemeine einschränken (`.karte p:not(.label)`).

## Barrierefreiheit
- **Kontrast:** alle Texte ≥ 4.5:1 (gemessen), grosse Überschriften ≥ 3:1.
- **Tippflächen:** Hauptknöpfe 56 px, Menü 52 px, Links in Listen ≥ 44 px.
- **Lesbarkeit:** Fliesstext 17–18 px, Zeilenabstand 1.65; keine Texte in Bildern.
- **Bewegung:** Wer „Bewegung reduzieren" eingestellt hat, sieht eine ruhige Seite ohne 3D.
- **Tastatur/Screenreader:** axe-core 0 Verstösse; Menü und Bild-Grossansicht mit Fokus-Führung.

## Was gut funktioniert
- Markenstil konsequent: Wellen im Kopf, in Karten, im Footer und sogar auf der Fehlerseite.
- Der 3D-Effekt bleibt Dekoration – Inhalte sind auch ohne JavaScript und ohne Grafikkarte lesbar.
- Handy: feste Leiste „Anrufen / Termin anfragen", grosse Formularfelder, kein seitliches Wischen.
- Ehrliche, sachliche Sprache ohne Heilversprechen.

## Empfehlungen nach Priorität
1. **Echte Fotos der Behandlung** (Hasan bei der Arbeit, mit Einwilligung der abgebildeten Person):
   Das stärkste Vertrauenssignal, das der Seite noch fehlt. Ersetzt Herstellerfotos der Geräte.
2. **Online-Terminbuchung** anbinden – senkt die Hürde ausserhalb der Telefonzeit weiter.
3. **Google-Bewertungen** sammeln und im Unternehmensprofil pflegen (auf der Website selbst keine
   Patientenstimmen: bei Gesundheitswerbung heikel).
