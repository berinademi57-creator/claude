#!/usr/bin/env python3
"""
Erzeugt das blaue Wellen-/Seidenmuster (wie auf Visitenkarte & Praxisschild) als SVG.
Gleiche Mathematik wie die 3D-Welle in assets/js/wave.js -> sieht identisch aus,
wird als Hintergrund-Deko und als Fallback ohne WebGL genutzt.

Aufruf: python3 tools/make_silk_svg.py
"""
import math
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "public" / "assets" / "img"

# offsetY, slope, A1, f1, A2, f2, Az, f3, tw0, tw1, width, phase, lines, alpha
RIBBONS = [
    (0.70, -0.12, 0.16, 1.20, 0.06, 2.4, 0.45, 0.9, 0.3, 1.10, 0.78, 0.4, 26, 0.60),
    (-0.56, 0.32, 0.20, 1.00, 0.07, 2.1, 0.40, 0.8, -0.8, 1.30, 0.98, 2.1, 30, 0.65),
    (-0.02, 0.22, 0.24, 0.80, 0.05, 1.8, 0.35, 0.7, 1.2, 0.90, 0.32, 4.2, 12, 0.45),
]


def ribbon_point(x, v, r, t=0.0):
    oy, sl, a1, f1, a2, f2, az, f3, tw0, tw1, w, ph, *_ = r
    y = oy + sl * x + a1 * math.sin(f1 * x + ph + t * 0.55) + a2 * math.sin(f2 * x - ph * 1.7 - t * 0.8)
    z = az * math.cos(f3 * x + ph * 0.6 + t * 0.4)
    th = tw0 + tw1 * x + 0.7 * math.sin(0.9 * x + ph + t * 0.35)
    ww = w * (0.65 + 0.35 * math.sin(1.4 * x + ph * 2.1 + t * 0.3))
    o = (v - 0.5) * ww
    return x, y + o * math.cos(th), z + o * math.sin(th)


def project(p, aspect, W, H):
    x, y, z = p
    depth = 3.0 - z
    f = 2.2
    nx = x * f / aspect / depth
    ny = y * f / depth
    return (nx * 0.5 + 0.5) * W, (1 - (ny * 0.5 + 0.5)) * H, z


def build(W=1600, H=900, color_a="#36A9E1", color_b="#1F5DC8"):
    aspect = W / H
    span = 1.4 * aspect + 0.3
    paths = []
    for ri, r in enumerate(RIBBONS):
        lines = r[12]
        alpha = r[13]
        for j in range(lines):
            v = j / (lines - 1)
            pts = []
            for i in range(0, 61):
                x = -span + 2 * span * i / 60
                px, py, _ = project(ribbon_point(x, v, r), aspect, W, H)
                pts.append(f"{px:.0f} {py:.0f}")
            edge = abs(v - 0.5) * 2
            op = alpha * (0.35 + 0.65 * edge ** 3)
            col = color_b if (v > 0.55) else color_a
            paths.append(
                f'<path d="M{" L".join(pts)}" stroke="{col}" stroke-opacity="{op:.2f}"/>'
            )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice">'
        f'<g fill="none" stroke-width="1.1" stroke-linecap="round">{"".join(paths)}</g></svg>'
    )


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "silk.svg").write_text(build(), encoding="utf-8")
    (OUT / "silk-light.svg").write_text(build(color_a="#9FD6F5", color_b="#FFFFFF"), encoding="utf-8")
    print("silk.svg + silk-light.svg geschrieben")
