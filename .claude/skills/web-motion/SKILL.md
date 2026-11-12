---
name: web-motion
description: Standard-Motion-Stack für JEDE Website/Landingpage/Web-UI - GSAP (+ScrollTrigger), Lenis Smooth Scroll und React Bits Komponenten. Immer laden, wenn eine Website, Landingpage, Portfolio, Shop-Seite oder ein Web-Artifact gebaut wird, zusammen mit den anderen Design-Skills (artifact-design, ademi-website-qa usw.).
---

# Web Motion Stack: GSAP + Lenis + React Bits

Wenn eine Website gebaut wird, IMMER diese drei Bibliotheken einsetzen – ergänzend zu allen anderen Design-/QA-Skills, nicht als Ersatz.

Quellen:
- GSAP: https://github.com/greensock/GSAP (seit 3.13 komplett kostenlos inkl. SplitText, ScrollSmoother, MorphSVG …)
- Lenis: https://github.com/darkroomengineering/lenis
- React Bits: https://github.com/DavidHDev/react-bits (https://reactbits.dev)

## 1. Installation

### React / Next.js / Vite
```bash
npm i gsap @gsap/react lenis
# React Bits: Komponenten per shadcn- oder jsrepo-CLI einzeln holen (Copy-in, kein npm-Paket)
npx shadcn@latest add "https://reactbits.dev/r/SplitText-TS-TW"
# oder: npx jsrepo add https://reactbits.dev/ts/tailwind/TextAnimations/SplitText
```
Varianten: `JS-CSS`, `JS-TW`, `TS-CSS`, `TS-TW` – passend zum Projekt wählen (TS + Tailwind bevorzugt).

### Plain HTML / Artifact (nur CDN)
```html
<script src="https://cdn.jsdelivr.net/npm/gsap@3.13.0/dist/gsap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.13.0/dist/ScrollTrigger.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.13.0/dist/SplitText.min.js"></script>
<script src="https://unpkg.com/lenis@1.3.4/dist/lenis.min.js"></script>
<link rel="stylesheet" href="https://unpkg.com/lenis@1.3.4/dist/lenis.css">
```
React Bits ist React-only: in Plain-HTML die Effekte (SplitText, BlurText, Magnet, ClickSpark, Aurora …) mit GSAP nachbauen.

## 2. Lenis + GSAP ScrollTrigger korrekt koppeln

Vanilla:
```js
gsap.registerPlugin(ScrollTrigger);
const lenis = new Lenis({ autoRaf: false, lerp: 0.1 });
lenis.on('scroll', ScrollTrigger.update);
gsap.ticker.add((t) => lenis.raf(t * 1000));
gsap.ticker.lagSmoothing(0);
```

React (`lenis/react`):
```tsx
'use client';
import { ReactLenis } from 'lenis/react';
import { useEffect, useRef } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
gsap.registerPlugin(ScrollTrigger);

export function SmoothScroll({ children }: { children: React.ReactNode }) {
  const lenisRef = useRef<any>(null);
  useEffect(() => {
    const update = (t: number) => lenisRef.current?.lenis?.raf(t * 1000);
    gsap.ticker.add(update);
    gsap.ticker.lagSmoothing(0);
    return () => gsap.ticker.remove(update);
  }, []);
  return <ReactLenis root options={{ autoRaf: false }} ref={lenisRef}>{children}</ReactLenis>;
}
```

Animationen in React immer mit `useGSAP` (`@gsap/react`) und `scope`, damit Cleanup automatisch läuft.

## 3. Wo was einsetzen
| Bereich | Werkzeug |
|---|---|
| Hero-Headline | React Bits `SplitText`/`BlurText` oder GSAP SplitText (Chars/Words staggern) |
| Hintergründe | React Bits `Aurora`, `Silk`, `Particles`, `Iridescence` (sparsam, max. 1 pro Seite) |
| Sections beim Scrollen | GSAP ScrollTrigger: fade/slide-up, `stagger: 0.08`, `start: 'top 80%'` |
| Pinned Storytelling / horizontale Scroll-Strecke | ScrollTrigger `pin: true`, `scrub: 1` |
| Buttons/CTAs | React Bits `Magnet`, `ClickSpark`, `StarBorder` |
| Zahlen/Stats | React Bits `CountUp` oder GSAP-Tween auf Zahl |
| Karten/Galerie | React Bits `TiltedCard`, `SpotlightCard`, `Masonry` |
| Gesamtes Scrollgefühl | Lenis (immer) |

## 4. Qualitätsregeln
- `prefers-reduced-motion`: Lenis aus (`lenis.destroy()`), GSAP mit `gsap.matchMedia()` nur Opacity-Fades.
- Nur `transform`/`opacity` animieren; keine Layout-Properties.
- Dauer 0.6–1.2s, Ease `power3.out`/`expo.out`; nichts animiert länger als nötig.
- Inhalt muss ohne JS sichtbar/lesbar bleiben (Startzustände per `gsap.from`, nicht per CSS `opacity:0`).
- Mobile: Pins/Scrub vereinfachen, Lenis `syncTouch` nicht erzwingen.
- Danach weiterhin die anderen Skills anwenden (z. B. `ademi-website-qa`, `artifact-design`, Accessibility-Review).
