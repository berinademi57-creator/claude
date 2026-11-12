/*!
 * Physiotherapie Central Plaza – 3D-Seidenwelle (WebGL)
 * Eigenentwicklung, keine externen Bibliotheken.
 * - Gleiche Mathematik wie tools/make_silk_svg.py (Fallback-Bild)
 * - pausiert, wenn nicht sichtbar oder Tab im Hintergrund
 * - respektiert "Bewegung reduzieren" (zeigt dann ein ruhiges Standbild)
 */
(function () {
  "use strict";

  var canvas = document.getElementById("hero-wave");
  if (!canvas) return;

  // Erst starten, wenn die Seite geladen ist und der Browser Leerlauf hat
  // -> Text und Bilder erscheinen sofort, die Animation kommt danach dazu.
  function whenIdle(fn) {
    var run = function () {
      if ("requestIdleCallback" in window) window.requestIdleCallback(fn, { timeout: 2500 });
      else window.setTimeout(fn, 700);
    };
    if (document.readyState === "complete") run();
    else window.addEventListener("load", run, { once: true });
  }
  whenIdle(init);

  function init() {
  var root = document.documentElement;
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

  var gl = null;
  try {
    gl = canvas.getContext("webgl", {
      alpha: true,
      antialias: true,
      premultipliedAlpha: true,
      depth: false,
      stencil: false,
      powerPreference: "low-power",
      failIfMajorPerformanceCaveat: true
    });
  } catch (e) {
    gl = null;
  }
  if (!gl) {
    root.classList.add("no-webgl");
    return;
  }

  // Ohne echte Grafikkarte (Software-Rendering) wäre die Animation ruckelig
  // und würde das Gerät belasten -> stattdessen das ruhige Wellenbild zeigen.
  var renderer = "";
  try {
    var dbg = gl.getExtension("WEBGL_debug_renderer_info");
    renderer = String(dbg ? gl.getParameter(dbg.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER));
  } catch (e) {
    renderer = "";
  }
  if (/swiftshader|llvmpipe|softpipe|software|basic render/i.test(renderer)) {
    var lose = gl.getExtension("WEBGL_lose_context");
    if (lose) lose.loseContext();
    root.classList.add("no-webgl");
    return;
  }

  // offsetY, slope, A1, f1 | A2, f2, Az, f3 | tw0, tw1, width, phase | lines, alpha
  var RIBBONS = [
    [0.70, -0.12, 0.16, 1.20, 0.06, 2.4, 0.45, 0.9, 0.3, 1.10, 0.78, 0.4, 26, 0.60],
    [-0.56, 0.32, 0.20, 1.00, 0.07, 2.1, 0.40, 0.8, -0.8, 1.30, 0.98, 2.1, 30, 0.65],
    [-0.02, 0.22, 0.24, 0.80, 0.05, 1.8, 0.35, 0.7, 1.2, 0.90, 0.32, 4.2, 12, 0.45]
  ];

  var VS = [
    "attribute vec2 aUV;",
    "uniform float uTime;",
    "uniform float uAspect;",
    "uniform float uSpan;",
    "uniform float uScroll;",
    "uniform vec2 uMouse;",
    "uniform vec4 uP0;",
    "uniform vec4 uP1;",
    "uniform vec4 uP2;",
    "varying float vV;",
    "varying float vZ;",
    "varying float vX;",
    "void main() {",
    "  float x = mix(-uSpan, uSpan, aUV.x);",
    "  float t = uTime;",
    "  float ph = uP2.w;",
    "  float y = uP0.x + uP0.y * x + uP0.z * sin(uP0.w * x + ph + t * 0.55) + uP1.x * sin(uP1.y * x - ph * 1.7 - t * 0.8);",
    "  float z = uP1.z * cos(uP1.w * x + ph * 0.6 + t * 0.4);",
    "  float th = uP2.x + uP2.y * x + 0.7 * sin(0.9 * x + ph + t * 0.35);",
    "  float w = uP2.z * (0.65 + 0.35 * sin(1.4 * x + ph * 2.1 + t * 0.3));",
    "  float o = (aUV.y - 0.5) * w;",
    "  vec3 p = vec3(x, y + o * cos(th), z + o * sin(th));",
    "  float ry = uMouse.x * 0.10;",
    "  float rx = -uMouse.y * 0.07 + uScroll * 0.22;",
    "  p = vec3(p.x * cos(ry) + p.z * sin(ry), p.y, -p.x * sin(ry) + p.z * cos(ry));",
    "  p = vec3(p.x, p.y * cos(rx) - p.z * sin(rx), p.y * sin(rx) + p.z * cos(rx));",
    "  p.y += uScroll * 0.30;",
    "  float depth = 3.0 - p.z;",
    "  gl_Position = vec4(p.x * 2.2 / uAspect, p.y * 2.2, 0.0, depth);",
    "  vV = aUV.y; vZ = p.z; vX = x / uSpan;",
    "}"
  ].join("\n");

  var FS = [
    "precision mediump float;",
    "uniform vec3 uColA;",
    "uniform vec3 uColB;",
    "uniform float uAlpha;",
    "uniform float uEdge;",
    "uniform float uFadeLeft;",
    "varying float vV;",
    "varying float vZ;",
    "varying float vX;",
    "void main() {",
    "  float edge = pow(abs(vV - 0.5) * 2.0, 3.0);",
    "  float k = clamp(vV * 0.75 + vZ * 0.35, 0.0, 1.0);",
    "  vec3 col = mix(uColA, uColB, k);",
    "  float a = uAlpha * mix(1.0, 0.35 + 0.65 * edge, uEdge) * (0.8 + 0.3 * clamp(vZ + 0.4, 0.0, 1.0));",
    "  a *= mix(uFadeLeft, 1.0, smoothstep(-0.85, 0.15, vX));",
    "  gl_FragColor = vec4(col * a, a);",
    "}"
  ].join("\n");

  function compile(type, src) {
    var s = gl.createShader(type);
    gl.shaderSource(s, src);
    gl.compileShader(s);
    if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) {
      gl.deleteShader(s);
      return null;
    }
    return s;
  }

  var vs = compile(gl.VERTEX_SHADER, VS);
  var fs = compile(gl.FRAGMENT_SHADER, FS);
  if (!vs || !fs) {
    root.classList.add("no-webgl");
    return;
  }
  var prog = gl.createProgram();
  gl.attachShader(prog, vs);
  gl.attachShader(prog, fs);
  gl.linkProgram(prog);
  if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) {
    root.classList.add("no-webgl");
    return;
  }
  gl.useProgram(prog);

  var loc = {
    aUV: gl.getAttribLocation(prog, "aUV"),
    uTime: gl.getUniformLocation(prog, "uTime"),
    uAspect: gl.getUniformLocation(prog, "uAspect"),
    uSpan: gl.getUniformLocation(prog, "uSpan"),
    uScroll: gl.getUniformLocation(prog, "uScroll"),
    uMouse: gl.getUniformLocation(prog, "uMouse"),
    uP0: gl.getUniformLocation(prog, "uP0"),
    uP1: gl.getUniformLocation(prog, "uP1"),
    uP2: gl.getUniformLocation(prog, "uP2"),
    uColA: gl.getUniformLocation(prog, "uColA"),
    uColB: gl.getUniformLocation(prog, "uColB"),
    uAlpha: gl.getUniformLocation(prog, "uAlpha"),
    uEdge: gl.getUniformLocation(prog, "uEdge"),
    uFadeLeft: gl.getUniformLocation(prog, "uFadeLeft")
  };

  var isSmall = window.matchMedia("(max-width: 760px)");
  var SEG = isSmall.matches ? 110 : 180;

  // Pro Band: Gitter aus Linien (entlang x) + Dreiecke für die zarte "Seiden-Fläche"
  var meshes = RIBBONS.map(function (r) {
    var lines = isSmall.matches ? Math.max(8, Math.round(r[12] * 0.7)) : r[12];
    var verts = new Float32Array(lines * (SEG + 1) * 2);
    var p = 0, i, j;
    for (j = 0; j < lines; j++) {
      for (i = 0; i <= SEG; i++) {
        verts[p++] = i / SEG;
        verts[p++] = j / (lines - 1);
      }
    }
    var lineIdx = new Uint16Array(lines * SEG * 2);
    p = 0;
    for (j = 0; j < lines; j++) {
      for (i = 0; i < SEG; i++) {
        var a = j * (SEG + 1) + i;
        lineIdx[p++] = a;
        lineIdx[p++] = a + 1;
      }
    }
    var triIdx = new Uint16Array((lines - 1) * SEG * 6);
    p = 0;
    for (j = 0; j < lines - 1; j++) {
      for (i = 0; i < SEG; i++) {
        var q = j * (SEG + 1) + i;
        var c = q + SEG + 1;
        triIdx[p++] = q; triIdx[p++] = q + 1; triIdx[p++] = c;
        triIdx[p++] = q + 1; triIdx[p++] = c + 1; triIdx[p++] = c;
      }
    }
    var vb = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, vb);
    gl.bufferData(gl.ARRAY_BUFFER, verts, gl.STATIC_DRAW);
    var lb = gl.createBuffer();
    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, lb);
    gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, lineIdx, gl.STATIC_DRAW);
    var tb = gl.createBuffer();
    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, tb);
    gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, triIdx, gl.STATIC_DRAW);
    return { r: r, vb: vb, lb: lb, lc: lineIdx.length, tb: tb, tc: triIdx.length };
  });

  gl.enable(gl.BLEND);
  gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA);
  gl.clearColor(0, 0, 0, 0);

  var COL_A = [0x36 / 255, 0xa9 / 255, 0xe1 / 255]; // helles Cyan-Blau
  var COL_B = [0x1f / 255, 0x5d / 255, 0xc8 / 255]; // Praxis-Blau

  var W = 1, H = 1, aspect = 1, span = 1;
  var dpr = 1;

  function resize() {
    var rect = canvas.getBoundingClientRect();
    // bewusst max. 1.25: Linien wirken weicher/kräftiger und die Grafikkarte wird geschont
    dpr = Math.min(window.devicePixelRatio || 1, 1.25);
    W = Math.max(1, Math.round(rect.width * dpr));
    H = Math.max(1, Math.round(rect.height * dpr));
    if (canvas.width !== W || canvas.height !== H) {
      canvas.width = W;
      canvas.height = H;
    }
    gl.viewport(0, 0, W, H);
    aspect = W / H;
    span = 1.4 * aspect + 0.3;
    if (!running) draw(time);
  }

  var mouse = [0, 0], mouseTarget = [0, 0];
  var scroll = 0;
  var time = 8.0;
  var last = 0;
  var running = false;
  var visible = true;
  var rafId = 0;

  function draw(t) {
    gl.clear(gl.COLOR_BUFFER_BIT);
    gl.uniform1f(loc.uTime, t);
    gl.uniform1f(loc.uAspect, aspect);
    gl.uniform1f(loc.uSpan, span);
    gl.uniform1f(loc.uScroll, scroll);
    gl.uniform2f(loc.uMouse, mouse[0], mouse[1]);
    gl.uniform3fv(loc.uColA, COL_A);
    gl.uniform3fv(loc.uColB, COL_B);
    // Auf breiten Bildschirmen steht links der Text -> Wellen dort zarter
    gl.uniform1f(loc.uFadeLeft, aspect > 1.15 ? 0.42 : 0.75);

    for (var m = 0; m < meshes.length; m++) {
      var mesh = meshes[m], r = mesh.r;
      gl.uniform4f(loc.uP0, r[0], r[1], r[2], r[3]);
      gl.uniform4f(loc.uP1, r[4], r[5], r[6], r[7]);
      gl.uniform4f(loc.uP2, r[8], r[9], r[10], r[11]);
      gl.bindBuffer(gl.ARRAY_BUFFER, mesh.vb);
      gl.enableVertexAttribArray(loc.aUV);
      gl.vertexAttribPointer(loc.aUV, 2, gl.FLOAT, false, 0, 0);

      // 1) transparente Seidenfläche
      gl.uniform1f(loc.uEdge, 0.0);
      gl.uniform1f(loc.uAlpha, 0.05 * r[13]);
      gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, mesh.tb);
      gl.drawElements(gl.TRIANGLES, mesh.tc, gl.UNSIGNED_SHORT, 0);

      // 2) feine Linien
      gl.uniform1f(loc.uEdge, 1.0);
      gl.uniform1f(loc.uAlpha, 1.0 * r[13]);
      gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, mesh.lb);
      gl.drawElements(gl.LINES, mesh.lc, gl.UNSIGNED_SHORT, 0);
    }
  }

  var samples = [];
  var degraded = false;

  function watchdog(deltaMs) {
    if (degraded || samples.length >= 45) return;
    samples.push(deltaMs);
    if (samples.length === 45) {
      var sorted = samples.slice(10).sort(function (a, b) { return a - b; });
      var median = sorted[Math.floor(sorted.length / 2)];
      if (median > 34) {
        // weniger als ~30 Bilder/Sekunde -> Gerät schonen, Standbild behalten
        degraded = true;
        stop();
      }
    }
  }

  function frame(now) {
    rafId = 0;
    if (!running) return;
    if (last) watchdog(now - last);
    if (degraded) return;
    var dt = last ? Math.min((now - last) / 1000, 0.05) : 0.016;
    last = now;
    time += dt * 0.42;
    mouse[0] += (mouseTarget[0] - mouse[0]) * 0.045;
    mouse[1] += (mouseTarget[1] - mouse[1]) * 0.045;
    draw(time);
    rafId = window.requestAnimationFrame(frame);
  }

  function start() {
    if (running || degraded || reduceMotion.matches || !visible || document.hidden) return;
    running = true;
    last = 0;
    rafId = window.requestAnimationFrame(frame);
  }

  function stop() {
    running = false;
    if (rafId) window.cancelAnimationFrame(rafId);
    rafId = 0;
  }

  // Sichtbarkeit: nur animieren, wenn der Hero im Bild ist
  if ("IntersectionObserver" in window) {
    new IntersectionObserver(function (entries) {
      visible = entries[0].isIntersecting;
      if (visible) start(); else stop();
    }, { threshold: 0 }).observe(canvas);
  }

  document.addEventListener("visibilitychange", function () {
    if (document.hidden) stop(); else start();
  });

  var onMotionChange = function () {
    if (reduceMotion.matches) { stop(); draw(time); } else { start(); }
  };
  if (reduceMotion.addEventListener) reduceMotion.addEventListener("change", onMotionChange);

  // Maus-Parallaxe (nur Geräte mit echter Maus)
  if (window.matchMedia("(hover: hover) and (pointer: fine)").matches) {
    window.addEventListener("pointermove", function (e) {
      mouseTarget[0] = (e.clientX / window.innerWidth) * 2 - 1;
      mouseTarget[1] = (e.clientY / window.innerHeight) * 2 - 1;
    }, { passive: true });
  }

  // Scroll-Parallaxe
  var hero = canvas.closest(".hero") || canvas.parentElement;
  window.addEventListener("scroll", function () {
    var h = hero.offsetHeight || 1;
    scroll = Math.max(0, Math.min(1, window.scrollY / h));
    if (!running) draw(time);
  }, { passive: true });

  if ("ResizeObserver" in window) {
    new ResizeObserver(resize).observe(canvas);
  } else {
    window.addEventListener("resize", resize);
  }

  canvas.addEventListener("webglcontextlost", function (e) {
    e.preventDefault();
    stop();
    root.classList.add("no-webgl");
  });

  resize();
  draw(time);
  root.classList.add("webgl-ready");
  start();
  }
})();
