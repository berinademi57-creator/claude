# Website Festim Ademi

Die ganze Seite steckt in **einer Datei**: `index.html`. Bilder liegen in `bilder/`,
Logos in `bilder/logos/`.

## Veröffentlichen

Ordner (oder die ZIP) auf **https://app.netlify.com/drop** ziehen. Bei einer
bestehenden Seite: *Deploys → Drag & Drop* – dann bleibt die Adresse gleich.

---

## ⚠️ Kontaktformular – einmalig bestätigen

Beim **allerersten** Absenden über die Website kommt eine Mail von *FormSubmit*
an **fa@festimademi.com** mit einem Bestätigungslink (Betreff sinngemäss
„Activate your form"). **Diesen Link einmal anklicken.**

Danach kommt jede weitere Nachricht automatisch an. Ohne diesen einen Klick
kommt **keine** Mail an – das ist der Spamschutz des Dienstes.

> Auch im Spam-Ordner nachsehen, falls die Bestätigungsmail nicht auftaucht.

Zusätzlich wird jede Nachricht als Sicherungskopie im Netlify-Dashboard unter
**Forms** abgelegt.

Andere Empfängeradresse? In `index.html` nach `EMPFAENGER` suchen und die
Adresse ersetzen – die neue Adresse muss dann wieder einmal bestätigt werden.

---

## Bilanz und Kämpfe pflegen

In `index.html` ganz oben im `<script>` nach **`const BILANZ`** suchen:

```js
const BILANZ = { siege: 3, niederlagen: 0, unentschieden: 0, koSiege: 1, koNiederlagen: 0 };
const KAEMPFE = [
  { datum:'Juli 2026', label:'Kampf 3', gegner:'Sven Constantin', ort:'…', ergebnis:'sieg' },
  …
];
```

Nur hier ändern – die farbigen Kästen, die Liste darunter und die Kampfkarten
aktualisieren sich automatisch, in allen drei Sprachen.

> BoxRec lässt sich nicht automatisch auslesen: es gibt keine öffentliche
> Schnittstelle, automatische Zugriffe werden blockiert und laut
> Nutzungsbedingungen ist das Auslesen nicht erlaubt.

## Nächster Kampf / Countdown

Nach **`KAMPF_DATUM`** suchen:

```js
const KAMPF_DATUM = '2026-11-21T20:00:00';   // null = "Ankündigung folgt"
const KAMPF_ORT   = 'Zürich, Schweiz';
```

## Sprachen

Deutsch steht direkt im HTML. Englisch und Französisch stehen im `<script>`
unter **`TEXTE.en`** und **`TEXTE.fr`**. Neuer Text: im HTML
`data-i18n="schluessel"` setzen und den Schlüssel in beiden Listen ergänzen.

## Bilder tauschen

Datei in `bilder/` mit gleichem Namen ersetzen – fertig.
