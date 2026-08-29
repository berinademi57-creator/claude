# ADEMI Website - Anleitung

Professionelle Website für ADEMI Malerei, Gipserei & Reinigung

---

## 📁 Projektstruktur

```
ademi-website/
├── index.html          ✅ Komplette Website (HTML + CSS)
├── netlify.toml        ✅ Netlify-Konfiguration
├── package.json        ✅ Projektmetadaten
├── README.md           ✅ Englische Dokumentation
├── ANLEITUNG.md        📄 Diese Datei
└── .gitignore          ✅ Git-Ignore Datei
```

---

## 🚀 Lokal testen

### 1. Lokal im Browser öffnen
Doppelklick auf `index.html` → öffnet im Standard-Browser

### 2. Mit lokalem Server (optional)
```bash
# Mit Python 3
python -m http.server 8000

# Mit Node.js (http-server installieren)
npm install -g http-server
http-server . -p 8000
```

Dann öffne: `http://localhost:8000`

---

## 🌐 Auf Netlify deployen

### Option A: Netlify CLI (schnell)

```bash
# 1. Netlify CLI installieren
npm install -g netlify-cli

# 2. Bei Netlify anmelden
netlify login

# 3. Website deployen
netlify deploy --prod
```

**Fertig!** URL wird angezeigt.

### Option B: GitHub Integration (empfohlen)

1. **Repository auf GitHub pushen**
   ```bash
   git add .
   git commit -m "ADEMI website ready for deployment"
   git push origin claude/ademi-malerei-gipserei-site-ugzd42
   ```

2. **Auf [netlify.com](https://netlify.com) anmelden**

3. **„New site from Git"** klicken

4. **GitHub verbinden** und Repository wählen

5. **Deploy-Settings:**
   - Build command: (leer lassen)
   - Publish directory: `.`
   - Klicke „Deploy site"

6. **Automatisches Deployment:** Jeder Push zu GitHub → automatisches Update auf Netlify

### Option C: Drag & Drop (einfach)

1. Öffne [netlify.com](https://netlify.com)
2. Ziehe den Ordner in die Ablage
3. **Fertig!**

---

## ✏️ Website bearbeiten

### Texte ändern
Öffne `index.html` und suche nach dem Text, den du ändern möchtest.

**Beispiele:**
- Unternehmensinformationen: Suche nach „Ali Ademi"
- Telefon: Suche nach „076 399 17 13"
- Service-Beschreibungen: Suche nach den Sektion-Titeln

### Farben anpassen
Oben in `index.html`, im `<style>`-Bereich, findest du die CSS-Variablen:

```css
:root {
    --primary-red: #d4363d;      /* Hauptrot - hier ändern */
    --primary-black: #1a1a1a;    /* Hauptschwarz */
    --primary-white: #ffffff;    /* Weiß */
}
```

### Fotos hinzufügen

In der **Gallery-Sektion** sind SVG-Placeholder. Diese ersetzen mit echten Bildern:

```html
<!-- ALT (aktuell) -->
<img src="data:image/svg+xml,..." alt="Innenmaler">

<!-- NEU (mit Foto) -->
<img src="fotos/malerei-1.jpg" alt="Innenmaler">
```

Dann `fotos/` Ordner erstellen und JPG-Dateien hochladen.

### Öffnungszeiten ändern
Suche nach „Öffnungszeiten" und update die Zeiten.

---

## 📞 Kontaktformular

Das Formular nutzt **Netlify Forms** – völlig automatisch!

**Nach dem Deploy:**
1. Melde dich bei [netlify.com](https://netlify.com) an
2. Öffne deine Website
3. Gehe zu „Forms" → Einträge werden hier angezeigt
4. Optional: Notifications → E-Mail-Benachrichtigungen einrichten

---

## 🌍 Eigene Domain verbinden

Nach dem Deploy kannst du eine **eigene Domain** verbinden:

1. **Domain kaufen** bei Registrar (z.B. Infomaniak, Namecheap, GoDaddy)
2. **In Netlify:** Domain settings → Connect domain
3. **DNS-Records updaten** (Netlify zeigt die Anleitung)
4. **Warten** (24-48 Std.)

---

## 📱 Mobile optimiert?

✅ **JA!** Die Website ist vollständig responsive:
- Desktop (1200px+)
- Tablet (768px - 1200px)
- Handy (320px - 768px)

Teste mit DevTools: F12 → Toggle device toolbar

---

## 🔐 Sicherheit

- ✅ Keine sensieven Daten in Git
- ✅ .env ist in .gitignore
- ✅ Kontaktformular verschlüsselt über Netlify
- ✅ Keine Logging von Personendaten

---

## 🐛 Häufige Probleme

### "Kontaktformular funktioniert nicht"
→ Muss auf Netlify gehostet sein (nicht lokal)  
→ Nach Deploy 24 Std. warten

### "Seite lädt nicht"
→ Browser-Cache leeren (Strg+Shift+Entf)  
→ oder Incognito-Fenster testen

### "Bilder werden nicht geladen"
→ Bildpfade prüfen  
→ Nur JPG, PNG, WebP verwenden

---

## 💡 Tipps

- **Backup:** Git-Commits machen vor großen Änderungen
- **A/B-Tests:** Netlify Split Testing für Varianten
- **Analytics:** Google Analytics hinzufügen (optional)
- **SEO:** Meta-Tags sind bereits optimiert

---

## 📞 Support

- **Netlify Docs:** https://docs.netlify.com
- **HTML/CSS Hilfe:** https://developer.mozilla.org
- **Kontakt:** ademi.maler.gipser@gmail.com

---

**Viel Erfolg mit deiner Website!** 🚀
