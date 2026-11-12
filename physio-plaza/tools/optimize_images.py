#!/usr/bin/env python3
"""
Bild-Optimierung für die Physio-Plaza-Website.

Was das Skript macht:
  1. Liest die Originalbilder (vom alten Wix-Auftritt) aus RAW_DIR.
  2. Dreht sie korrekt (EXIF-Orientierung) und entfernt ALLE Metadaten
     (Kamera, Datum, GPS-Standort) -> Datenschutz.
  3. Exportiert jede Datei in mehreren Breiten als AVIF + WebP,
     damit Handys kleine und PCs grosse Bilder laden (schneller = besseres Google-Ranking).

Aufruf:  python3 tools/optimize_images.py <ordner-mit-originalen>
Benötigt: Pillow >= 11 (mit AVIF-Unterstützung)
"""
import sys
from pathlib import Path
from PIL import Image, ImageOps, ImageChops

RAW_DIR = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("raw")
OUT_DIR = Path(__file__).resolve().parent.parent / "public" / "assets" / "img"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# name -> (wix-datei, typ, breiten)
#   photo  = Foto, Seitenverhältnis bleibt
#   device = Gerät auf weissem Grund, wird zugeschnitten und auf 4:3 gesetzt
IMAGES = {
    # Eigene Praxisfotos
    "praxis-rezeption":      ("f9c328_c5f09b3d71d74fca9279b6ce6cdff8a2~mv2.png", "photo", [480, 800, 1200]),
    "praxis-wartezimmer":    ("f9c328_78d686dcc22846179f164bef8d8f4de2~mv2.png", "photo", [480, 800, 1200]),
    "praxis-eingang":        ("f9c328_87846e7831e84a15886c18f752c9c994~mv2.png", "photo", [480, 800, 1200]),
    "praxis-raum-1":         ("f9c328_f34ede01b8ca4c389184d6a359c7bd8a~mv2.png", "photo", [480, 800, 1200]),
    "praxis-raum-1-wand":    ("f9c328_1d15ba9c85c84301ad4be54cb43fbf5e~mv2.png", "photo", [480, 800, 1200]),
    "praxis-raum-3":         ("f9c328_591accb9767a4dd286796dc2d812b3f9~mv2.png", "photo", [480, 800, 1200]),
    "praxis-raum-4":         ("f9c328_914f23d5d32f47d1b050763d4b51b633~mv2.png", "photo", [480, 800, 1200]),
    "praxis-traktionsliege": ("f9c328_305db96d747446d68c6fbb8e3964487b~mv2.png", "photo", [480, 800, 1200]),
    "praxis-visitenkarten":  ("f9c328_0035c4a3dd05442da07d6cc03f8acf3b~mv2.png", "photo", [480, 800, 1200]),
    # Porträt
    "hasan-zeciri":          ("f9c328_c000769b4d9d4689b412feaf652b9224~mv2.jpg", "photo", [400, 640, 960, 1280]),
    # Anfahrt / Parkplätze
    "parkplaetze":           ("f9c328_a40c0d4afc6f4051b90d3c0021e69ced~mv2.png", "photo", [588]),
    # Behandlungen
    "dry-needling":          ("f9c328_2892d0bc5cb9444c8235c748ab53d348~mv2.jpg", "photo", [480, 800]),
    "ultraschalldiagnostik": ("nsplsh_be883fa92cf740648a6a00efef442088~mv2.jpg", "photo", [480, 800]),
    # Geräte (weisser Hintergrund)
    "geraet-elektrotherapie":  ("f9c328_5eecefb1b21f48338056f6d11356c8d4~mv2.jpg", "device", [400, 800]),
    "geraet-ultraschall":      ("f9c328_07ca0a6a6ab2477f9991d17e7f1a63cc~mv2.jpg", "device", [400, 800]),
    "geraet-vakuum":           ("f9c328_4e1e36433bcd47b2b84e00cdd0604f5c~mv2.jpg", "device", [400, 800]),
    "geraet-induktion":        ("f9c328_11b345cfb93a4ee48050cfb01bf2b826~mv2.png", "device", [400, 800]),
    "geraet-stosswelle":       ("f9c328_d48b8f3a70584bd0b30a935922c00758~mv2.jpg", "device", [400, 800]),
    "geraet-laser":            ("f9c328_a8a3b8084c1842e98dba8285930ee6d1~mv2.jpg", "device-whiten", [400, 800]),
    "geraet-cpm-knie":         ("f9c328_ae8b30014c5745ea88a52de2d4be6134~mv2.jpg", "device", [400, 800]),
    "geraet-kryotherapie":     ("f9c328_8a96a87fedb54511ab4eeb9b98f38ed1~mv2.jpg", "device", [400, 800]),
}


def load(path: Path) -> Image.Image:
    im = Image.open(path)
    im = ImageOps.exif_transpose(im)  # richtige Drehung, bevor EXIF wegfällt
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
        bg.alpha_composite(im)
        im = bg
    return im.convert("RGB")


def whiten_background(im: Image.Image) -> Image.Image:
    """Grauen Studio-Hintergrund zu Weiss ziehen (nur helle, farblose Pixel)."""
    import numpy as np  # nur für diesen Schritt nötig

    a = np.asarray(im).astype(np.float32)
    lum = a.mean(axis=2)
    chroma = a.max(axis=2) - a.min(axis=2)

    def smooth(e0, e1, x):
        t = np.clip((x - e0) / (e1 - e0), 0, 1)
        return t * t * (3 - 2 * t)

    t = smooth(196, 232, lum) * (1 - smooth(10, 24, chroma))
    out = a + (255 - a) * t[..., None]
    return Image.fromarray(out.clip(0, 255).astype(np.uint8))


def to_device_canvas(im: Image.Image) -> Image.Image:
    """Weissraum wegschneiden und das Gerät zentriert auf eine 4:3-Fläche setzen."""
    bg = Image.new("RGB", im.size, (255, 255, 255))
    diff = ImageChops.difference(im, bg).convert("L").point(lambda p: 255 if p > 18 else 0)
    box = diff.getbbox() or (0, 0, im.width, im.height)
    im = im.crop(box)
    W = max(im.width / 0.84, (im.height / 0.84) * 4 / 3)
    H = W * 3 / 4
    canvas = Image.new("RGB", (round(W), round(H)), (255, 255, 255))
    canvas.paste(im, ((canvas.width - im.width) // 2, (canvas.height - im.height) // 2))
    return canvas


def save_variants(name: str, im: Image.Image, widths, allow_upscale=False):
    for w in widths:
        if not allow_upscale:
            w = min(w, im.width)
        h = round(im.height * w / im.width)
        resized = im.resize((w, h), Image.LANCZOS)
        # Neue Bilder ohne exif/icc/xmp speichern -> keine Metadaten im Output
        resized.save(OUT_DIR / f"{name}-{w}.avif", "AVIF", quality=58, speed=4)
        resized.save(OUT_DIR / f"{name}-{w}.webp", "WEBP", quality=80, method=6)
        print(f"  {name}-{w}  ({w}x{h})")


def main():
    for name, (src, kind, widths) in IMAGES.items():
        path = RAW_DIR / src
        if not path.exists():
            print(f"FEHLT: {src}")
            continue
        im = load(path)
        if kind == "device-whiten":
            im = whiten_background(im)
        if kind.startswith("device"):
            im = to_device_canvas(im)
        print(f"{name}: {im.width}x{im.height}")
        save_variants(name, im, widths, allow_upscale=kind.startswith("device"))


if __name__ == "__main__":
    main()
