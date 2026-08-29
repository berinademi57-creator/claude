# 📸 Fotos hinzufügen - Anleitung

Wie du deine eigenen professionellen Fotos in die Website integrierst.

---

## 📁 Schritt 1: Ordner erstellen

Erstelle einen Ordner `fotos` im Projekt:

```
ademi-website/
├── index.html
├── fotos/              ← NEUER ORDNER
│   ├── malerei-1.jpg
│   ├── gipser-1.jpg
│   └── reinigung-1.jpg
└── ...
```

---

## 🖼️ Schritt 2: Fotos vorbereiten

**Bildgröße:** Optimal 800x600px oder 1200x900px  
**Format:** JPG (beste Größe) oder PNG  
**Qualität:** Mindestens 300dpi für Druck  
**Größe:** Max 2MB pro Bild (für schnelle Ladenzeiten)

### Mit kostenlosen Tools optimieren:
- **TinyJPG.com** → Komprimieren
- **Pixlr.com** → Bearbeiten
- **Canva.com** → Designer-Vorlagen

---

## 🎨 Schritt 3: Code in index.html ersetzen

In `index.html`, in der **Gallery-Sektion**, findest du:

```html
<div class="gallery-item">
    <img src="data:image/svg+xml,..." alt="Innenmaler">
    <div class="gallery-overlay">
        <h4>Innenmaler</h4>
    </div>
</div>
```

### Ersetze mit deinem Foto:

```html
<div class="gallery-item">
    <img src="fotos/malerei-1.jpg" alt="Professionelle Innenmaler-Arbeiten">
    <div class="gallery-overlay">
        <h4>Innenmaler</h4>
    </div>
</div>
```

---

## 📝 Beispiel-Galerie (alle 6 Bilder)

```html
<!-- Innenmaler -->
<div class="gallery-item">
    <img src="fotos/malerei-innen.jpg" alt="Innenmaler">
    <div class="gallery-overlay">
        <h4>Innenmaler</h4>
    </div>
</div>

<!-- Außenmalerei -->
<div class="gallery-item">
    <img src="fotos/malerei-außen.jpg" alt="Außenmalerei">
    <div class="gallery-overlay">
        <h4>Außenmalerei</h4>
    </div>
</div>

<!-- Gipsarbeiten -->
<div class="gallery-item">
    <img src="fotos/gipser-arbeiten.jpg" alt="Gipsarbeiten">
    <div class="gallery-overlay">
        <h4>Gipsarbeiten</h4>
    </div>
</div>

<!-- Feinputz -->
<div class="gallery-item">
    <img src="fotos/feinputz.jpg" alt="Feinputz">
    <div class="gallery-overlay">
        <h4>Feinputz</h4>
    </div>
</div>

<!-- Reinigung -->
<div class="gallery-item">
    <img src="fotos/reinigung.jpg" alt="Gebäudereinigung">
    <div class="gallery-overlay">
        <h4>Gebäudereinigung</h4>
    </div>
</div>

<!-- Handwerk -->
<div class="gallery-item">
    <img src="fotos/handwerk.jpg" alt="Professionelles Handwerk">
    <div class="gallery-overlay">
        <h4>Professionelles Handwerk</h4>
    </div>
</div>
```

---

## 🌟 Hero-Bild hinzufügen (optional)

Für ein professionelles Hintergrundbild in der Hero-Sektion:

**Alte Variante (Farbgradient):**
```css
.hero {
    background: linear-gradient(135deg, var(--primary-red) 0%, #b8282d 100%);
}
```

**Neue Variante (mit Foto):**
```css
.hero {
    background: url('fotos/hero.jpg') center/cover;
    background-attachment: fixed;
}

.hero::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(212, 54, 61, 0.5);
    z-index: -1;
}
```

---

## ✨ Tipps für professionelle Fotos

### Was fotografieren?
- ✅ Fertige Arbeiten (Wand nach Anstrich)
- ✅ Arbeitsbereich (mit Werkzeug)
- ✅ Vorher/Nachher Bilder
- ✅ Team bei der Arbeit
- ✅ Kundenzufriedenheit

### Fotografie-Tipps:
1. **Beleuchtung** → Tageslicht verwenden
2. **Winkel** → Mehrere Perspektiven fotografieren
3. **Sauberkeit** → Bereich vor Foto saubermachen
4. **Konsistenz** → Einheitlicher Stil (Filter, Format)

### Kostenlose Foto-Ressourcen (Fallback):
- **Unsplash.com** → Hochwertige freie Bilder
- **Pexels.com** → Kostenlose Stock-Fotos
- **Pixabay.com** → Lizenzfreie Bilder

---

## 🔍 SEO-Optimierung für Bilder

Verwende aussagekräftige `alt`-Texte:

```html
<!-- ❌ FALSCH -->
<img src="fotos/1.jpg" alt="Bild">

<!-- ✅ RICHTIG -->
<img src="fotos/malerei-innen.jpg" alt="Professionelle Innenmaler-Arbeiten in Biel">
```

**Format:** `[Was] [Wo] [von wem]`

---

## 📱 Bilder für Mobile optimieren

Verwende Responsive Images:

```html
<img 
    srcset="fotos/malerei-600w.jpg 600w, fotos/malerei-1200w.jpg 1200w" 
    sizes="(max-width: 600px) 100vw, 50vw"
    src="fotos/malerei-1200w.jpg" 
    alt="Innenmaler"
>
```

---

## ☁️ Netlify Deploy mit Fotos

Nach Änderungen:

```bash
git add fotos/
git commit -m "Add professional photos to gallery"
git push origin claude/ademi-malerei-gipserei-site-ugzd42
```

Netlify deployt automatisch! ✅

---

## 🎬 Video-Tutorial (YouTube)

Suche nach: "Website Bilder optimieren und einfügen"

---

**Brauchst du Hilfe?** → ademi.maler.gipser@gmail.com 📧
