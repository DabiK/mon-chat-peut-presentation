(() => {
  // Textes et aliments de la langue de la page, injectés par build.py
  const L = JSON.parse(document.getElementById("i18n").textContent);
  const RAW = L.foods;

  const norm = s => s.toLowerCase().replace(/œ/g, "oe").replace(/æ/g, "ae")
    .normalize("NFD").replace(/[̀-ͯ]/g, "")
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
  const $ = id => document.getElementById(id);
  const hero = $("test"), input = $("food"), measure = $("measure"), stamp = $("stamp"), reason = $("reason");
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Vivi réagit au verdict : les images pas encore vues se chargent à la demande
  const vivis = [...document.querySelectorAll(".vivi-react img, .vivi-mini img")];
  const reveal = img => { if (img.dataset.src) { img.src = img.dataset.src; img.removeAttribute("data-src"); } };
  const setVivi = v => vivis.forEach(img => {
    const on = img.dataset.v === v;
    if (on) reveal(img);
    img.classList.toggle("on", on);
  });
  addEventListener("load", () => vivis.forEach(reveal));

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
    setVivi(v);
    $("stamp-word").textContent = V.stamp;
    if (!reduce && !instant) { stamp.classList.remove("thump"); void stamp.offsetWidth; stamp.classList.add("thump"); }
    setReason(food ? firstSentence(food.why) : L.unknownReason, instant);
    const name = food ? food.name : cap(strip(text) || L.unknownFood);
    const why = food ? food.why : L.unknownWhy;
    $("f-band").textContent = V.band;
    $("f-name").textContent = name;
    $("f-brief").textContent = V.sub;
    $("f-why").textContent = why;
    // annonce pour les lecteurs d'écran, quelle que soit la mise en page (la fiche est masquée sur téléphone)
    if (!instant) $("sr-verdict").textContent = `${name}. ${V.stamp} ${V.sub} ${why}`;
    document.querySelectorAll(".chip").forEach(c => c.setAttribute("aria-pressed", String(!!food && find(c.dataset.q) === food)));
  }

  // auto-démo, coupée dès que la personne interagit
  let demoOn = !reduce, heroVisible = true;
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  new IntersectionObserver(([e]) => { heroVisible = e.isIntersecting; }).observe(hero);
  // l'ancien mot s'efface lettre par lettre, le nouveau se tape : le texte reste toujours bien contrasté,
  // et rien d'autre ne bouge dans le hero
  async function typeTo(t) {
    input.placeholder = "";
    setVivi("q");
    while (input.value) { if (!demoOn) return; input.value = input.value.slice(0, -1); size(); await sleep(24); }
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
  const stopDemo = () => { demoOn = false; input.placeholder = L.placeholder; };

  function pick(q) { stopDemo(); input.value = q; size(); show(q, true); }
  document.addEventListener("click", e => {
    const b = e.target.closest("[data-q]");
    if (b) pick(b.dataset.q);
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

  show(input.value, true, true);
  size();
  (document.fonts ? document.fonts.ready : Promise.resolve()).then(size);
  addEventListener("resize", size);
  if (demoOn) demo();

  // ---------- Une journée avec Vivi : le bloc reste épinglé, chaque tranche de défilement montre le moment suivant ----------
  const day = $("journee");
  const track = day.querySelector(".day-track"), pin = day.querySelector(".day-pin");
  const items = [...day.querySelectorAll(".day-item")];
  const screens = [...day.querySelectorAll(".ds")];
  const dayVivis = [...day.querySelectorAll(".day-vivi img")];
  const dots = [...day.querySelectorAll(".day-dots span")];
  const bandTime = $("day-band-time"), bandLabel = $("day-band-label");
  let step = 0;
  function setStep(i) {
    if (i === step) return;
    step = i;
    day.dataset.step = i;
    items.forEach((el, k) => {
      el.classList.toggle("on", k === i);
      el.classList.toggle("done", k < i);
      el.querySelector("button").setAttribute("aria-pressed", String(k === i));
    });
    screens.forEach((el, k) => { el.classList.toggle("on", k === i); el.classList.toggle("before", k < i); });
    dayVivis.forEach((el, k) => el.classList.toggle("on", k === i));
    dots.forEach((el, k) => { el.classList.toggle("on", k === i); el.classList.toggle("done", k < i); });
    bandTime.textContent = items[i].dataset.time;
    bandLabel.textContent = items[i].dataset.label;
  }
  // progression dans le bloc épinglé : 0 quand il se fixe, 1 quand il se libère
  function measureTrack() {
    const total = track.offsetHeight - pin.offsetHeight;
    const pinTop = parseFloat(getComputedStyle(pin).top) || 0;
    return { total, pinTop, start: track.getBoundingClientRect().top + scrollY - pinTop };
  }
  let dayRaf = 0;
  function onDayScroll() {
    if (dayRaf) return;
    dayRaf = requestAnimationFrame(() => {
      dayRaf = 0;
      const { total, start } = measureTrack();
      if (total <= 0) return;
      const p = Math.min(1, Math.max(0, (scrollY - start) / total));
      setStep(Math.min(items.length - 1, Math.floor(p * items.length)));
    });
  }
  // un clic sur un moment fait défiler la page jusqu'à sa tranche
  items.forEach((el, i) => el.querySelector("button").addEventListener("click", () => {
    const { total, start } = measureTrack();
    if (total <= 0) { setStep(i); return; }
    scrollTo({ top: start + total * ((i + 0.5) / items.length), behavior: reduce ? "auto" : "smooth" });
  }));
  addEventListener("scroll", onDayScroll, { passive: true });
  addEventListener("resize", onDayScroll);
  onDayScroll();

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
