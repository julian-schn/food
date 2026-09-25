(function () {
  "use strict";
  var html = document.documentElement;
  var $ = function (sel, el) { return (el || document).querySelector(sel); };
  var $$ = function (sel, el) { return Array.prototype.slice.call((el || document).querySelectorAll(sel)); };
  var lang = function () { return html.dataset.lang; };

  function store(key, val) { try { localStorage.setItem(key, val); } catch (e) {} }

  // --- language -----------------------------------------------------------
  function applyLang(l) {
    html.dataset.lang = l;
    html.lang = l;
    $$("[data-ph-" + l + "]").forEach(function (el) { el.placeholder = el.dataset["ph" + l[0].toUpperCase() + l[1]]; });
    $$("[data-set-lang]").forEach(function (b) { b.setAttribute("aria-pressed", b.dataset.setLang === l); });
    document.dispatchEvent(new Event("langchange"));
  }
  $$("[data-set-lang]").forEach(function (b) {
    b.addEventListener("click", function () { store("lang", b.dataset.setLang); applyLang(b.dataset.setLang); });
  });
  applyLang(lang());

  // --- index: search + facet filters -------------------------------------
  var dataEl = $("#recipe-data");
  if (dataEl) {
    var recipes = JSON.parse(dataEl.textContent);
    var q = $("#q"), facets = $("#facets");
    var boxes = $$(".facet input", facets);
    var norm = function (s) { return (s || "").toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, ""); };
    recipes.forEach(function (r) {
      r.haystack = norm([r.title.de, r.title.en, r.description && r.description.de,
        r.description && r.description.en].join(" "));
      r.card = $('.card[data-id="' + r.id + '"]');
    });

    var render = function () {
      var byFacet = {};
      boxes.filter(function (b) { return b.checked; }).forEach(function (b) {
        var f = b.closest(".facet").dataset.facet;
        (byFacet[f] = byFacet[f] || []).push(b.value);
      });
      var terms = norm(q.value).split(/\s+/).filter(Boolean);
      var shown = 0;
      recipes.forEach(function (r) {
        var ok = terms.every(function (t) { return r.haystack.indexOf(t) !== -1; }) &&
          Object.keys(byFacet).every(function (f) {  // OR within a facet, AND across facets
            return byFacet[f].some(function (t) { return r.tags.indexOf(t) !== -1; });
          });
        r.card.hidden = !ok;
        if (ok) shown++;
      });
      var active = boxes.filter(function (b) { return b.checked; }).map(function (b) { return b.value; });
      var count = $("#active-count");
      count.hidden = !active.length;
      count.textContent = active.length;
      $("#empty").hidden = shown > 0;
      $("#result-count").textContent = lang() === "de"
        ? shown + (shown === 1 ? " Rezept" : " Rezepte")
        : shown + (shown === 1 ? " recipe" : " recipes");
      var hash = active.map(encodeURIComponent).join(",");
      if (hash !== location.hash.slice(1)) history.replaceState(null, "", hash ? "#" + hash : location.pathname);
    };

    var fromHash = function () {
      var want = location.hash.slice(1).split(",").map(decodeURIComponent);
      boxes.forEach(function (b) { b.checked = want.indexOf(b.value) !== -1; });
      if (want.some(Boolean)) facets.open = true;
      render();
    };
    boxes.forEach(function (b) { b.addEventListener("change", render); });
    q.addEventListener("input", render);
    $("#clear").addEventListener("click", function () { boxes.forEach(function (b) { b.checked = false; }); render(); });
    window.addEventListener("hashchange", fromHash);
    document.addEventListener("langchange", render);
    fromHash();
  }

  // --- recipe: ingredient highlight ---------------------------------------
  var highlight = function (id, on) {
    $$('[data-ing="' + id + '"]').forEach(function (el) { el.classList.toggle("hl", on); });
  };
  $$(".ing").forEach(function (el) {
    el.addEventListener("mouseenter", function () { highlight(el.dataset.ing, true); });
    el.addEventListener("mouseleave", function () { highlight(el.dataset.ing, false); });
    el.addEventListener("click", function () {
      var on = !el.classList.contains("hl");
      $$(".hl").forEach(function (h) { h.classList.remove("hl"); });
      highlight(el.dataset.ing, on);
    });
  });

  // --- recipe: sticky ingredients only when the whole list fits on screen --
  var ingBox = $(".ingredients");
  var fitIngredients = function () {
    if (ingBox) ingBox.classList.toggle("fits", ingBox.offsetHeight <= window.innerHeight - 32);
  };
  window.addEventListener("resize", fitIngredients);
  document.addEventListener("langchange", fitIngredients);
  fitIngredients();

  // --- recipe: servings scaler --------------------------------------------
  var scaler = $(".scaler");
  if (scaler) {
    var base = +scaler.dataset.base, servings = base, out = $("#servings");
    var round = function (x, unit) {
      if (unit === "g" || unit === "ml") return x >= 10 ? Math.round(x) : Math.round(x * 10) / 10;
      if (unit === "kg" || unit === "l") return Math.round(x * 100) / 100;
      return Math.max(0.5, Math.round(x * 2) / 2);  // tsp, tbsp, pinch, piece: to the half
    };
    // 1500 g reads better than 1.5 kg once scaled down, and vice versa.
    var fmt = function (x, unit, l) {
      if (unit === "kg" && x < 1) { x *= 1000; unit = "g"; }
      if (unit === "l" && x < 1) { x *= 1000; unit = "ml"; }
      if (unit === "g" && x >= 1000) { x /= 1000; unit = "kg"; }
      if (unit === "ml" && x >= 1000) { x /= 1000; unit = "l"; }
      var n = String(round(x, unit));
      return { n: l === "de" ? n.replace(".", ",") : n, unit: unit };
    };
    var UNIT = { tsp: ["TL", "tsp"], tbsp: ["EL", "tbsp"], pinch: ["Prise", "pinch"],
      g: ["g", "g"], kg: ["kg", "kg"], ml: ["ml", "ml"], l: ["l", "l"], piece: ["", ""] };
    var amts = $$(".amt[data-amount]");
    amts.forEach(function (el) { el.dataset.orig = el.innerHTML; });
    var rescale = function () {
      out.textContent = servings;
      $("#scale-note").classList.toggle("is-hidden", servings === base);
      amts.forEach(function (el) {
        if (servings === base) { el.innerHTML = el.dataset.orig; return; }
        var x = +el.dataset.amount * servings / base, unit = el.dataset.unit;
        el.innerHTML = ["de", "en"].map(function (l, i) {
          var f = fmt(x, unit, l), u = UNIT[f.unit] ? UNIT[f.unit][i] : f.unit;
          return '<span class="l-' + l + '" lang="' + l + '">' + f.n + (u ? "\u00a0" + u : "") + "</span>";
        }).join("");
      });
    };
    $$("button", scaler).forEach(function (b) {
      b.addEventListener("click", function () {
        servings = Math.max(1, servings + +b.dataset.step);
        rescale();
        fitIngredients();
      });
    });
  }

  // --- recipe: cook mode (wake lock) --------------------------------------
  var cookBtn = $("#cook-toggle"), wakeLock = null;
  var requestLock = function () {
    if (!("wakeLock" in navigator)) return;
    navigator.wakeLock.request("screen").then(function (l) { wakeLock = l; }).catch(function () {});
  };
  if (cookBtn) {
    cookBtn.addEventListener("click", function () {
      var on = !document.body.classList.contains("cooking");
      document.body.classList.toggle("cooking", on);
      cookBtn.setAttribute("aria-pressed", on);
      fitIngredients();
      if (on) requestLock();
      else if (wakeLock) { wakeLock.release(); wakeLock = null; }
    });
    // The browser drops the lock when the tab is hidden; take it back on return.
    document.addEventListener("visibilitychange", function () {
      if (document.visibilityState === "visible" && document.body.classList.contains("cooking")) requestLock();
    });
  }

  // --- recipe: step timers ------------------------------------------------
  var audio = null;
  var beep = function () {
    try {
      audio = audio || new (window.AudioContext || window.webkitAudioContext)();
      [0, 0.4, 0.8].forEach(function (t) {
        var o = audio.createOscillator(), g = audio.createGain();
        o.frequency.value = 880;
        g.gain.setValueAtTime(0.2, audio.currentTime + t);
        g.gain.exponentialRampToValueAtTime(0.001, audio.currentTime + t + 0.3);
        o.connect(g).connect(audio.destination);
        o.start(audio.currentTime + t);
        o.stop(audio.currentTime + t + 0.3);
      });
    } catch (e) {}
    if (navigator.vibrate) navigator.vibrate([200, 100, 200]);
  };
  var clock = function (s) {
    var h = Math.floor(s / 3600), m = Math.floor(s % 3600 / 60), sec = s % 60;
    var mm = h ? String(m).padStart(2, "0") : m;
    return (h ? h + ":" : "") + mm + ":" + String(sec).padStart(2, "0");
  };
  $$(".timer").forEach(function (btn) {
    var total = +btn.dataset.seconds, left = total, endAt = null, tick = null;
    var label = $(".timer-left", btn);
    var stop = function () {
      clearInterval(tick); tick = null;
      btn.classList.remove("running"); btn.setAttribute("aria-pressed", "false");
    };
    btn.addEventListener("click", function () {
      if (btn.classList.contains("done")) {  // reset after finishing
        btn.classList.remove("done"); left = total; label.textContent = clock(left); return;
      }
      if (tick) { stop(); return; }  // pause
      if (audio && audio.state === "suspended") audio.resume();
      else if (!audio) { try { audio = new (window.AudioContext || window.webkitAudioContext)(); } catch (e) {} }
      endAt = Date.now() + left * 1000;  // wall clock, so a backgrounded tab stays correct
      btn.classList.add("running"); btn.setAttribute("aria-pressed", "true");
      tick = setInterval(function () {
        left = Math.max(0, Math.round((endAt - Date.now()) / 1000));
        label.textContent = clock(left);
        if (left === 0) { stop(); btn.classList.add("done"); beep(); }
      }, 250);
    });
  });
})();
