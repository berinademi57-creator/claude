# Website: Festim Ademi – Profi-Boxer 🥊

Professionelle One-Page-Website im dunklen Design (Schwarz / Anthrazit / Gold).
Alles in **einer Datei** (`index.html`) – keine Installation nötig.

## 🚀 Auf Netlify veröffentlichen (2 Minuten)

1. Gehe auf **https://app.netlify.com/drop**
2. Ziehe den kompletten Ordner **`website/`** per Drag & Drop in das Fenster
3. Fertig – du bekommst sofort eine Live-URL (z.B. `festim-ademi.netlify.app`)

> Alternativ: Netlify mit diesem GitHub-Repo verbinden und als
> "Publish directory" den Ordner `website` angeben (siehe `netlify.toml`).

## 📸 Bilder von Instagram einfügen

Die Seite ist so gebaut, dass sie **auch ohne Bilder** gut aussieht
(elegante Platzhalter). Instagram erlaubt kein automatisches Herunterladen,
deshalb so:

1. Fotos vom eigenen Profil [@ademi_festim](https://www.instagram.com/ademi_festim/)
   herunterladen (eigene Beiträge: **„…" → Herunterladen** in der App)
2. In den Ordner `website/bilder/` legen
3. Genau so benennen:

| Datei | Verwendung |
|---|---|
| `bilder/hero.jpg` | Großes Hintergrundbild oben (Kampf-/Posingfoto, quer) |
| `bilder/portrait.jpg` | Porträt im Bereich „Über mich" (hochkant) |
| `bilder/foto-1.jpg` … `foto-6.jpg` | Galerie (am besten quadratisch) |

## ✏️ Inhalte anpassen (in `index.html`)

- **Kampfrekord**: Suche nach `REKORD ANPASSEN` – die Zahlen (Siege, K.o.,
  Niederlagen, Jahre) sind **Beispielwerte** und müssen mit den echten Daten
  (z.B. von [BoxRec](https://boxrec.com/en/box-pro/1373025)) ersetzt werden.
- **Steckbrief**: Gewichtsklasse und Auslage im Bereich „Über mich" eintragen.
- **Kämpfe**: Suche nach `KÄMPFE ANPASSEN` – Kampfblöcke kopieren/ändern.
- **E-Mail**: Suche nach `E-MAIL ANPASSEN` und die echte Adresse eintragen.

## 📬 Kontaktformular

Das Formular nutzt **Netlify Forms** und funktioniert automatisch nach dem
Deploy auf Netlify. Eingehende Nachrichten findest du im Netlify-Dashboard
unter **Forms** (dort auch E-Mail-Benachrichtigung aktivierbar).
