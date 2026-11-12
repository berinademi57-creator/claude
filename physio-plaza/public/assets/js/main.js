/*!
 * Physiotherapie Central Plaza – Interaktionen
 * Ohne externe Bibliotheken. Kein innerHTML (Trusted-Types-kompatibel).
 */
(function () {
  "use strict";

  var doc = document;
  var root = doc.documentElement;
  var body = doc.body;
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  var finePointer = window.matchMedia("(hover: hover) and (pointer: fine)");

  function $(sel, ctx) { return (ctx || doc).querySelector(sel); }
  function $$(sel, ctx) { return Array.prototype.slice.call((ctx || doc).querySelectorAll(sel)); }
  function clamp(v, a, b) { return Math.max(a, Math.min(b, v)); }

  // Nicht dringende Aufgaben erst ausführen, wenn der Browser Leerlauf hat
  function whenIdle(fn) {
    if ("requestIdleCallback" in window) window.requestIdleCallback(fn, { timeout: 2000 });
    else window.setTimeout(fn, 300);
  }

  function rafThrottle(fn) {
    var queued = false;
    return function () {
      if (queued) return;
      queued = true;
      window.requestAnimationFrame(function () { queued = false; fn(); });
    };
  }

  /* ------------------------------------------------------------------
   * 1. Kopfzeile & mobile Aktionsleiste
   * ------------------------------------------------------------------ */
  var header = $("#site-header");
  var actionBar = $("#action-bar");

  var onScroll = rafThrottle(function () {
    var y = window.scrollY || window.pageYOffset;
    if (header) header.classList.toggle("is-scrolled", y > 16);
    if (actionBar) actionBar.classList.toggle("is-visible", y > window.innerHeight * 0.55);
    updateTimeline();
  });
  window.addEventListener("scroll", onScroll, { passive: true });

  /* ------------------------------------------------------------------
   * 2. Mobile-Menü (mit Fokus-Falle via "inert")
   * ------------------------------------------------------------------ */
  var toggle = $(".menu-toggle");
  var menu = $("#mobile-menu");
  var main = $("#main");
  var footer = $(".site-footer");

  function setMenu(open, returnFocus) {
    if (!toggle || !menu) return;
    menu.classList.toggle("is-open", open);
    menu.inert = !open;
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
    toggle.setAttribute("aria-label", open ? "Menü schliessen" : "Menü öffnen");
    body.classList.toggle("menu-open", open);
    [main, footer, actionBar].forEach(function (el) { if (el) el.inert = open; });
    if (open) {
      var first = $("a", menu);
      if (first) window.setTimeout(function () { first.focus(); }, 60);
    } else if (returnFocus) {
      toggle.focus();
    }
  }

  if (toggle && menu) {
    toggle.addEventListener("click", function () {
      setMenu(toggle.getAttribute("aria-expanded") !== "true", true);
    });
    $$("a", menu).forEach(function (a) {
      a.addEventListener("click", function () { setMenu(false, false); });
    });
    doc.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && menu.classList.contains("is-open")) setMenu(false, true);
    });
    window.matchMedia("(min-width: 1025px)").addEventListener("change", function (e) {
      if (e.matches) setMenu(false, false);
    });
  }

  /* ------------------------------------------------------------------
   * 3. Aktiver Menüpunkt
   * ------------------------------------------------------------------ */
  var navLinks = $$(".nav__link");
  if ("IntersectionObserver" in window && navLinks.length) {
    var byId = {};
    navLinks.forEach(function (l) { byId[l.getAttribute("href").slice(1)] = l; });
    var sectionObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        navLinks.forEach(function (l) { l.removeAttribute("aria-current"); });
        var link = byId[entry.target.id];
        if (link) link.setAttribute("aria-current", "true");
      });
    }, { rootMargin: "-45% 0px -50% 0px" });
    Object.keys(byId).forEach(function (id) {
      var s = doc.getElementById(id);
      if (s) sectionObserver.observe(s);
    });
  }

  /* ------------------------------------------------------------------
   * 4. Einblend-Animationen beim Scrollen
   * ------------------------------------------------------------------ */
  // Nur Elemente, die beim Laden noch unterhalb des sichtbaren Bereichs liegen,
  // werden versteckt und beim Scrollen eingeblendet. Was schon sichtbar ist, bleibt sichtbar.
  var revealEls = $$("[data-reveal]");

  if ("IntersectionObserver" in window && !reduceMotion.matches) {
    // gestaffelte Verzögerung in Rastern
    $$(".svc-grid, .steps, .info-cards, .timeline").forEach(function (group) {
      $$(":scope > [data-reveal]", group).forEach(function (el, i) {
        el.style.setProperty("--delay", (Math.min(i, 6) * 0.08).toFixed(2) + "s");
      });
    });

    var revealObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var el = entry.target;
        revealObserver.unobserve(el);
        el.classList.add("is-in");
        // Nach der Animation Klassen entfernen -> normale Hover-Übergänge greifen wieder
        var delay = parseFloat(el.style.getPropertyValue("--delay")) || 0;
        window.setTimeout(function () {
          el.classList.remove("will-reveal", "is-in");
        }, 1100 + delay * 1000);
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -6% 0px" });

    var fold = window.innerHeight * 0.92;
    revealEls.forEach(function (el) {
      if (el.getBoundingClientRect().top > fold) {
        el.classList.add("will-reveal");
        revealObserver.observe(el);
      }
    });
  }

  /* ------------------------------------------------------------------
   * 5. Zähler (Kennzahlen)
   * ------------------------------------------------------------------ */
  var counters = $$("[data-count]");
  function runCounter(el) {
    var target = parseInt(el.getAttribute("data-count"), 10) || 0;
    var suffix = el.getAttribute("data-suffix") || "";
    var start = null;
    var dur = 1600;
    function step(ts) {
      if (!start) start = ts;
      var p = clamp((ts - start) / dur, 0, 1);
      var eased = 1 - Math.pow(1 - p, 3);
      el.textContent = Math.round(target * eased) + suffix;
      if (p < 1) window.requestAnimationFrame(step);
    }
    window.requestAnimationFrame(step);
  }
  if (counters.length && "IntersectionObserver" in window && !reduceMotion.matches) {
    var countObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          runCounter(entry.target);
          countObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.6 });
    counters.forEach(function (c) { countObserver.observe(c); });
  }

  /* ------------------------------------------------------------------
   * 6. 3D-Effekte (nur mit Maus, nicht bei "Bewegung reduzieren")
   * ------------------------------------------------------------------ */
  function canTilt() { return finePointer.matches && !reduceMotion.matches; }

  // Hero-Bühne folgt der Maus
  var hero = $(".hero");
  var stageInner = $(".stage__inner");
  if (hero && stageInner) {
    var tx = 0, ty = 0;
    var applyStage = rafThrottle(function () {
      stageInner.style.setProperty("--rx", (ty * -7).toFixed(2) + "deg");
      stageInner.style.setProperty("--ry", (tx * 10).toFixed(2) + "deg");
    });
    hero.addEventListener("pointermove", function (e) {
      if (!canTilt()) return;
      var r = hero.getBoundingClientRect();
      tx = ((e.clientX - r.left) / r.width) * 2 - 1;
      ty = ((e.clientY - r.top) / r.height) * 2 - 1;
      applyStage();
    });
    hero.addEventListener("pointerleave", function () {
      tx = 0; ty = 0; applyStage();
    });
  }

  // Karten kippen + Lichtreflex
  $$(".svc").forEach(function (card) {
    var px = 0.5, py = 0.5;
    var apply = rafThrottle(function () {
      card.style.setProperty("--rx", ((0.5 - py) * 7).toFixed(2) + "deg");
      card.style.setProperty("--ry", ((px - 0.5) * 9).toFixed(2) + "deg");
      card.style.setProperty("--mx", (px * 100).toFixed(1) + "%");
      card.style.setProperty("--my", (py * 100).toFixed(1) + "%");
    });
    card.addEventListener("pointermove", function (e) {
      if (!canTilt()) return;
      var r = card.getBoundingClientRect();
      px = clamp((e.clientX - r.left) / r.width, 0, 1);
      py = clamp((e.clientY - r.top) / r.height, 0, 1);
      apply();
    });
    card.addEventListener("pointerleave", function () {
      px = 0.5; py = 0.5;
      card.style.setProperty("--rx", "0deg");
      card.style.setProperty("--ry", "0deg");
    });
  });

  /* ------------------------------------------------------------------
   * 7. Leistungen filtern
   * ------------------------------------------------------------------ */
  var filters = $$("[data-filter]");
  filters.forEach(function (btn) {
    btn.addEventListener("click", function () {
      var cat = btn.getAttribute("data-filter");
      filters.forEach(function (b) { b.setAttribute("aria-pressed", b === btn ? "true" : "false"); });
      $$(".svc").forEach(function (card) {
        var show = cat === "alle" || card.getAttribute("data-cat") === cat;
        card.classList.toggle("is-hidden", !show);
        if (show) card.classList.add("is-in");
      });
      var feature = $(".feature");
      if (feature) feature.hidden = cat === "geraet";
    });
  });

  /* ------------------------------------------------------------------
   * 8. Bild-Grossansicht (Lightbox)
   * ------------------------------------------------------------------ */
  var lightbox = $("#lightbox");
  var lbImg = $("#lightbox-img");
  var lbCap = $("#lightbox-caption");
  var lbList = [];
  var lbIndex = 0;
  var lbTrigger = null;

  function lbShow(i) {
    if (!lbList.length) return;
    lbIndex = (i + lbList.length) % lbList.length;
    var btn = lbList[lbIndex];
    var thumb = $("img", btn);
    lbImg.src = btn.getAttribute("data-full");
    lbImg.alt = thumb ? thumb.alt : "";
    lbCap.textContent = btn.getAttribute("data-caption") || "";
  }

  function lbOpen(list, index, trigger) {
    if (!lightbox || typeof lightbox.showModal !== "function") {
      // sehr alte Browser: Bild direkt öffnen
      window.location.href = list[index].getAttribute("data-full");
      return;
    }
    lbList = list;
    lbTrigger = trigger || null;
    var multi = list.length > 1;
    $("[data-prev]", lightbox).hidden = !multi;
    $("[data-next]", lightbox).hidden = !multi;
    lbShow(index);
    lightbox.showModal();
    body.classList.add("menu-open");
  }

  if (lightbox) {
    $("[data-close]", lightbox).addEventListener("click", function () { lightbox.close(); });
    $("[data-prev]", lightbox).addEventListener("click", function () { lbShow(lbIndex - 1); });
    $("[data-next]", lightbox).addEventListener("click", function () { lbShow(lbIndex + 1); });
    lightbox.addEventListener("click", function (e) {
      if (e.target === lightbox) lightbox.close();
    });
    lightbox.addEventListener("keydown", function (e) {
      if (lbList.length < 2) return;
      if (e.key === "ArrowLeft") lbShow(lbIndex - 1);
      if (e.key === "ArrowRight") lbShow(lbIndex + 1);
    });
    lightbox.addEventListener("close", function () {
      body.classList.remove("menu-open");
      if (lbTrigger) lbTrigger.focus();
    });
    // Wischen auf dem Handy
    var sx = null;
    lightbox.addEventListener("pointerdown", function (e) { sx = e.clientX; });
    lightbox.addEventListener("pointerup", function (e) {
      if (sx === null || lbList.length < 2) return;
      var dx = e.clientX - sx;
      sx = null;
      if (Math.abs(dx) > 50) lbShow(lbIndex + (dx < 0 ? 1 : -1));
    });
  }

  var mapBtn = $(".directions__map");
  if (mapBtn) {
    mapBtn.addEventListener("click", function () { lbOpen([mapBtn], 0, mapBtn); });
  }

  /* ------------------------------------------------------------------
   * 9. 3D-Karussell der Praxis
   * ------------------------------------------------------------------ */
  var carousel = $("#carousel");
  if (carousel) whenIdle(function () { initCarousel(carousel); });

  function initCarousel(el) {
    var viewport = $("#carousel-viewport", el);
    var ring = $("#carousel-ring", el);
    var items = $$(".carousel__item", el);
    var buttons = items.map(function (it) { return $(".carousel__btn", it); });
    var controls = $("#carousel-controls", el);
    var dotsWrap = $("#carousel-dots", el);
    var status = $("#carousel-status", el);
    var n = items.length;
    var theta = 360 / n;
    var index = 0;
    var angle = 0;
    var radius = 480;
    var is3d = false;
    var autoTimer = 0;
    var inView = false;
    var paused = false;
    var dots = [];
    var mq = window.matchMedia("(min-width: 761px)");

    // Punkte-Navigation
    buttons.forEach(function (b, i) {
      var d = doc.createElement("button");
      d.type = "button";
      d.setAttribute("aria-label", "Bild " + (i + 1) + ": " + b.getAttribute("data-caption"));
      d.addEventListener("click", function () { go(i); });
      dotsWrap.appendChild(d);
      dots.push(d);
    });

    function layout() {
      var h = viewport.clientHeight - 40;
      var w = Math.round(h * 0.75);
      radius = Math.round((w / 2) / Math.tan(Math.PI / n)) + 40;
      ring.style.setProperty("--card-w", w + "px");
      ring.style.setProperty("--radius3d", radius + "px");
      items.forEach(function (it, i) {
        it.style.transform = "rotateY(" + (i * theta) + "deg) translateZ(" + radius + "px)";
      });
    }

    function render() {
      ring.style.setProperty("--angle", angle + "deg");
      items.forEach(function (it, i) { it.classList.toggle("is-front", i === index); });
      dots.forEach(function (d, i) {
        if (i === index) d.setAttribute("aria-current", "true"); else d.removeAttribute("aria-current");
      });
      status.textContent = "Bild " + (index + 1) + " von " + n + ": " + buttons[index].getAttribute("data-caption");
    }

    function go(i) {
      var target = ((i % n) + n) % n;
      // kürzester Weg um den Ring
      var diff = target - index;
      if (diff > n / 2) diff -= n;
      if (diff < -n / 2) diff += n;
      index = target;
      angle -= diff * theta;
      render();
    }

    function startAuto() {
      stopAuto();
      if (!is3d || reduceMotion.matches || !inView || paused) return;
      autoTimer = window.setInterval(function () { go(index + 1); }, 4200);
    }
    function stopAuto() {
      if (autoTimer) window.clearInterval(autoTimer);
      autoTimer = 0;
    }

    function enable3d() {
      is3d = true;
      el.classList.remove("carousel--flat");
      controls.hidden = false;
      dotsWrap.hidden = false;
      layout();
      render();
      startAuto();
    }

    function disable3d() {
      is3d = false;
      stopAuto();
      el.classList.add("carousel--flat");
      controls.hidden = true;
      dotsWrap.hidden = true;
      items.forEach(function (it) { it.style.transform = ""; });
    }

    function decide() {
      if (mq.matches && !reduceMotion.matches) enable3d(); else disable3d();
    }

    // Klick: vorderes Bild -> Grossansicht, sonst nach vorne drehen
    var dragged = false;
    buttons.forEach(function (b, i) {
      b.addEventListener("click", function (e) {
        if (dragged) { e.preventDefault(); return; }
        if (is3d && i !== index) { go(i); return; }
        lbOpen(buttons, i, b);
      });
      b.addEventListener("focus", function () {
        if (is3d && i !== index) go(i);
      });
    });

    $("#carousel-prev", el).addEventListener("click", function () { go(index - 1); });
    $("#carousel-next", el).addEventListener("click", function () { go(index + 1); });

    viewport.addEventListener("keydown", function (e) {
      if (!is3d) return;
      if (e.key === "ArrowLeft") { e.preventDefault(); go(index - 1); }
      if (e.key === "ArrowRight") { e.preventDefault(); go(index + 1); }
    });

    // Ziehen mit Maus / Finger
    var startX = 0, startAngle = 0, pointerId = null;
    viewport.addEventListener("pointerdown", function (e) {
      if (!is3d || e.button !== 0) return;
      pointerId = e.pointerId;
      startX = e.clientX;
      startAngle = angle;
      dragged = false;
    });
    viewport.addEventListener("pointermove", function (e) {
      if (!is3d || pointerId !== e.pointerId) return;
      var dx = e.clientX - startX;
      if (!dragged && Math.abs(dx) > 6) {
        dragged = true;
        viewport.classList.add("is-dragging");
        try { viewport.setPointerCapture(e.pointerId); } catch (err) { /* ignorieren */ }
      }
      if (dragged) {
        angle = startAngle + dx * 0.22;
        ring.style.setProperty("--angle", angle + "deg");
      }
    });
    function endDrag(e) {
      if (pointerId === null || (e && pointerId !== e.pointerId)) return;
      pointerId = null;
      viewport.classList.remove("is-dragging");
      if (dragged) {
        var steps = Math.round((angle - startAngle) / theta);
        angle = startAngle;
        go(index - steps);
        window.setTimeout(function () { dragged = false; }, 50);
      }
    }
    viewport.addEventListener("pointerup", endDrag);
    viewport.addEventListener("pointercancel", endDrag);

    // Pausieren bei Hover/Fokus und ausserhalb des Bildschirms
    el.addEventListener("pointerenter", function () { paused = true; stopAuto(); });
    el.addEventListener("pointerleave", function () { paused = false; startAuto(); });
    el.addEventListener("focusin", function () { paused = true; stopAuto(); });
    el.addEventListener("focusout", function () { paused = false; startAuto(); });

    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (entries) {
        inView = entries[0].isIntersecting;
        if (inView) startAuto(); else stopAuto();
      }, { threshold: 0.35 }).observe(viewport);
    }

    window.addEventListener("resize", rafThrottle(function () { if (is3d) layout(); }));
    mq.addEventListener("change", decide);
    reduceMotion.addEventListener("change", decide);
    decide();
  }

  /* ------------------------------------------------------------------
   * 10. Öffnungszeiten: "Jetzt geöffnet" (Zeitzone Zürich)
   * ------------------------------------------------------------------ */
  var HOURS = { 0: null, 1: [8, 21], 2: [8, 21], 3: [8, 21], 4: [8, 21], 5: [8, 21], 6: [7, 19] };
  var DAY_NAMES = ["Sonntag", "Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag"];
  var WD = { Sun: 0, Mon: 1, Tue: 2, Wed: 3, Thu: 4, Fri: 5, Sat: 6 };

  function pad(h) { return (h < 10 ? "0" : "") + h + ":00"; }

  function zurichNow() {
    try {
      var parts = new Intl.DateTimeFormat("en-GB", {
        timeZone: "Europe/Zurich", weekday: "short", hour: "2-digit", minute: "2-digit", hourCycle: "h23"
      }).formatToParts(new Date());
      var o = {};
      parts.forEach(function (p) { o[p.type] = p.value; });
      return { day: WD[o.weekday], min: parseInt(o.hour, 10) * 60 + parseInt(o.minute, 10) };
    } catch (e) {
      var d = new Date();
      return { day: d.getDay(), min: d.getHours() * 60 + d.getMinutes() };
    }
  }

  function openState() {
    var now = zurichNow();
    var today = HOURS[now.day];
    if (today && now.min >= today[0] * 60 && now.min < today[1] * 60) {
      return { open: true, title: "Jetzt geöffnet", sub: "heute bis " + pad(today[1]) + " Uhr", day: now.day };
    }
    if (today && now.min < today[0] * 60) {
      return { open: false, title: "Zurzeit geschlossen", sub: "öffnet heute um " + pad(today[0]) + " Uhr", day: now.day };
    }
    for (var i = 1; i <= 7; i++) {
      var d = (now.day + i) % 7;
      if (HOURS[d]) {
        var when = i === 1 ? "morgen" : "am " + DAY_NAMES[d];
        return { open: false, title: "Zurzeit geschlossen", sub: "öffnet " + when + " um " + pad(HOURS[d][0]) + " Uhr", day: now.day };
      }
    }
    return { open: false, title: "Zurzeit geschlossen", sub: "", day: now.day };
  }

  function updateOpenStatus() {
    var s = openState();
    // Kontaktbereich: sachlicher Status (grau = geschlossen)
    var badgeDot = $("#open-status [data-open-dot]");
    if (badgeDot) badgeDot.classList.toggle("is-closed", !s.open);
    // Hero-Chip: positiv formuliert – Anfragen sind immer möglich
    var heroDot = $(".chip--status [data-open-dot]");
    if (heroDot) heroDot.classList.toggle("is-request", !s.open);
    var t = $("[data-open-title]");
    var sub = $("[data-open-sub]");
    if (t) t.textContent = s.open ? s.title : "Online-Anfrage jederzeit";
    if (sub) sub.textContent = s.sub;
    var badge = $("#open-status");
    if (badge) {
      badge.hidden = false;
      badge.classList.toggle("is-closed", !s.open);
      $("[data-open-text]", badge).textContent = s.title + (s.sub ? " · " + s.sub : "");
    }
    $$("#hours tr[data-days]").forEach(function (tr) {
      var days = tr.getAttribute("data-days").split(",");
      tr.classList.toggle("is-today", days.indexOf(String(s.day)) !== -1);
    });
  }
  updateOpenStatus();
  window.setInterval(updateOpenStatus, 60000);

  /* ------------------------------------------------------------------
   * 11. Kontaktformular (Netlify Forms + Spam-Schutz)
   * ------------------------------------------------------------------ */
  var form = $("#contact-form");
  if (form) initForm(form);

  function initForm(f) {
    var loadedAt = Date.now();
    var statusEl = $("#form-status");
    var wrap = $("#form-wrap");
    var success = $("#form-success");
    var submitLabel = $("[data-submit-label]", f);
    var reEmail = /^[^\s@<>()[\]\\,;:"]+@[^\s@<>()[\]\\,;:"]+\.[^\s@<>()[\]\\,;:"]{2,}$/;
    var rePhone = /^[0-9+()\/ .\-]{7,30}$/;

    function fieldOf(input) { return input.closest(".field"); }

    function setError(input, bad) {
      var field = fieldOf(input);
      if (field) field.classList.toggle("has-error", bad);
      if (bad) input.setAttribute("aria-invalid", "true"); else input.removeAttribute("aria-invalid");
    }

    function check(input) {
      var v = (input.value || "").trim();
      var bad = false;
      switch (input.name) {
        case "name": bad = v.length < 2; break;
        case "telefon": bad = !rePhone.test(v) || v.replace(/\D/g, "").length < 7; break;
        case "email": bad = v.length > 0 && !reEmail.test(v); break;
        case "datenschutz": bad = !input.checked; break;
        default: bad = false;
      }
      setError(input, bad);
      return !bad;
    }

    var validated = ["name", "telefon", "email", "datenschutz"].map(function (n) { return f.elements[n]; });
    // Fehler erst nach dem ersten Absenden zeigen, dann live korrigieren.
    // (Keine Prüfung beim Verlassen eines Feldes: eine plötzlich erscheinende
    //  Meldung würde das Layout verschieben und auf dem Handy Fehl-Tipps auslösen.)
    validated.forEach(function (input) {
      if (!input) return;
      input.addEventListener(input.type === "checkbox" ? "change" : "input", function () {
        if (fieldOf(input).classList.contains("has-error")) check(input);
      });
    });

    function showSuccess() {
      wrap.hidden = true;
      success.classList.add("is-visible");
      success.focus();
    }

    function showError(msg) {
      statusEl.textContent = msg;
      statusEl.classList.add("is-error");
    }

    f.addEventListener("submit", function (e) {
      e.preventDefault();
      statusEl.textContent = "";
      statusEl.classList.remove("is-error");

      var firstBad = null;
      validated.forEach(function (input) {
        if (input && !check(input) && !firstBad) firstBad = input;
      });
      if (firstBad) {
        firstBad.focus();
        return;
      }

      // Spam-Schutz 1: Honeypot (für Menschen unsichtbares Feld)
      // Spam-Schutz 2: Bots senden in Sekundenbruchteilen
      var hp = f.elements.firma;
      if ((hp && hp.value) || Date.now() - loadedAt < 2500) {
        showSuccess();
        return;
      }

      // Spam-Schutz 3: kein Mehrfach-Versand innerhalb kurzer Zeit
      try {
        var last = parseInt(window.sessionStorage.getItem("pp-form-sent") || "0", 10);
        if (Date.now() - last < 60000) {
          showError("Ihre Anfrage wurde bereits gesendet. Bitte warten Sie einen Moment, bevor Sie eine weitere Anfrage senden.");
          return;
        }
      } catch (err) { /* Speicher nicht verfügbar – ignorieren */ }

      var data = new FormData(f);
      var params = new URLSearchParams();
      data.forEach(function (value, key) {
        params.append(key, String(value).slice(0, 2000));
      });

      f.classList.add("is-sending");
      if (submitLabel) submitLabel.textContent = "Wird gesendet …";

      window.fetch("/", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: params.toString(),
        credentials: "same-origin"
      }).then(function (res) {
        if (!res.ok) throw new Error("HTTP " + res.status);
        try { window.sessionStorage.setItem("pp-form-sent", String(Date.now())); } catch (err) { /* ignorieren */ }
        f.reset();
        showSuccess();
      }).catch(function () {
        showError("Leider ist beim Senden ein Fehler aufgetreten. Bitte versuchen Sie es erneut oder rufen Sie uns an: 041 554 55 41.");
      }).then(function () {
        f.classList.remove("is-sending");
        if (submitLabel) submitLabel.textContent = "Anfrage senden";
      });
    });
  }

  /* ------------------------------------------------------------------
   * 12. Zeitstrahl füllt sich beim Scrollen
   * ------------------------------------------------------------------ */
  var timeline = $("#timeline");
  var tlItems = timeline ? $$(".tl-item", timeline) : [];
  function updateTimeline() {
    if (!timeline) return;
    var vh = window.innerHeight;
    var r = timeline.getBoundingClientRect();
    var p = clamp((vh * 0.62 - r.top) / r.height, 0, 1);
    timeline.style.setProperty("--progress", p.toFixed(3));
    tlItems.forEach(function (it) {
      var dot = $(".tl-item__dot", it);
      var top = dot.getBoundingClientRect().top;
      it.classList.toggle("is-active", top < vh * 0.62);
    });
  }

  /* ------------------------------------------------------------------
   * 13. Kleinigkeiten
   * ------------------------------------------------------------------ */
  $$("[data-year]").forEach(function (el) { el.textContent = String(new Date().getFullYear()); });

  onScroll();
  updateTimeline();
})();
