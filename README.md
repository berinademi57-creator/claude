# ADEMI - Malerei, Gipserei & Reinigung Website

Professionelle statische Website für ADEMI, ein Handwerksunternehmen in Biel-Bienne, Schweiz.

Die Website zeigt Dienstleistungen, Kontaktinformationen und ein Kontaktformular.

---

## Features

- **Responsive Design** – Optimiert für Desktop, Tablet und Mobilgeräte
- **Moderne Ästhetik** – Rote und schwarze Farbschema basierend auf Logo
- **Kontaktformular** – Mit Netlify Forms integriert
- **SEO-optimiert** – Meta-Tags und strukturierte Navigation
- **Schnelle Ladezeiten** – Reine HTML/CSS, keine großen Dependencies

---

## Dateien

- `index.html` – Vollständige Website (HTML + CSS + JS)
- `netlify.toml` – Netlify-Konfiguration
- `package.json` – Projektmetadaten

---

## Lokale Entwicklung

### Server starten

```bash
npm run serve
```

Öffne dann `http://localhost:8000` im Browser.

---

## Auf Netlify deployen

### Variante 1: Via Netlify CLI (schnell)

```bash
# Netlify CLI installieren
npm install -g netlify-cli

# Einloggen
netlify login

# Deploy
netlify deploy --prod
```

### Variante 2: Via GitHub (empfohlen für Dauerhostung)

1. Push dieses Repo zu GitHub
2. Gehe auf [netlify.com](https://netlify.com)
3. Klicke „Add new site” → „Import an existing project”
4. Verbinde dein GitHub-Konto
5. Wähle das Repository
6. Deploy wird automatisch gestartet

### Variante 3: Drag & Drop auf Netlify

1. Öffne [netlify.com](https://netlify.com)
2. Ziehe den gesamten Projektordner in die Ablage
3. Fertig – Website ist live!

---

## Kontaktformular konfigurieren

Das Formular nutzt **Netlify Forms**. Nach dem Deploy sind Einträge automatisch sichtbar:

1. Melde dich bei [netlify.com](https://netlify.com) an
2. Öffne deine Website
3. Gehe zu „Forms” → neue Einträge werden hier angezeigt
4. Optional: Konfiguriere E-Mail-Benachrichtigungen

---

## Domain verbinden

Nach dem Deploy kann man eine eigene Domain verbinden (z. B. `ademi-biel.ch`):

1. Kaufe eine Domain bei einem Registrar (z. B. Infomaniak, Namecheap)
2. In Netlify gehe zu „Domain settings”
3. Verbinde die Domain
4. Aktualisiere die DNS-Einträge beim Registrar (Netlify zeigt die Anleitung)

---

## Änderungen machen

Bearbeite `index.html` direkt:
- **Texte** – Suche nach dem Text und ändere ihn
- **Farben** – Ändere die CSS-Variablen oben in der `<style>`-Section
- **Inhalte** – Erweitere/kürze Abschnitte nach Bedarf

Nach Änderungen speichern und neu deployen:
```bash
git add .
git commit -m “Update content”
git push origin claude/ademi-malerei-gipserei-site-ugzd42
```

---

## Support

Für Fragen zu Netlify: [netlify.com/docs](https://netlify.com/docs)

