// Dancing with the SARS: The Hidden Steps. One static page, no build step.
// Pinned libraries: maplibre-gl 6.18.0 (ES module), pmtiles 4.5.0 (global `pmtiles`,
// loaded by index.html) and @maplibre/maplibre-gl-compare 0.5.0 (loaded on step 2;
// it attaches itself to window.maplibregl).
// Every result number comes from data/results.json; until a value exists it reads "not available".

// maplibre is imported dynamically so the data files and the first tile header
// load in parallel with it instead of after it.
const mlModule = import('https://cdn.jsdelivr.net/npm/maplibre-gl@6.18.0/dist/maplibre-gl.mjs');

const VERSIONS = { 'maplibre-gl': '6.18.0', pmtiles: '4.5.0', '@maplibre/maplibre-gl-compare': '0.5.0' };
const COMPARE_JS = 'https://cdn.jsdelivr.net/npm/@maplibre/maplibre-gl-compare@0.5.0/dist/maplibre-gl-compare.js';
const BASEMAP = 'https://tiles.openfreemap.org/styles/positron';
const NSTEPS = 5;
const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

// Set in main(). The compare plugin is a classic script that looks for a global
// `maplibregl` object; a module namespace cannot be extended, so it gets a plain copy.
let maplibregl = null;

const params = new URLSearchParams(location.search);
const VIDEO = params.get('video') === '1';
const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
const phone = window.matchMedia('(max-width: 760px)');

const api = (window.__dwts = {
  versions: VERSIONS,
  firstDrawMs: null,
  styleLoadMs: null,
  step: null,
  ready: false,
  missing: [],
  errors: [],
  videoReady: false,
  videoDone: false,
});

const S = {
  steps: null,
  layersCfg: null,
  defs: {},
  avail: {},
  results: null,
  current: null,
  lastStep: 1,
  gen: 0,
  exploreOn: null,
  checkMode: null,
  muted: false,
  sample: null,
  timeline: null,
  videoSlider: null,
  viewOverride: null,
};

let map = null;
let mapB = null;
let mapBReady = null;
let compare = null;
let tapMarker = null;
let pins = [];
let audio = null;
let SOUND = null;

const protocol = new pmtiles.Protocol();

// ---------- small helpers ----------

const $ = (sel) => document.querySelector(sel);

function el(tag, attrs, ...kids) {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (v == null || v === false) continue;
    if (k === 'class') e.className = v;
    else if (k === 'text') e.textContent = v;
    else if (k === 'html') e.innerHTML = v;
    else if (k.startsWith('on') && typeof v === 'function') e.addEventListener(k.slice(2), v);
    else e.setAttribute(k, v === true ? '' : v);
  }
  for (const kid of kids.flat()) {
    if (kid == null || kid === false) continue;
    e.append(kid.nodeType ? kid : document.createTextNode(String(kid)));
  }
  return e;
}

const SVGNS = 'http://www.w3.org/2000/svg';
function sv(tag, attrs, ...kids) {
  const e = document.createElementNS(SVGNS, tag);
  for (const [k, v] of Object.entries(attrs || {})) if (v != null) e.setAttribute(k, v);
  for (const kid of kids.flat()) if (kid != null) e.append(kid.nodeType ? kid : document.createTextNode(String(kid)));
  return e;
}

function note(err) {
  const msg = String((err && (err.message || err.error?.message)) || err);
  if (/abort/i.test(msg)) return;
  api.errors.push(msg);
}

async function getJSON(url) {
  try {
    const r = await fetch(url, { cache: 'no-cache' });
    if (!r.ok) return null;
    return await r.json();
  } catch (e) {
    return null;
  }
}

async function getText(url) {
  try {
    const r = await fetch(url, { cache: 'no-cache' });
    if (!r.ok) return null;
    return await r.text();
  } catch (e) {
    return null;
  }
}

function fmtDate(iso, withYear = true) {
  if (!iso) return '';
  const [y, m, d] = iso.split('-').map(Number);
  return `${d} ${MONTHS[m - 1]}${withYear ? ' ' + y : ''}`;
}

// ---------- numbers from results.json ----------

const isNum = (v) => typeof v === 'number' && Number.isFinite(v);
const real = (v) => isNum(v); // a missing value reads "not available"; a real 0 is shown as 0
const realCI = (ci) => Array.isArray(ci) && ci.length === 2 && ci.every(isNum);
const UTC_MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
function fmtPass(iso) {
  if (!iso) return 'not available';
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return 'not available';
  const hh = String(d.getUTCHours()).padStart(2, '0');
  const mm = String(d.getUTCMinutes()).padStart(2, '0');
  return `${d.getUTCDate()} ${UTC_MONTHS[d.getUTCMonth()]}, ${hh}:${mm} UTC`;
}
const minus = (s) => s.replace(/^-/, '−');
const f2 = (v) => minus((Math.abs(v) < 0.005 ? 0 : v).toFixed(2));
const km = (v) => minus(Math.round(v).toLocaleString('en-US'));

function numbers() {
  const R = S.results || {};
  const c1 = R.claim1 || {};
  const c1a = R.claim1a || {};
  const c2 = (R.claim2 || {}).vegetation || {};
  const P = {};

  const c2real = real(c2.excess_km2);
  P.claim2_ok = c2real && typeof c2.passes === 'boolean' ? c2.passes : null;
  P.claim2_km2 = c2real ? km(c2.excess_km2) : 'not available';
  P.claim2_ci = c2real && realCI(c2.ci95) ? `95% interval ${km(c2.ci95[0])} to ${km(c2.ci95[1])} km²` : '95% interval not available';
  P.claim2_line = `On low ground under trees, NISAR flagged ${P.claim2_km2} km² more flooding than in the 12 days before, where Sentinel-1 saw dry land.`;
  const passes = R.passes || {};
  const offs = R.time_offsets_h || {};
  const fg = R.failure_gallery || {};
  const pct = (a, b) => (isNum(a) && isNum(b) && b > 0 ? String(Math.round((100 * a) / b)) : 'not available');
  P.fail_dark_pct = pct(fg.referee_only_dark_on_16sep, fg.referee_only_px);
  P.fail_missed_px = isNum(fg.referee_only_px) ? fg.referee_only_px.toLocaleString('en-US') : 'not available';
  P.fail_flag_on_s1_water_pct = pct(fg.veg_flags_on_s1_water, fg.veg_flags_s1_known);
  P.s1_dark_pct = pct(fg.s1_referee_only_dark_on_17sep, fg.s1_referee_only_px);
  P.hidden_near_built_pct = pct(fg.hidden_near_builtup_px, fg.hidden_px);
  P.set_near_built_pct = pct(fg.claim2_set_near_builtup_px, fg.claim2_set_px);
  const crop = (R.claim2 || {}).cropland || {};
  P.crop_km2 = isNum(crop.excess_km2) ? km(crop.excess_km2) : 'not available';
  P.crop_ci = realCI(crop.ci95) ? `95% interval ${km(crop.ci95[0])} to ${km(crop.ci95[1])} km²` : '95% interval not available';
  P.nisar_post_time = fmtPass(passes.nisar_post);
  P.s1_post_time = fmtPass(passes.s1_post);
  P.s1_offset_h = isNum(offs.s1) ? String(Math.round(Math.abs(offs.s1))) : 'not available';
  P.claim2_line_fail = `On low ground under trees, NISAR flagged ${P.claim2_km2} km² more than in the 12 days before (${P.claim2_ci}), a range that includes zero, so this is not a clear signal.`;

  const n1 = c1.nisar_twosided?.f1;
  const s1 = c1.s1_twosided?.f1;
  const n1s = real(n1) ? f2(n1) : 'not available';
  const s1s = real(s1) ? f2(s1) : 'not available';
  P.claim1_line =
    c1.noninferior === true && real(n1) && real(s1)
      ? `On open water, NISAR keeps up with Sentinel-1: F1 ${n1s} for NISAR and ${s1s} for Sentinel-1, checked against optical satellites.`
      : `On open water: F1 ${n1s} for NISAR and ${s1s} for Sentinel-1, checked against optical satellites.`;
  P.claim1_diff =
    real(n1) && real(s1) && isNum(c1.diff) && realCI(c1.ci95)
      ? `The difference, NISAR minus Sentinel-1, is ${f2(c1.diff)} (95% interval ${f2(c1.ci95[0])} to ${f2(c1.ci95[1])}). ` +
        (c1.noninferior === true
          ? `Its lower end is at or above the ${f2(c1.margin)} margin fixed before the event, so NISAR passes the test of keeping up.`
          : `Its lower end is below the ${isNum(c1.margin) ? f2(c1.margin) : ''} margin fixed before the event, so NISAR failed the test of keeping up with Sentinel-1 on open water.`)
      : 'The difference, NISAR minus Sentinel-1, with its 95% interval: not available.';

  const a = c1a.nisar_twosided || {};
  const aF1 = real(a.f1) ? f2(a.f1) : 'not available';
  const aCI = real(a.f1) && realCI(a.ci95) ? `95% interval ${f2(a.ci95[0])} to ${f2(a.ci95[1])}` : '95% interval not available';
  P.claim1a_line = `NISAR alone, checked against the 29 Sep optical map in the west: F1 ${aF1} (${aCI}).`;
  if (isNum(c1a.diff) && realCI(c1a.ci95)) {
    const d3 = (v) => minus(v.toFixed(3));
    P.claim1a_line += ` Adding HV to HH changed F1 by ${d3(c1a.diff)} (95% interval ${d3(c1a.ci95[0])} to ${d3(c1a.ci95[1])})${c1a.passes ? ', a small but consistent gain' : ', not a clear gain'}.`;
  }
  return P;
}

function fill(template, P) {
  return String(template || '').replace(/\{(\w+)\}/g, (m, k) => (k in P ? P[k] : m));
}

// ---------- map setup ----------

function makeMap(container, view) {
  const m = new maplibregl.Map({
    container,
    style: BASEMAP,
    center: view.center,
    zoom: view.zoom,
    minZoom: 5,
    maxZoom: 14,
    pixelRatio: Math.min(window.devicePixelRatio || 1, 2),
    attributionControl: false,
    dragRotate: false,
    pitchWithRotate: false,
    touchPitch: false,
  });
  m.touchZoomRotate.disableRotation();
  m.keyboard.disableRotation();
  m.addControl(new maplibregl.AttributionControl({ compact: false }), 'bottom-right');
  m.on('error', (e) => note(e.error || e));
  m.on('click', onMapClick);
  return m;
}

function hatchImage() {
  const n = 12;
  const c = document.createElement('canvas');
  c.width = c.height = n;
  const g = c.getContext('2d');
  g.strokeStyle = 'rgba(60, 70, 80, 0.9)';
  g.lineWidth = 2;
  g.beginPath();
  for (let k = -n; k <= n; k += 6) {
    g.moveTo(k, n);
    g.lineTo(k + n, 0);
  }
  g.stroke();
  return g.getImageData(0, 0, n, n);
}

function rank(id) {
  if (id.startsWith('hh_')) return 10;
  if (id.startsWith('lr_')) return 20;
  if (id === 's1_twosided' || id === 'nisar_twosided') return 30;
  if (id === 'hidden') return 40;
  if (id === 'gaps') return 50;
  return 60;
}
const baseOf = (layerId) => layerId.slice(2).replace(/--line$/, '');
const layerIdsOf = (id) => (id === 'gaps' ? ['L-gaps', 'L-gaps--line'] : [`L-${id}`]);

function beforeId(m, id) {
  const r = rank(id);
  for (const l of m.getStyle().layers) {
    if (l.id.startsWith('L-')) {
      if (rank(baseOf(l.id)) > r) return l.id;
    } else if (l.type === 'symbol') {
      return l.id;
    }
  }
  return undefined;
}

// Checks a layer's PMTiles header once; a missing file is skipped quietly.
function probe(id) {
  if (!S.avail[id]) {
    const def = S.defs[id];
    S.avail[id] = !def
      ? Promise.resolve(false)
      : (async () => {
          try {
            const url = new URL(def.file, document.baseURI).href;
            const p = new pmtiles.PMTiles(url);
            await p.getHeader();
            protocol.add(p);
            def._url = url;
            return true;
          } catch (e) {
            api.missing.push(id);
            return false;
          }
        })();
  }
  return S.avail[id];
}

async function addRaster(m, id) {
  if (m.getLayer(`L-${id}`)) return true;
  if (!(await probe(id))) return false;
  if (m.getLayer(`L-${id}`)) return true;
  const def = S.defs[id];
  if (!m.getSource(`S-${id}`)) m.addSource(`S-${id}`, { type: 'raster', url: `pmtiles://${def._url}`, tileSize: 256 });
  m.addLayer(
    {
      id: `L-${id}`,
      type: 'raster',
      source: `S-${id}`,
      layout: { visibility: 'none' },
      paint: {
        'raster-opacity': 0,
        'raster-fade-duration': 0,
        'raster-resampling': def.kind === 'class' ? 'nearest' : 'linear',
      },
    },
    beforeId(m, id)
  );
  return true;
}

let gapsData = null;
async function addGaps(m) {
  if (m.getLayer('L-gaps')) return true;
  if (!gapsData) gapsData = getJSON('data/gaps.geojson');
  const data = await gapsData;
  if (!data || m.getLayer('L-gaps')) return !!data;
  if (!m.hasImage('hatch')) m.addImage('hatch', hatchImage());
  if (!m.getSource('S-gaps')) m.addSource('S-gaps', { type: 'geojson', data });
  const b = beforeId(m, 'gaps');
  m.addLayer({ id: 'L-gaps', type: 'fill', source: 'S-gaps', layout: { visibility: 'none' }, paint: { 'fill-pattern': 'hatch' } }, b);
  m.addLayer(
    { id: 'L-gaps--line', type: 'line', source: 'S-gaps', layout: { visibility: 'none' }, paint: { 'line-color': '#3c4650', 'line-width': 1 } },
    b
  );
  return true;
}

function setOpacity(m, id, op, fadeMs = 0) {
  for (const lid of layerIdsOf(id)) {
    const l = m.getLayer(lid);
    if (!l) continue;
    m.setLayoutProperty(lid, 'visibility', 'visible');
    if (l.type === 'raster') {
      m.setPaintProperty(lid, 'raster-opacity-transition', { duration: fadeMs, delay: 0 });
      m.setPaintProperty(lid, 'raster-opacity', op);
    }
  }
}

// Shows exactly the layers in `wanted` ({id: opacity}) and hides the others.
async function setLayers(m, wanted, fadeMs = 0) {
  m.__gen = (m.__gen || 0) + 1;
  const gen = m.__gen;
  const keep = new Set(Object.keys(wanted));
  for (const l of m.getStyle().layers) {
    if (l.id.startsWith('L-') && !keep.has(baseOf(l.id))) m.setLayoutProperty(l.id, 'visibility', 'none');
  }
  await Promise.all(Object.keys(wanted).map((id) => (id === 'gaps' ? addGaps(m) : addRaster(m, id))));
  if (gen !== m.__gen) return false;
  for (const [id, op] of Object.entries(wanted)) setOpacity(m, id, op, fadeMs);
  return true;
}

function waitIdle(m, ms = 8000) {
  return new Promise((resolve) => {
    let done = false;
    const fin = (v) => {
      if (done) return;
      done = true;
      clearTimeout(timer);
      m.off('idle', on);
      resolve(v);
    };
    const on = () => fin(true);
    const timer = setTimeout(() => fin(false), ms);
    m.on('idle', on);
    m.triggerRepaint();
  });
}

function padding() {
  const card = $('#card');
  return phone.matches ? { top: 0, left: 0, right: 0, bottom: Math.round(card.getBoundingClientRect().height) } : { top: 0, left: 0, right: 0, bottom: 0 };
}

function flyTo(view, instant = false) {
  if (!view || !view.center) return;
  const opts = { center: view.center, zoom: view.zoom ?? map.getZoom(), padding: padding() };
  if (instant || reduceMotion.matches) map.jumpTo(opts);
  else map.flyTo({ ...opts, duration: VIDEO ? S.timeline?.fly_ms ?? 600 : 1400, essential: true });
}

// ---------- ripple and taps ----------

function ripple(x, y) {
  const r = el('div', { class: 'ripple' });
  r.style.left = `${x}px`;
  r.style.top = `${y}px`;
  $('#maps').append(r);
  const kill = () => r.remove();
  r.addEventListener('animationend', kill);
  setTimeout(kill, 1500);
}

function onMapClick(e) {
  ripple(e.point.x, e.point.y);
  if (S.current === 4) tapAt(e.lngLat.lng, e.lngLat.lat);
}

// ---------- routing ----------

function parseHash() {
  const h = location.hash.replace(/^#/, '');
  if (h === 'explore') return 'explore';
  const m = h.match(/step=(\d+)/);
  if (m) {
    const n = Number(m[1]);
    if (n >= 1 && n <= NSTEPS) return n;
  }
  return 1;
}

function nav(target) {
  const h = target === 'explore' ? '#explore' : `#step=${target}`;
  if (location.hash === h) go(target, { force: true });
  else location.hash = h;
}

function leave(prev) {
  stopDance();
  stopSound();
  exitCompare();
  $('#date-badge').hidden = true;
  $('#maps').classList.remove('with-badge');
  $('#mute').hidden = true;
  $('#maps').classList.remove('with-mute');
  $('#endcard').hidden = true;
  if (tapMarker) {
    tapMarker.remove();
    tapMarker = null;
  }
  for (const p of pins) p.remove();
  pins = [];
}

async function go(target, opts = {}) {
  if (S.current === target && !opts.force) return;
  const prev = S.current;
  S.current = target;
  S.gen += 1;
  api.step = target;
  if (target !== 'explore') S.lastStep = target;
  leave(prev);
  renderNav();
  try {
    if (target === 'explore') {
      await enterExplore();
    } else {
      const st = S.steps.steps[target - 1];
      renderCard(st);
      const view = S.viewOverride || st.view;
      S.viewOverride = null;
      flyTo(view, prev == null || opts.instant === true);
      await enterStep(st);
    }
  } catch (e) {
    note(e);
  }
  markFirstDraw();
  api.ready = true;
}

function renderNav() {
  const cur = S.current;
  const inTour = cur !== 'explore';
  $('#btn-back').disabled = inTour && cur === 1;
  $('#btn-next').disabled = !inTour;
  $('#btn-explore').setAttribute('aria-pressed', String(!inTour));
  $('#btn-explore').textContent = inTour ? 'Explore' : 'Tour';
  for (const b of document.querySelectorAll('#dots button')) {
    if (Number(b.dataset.n) === cur) b.setAttribute('aria-current', 'step');
    else b.removeAttribute('aria-current');
  }
}

function setupNav() {
  const dots = $('#dots');
  for (let n = 1; n <= NSTEPS; n++) {
    dots.append(el('button', { type: 'button', 'data-n': n, 'aria-label': `Step ${n}`, onclick: () => nav(n) }));
  }
  $('#btn-back').addEventListener('click', () => nav(S.current === 'explore' ? S.lastStep : Math.max(1, S.current - 1)));
  $('#btn-next').addEventListener('click', () => {
    if (S.current === 'explore') return;
    nav(S.current >= NSTEPS ? 'explore' : S.current + 1);
  });
  $('#btn-explore').addEventListener('click', () => nav(S.current === 'explore' ? S.lastStep : 'explore'));
  window.addEventListener('keydown', (e) => {
    if (VIDEO || e.altKey || e.ctrlKey || e.metaKey) return;
    if (/input|select|textarea/i.test(document.activeElement?.tagName || '')) return;
    if (e.key === 'ArrowRight' && S.current !== 'explore') $('#btn-next').click();
    if (e.key === 'ArrowLeft') $('#btn-back').click();
  });
  window.addEventListener('hashchange', () => {
    if (!VIDEO) go(parseHash());
  });
}

function setupSheet() {
  const card = $('#card');
  const handle = $('#card-handle');
  const setExpanded = (on) => {
    card.classList.toggle('expanded', on);
    handle.setAttribute('aria-expanded', String(on));
    handle.setAttribute('aria-label', on ? 'Show less of the card' : 'Show more of the card');
  };
  handle.addEventListener('click', () => setExpanded(!card.classList.contains('expanded')));
  let y0 = null;
  for (const t of [handle, $('#card-head')]) {
    t.addEventListener('touchstart', (e) => (y0 = e.touches[0].clientY), { passive: true });
    t.addEventListener(
      'touchend',
      (e) => {
        if (y0 == null) return;
        const dy = e.changedTouches[0].clientY - y0;
        y0 = null;
        if (dy < -30) setExpanded(true);
        else if (dy > 30) setExpanded(false);
      },
      { passive: true }
    );
  }
  const ro = new ResizeObserver(() => {
    const h = phone.matches ? Math.round(card.getBoundingClientRect().height) : 0;
    document.documentElement.style.setProperty('--card-h', `${h}px`);
  });
  ro.observe(card);
}

// ---------- card ----------

function renderLegend(items) {
  const L = $('#legend');
  L.replaceChildren();
  if (!items || !items.length) {
    L.hidden = true;
    return;
  }
  for (const it of items) L.append(el('div', { class: 'row' }, swatch(it), el('span', { text: it.label })));
  L.hidden = false;
}

function swatch(it) {
  if (it.gradient) return el('span', { class: 'sw grad', style: `background: linear-gradient(90deg, ${it.gradient.join(', ')})` });
  if (it.hatch) return el('span', { class: 'sw hatch' });
  if (it.outline) return el('span', { class: 'sw outline', style: `border-color: ${it.outline}` });
  return el('span', { class: 'sw', style: `background: ${it.color}` });
}

function renderCard(st) {
  const P = numbers();
  const failMode = !!st.fail && P.claim2_ok === false;
  $('#step-num').textContent = `Step ${st.n} of ${NSTEPS}`;
  $('#card-title').textContent = failMode ? st.fail.title : st.title;
  $('#card-text').textContent = fill(failMode ? st.fail.text : st.text, P);
  const box = $('#card-extras');
  box.replaceChildren();
  const ex = st.extras || {};
  if (ex.type === 'dance') box.append(...danceControls(ex));
  if (ex.type === 'hidden') box.append(...hiddenExtras(ex, P, failMode));
  if (ex.type === 'listen') box.append(...listenExtras(ex));
  if (ex.type === 'check') box.append(...checkExtras(ex, P));
  renderLegend(st.legend);
  $('#card-body').scrollTop = 0;
}

function renderAbout() {
  const a = S.steps.about || {};
  $('#about').replaceChildren(
    el('p', {}, el('strong', { text: a.title })),
    el('p', { text: a.line }),
    el(
      'p',
      {},
      el('a', { href: a.repo, target: '_blank', rel: 'noopener' }, 'Code on GitHub'),
      ' · ',
      el('a', { href: a.ai_use, target: '_blank', rel: 'noopener' }, 'AI use')
    ),
    el('p', { text: a.basemap })
  );
}

// ---------- step 1: the dance ----------

const dance = { ids: [], timer: null, k: 0 };

function danceControls(ex) {
  if (reduceMotion.matches && !VIDEO) {
    const input = el('input', { type: 'range', min: 0, max: Math.max(0, ex.dates.length - 1), step: 1, value: 0, id: 'date-range' });
    input.addEventListener('input', () => showDate(Number(input.value), 0));
    return [el('div', { class: 'date-slider' }, el('label', { for: 'date-range', text: ex.slider_label }), input)];
  }
  const btn = el('button', { type: 'button', class: 'btn replay', id: 'replay', disabled: true, text: ex.replay_label });
  btn.addEventListener('click', () => playDance(ex.ms_per_date, ex.fade_ms));
  return [el('div', { class: 'btn-row' }, btn)];
}

function showBadge(id) {
  const d = S.defs[id]?.date;
  const b = $('#date-badge');
  if (!d) {
    b.hidden = true;
    return;
  }
  b.replaceChildren(el('small', { text: 'NISAR radar' }), fmtDate(d));
  b.hidden = false;
  $('#maps').classList.add('with-badge');
}

function showDate(k, fadeMs) {
  const ids = dance.ids;
  if (!ids.length) return;
  k = Math.max(0, Math.min(ids.length - 1, k));
  const prevK = dance.k;
  dance.k = k;
  if (fadeMs > 0 && k > prevK) {
    // fade the newer (upper) layer in over the older one, then drop the older one
    setOpacity(map, ids[k], 1, fadeMs);
    const gen = S.gen;
    setTimeout(() => {
      if (S.gen !== gen || dance.k !== k) return;
      ids.forEach((id, i) => i !== k && setOpacity(map, id, 0, 0));
    }, fadeMs);
  } else {
    ids.forEach((id, i) => setOpacity(map, id, i === k ? 1 : 0, 0));
  }
  showBadge(ids[k]);
}

function stopDance() {
  if (dance.timer) clearInterval(dance.timer);
  dance.timer = null;
}

function playDance(ms, fadeMs) {
  stopDance();
  if (!dance.ids.length) return;
  const btn = $('#replay');
  if (btn) btn.disabled = true;
  dance.k = 0;
  showDate(0, 0);
  let k = 0;
  dance.timer = setInterval(() => {
    k += 1;
    if (k >= dance.ids.length) {
      stopDance();
      const b = $('#replay');
      if (b) b.disabled = false;
      return;
    }
    showDate(k, fadeMs);
  }, ms);
}

async function enterDance(st) {
  const gen = S.gen;
  const ex = st.extras;
  const ids = ex.dates;
  // One layer first, so the first view draws fast; the other dates load after that.
  await setLayers(map, { [ids[0]]: 1 });
  if (gen !== S.gen) return;
  showBadge(ids[0]);
  markFirstDraw();
  await firstDraw;
  if (gen !== S.gen) return;
  await setLayers(map, Object.fromEntries(ids.map((id, i) => [id, i === 0 ? 1 : 0])));
  if (gen !== S.gen) return;
  dance.ids = ids.filter((id) => map.getLayer(`L-${id}`));
  dance.k = 0;
  resolveDanceLayers();
  if (!dance.ids.length) {
    $('#date-badge').hidden = true;
    return;
  }
  if (reduceMotion.matches && !VIDEO) {
    const r = $('#date-range');
    if (r) r.max = String(dance.ids.length - 1);
    return;
  }
  await waitIdle(map, 6000);
  if (gen !== S.gen) return;
  if (VIDEO) return; // the storyboard starts the dance at its own time
  playDance(ex.ms_per_date, ex.fade_ms);
}

// ---------- step 2: two radars ----------

function styleReady(m) {
  return new Promise((resolve) => (m.isStyleLoaded() ? resolve() : m.once('style.load', resolve)));
}

function ensureMapB() {
  if (!mapB) {
    mapB = makeMap('map-b', { center: map.getCenter().toArray(), zoom: map.getZoom() });
    mapBReady = styleReady(mapB);
  }
  return mapBReady;
}

let comparePromise = null;
function loadCompare() {
  if (!comparePromise) {
    comparePromise = new Promise((resolve) => {
      const s = el('script', { src: COMPARE_JS, crossorigin: 'anonymous' });
      s.onload = () => resolve(window.maplibregl.Compare || SimpleCompare);
      s.onerror = () => resolve(SimpleCompare);
      document.head.append(s);
    });
  }
  return comparePromise;
}

// Fallback slider with the same API as the plugin, used only if the plugin fails to load.
class SimpleCompare {
  constructor(a, b, container) {
    this._a = a;
    this._b = b;
    this._box = typeof container === 'string' ? document.querySelector(container) : container;
    this._ctl = el('div', { class: 'maplibregl-compare' }, el('div', { class: 'compare-swiper-vertical' }));
    this._box.append(this._ctl);
    this._sync = (src, dst) => () => {
      if (this._lock) return;
      this._lock = true;
      dst.jumpTo({ center: src.getCenter(), zoom: src.getZoom(), bearing: src.getBearing(), pitch: src.getPitch() });
      this._lock = false;
    };
    this._ab = this._sync(a, b);
    this._ba = this._sync(b, a);
    a.on('move', this._ab);
    b.on('move', this._ba);
    const down = (e) => {
      e.preventDefault();
      const move = (ev) => {
        const x = (ev.touches ? ev.touches[0].clientX : ev.clientX) - this._box.getBoundingClientRect().left;
        this.setSlider(x);
      };
      const up = () => {
        document.removeEventListener('mousemove', move);
        document.removeEventListener('touchmove', move);
        document.removeEventListener('mouseup', up);
        document.removeEventListener('touchend', up);
      };
      document.addEventListener('mousemove', move);
      document.addEventListener('touchmove', move, { passive: true });
      document.addEventListener('mouseup', up);
      document.addEventListener('touchend', up);
    };
    this._ctl.firstChild.addEventListener('mousedown', down);
    this._ctl.firstChild.addEventListener('touchstart', down);
    this.setSlider(this._box.clientWidth / 2);
  }
  setSlider(x) {
    const w = this._box.clientWidth;
    x = Math.max(0, Math.min(w, x));
    this.currentPosition = x;
    this._ctl.style.transform = `translate(${x}px, 0)`;
    this._b.getContainer().style.clip = `rect(0, 999em, ${this._box.clientHeight}px, ${x}px)`;
  }
  remove() {
    this._a.off('move', this._ab);
    this._b.off('move', this._ba);
    this._ctl.remove();
  }
}

async function enterCompare(st) {
  const gen = S.gen;
  const ex = st.extras;
  $('#side-left-name').textContent = ex.left.label;
  $('#side-left-time').textContent = fill(ex.left.time, numbers());
  $('#side-right-name').textContent = ex.right.label;
  $('#side-right-time').textContent = fill(ex.right.time, numbers());
  $('#side-labels').hidden = false;
  $('#maps').classList.add('comparing');
  const left = setLayers(map, ex.left.layers);
  await ensureMapB();
  if (gen !== S.gen) return;
  $('#map-b').classList.add('on');
  mapB.resize();
  const right = setLayers(mapB, ex.right.layers);
  const Compare = await loadCompare();
  await Promise.all([left, right]);
  if (gen !== S.gen) return;
  mapB.setPadding(map.getPadding());
  mapB.jumpTo({ center: map.getCenter(), zoom: map.getZoom(), bearing: 0, pitch: 0 });
  try {
    compare = new Compare(map, mapB, '#maps', {});
  } catch (e) {
    note(e);
    compare = new SimpleCompare(map, mapB, '#maps');
  }
  const frac = VIDEO && S.videoSlider != null ? S.videoSlider : ex.slider_start ?? 0.5;
  setSliderFrac(frac);
}

function setSliderFrac(frac) {
  if (!compare) return;
  compare.setSlider(Math.round(frac * $('#maps').clientWidth));
}

function exitCompare() {
  if (compare) {
    try {
      compare.remove();
    } catch (e) {
      note(e);
    }
    compare = null;
  }
  $('#side-labels').hidden = true;
  $('#maps').classList.remove('comparing');
  const b = $('#map-b');
  b.classList.remove('on');
  b.style.clip = '';
}

// ---------- step 3: the hidden steps ----------

function diagramMirror() {
  return `<svg viewBox="0 0 160 120" role="img" aria-label="Diagram: the radar beam hits flat open water and bounces away, so little comes back.">
  <defs><marker id="arrA" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#14202b"/></marker>
  <marker id="arrA2" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#8a949c"/></marker></defs>
  <rect x="8" y="12" width="12" height="9" rx="1.5" fill="#56616b"/><rect x="-2" y="14" width="9" height="5" fill="#0b2a43"/><rect x="21" y="14" width="9" height="5" fill="#0b2a43"/>
  <text x="14" y="32" font-size="8" text-anchor="middle" fill="#14202b">radar</text>
  <line x1="22" y1="24" x2="76" y2="90" stroke="#14202b" stroke-width="2" marker-end="url(#arrA)"/>
  <line x1="80" y1="92" x2="140" y2="34" stroke="#14202b" stroke-width="2" marker-end="url(#arrA)"/>
  <line x1="80" y1="92" x2="66" y2="76" stroke="#8a949c" stroke-width="1.2" stroke-dasharray="2 2" marker-end="url(#arrA2)"/>
  <rect x="0" y="92" width="160" height="28" fill="#0072B2"/>
  <line x1="0" y1="92" x2="160" y2="92" stroke="#bfe1f5" stroke-width="1.5"/>
  <text x="80" y="110" font-size="9" font-weight="700" text-anchor="middle" fill="#fff">HH dark, HV dark</text>
</svg>`;
}

function diagramDoubleBounce() {
  return `<svg viewBox="0 0 160 120" role="img" aria-label="Diagram: the radar beam bounces off water under a tree onto the trunk and straight back to the radar.">
  <defs><marker id="arrB" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#14202b"/></marker>
  <marker id="arrB2" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#E69F00"/></marker></defs>
  <rect x="8" y="12" width="12" height="9" rx="1.5" fill="#56616b"/><rect x="-2" y="14" width="9" height="5" fill="#0b2a43"/><rect x="21" y="14" width="9" height="5" fill="#0b2a43"/>
  <text x="14" y="32" font-size="8" text-anchor="middle" fill="#14202b">radar</text>
  <rect x="112" y="46" width="9" height="50" fill="#7a5230"/>
  <circle cx="116" cy="38" r="20" fill="#4f7d3a" opacity="0.85"/>
  <circle cx="102" cy="46" r="11" fill="#4f7d3a" opacity="0.85"/>
  <line x1="22" y1="24" x2="88" y2="92" stroke="#14202b" stroke-width="2" marker-end="url(#arrB)"/>
  <line x1="90" y1="93" x2="110" y2="78" stroke="#14202b" stroke-width="2" marker-end="url(#arrB)"/>
  <line x1="111" y1="76" x2="30" y2="25" stroke="#E69F00" stroke-width="3.2" marker-end="url(#arrB2)"/>
  <rect x="0" y="94" width="160" height="26" fill="#0072B2"/>
  <line x1="0" y1="94" x2="160" y2="94" stroke="#bfe1f5" stroke-width="1.5"/>
  <text x="80" y="111" font-size="9" font-weight="700" text-anchor="middle" fill="#fff">HH bright, HV much less</text>
</svg>`;
}

function hiddenExtras(ex, P, failMode) {
  const out = [];
  out.push(el('p', {}, el('span', { class: 'badge-veg', text: ex.badge })));
  if (!failMode) out.push(el('p', { class: 'interval', text: P.claim2_ci }));
  const svgs = { mirror: diagramMirror(), 'double-bounce': diagramDoubleBounce() };
  out.push(
    el(
      'div',
      { class: 'diagrams' },
      ex.diagrams.map((d) =>
        el('figure', { class: 'diagram' }, el('div', { html: svgs[d.id] || '' }), el('figcaption', {}, d.caption, el('span', { class: 'ai-note', text: ex.diagram_note })))
      )
    )
  );
  out.push(el('details', { class: 'more' }, el('summary', { text: ex.more_title }), el('p', { text: fill(ex.more, numbers()) })));
  return out;
}

// ---------- step 4: listen ----------

function listenExtras(ex) {
  const out = [];
  const chart = el('div', { class: 'chart-box', id: 'chart-box' }, el('p', { class: 'hint', text: ex.prompt }));
  out.push(chart);
  const btn = el('button', { type: 'button', class: 'btn primary', id: 'listen', disabled: true }, 'Listen');
  btn.addEventListener('click', onListen);
  out.push(el('div', { class: 'btn-row', id: 'listen-row' }, btn));
  const places = (ex.places || []).filter((p) => isNum(p.lon) && isNum(p.lat));
  if (places.length) {
    out.push(
      el(
        'div',
        { class: 'places' },
        el('h3', { text: ex.places_title }),
        el(
          'div',
          { class: 'btn-row' },
          places.map((p) => el('button', { type: 'button', class: 'btn', onclick: () => goPlace(p) }, p.name))
        )
      )
    );
  }
  return out;
}

function goPlace(p) {
  const gen = S.gen;
  const view = { center: [p.lon, p.lat], zoom: p.zoom || 12 };
  flyTo(view);
  map.once('moveend', () => {
    if (gen !== S.gen) return;
    const pt = map.project([p.lon, p.lat]);
    ripple(pt.x, pt.y);
    tapAt(p.lon, p.lat);
  });
}

let listenIndex = null;
function loadListen() {
  if (!listenIndex) listenIndex = getJSON('data/listen/index.json');
  return listenIndex;
}
const chunkCache = new Map();

// WGS84 to UTM (northern hemisphere), Snyder's Transverse Mercator series; error well under a metre here.
function utmForward(lon, lat, zone) {
  const a = 6378137;
  const f = 1 / 298.257223563;
  const k0 = 0.9996;
  const e2 = f * (2 - f);
  const ep2 = e2 / (1 - e2);
  const e4 = e2 * e2;
  const e6 = e4 * e2;
  const rad = Math.PI / 180;
  const phi = lat * rad;
  const lam0 = ((zone - 1) * 6 - 180 + 3) * rad;
  const sin = Math.sin(phi);
  const cos = Math.cos(phi);
  const tan = Math.tan(phi);
  const N = a / Math.sqrt(1 - e2 * sin * sin);
  const T = tan * tan;
  const C = ep2 * cos * cos;
  const A = cos * (lon * rad - lam0);
  const M =
    a *
    ((1 - e2 / 4 - (3 * e4) / 64 - (5 * e6) / 256) * phi -
      ((3 * e2) / 8 + (3 * e4) / 32 + (45 * e6) / 1024) * Math.sin(2 * phi) +
      ((15 * e4) / 256 + (45 * e6) / 1024) * Math.sin(4 * phi) -
      ((35 * e6) / 3072) * Math.sin(6 * phi));
  const x = k0 * N * (A + ((1 - T + C) * A ** 3) / 6 + ((5 - 18 * T + T * T + 72 * C - 58 * ep2) * A ** 5) / 120) + 500000;
  let y = k0 * (M + N * tan * ((A * A) / 2 + ((5 - T + 9 * C + 4 * C * C) * A ** 4) / 24 + ((61 - 58 * T + T * T + 600 * C - 330 * ep2) * A ** 6) / 720));
  if (lat < 0) y += 10000000;
  return [x, y];
}

async function sampleAt(lon, lat) {
  const ix = await loadListen();
  if (!ix) return { status: 'nogrid' };
  const [x, y] = utmForward(lon, lat, ix.utm_zone || 44);
  const i = Math.floor((x - ix.x0) / ix.cell);
  const j = Math.floor((ix.y0 - y) / ix.cell);
  if (i < 0 || j < 0 || i >= ix.width || j >= ix.height) return { status: 'outside' };
  const C = ix.chunk;
  const col = Math.floor(i / C);
  const row = Math.floor(j / C);
  const key = `${col}_${row}`;
  if (!(ix.chunks || []).includes(key)) return { status: 'nodata' };
  if (!chunkCache.has(key)) {
    chunkCache.set(
      key,
      fetch(`data/listen/${key}.bin`)
        .then((r) => (r.ok ? r.arrayBuffer() : null))
        .catch(() => null)
    );
  }
  const ab = await chunkCache.get(key);
  if (!ab) return { status: 'nodata' };
  const u8 = new Uint8Array(ab);
  const D = ix.dates.length;
  const Ch = ix.channels.length;
  let w = C;
  let h = C;
  if (u8.length !== D * Ch * C * C) {
    w = Math.min(C, ix.width - col * C);
    h = Math.min(C, ix.height - row * C);
    if (u8.length !== D * Ch * w * h) return { status: 'nodata' };
  }
  const ci = i - col * C;
  const cj = j - row * C;
  const nodata = ix.nodata ?? 255;
  const bytes = {};
  ix.channels.forEach((ch, c) => {
    bytes[ch] = ix.dates.map((_, d) => {
      const v = u8[((d * Ch + c) * h + cj) * w + ci];
      return v === nodata ? null : v;
    });
  });
  const any = Object.values(bytes).some((arr) => arr.some((v) => v != null));
  return { status: any ? 'ok' : 'nodata', bytes, dates: ix.dates, flood: ix.flood_date, lon, lat, cell: [i, j] };
}

const decode = (b) => b / 4 - 40;

async function tapAt(lon, lat) {
  const gen = S.gen;
  if (tapMarker) tapMarker.remove();
  tapMarker = new maplibregl.Marker({ element: el('div', { class: 'tap-marker' }) }).setLngLat([lon, lat]).addTo(map);
  stopSound();
  const s = await sampleAt(lon, lat);
  if (gen !== S.gen) return s;
  S.sample = s.status === 'ok' ? s : null;
  api.lastSample = s;
  const box = $('#chart-box');
  if (!box) return s;
  const msg = {
    nogrid: 'The listening grid is still being computed. Try again later.',
    outside: 'No radar data here. Tap inside the area NISAR imaged.',
    nodata: 'No radar data at this spot. Try a spot nearby.',
  };
  if (s.status !== 'ok') {
    box.replaceChildren(el('p', { class: 'hint', text: msg[s.status] || msg.nodata }));
  } else {
    box.replaceChildren(drawChart(s), el('p', { class: 'where', text: `Cell at ${lat.toFixed(4)}° N, ${lon.toFixed(4)}° E, about 240 m across.` }));
  }
  const btn = $('#listen');
  if (btn) btn.disabled = !S.sample;
  return s;
}

function drawChart(s) {
  const W = 320;
  const H = 172;
  const m = { l: 34, r: 24, t: 18, b: 28 };
  const n = s.dates.length;
  const x = (k) => m.l + ((W - m.l - m.r) * (n === 1 ? 0.5 : k / (n - 1)));
  const lo = -35;
  const hi = 0;
  const y = (db) => m.t + ((H - m.t - m.b) * (hi - Math.max(lo, Math.min(hi, db)))) / (hi - lo);
  const root = sv('svg', { viewBox: `0 0 ${W} ${H}`, class: 'chart', role: 'img' });
  const summary = ['hh', 'hv']
    .filter((c) => s.bytes[c])
    .map((c) => `${c.toUpperCase()}: ${s.bytes[c].map((b, k) => `${fmtDate(s.dates[k], false)} ${b == null ? 'no data' : decode(b).toFixed(1) + ' dB'}`).join(', ')}`)
    .join('. ');
  root.setAttribute('aria-label', `Radar signal at the tapped spot over seven dates. ${summary}.`);

  const grid = sv('g', { class: 'grid' });
  for (const v of [-30, -20, -10, 0]) {
    grid.append(sv('line', { x1: m.l, x2: W - m.r, y1: y(v), y2: y(v) }));
    grid.append(sv('text', { x: m.l - 5, y: y(v) + 3, 'text-anchor': 'end' }, minus(String(v))));
  }
  grid.append(sv('text', { x: m.l - 5, y: m.t - 7, 'text-anchor': 'end' }, 'dB'));
  root.append(grid);

  const fk = s.dates.indexOf(s.flood);
  if (fk >= 0) {
    root.append(
      sv(
        'g',
        { class: 'flood' },
        sv('line', { x1: x(fk), x2: x(fk), y1: m.t - 4, y2: H - m.b }),
        sv('text', { x: x(fk), y: m.t - 7, 'text-anchor': 'middle' }, `Flood, ${fmtDate(s.flood, false)}`)
      )
    );
  }
  // the 6 Jul to 23 Aug gap is longer than 12 days: mark the break on the axis
  if (n > 1) {
    const xb = (x(0) + x(1)) / 2;
    root.append(sv('text', { x: xb, y: H - m.b + 4, 'text-anchor': 'middle', class: 'xlab' }, '//'));
  }
  s.dates.forEach((d, k) => root.append(sv('text', { x: x(k), y: H - 8, 'text-anchor': 'middle', class: 'xlab' }, fmtDate(d, false))));

  const play = sv('line', { class: 'playhead', x1: x(0), x2: x(0), y1: m.t, y2: H - m.b });
  root.append(play);

  for (const ch of ['hv', 'hh']) {
    const arr = s.bytes[ch];
    if (!arr) continue;
    const g = sv('g', { class: ch });
    let d = '';
    let pen = false;
    arr.forEach((b, k) => {
      if (b == null) {
        pen = false;
        return;
      }
      d += `${pen ? 'L' : 'M'}${x(k).toFixed(1)} ${y(decode(b)).toFixed(1)}`;
      pen = true;
    });
    g.append(sv('path', { d }));
    arr.forEach((b, k) => {
      if (b != null) g.append(sv('circle', { class: 'beat', 'data-k': k, cx: x(k), cy: y(decode(b)), r: 3.2 }));
    });
    let last = -1;
    arr.forEach((b, k) => b != null && (last = k));
    if (last >= 0) {
      g.append(
        sv('text', { class: 'lab', x: x(last) + 6, y: y(decode(arr[last])) + (ch === 'hh' ? -3 : 9), fill: ch === 'hh' ? '#14202b' : '#6b757e' }, ch.toUpperCase())
      );
    }
    root.append(g);
  }
  root.__x = x;
  return root;
}

async function loadSound() {
  if (!SOUND) SOUND = await getJSON('data/sound.json');
  return SOUND;
}

// The pitch and loudness of one note, exactly as the "mapping" string in sound.json says.
function noteFor(voice, db) {
  const v = SOUND.voices[voice];
  const sc = SOUND.scale;
  const x = Math.min(1, Math.max(0, (db - v.db_min) / (v.db_max - v.db_min)));
  const s = Math.min(sc.steps - 1, Math.floor(x * sc.steps));
  const n = sc.intervals.length;
  const midi = v.base_midi + 12 * Math.floor(s / n) + sc.intervals[s % n];
  return { midi, freq: 440 * 2 ** ((midi - 69) / 12), gain: v.gain_min + (v.gain_max - v.gain_min) * x };
}

function stopSound() {
  if (!audio) return;
  for (const o of audio.nodes) {
    try {
      o.stop();
    } catch (e) {
      /* already stopped */
    }
  }
  audio.nodes = [];
  if (audio.raf) cancelAnimationFrame(audio.raf);
  audio.raf = null;
  const ph = document.querySelector('.chart .playhead');
  if (ph) ph.classList.remove('on');
  const btn = $('#listen');
  if (btn && S.sample) {
    btn.textContent = 'Listen';
    btn.disabled = false;
  }
}

async function onListen() {
  if (!S.sample) return;
  if (audio && audio.nodes.length) {
    stopSound();
    return;
  }
  if (!(await loadSound())) return;
  const AC = window.AudioContext || window.webkitAudioContext;
  if (!AC) return;
  if (!audio) {
    // created only here, on the user's click
    const ctx = new AC();
    const master = ctx.createGain();
    master.connect(ctx.destination);
    audio = { ctx, master, nodes: [], raf: null };
  }
  const { ctx, master } = audio;
  try {
    await ctx.resume();
  } catch (e) {
    note(e);
  }
  master.gain.value = S.muted ? 0 : SOUND.master_gain;
  const beat = SOUND.beat_s;
  const t0 = ctx.currentTime + SOUND.lead_in_s;
  const nodata = SOUND.nodata ?? 255;
  const nBeats = S.sample.dates.length;
  for (let k = 0; k < nBeats; k++) {
    for (const voice of Object.keys(SOUND.voices)) {
      const b = S.sample.bytes[voice]?.[k];
      if (b == null || b === nodata) continue;
      const v = SOUND.voices[voice];
      const nt = noteFor(voice, decode(b));
      const ts = t0 + k * beat;
      const osc = ctx.createOscillator();
      osc.type = v.waveform;
      osc.frequency.setValueAtTime(nt.freq, ts);
      const g = ctx.createGain();
      g.gain.setValueAtTime(0, ts);
      g.gain.linearRampToValueAtTime(nt.gain, ts + v.attack_s);
      g.gain.setTargetAtTime(0, ts + v.attack_s, v.decay_s / 5);
      osc.connect(g);
      g.connect(master);
      osc.start(ts);
      osc.stop(ts + v.attack_s + v.decay_s);
      audio.nodes.push(osc);
    }
  }
  const btn = $('#listen');
  if (btn) btn.textContent = 'Stop';
  const svg = document.querySelector('#chart-box svg.chart');
  const ph = svg && svg.querySelector('.playhead');
  const end = t0 + (nBeats - 1) * beat + 0.45;
  const tick = () => {
    const t = ctx.currentTime;
    if (t >= end) {
      stopSound();
      return;
    }
    const k = Math.max(0, Math.min(nBeats - 1, Math.floor((t - t0) / beat)));
    if (ph && svg.__x) {
      const xx = svg.__x(k);
      ph.setAttribute('x1', xx);
      ph.setAttribute('x2', xx);
      ph.classList.toggle('on', t >= t0);
    }
    if (svg) for (const c of svg.querySelectorAll('circle.beat')) c.setAttribute('r', Number(c.dataset.k) === k && t >= t0 ? 5 : 3.2);
    audio.raf = requestAnimationFrame(tick);
  };
  audio.raf = requestAnimationFrame(tick);
}

function setMuted(on) {
  S.muted = on;
  const b = $('#mute');
  b.setAttribute('aria-pressed', String(on));
  $('#mute-label').textContent = on ? 'Muted' : 'Sound on';
  if (audio && SOUND) audio.master.gain.setTargetAtTime(on ? 0 : SOUND.master_gain, audio.ctx.currentTime, 0.02);
}

async function enterListen(st) {
  $('#mute').hidden = false;
  $('#maps').classList.add('with-mute');
  await setLayers(map, st.layers || {});
  loadListen();
  loadSound();
}

// ---------- step 5: how we know ----------

function checkExtras(ex, P) {
  const out = [];
  out.push(
    el(
      'div',
      { class: 'btn-row view-buttons' },
      (ex.views || []).map((v) => el('button', { type: 'button', class: 'btn', onclick: () => flyTo(v) }, v.name))
    )
  );
  const seg = el('div', { class: 'seg', role: 'group', 'aria-label': 'Which change map' });
  for (const key of ['naive', 'trust']) {
    const m = ex.modes[key];
    seg.append(el('button', { type: 'button', 'data-mode': key, 'aria-pressed': 'false', onclick: () => setCheckMode(key) }, m.label));
  }
  out.push(seg);
  const claim2 = P.claim2_ok === false ? P.claim2_line_fail : `${P.claim2_line} (${P.claim2_ci}.)`;
  out.push(
    el(
      'div',
      { class: 'numbers' },
      el('h3', { text: ex.numbers_title }),
      el('p', { text: P.claim1_line }),
      el('p', { class: 'small', text: P.claim1_diff }),
      el('p', { text: P.claim1a_line }),
      el('p', { text: claim2 }),
      el('p', { class: 'small', text: ex.f1_note })
    )
  );
  if (Array.isArray(ex.failures) && ex.failures.length) {
    out.push(
      el(
        'div',
        { class: 'numbers failures' },
        el('h3', { text: ex.failures_title || 'Where NISAR got it wrong' }),
        ex.failures.map((f) => el('p', {}, el('strong', { text: f.title + ' ' }), el('span', { text: fill(f.text, P) })))
      )
    );
  }
  out.push(el('div', { class: 'limits' }, el('h3', { text: ex.limits.title }), el('ul', {}, ex.limits.items.map((t) => el('li', { text: t })))));
  return out;
}

function setCheckMode(mode) {
  const st = S.steps.steps[4];
  if (S.current !== 5) return;
  S.checkMode = mode;
  for (const b of document.querySelectorAll('.seg button')) b.setAttribute('aria-pressed', String(b.dataset.mode === mode));
  setLayers(map, st.extras.modes[mode].layers).catch(note);
}

async function enterStep(st) {
  const type = st.extras?.type;
  if (type === 'dance') return enterDance(st);
  if (type === 'compare') return enterCompare(st);
  if (type === 'listen') return enterListen(st);
  if (type === 'check') return setCheckMode(S.checkMode || st.extras.default_mode);
  return setLayers(map, st.layers || {});
}

// ---------- explore ----------

let breach = null;
function loadBreach() {
  if (!breach) breach = getText('data/breach_sites.csv').then((t) => (t ? parseCSV(t) : []));
  return breach;
}

function parseCSV(text) {
  const rows = [];
  let row = [];
  let f = '';
  let q = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (q) {
      if (c === '"') {
        if (text[i + 1] === '"') {
          f += '"';
          i++;
        } else q = false;
      } else f += c;
    } else if (c === '"') q = true;
    else if (c === ',') {
      row.push(f);
      f = '';
    } else if (c === '\n' || c === '\r') {
      if (c === '\r' && text[i + 1] === '\n') i++;
      row.push(f);
      rows.push(row);
      row = [];
      f = '';
    } else f += c;
  }
  if (f !== '' || row.length) {
    row.push(f);
    rows.push(row);
  }
  if (!rows.length) return [];
  const head = rows.shift().map((h) => h.trim().toLowerCase());
  return rows.filter((r) => r.some((v) => v.trim())).map((r) => Object.fromEntries(head.map((h, k) => [h, (r[k] || '').trim()])));
}

function exploreItems() {
  const items = (S.layersCfg?.layers || []).map((d) => ({ id: d.id, title: d.title, description: d.description, legend: d.legend || [] }));
  for (const x of S.steps.explore.extra_layers || []) items.push(x);
  return items;
}

function exploreLegend() {
  const rows = [];
  const seen = new Set();
  for (const it of exploreItems()) {
    if (!(it.id in S.exploreOn)) continue;
    for (const lg of it.legend || []) {
      const k = JSON.stringify(lg);
      if (seen.has(k)) continue;
      seen.add(k);
      rows.push(lg);
    }
  }
  renderLegend(rows.slice(0, 8));
}

async function enterExplore() {
  const gen = S.gen;
  const ex = S.steps.explore;
  if (!S.exploreOn) S.exploreOn = { ...ex.default_layers };
  $('#step-num').textContent = 'Explore';
  $('#card-title').textContent = ex.title;
  $('#card-text').textContent = ex.text;
  const box = $('#card-extras');
  box.replaceChildren();
  const items = exploreItems();
  const list = el('ul', { class: 'layer-list' });
  if (!(S.layersCfg?.layers || []).length) list.append(el('li', { class: 'na' }, 'The map layers are still being computed.'));
  for (const it of items) {
    const cb = el('input', { type: 'checkbox', 'data-id': it.id });
    cb.checked = it.id in S.exploreOn;
    cb.addEventListener('change', () => {
      if (cb.checked) S.exploreOn[it.id] = 1;
      else delete S.exploreOn[it.id];
      setLayers(map, S.exploreOn).catch(note);
      exploreLegend();
    });
    const lg = el('span', { class: 'lg' }, (it.legend || []).map((l) => el('span', {}, swatch(l), l.label)));
    const li = el('li', {}, el('label', {}, cb, el('span', {}, el('span', { class: 't', text: it.title }), el('span', { class: 'd', text: it.description }), lg)));
    list.append(li);
    const ok = it.id === 'gaps' ? (gapsData || (gapsData = getJSON('data/gaps.geojson'))).then(Boolean) : probe(it.id);
    ok.then((yes) => {
      if (yes) return;
      li.classList.add('na');
      cb.disabled = true;
      cb.checked = false;
      delete S.exploreOn[it.id];
      li.querySelector('.d').textContent = `${it.description} Not available yet.`;
    });
  }
  box.append(list);
  const pinsNote = el('p', { class: 'small', hidden: true, text: ex.pins_text });
  box.append(pinsNote);
  exploreLegend();
  await setLayers(map, S.exploreOn);
  const sites = await loadBreach();
  if (gen !== S.gen) return;
  for (const s of sites) {
    const lat = Number(s.lat);
    const lon = Number(s.lon);
    if (!Number.isFinite(lat) || !Number.isFinite(lon)) continue;
    const elp = el('div', { class: 'pin', title: `${s.name}, ${s.district}` }, el('i'), el('b', { text: s.name }));
    pins.push(new maplibregl.Marker({ element: elp, anchor: 'left', offset: [-8, 0] }).setLngLat([lon, lat]).addTo(map));
  }
  if (pins.length) pinsNote.hidden = false;
}

// ---------- video mode ----------

async function runVideo() {
  document.body.classList.add('video');
  const tl = await getJSON('data/timeline.json');
  S.timeline = tl;
  if (!tl) {
    api.videoError = 'data/timeline.json not found';
    return;
  }
  api.timeline = tl;
  await firstDraw;
  await Promise.race([danceLayers, new Promise((r) => setTimeout(r, 10000))]);
  await waitIdle(map, 8000);
  // load the second map before the clock starts, so step 2 draws at once
  await ensureMapB();
  const st2 = S.steps.steps[1];
  await setLayers(mapB, st2.extras.right.layers);
  if (params.get('warm') !== '0') await warmUp(tl);
  api.videoReady = true;
  api.startVideo = startVideo;
  if (params.get('autostart') !== '0') startVideo();
}

// Visit every storyboard view once before the clock starts, so each shot draws from its first frame
// (tiles stay in each source's cache). The renderer cuts the recording at videoStartMs, so none of
// this appears in the video.
async function warmUp(tl) {
  const t0 = performance.now();
  const idle = (m) => waitIdle(m, 20000);
  await go(5, { instant: true });
  await idle(map);
  setCheckMode('naive');
  await idle(map);
  setCheckMode('trust');
  await idle(map);
  if (tl.tap) S.viewOverride = { center: [tl.tap.lon, tl.tap.lat], zoom: tl.tap.zoom ?? 12 };
  await go(4);
  await idle(map);
  S.videoSlider = 1.0;
  await go(2, { instant: true });
  await idle(map);
  if (mapB) await idle(mapB);
  S.videoSlider = null;
  await go(1);
  await idle(map);
  api.warmUpMs = Math.round(performance.now() - t0);
}

function startVideo() {
  if (api.videoStartMs != null) return;
  const tl = S.timeline;
  api.videoStartMs = performance.now();
  for (const ev of tl.events) setTimeout(() => runEvent(ev).catch(note), ev.t_s * 1000);
}

async function runEvent(ev) {
  const tl = S.timeline;
  if (ev.do === 'step') {
    S.videoSlider = ev.slider ?? null;
    if (ev.step === 4 && tl.tap) S.viewOverride = { center: [tl.tap.lon, tl.tap.lat], zoom: tl.tap.zoom ?? 12 };
    if (S.current !== ev.step) await go(ev.step, { instant: ev.step === 2 || ev.step === 5 });
    if (ev.step === 1) playDance(tl.dance_ms_per_date ?? 700, 400);
    if (ev.step === 2 && ev.slider != null) setSliderFrac(ev.slider);
    if (ev.step === 5) {
      // Video: load both change maps at once (the naive one at opacity 0), so the scripted toggle
      // shows tiles that are already drawn instead of waiting for them to load.
      const ms = S.steps.steps[4].extras.modes;
      const hidden = Object.fromEntries(Object.keys(ms.naive.layers).filter((k) => !(k in ms.trust.layers)).map((k) => [k, 0]));
      setLayers(map, { ...hidden, ...ms.trust.layers }).catch(note);
    }
  } else if (ev.do === 'slider') {
    const t0 = performance.now();
    const dur = (ev.duration_s ?? 6) * 1000;
    const stepFn = () => {
      const u = Math.min(1, (performance.now() - t0) / dur);
      const e = u < 0.5 ? 2 * u * u : 1 - (-2 * u + 2) ** 2 / 2;
      setSliderFrac(ev.from + (ev.to - ev.from) * e);
      if (u < 1 && S.current === 2) requestAnimationFrame(stepFn);
    };
    requestAnimationFrame(stepFn);
  } else if (ev.do === 'tap') {
    const p = map.project([tl.tap.lon, tl.tap.lat]);
    ripple(p.x, p.y);
    await tapAt(tl.tap.lon, tl.tap.lat);
  } else if (ev.do === 'mode') {
    setCheckMode(ev.mode);
  } else if (ev.do === 'endcard') {
    $('#endcard-title').textContent = tl.end?.title || '';
    $('#endcard-link').textContent = tl.end?.link || '';
    $('#endcard').hidden = false;
  } else if (ev.do === 'done') {
    api.videoDone = true;
  }
}

// ---------- start ----------

// First draw: the first idle after the first step's layers were added.
let resolveFirstDraw;
const firstDraw = new Promise((r) => (resolveFirstDraw = r));
let firstDrawStarted = false;
function markFirstDraw() {
  if (firstDrawStarted) return;
  firstDrawStarted = true;
  // firstDrawMs: the first frame drawn with every tile of the view loaded (basemap and ours);
  // firstIdleMs: the map is idle (labels placed and faded in too).
  const allLoaded = () => {
    try {
      return Object.keys(map.getStyle().sources).every((id) => map.isSourceLoaded(id)) && map.areTilesLoaded();
    } catch (e) {
      return false;
    }
  };
  const onRender = () => {
    if (allLoaded()) {
      map.off('render', onRender);
      api.firstDrawMs = Math.round(performance.now());
      resolveFirstDraw();
    }
  };
  map.on('render', onRender);
  map.triggerRepaint();
  waitIdle(map, 20000).then(() => {
    api.firstIdleMs = Math.round(performance.now());
    if (api.firstDrawMs == null) onRender();
    if (api.firstDrawMs == null) {
      map.off('render', onRender);
      api.firstDrawMs = api.firstIdleMs;
      resolveFirstDraw();
    }
  });
}
let resolveDanceLayers;
const danceLayers = new Promise((r) => (resolveDanceLayers = r));

async function main() {
  const target = VIDEO ? 1 : parseHash();
  const data = Promise.all([getJSON('steps.json'), getJSON('data/layers.json'), getJSON('data/results.json')]).then(([steps, layersCfg, results]) => {
    S.steps = steps;
    S.layersCfg = layersCfg;
    S.results = results;
    for (const d of layersCfg?.layers || []) S.defs[d.id] = d;
    // start reading the first view's tile header while the map library downloads
    const st = steps?.steps?.[(target === 'explore' ? 1 : target) - 1];
    const first = st?.extras?.dates?.[0] || Object.keys(st?.layers || st?.extras?.left?.layers || {})[0];
    if (first) probe(first);
    return steps;
  });
  const [ML, steps] = await Promise.all([mlModule, data]);
  maplibregl = Object.assign({}, ML);
  window.maplibregl = maplibregl;
  maplibregl.addProtocol('pmtiles', protocol.tile);
  if (!steps) {
    $('#card-text').textContent = 'The tour could not load. Please reload the page.';
    return;
  }
  const layersCfg = S.layersCfg;
  api.layers = Object.keys(S.defs);
  api.hasResults = !!S.results;

  setupNav();
  setupSheet();
  renderAbout();
  $('#mute').addEventListener('click', () => setMuted(!S.muted));

  const firstStep = steps.steps[(target === 'explore' ? 1 : target) - 1];
  const view = firstStep.view || { center: layersCfg?.center || [84.1, 27.0], zoom: 9 };
  map = makeMap('map', view);
  if (!phone.matches) map.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'bottom-right');
  // add our layers as soon as the style is parsed, not after the basemap has finished drawing
  await styleReady(map);
  api.styleLoadMs = Math.round(performance.now());
  await go(target);
  if (VIDEO) runVideo().catch(note);
}

// test hooks for scripts/check_app.py and the video renderer
Object.assign(api, {
  waitIdle: (ms) => waitIdle(map, ms),
  sliderPos: () => (compare ? compare.currentPosition / $('#maps').clientWidth : null),
  setSlider: (f) => setSliderFrac(f),
  tapAt: (lon, lat) => tapAt(lon, lat),
  utm: (lon, lat, zone = 44) => utmForward(lon, lat, zone),
  note: async (voice, db) => ((await loadSound()) ? noteFor(voice, db) : null),
  numbers: () => numbers(),
  audioState: () => (audio ? audio.ctx.state : 'none'),
});

main().catch((e) => {
  note(e);
  $('#card-text').textContent = 'Something went wrong while loading the map. Please reload the page.';
});
