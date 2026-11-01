(() => {
  // Textes et aliments de la langue de la page, injectés par build.py
  const L = JSON.parse(document.getElementById("i18n").textContent);
  const RAW = L.foods;

  const norm = s => s.toLowerCase().replace(/œ/g, "oe").replace(/æ/g, "ae")
    .normalize("NFD").replace(/[\u0300-\u036f]/g, "")
    .replace(/[’`]/g, "'").replace(/[^a-z0-9' -]/g, " ").replace(/\s+/g, " ").trim();
  const ARTICLE = new RegExp(L.articles);
  const strip = s => { let t = norm(s); let prev; do { prev = t; t = t.replace(ARTICLE, "").trim(); } while (t !== prev); return t; };

  const FOODS = RAW.map(([name, phrase, v, keys, why]) => ({ name, phrase, v, keys: keys.split("|").map(norm), why }));
  const INDEX = new Map();
  FOODS.forEach(f => f.keys.forEach(k => INDEX.set(k, f)));

  function find(q) {
    const t = strip(q);
    if (t.length < 2) return null;
    if (INDEX.has(t)) return INDEX.get(t);
    const sing = t.replace(/(s|x)$/, "");
    if (INDEX.has(sing)) return INDEX.get(sing);
    let best = null, len = 0;
    for (const [k, f] of INDEX) {
      const hit = (` ${t} `).includes(` ${k} `) || (t.length >= 3 && k.startsWith(t));
      if (hit && k.length > len) { best = f; len = k.length; }
    }
    return best;
  }

  const VERDICT = L.verdict;
  const ICON = {
    oui: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>',
    peu: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"><path d="M6 12h12"/></svg>',
    non: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"><path d="M12 6v8M12 18v.01"/></svg>',
    q:   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.8" stroke-linecap="round"><path d="M9 9a3 3 0 1 1 4.2 2.75c-.75.33-1.2 1-1.2 1.8V14M12 18v.01"/></svg>'
  };

  const $ = id => document.getElementById(id);
  const hero = $("test"), input = $("food"), measure = $("measure"), stamp = $("stamp"), reason = $("reason");
  const screen = $("screen");
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const vivis = [...document.querySelectorAll(".vivi-react img")];
  const setVivi = v => vivis.forEach(img => img.classList.toggle("on", img.dataset.v === v));

  const blank = input.parentElement;
  // la case a une largeur fixe ; si l'aliment ne tient pas sur la ligne, seule sa police rétrécit
  function size() {
    measure.textContent = input.value || input.placeholder || " ";
    const w = measure.getBoundingClientRect().width + 8;
    const ratio = Math.max(0.45, Math.min(1, blank.clientWidth / w));
    input.style.fontSize = ratio < 1 ? ratio.toFixed(3) + "em" : "";
  }
  const firstSentence = s => (s.match(/^.*?[.!?](\s|$)/) || [s])[0].trim();
  const cap = s => s.charAt(0).toUpperCase() + s.slice(1);

  let current = null, swapTimer;
  function setReason(text, instant) {
    clearTimeout(swapTimer);
    if (instant || reduce) { reason.textContent = text; reason.classList.remove("swap"); return; }
    reason.classList.add("swap");
    swapTimer = setTimeout(() => { reason.textContent = text; reason.classList.remove("swap"); }, 170);
  }
  function show(text, force, instant) {
    const food = find(text);
    if (!food && !force) return;
    if (food && food === current && !force) return;
    current = food;
    const v = food ? food.v : "q";
    const V = VERDICT[v];
    hero.dataset.v = v;
    screen.dataset.v = v;
    setVivi(v);
    stamp.textContent = V.stamp;
    if (!reduce) { stamp.classList.remove("thump"); void stamp.offsetWidth; stamp.classList.add("thump"); }
    setReason(food
      ? firstSentence(food.why)
      : L.unknownReason, instant);
    $("s-icon").innerHTML = ICON[v];
    $("s-title").textContent = V.title;
    $("s-sub").textContent = V.sub;
    $("s-food").textContent = food ? food.name : cap(strip(text) || L.unknownFood);
    $("s-why").textContent = food
      ? food.why
      : L.unknownWhy;
    document.querySelectorAll(".chip").forEach(c => c.setAttribute("aria-pressed", String(!!food && find(c.dataset.q) === food)));
  }

  $("chips").innerHTML = L.chips.map(([q, label]) => `<button type="button" class="chip" data-q="${q}" aria-pressed="false">${label}</button>`).join("");
  $("count").textContent = L.count.replace("{n}", FOODS.length);

  // auto-démo, coupée dès que la personne interagit
  let demoOn = !reduce, heroVisible = true;
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  new IntersectionObserver(([e]) => { heroVisible = e.isIntersecting; }).observe(hero);
  // l'ancien mot s'efface en fondu, le nouveau se tape : rien d'autre ne bouge dans le hero
  async function typeTo(t) {
    input.placeholder = "";
    setVivi("q");
    input.classList.add("erasing");
    await sleep(200);
    if (!demoOn) return;
    input.value = ""; size();
    input.classList.remove("erasing");
    for (const ch of t) { if (!demoOn) return; input.value += ch; size(); await sleep(55); }
  }
  async function demo() {
    const seq = L.demo;
    let i = 0;
    await sleep(2600);
    while (demoOn) {
      if (!heroVisible || document.hidden) { await sleep(600); continue; }
      const t = seq[i++ % seq.length];
      await typeTo(t);
      if (!demoOn) break;
      show(t);
      await sleep(3000);
    }
  }
  const stopDemo = () => { demoOn = false; input.classList.remove("erasing"); input.placeholder = L.placeholder; };

  function pick(q) { stopDemo(); input.value = q; size(); show(q, true); }
  document.addEventListener("click", e => {
    const b = e.target.closest("[data-q]");
    if (!b) return;
    pick(b.dataset.q);
  });
  input.addEventListener("focus", () => { stopDemo(); setTimeout(() => input.select(), 0); });
  input.addEventListener("pointerdown", stopDemo);
  let timer;
  input.addEventListener("input", () => {
    stopDemo(); size();
    clearTimeout(timer);
    timer = setTimeout(() => show(input.value), 450);
  });
  $("ask").addEventListener("submit", e => { e.preventDefault(); stopDemo(); show(input.value, true); input.blur(); });
  $("again").addEventListener("click", () => { stopDemo(); input.focus(); });

  show(input.value, true, true);
  stamp.classList.remove("thump");
  size();
  (document.fonts ? document.fonts.ready : Promise.resolve()).then(size);
  addEventListener("resize", size);
  if (demoOn) demo();

  // ---------- Une journée avec Vivi : l'étape la plus proche de la ligne de lecture pilote le téléphone ----------
  const day = $("journee");
  const daySteps = [...day.querySelectorAll(".day-step")];
  const dayScreens = [...day.querySelectorAll(".ds")];
  const dayVivis = [...day.querySelectorAll(".day-vivi")];
  const clock = $("day-clock");
  const wide = matchMedia("(min-width: 900px)");
  let dayActive = -1;
  function countUp(el) {
    const to = +el.dataset.to;
    if (reduce) { el.textContent = to; return; }
    const t0 = performance.now(), dur = 1200;
    const step = now => {
      const k = Math.min(1, (now - t0) / dur), e = 1 - Math.pow(2, -10 * k);
      el.textContent = Math.round(to * e);
      if (k < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }
  function setDay(i) {
    if (i === dayActive) return;
    dayActive = i;
    daySteps.forEach((s, k) => s.classList.toggle("on", k === i));
    dayScreens.forEach((s, k) => s.classList.toggle("on", k === i));
    dayVivis.forEach((s, k) => s.classList.toggle("on", k === i));
    day.dataset.sky = daySteps[i].dataset.sky;
    clock.textContent = daySteps[i].dataset.clock;
    dayScreens[i].querySelectorAll(".count").forEach(countUp);
  }
  // section encore loin : on attend qu'elle arrive pour jouer l'animation du premier écran
  if (day.getBoundingClientRect().top > innerHeight * 0.75) {
    [...daySteps, ...dayScreens, ...dayVivis].forEach(el => el.classList.remove("on"));
  }
  function pickDay() {
    const box = day.getBoundingClientRect();
    day.classList.toggle("live", box.top < innerHeight && box.bottom > 0);
    if (box.top > innerHeight * 0.75 || box.bottom < 0) return;
    const line = innerHeight * (wide.matches ? 0.5 : 0.78);
    let best = 0, dist = Infinity;
    daySteps.forEach((s, k) => {
      const r = s.getBoundingClientRect(), d = Math.abs((r.top + r.bottom) / 2 - line);
      if (d < dist) { dist = d; best = k; }
    });
    setDay(best);
  }

  // ---------- Parallaxe : le téléphone du hero suit la souris, les images glissent au scroll ----------
  const device = hero.querySelector(".hero-device");
  const frame = document.querySelector(".moment-frame");
  let tx = 0, ty = 0, cx = 0, cy = 0, raf = 0;
  function frameTick() {
    raf = 0;
    cx += (tx - cx) * 0.1; cy += (ty - cy) * 0.1;
    const sy = Math.min(scrollY, innerHeight);
    device.style.setProperty("--rx", (-cy * 5).toFixed(2) + "deg");
    device.style.setProperty("--ry", (cx * 7).toFixed(2) + "deg");
    device.style.setProperty("--ty", (-sy * 0.07).toFixed(1) + "px");
    device.style.setProperty("--vx", (-cx * 12).toFixed(1) + "px");
    device.style.setProperty("--vy", (-sy * 0.16 - cy * 8).toFixed(1) + "px");
    const r = frame.getBoundingClientRect();
    if (r.bottom > 0 && r.top < innerHeight) {
      const p = (r.top + r.height / 2) / innerHeight - 0.5;
      frame.style.setProperty("--par", (p * -46).toFixed(1) + "px");
    }
    if (Math.abs(tx - cx) > 0.002 || Math.abs(ty - cy) > 0.002) request();
  }
  const request = () => { if (!raf) raf = requestAnimationFrame(frameTick); };
  addEventListener("scroll", () => { pickDay(); if (!reduce) request(); }, { passive: true });
  addEventListener("resize", pickDay);
  if (!reduce) {
    if (matchMedia("(pointer: fine)").matches) {
      hero.addEventListener("pointermove", e => {
        const r = hero.getBoundingClientRect();
        tx = (e.clientX - r.left) / r.width * 2 - 1;
        ty = (e.clientY - r.top) / r.height * 2 - 1;
        request();
      });
      hero.addEventListener("pointerleave", () => { tx = ty = 0; request(); });
    }
    request();
  }
  pickDay();

  // ---------- Apparitions : seulement pour ce qui est encore sous la ligne de flottaison ----------
  if (!reduce && "IntersectionObserver" in window) {
    const io = new IntersectionObserver(entries => entries.forEach(en => {
      if (en.isIntersecting) { en.target.classList.remove("pre"); io.unobserve(en.target); }
    }), { threshold: 0.15, rootMargin: "0px 0px -6% 0px" });
    document.querySelectorAll("[data-reveal]").forEach(el => {
      if (el.getBoundingClientRect().top > innerHeight * 0.92) { el.classList.add("pre"); io.observe(el); }
    });
  }
  // ---------- Images de Vivi pas encore visibles : chargées une fois la page prête ----------
  addEventListener("load", () => {
    document.querySelectorAll("img[data-src]").forEach(img => { img.src = img.dataset.src; img.removeAttribute("data-src"); });
  });

  // ---------- Google Analytics : chargé à la première interaction (ou après 6 s) pour ne pas freiner l'affichage ----------
  const GA_ID = L.gaId;
  let gaLoaded = false;
  function loadGA() {
    if (gaLoaded || !GA_ID) return;
    gaLoaded = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { dataLayer.push(arguments); };
    gtag("js", new Date());
    gtag("config", GA_ID);
    const sc = document.createElement("script");
    sc.async = true;
    sc.src = "https://www.googletagmanager.com/gtag/js?id=" + GA_ID;
    document.head.appendChild(sc);
  }
  ["pointerdown", "keydown", "scroll", "touchstart"].forEach(ev => addEventListener(ev, loadGA, { once: true, passive: true }));
  addEventListener("load", () => setTimeout(loadGA, 6000));
})();
