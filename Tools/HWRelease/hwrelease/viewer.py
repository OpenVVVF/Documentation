"""Generate the PCB Tool page from the release manifest.

The page is a self-contained HTML file written to
Docs/Tools/PCB-Tool/pcb-tool.html. It lists every exported board by part
number; selecting one shows the board renders, the interactive assembly (iBOM)
embedded in an iframe (fullscreenable / openable in a new tab), and links to
the schematic, BOM, gerbers, DRC, STEP, and the source tag in the hardware
repository.

Artifact links are relative to the built docgen site root (../../ from the
page), where docgen copies Data/Releases alongside the documents.
"""

import json
from pathlib import Path
from typing import Dict, Optional

from . import core

VIEWER_REL = Path("Docs") / "Tools" / "PCB-Tool" / "pcb-tool.html"
BOM_TOOL_REL = Path("Docs") / "Tools" / "BOM-Tool" / "bom-tool.html"

# Depth of <section>/Tools/<name>/ below the built site root.
_ROOT = "../../"

_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PCB Tool - OpenVVVF</title>
<link rel="icon" type="image/svg+xml" href="{root}brand/icon.svg">
<style>
@font-face {{ font-family: "Saira"; src: url("{root}brand/fonts/Saira-400.ttf") format("truetype"); font-weight: 400; font-display: swap; }}
@font-face {{ font-family: "Saira"; src: url("{root}brand/fonts/Saira-700.ttf") format("truetype"); font-weight: 700; font-display: swap; }}
:root {{
  --bg: #ffffff; --surface: #f8f9fa; --surface-2: #f1f3f5;
  --border: #d1d5db; --border-light: #e9ecef;
  --text: #1a1a1a; --text-muted: #5a5a5a;
  --accent: #fc0f27; --accent-dark: #c40d20;
  --font-body: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  --font-brand: "Saira", var(--font-body);
}}
* {{ box-sizing: border-box; }}
body {{ margin: 0; font-family: var(--font-body); color: var(--text); background: var(--bg); }}
header {{
  display: flex; align-items: center; gap: 12px;
  padding: 12px 20px; border-bottom: 1px solid var(--border-light); background: var(--surface);
}}
header img {{ height: 28px; }}
header h1 {{ font-family: var(--font-brand); font-size: 20px; font-weight: 700; margin: 0; }}
header h1 .sep {{ color: var(--text-muted); font-weight: 400; margin: 0 6px; }}
.layout {{ display: flex; min-height: calc(100vh - 54px); }}
aside {{
  width: 300px; flex-shrink: 0; border-right: 1px solid var(--border-light);
  background: var(--surface); padding: 12px; overflow-y: auto;
}}
aside input {{
  width: 100%; padding: 8px 10px; margin-bottom: 10px;
  border: 1px solid var(--border); border-radius: 6px; font-size: 14px;
}}
.chassis {{ font-family: var(--font-brand); font-weight: 700; font-size: 12px;
  text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-muted); margin: 14px 4px 6px; }}
.pn {{
  display: block; width: 100%; text-align: left; cursor: pointer;
  padding: 8px 10px; margin-bottom: 4px; border: 1px solid var(--border-light);
  border-radius: 6px; background: #fff; font-size: 13px;
}}
.pn small {{ display: block; color: var(--text-muted); }}
.pn:hover {{ border-color: var(--accent); }}
.pn.active {{ border-color: var(--accent); background: #fff5f6; box-shadow: inset 3px 0 0 var(--accent); }}
main {{ flex: 1; padding: 24px 28px; overflow-y: auto; }}
main h2 {{ font-family: var(--font-brand); margin: 0 0 4px; }}
.meta {{ color: var(--text-muted); font-size: 14px; margin-bottom: 18px; }}
.actions {{ display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 24px; }}
.actions a, .actions button {{
  display: inline-block; padding: 9px 16px; border-radius: 6px; font-size: 14px;
  text-decoration: none; border: 1px solid var(--border); color: var(--text);
  background: #fff; cursor: pointer; font-family: var(--font-body);
}}
.actions a.primary {{ background: var(--accent); border-color: var(--accent); color: #fff; font-weight: 600; }}
.actions a.primary:hover {{ background: var(--accent-dark); }}
.actions a:hover, .actions button:hover {{ border-color: var(--accent); }}
.renders {{ display: flex; flex-wrap: wrap; gap: 16px; margin-bottom: 24px; }}
.renders figure {{ margin: 0; }}
.renders img {{
  max-width: 420px; width: 100%; border: 1px solid var(--border-light);
  border-radius: 8px; background: var(--surface-2);
}}
.renders figcaption {{ font-size: 13px; color: var(--text-muted); margin-top: 6px; text-align: center; }}
.ibom-wrap {{
  border: 1px solid var(--border-light); border-radius: 8px; overflow: hidden;
  background: #fff;
}}
.ibom-wrap:fullscreen {{ border-radius: 0; }}
.ibom-wrap iframe {{ display: block; width: 100%; height: 70vh; border: 0; }}
.ibom-wrap:fullscreen iframe {{ height: 100vh; }}
.empty {{ color: var(--text-muted); margin-top: 40px; }}
.fabspec {{
  max-width: 720px; border: 1px solid var(--border-light); border-radius: 8px;
  background: var(--surface); padding: 4px 18px 12px; font-size: 14px;
}}
@media (max-width: 800px) {{
  .layout {{ flex-direction: column; }}
  aside {{ width: 100%; border-right: none; border-bottom: 1px solid var(--border-light); }}
}}
</style>
</head>
<body>
<header>
  <a href="{root}index.html"><img src="{root}brand/logo.png" alt="OpenVVVF"></a>
  <h1><span class="sep">/</span>PCB Tool</h1>
</header>
<div class="layout">
  <aside>
    <input id="filter" type="search" placeholder="Filter part numbers..." oninput="renderList()">
    <div id="list"></div>
  </aside>
  <main id="main"><p class="empty">Select a PCB on the left.</p></main>
</div>
<script>
const MANIFEST = {manifest};
const ROOT = "{root}";

const ARTIFACTS = [
  ["schematic_pdf", "Schematic PDF", true],
  ["bom_csv", "BOM (CSV)", true],
  ["gerber_zip", "Gerbers (ZIP)", true],
  ["drc", "DRC Report", true],
  ["step", "STEP Model", false],
];

function entries() {{
  return Object.values(MANIFEST).filter(e => e.board)
           .sort((a, b) => a.part_number.localeCompare(b.part_number));
}}

function renderList() {{
  const q = document.getElementById("filter").value.trim().toLowerCase();
  const list = document.getElementById("list");
  list.innerHTML = "";
  let lastChassis = null;
  for (const e of entries()) {{
    if (q && !e.part_number.toLowerCase().includes(q) && !e.board.toLowerCase().includes(q)) continue;
    if (e.chassis !== lastChassis) {{
      const h = document.createElement("div");
      h.className = "chassis";
      h.textContent = "Chassis " + e.chassis;
      list.appendChild(h);
      lastChassis = e.chassis;
    }}
    const b = document.createElement("button");
    b.className = "pn" + (location.hash === "#" + e.part_number ? " active" : "");
    b.innerHTML = e.part_number + "<small>" + e.board + "</small>";
    b.onclick = () => {{ location.hash = e.part_number; }};
    list.appendChild(b);
  }}
}}

function renderCaption(filename, board) {{
  const m = filename.replace(/\\.png$/, "").slice(board.length);
  if (m === "" || m === "-Front") return "Front";
  if (m === "-Back") return "Back";
  return m.replace(/^-/, "").replace(/-/g, " ");
}}

function renderSortKey(filename, board) {{
  const c = renderCaption(filename, board);
  return c === "Front" ? 0 : c === "Back" ? 1 : 2;
}}

function renderMain() {{
  const pn = location.hash.slice(1);
  const e = MANIFEST[pn];
  const main = document.getElementById("main");
  if (!e) {{ main.innerHTML = '<p class="empty">Select a PCB on the left.</p>'; renderList(); return; }}
  const base = ROOT + e.dir + "/";
  const a = e.artifacts || {{}};
  let html = "<h2>" + e.part_number + "</h2>";
  html += '<div class="meta">' + e.board + " · Chassis " + e.chassis +
          " · Rev " + e.rev + " · source tag <code>" + e.source_tag + "</code></div>";
  html += '<div class="actions">';
  if (a.ibom)
    html += '<a class="primary" href="' + base + a.ibom + '" target="_blank" rel="noopener">Open Interactive Assembly \\u2197</a>';
  if (a.ibom)
    html += "<button onclick=\\"document.getElementById('ibom-wrap').requestFullscreen()\\">Fullscreen</button>";
  if (e.source_url)
    html += '<a href="' + e.source_url + '" target="_blank" rel="noopener">Open Source (' + e.source_tag + ') \\u2197</a>';
  for (const [key, label, newTab] of ARTIFACTS) {{
    if (!a[key]) continue;
    html += '<a href="' + base + a[key] + '"' +
            (newTab ? ' target="_blank" rel="noopener"' : ' download') + '>' + label + "</a>";
  }}
  html += "</div>";
  if (a.renders && a.renders.length) {{
    const sorted = a.renders.slice().sort((x, y) => renderSortKey(x, e.board) - renderSortKey(y, e.board));
    html += '<div class="renders">';
    for (const r of sorted) {{
      const cap = renderCaption(r, e.board);
      html += '<figure><a href="' + base + r + '" target="_blank" rel="noopener"><img src="' + base + r + '" alt="' + cap + '"></a>' +
              "<figcaption>" + cap + "</figcaption></figure>";
    }}
    html += "</div>";
  }}
  if (a.ibom)
    html += '<div class="ibom-wrap" id="ibom-wrap"><iframe src="' + base + a.ibom + '" title="Interactive assembly"></iframe></div>';
  if (a.fab_spec)
    html += '<h3 style="margin-top:24px">Ordering specifications</h3><div class="fabspec" id="fabspec">Loading...</div>';
  main.innerHTML = html;
  if (a.fab_spec)
    fetch(base + a.fab_spec).then(r => r.text()).then(md => {{
      document.getElementById("fabspec").innerHTML = mdLite(md);
    }});
  renderList();
}}

function mdLite(md) {{
  const esc = s => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  const inline = s => esc(s).replace(/\\*\\*(.+?)\\*\\*/g, "<strong>$1</strong>")
                            .replace(/`(.+?)`/g, "<code>$1</code>");
  let html = "", inList = false;
  for (const line of md.split("\\n")) {{
    const t = line.trim();
    const closeList = () => {{ if (inList) {{ html += "</ul>"; inList = false; }} }};
    if (t.startsWith("## ")) {{ closeList(); html += "<h4>" + inline(t.slice(3)) + "</h4>"; }}
    else if (t.startsWith("# ")) {{ closeList(); html += "<h4>" + inline(t.slice(2)) + "</h4>"; }}
    else if (t.startsWith("- ")) {{
      if (!inList) {{ html += "<ul>"; inList = true; }}
      html += "<li>" + inline(t.slice(2)) + "</li>";
    }}
    else if (t === "") closeList();
    else {{ closeList(); html += "<p>" + inline(t) + "</p>"; }}
  }}
  if (inList) html += "</ul>";
  return html;
}}

window.addEventListener("hashchange", renderMain);
renderMain();
</script>
</body>
</html>
"""


def render_viewer_html(manifest: Dict[str, dict], root: str = _ROOT) -> str:
    data = json.dumps(manifest, sort_keys=True)
    return _PAGE.format(root=root, manifest=data)


_BOM_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>BOM Tool - OpenVVVF</title>
<link rel="icon" type="image/svg+xml" href="{root}brand/icon.svg">
<style>
@font-face {{ font-family: "Saira"; src: url("{root}brand/fonts/Saira-400.ttf") format("truetype"); font-weight: 400; font-display: swap; }}
@font-face {{ font-family: "Saira"; src: url("{root}brand/fonts/Saira-700.ttf") format("truetype"); font-weight: 700; font-display: swap; }}
:root {{
  --bg: #ffffff; --surface: #f8f9fa; --surface-2: #f1f3f5;
  --border: #d1d5db; --border-light: #e9ecef;
  --text: #1a1a1a; --text-muted: #5a5a5a;
  --accent: #fc0f27; --accent-dark: #c40d20;
  --font-body: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  --font-brand: "Saira", var(--font-body);
}}
* {{ box-sizing: border-box; }}
body {{ margin: 0; font-family: var(--font-body); color: var(--text); background: var(--bg); }}
header {{
  display: flex; align-items: center; gap: 12px;
  padding: 12px 20px; border-bottom: 1px solid var(--border-light); background: var(--surface);
}}
header img {{ height: 28px; }}
header h1 {{ font-family: var(--font-brand); font-size: 20px; font-weight: 700; margin: 0; }}
header h1 .sep {{ color: var(--text-muted); font-weight: 400; margin: 0 6px; }}
main {{ padding: 24px 28px; max-width: 1400px; }}
.controls {{ display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 20px; }}
.controls label {{ font-size: 13px; color: var(--text-muted); display: block; margin-bottom: 4px; }}
.controls select {{
  padding: 8px 12px; border: 1px solid var(--border); border-radius: 6px;
  font-size: 14px; background: #fff; min-width: 160px;
}}
.vendors {{ display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 20px; }}
.vendors button, .vendors a {{
  padding: 9px 16px; border-radius: 6px; font-size: 14px; cursor: pointer;
  border: 1px solid var(--border); background: #fff; color: var(--text);
  text-decoration: none; font-family: var(--font-body);
}}
.vendors button:hover, .vendors a:hover {{ border-color: var(--accent); }}
.vendors button.active {{ border-color: var(--accent); background: #fff5f6; box-shadow: inset 0 -3px 0 var(--accent); }}
.vendors a.download {{ background: var(--accent); border-color: var(--accent); color: #fff; font-weight: 600; }}
.vendors a.download:hover {{ background: var(--accent-dark); }}
.meta {{ color: var(--text-muted); font-size: 14px; margin-bottom: 16px; }}
table {{ border-collapse: collapse; width: 100%; font-size: 13px; }}
th, td {{ border: 1px solid var(--border-light); padding: 6px 10px; text-align: left; }}
th {{ background: var(--surface); font-family: var(--font-brand); position: sticky; top: 0; }}
tr:nth-child(even) {{ background: var(--surface); }}
.empty {{ color: var(--text-muted); margin-top: 40px; }}
.guide {{
  flex-direction: column; gap: 14px; margin-bottom: 20px; max-width: 900px;
}}
.guide img {{
  width: 100%; border: 1px solid var(--border-light); border-radius: 8px;
  background: var(--surface-2);
}}
.guide .copy-paste {{
  align-self: flex-start; padding: 9px 16px; border-radius: 6px; font-size: 14px;
  border: 1px solid var(--border); background: #fff; cursor: pointer;
}}
.guide .copy-paste:hover {{ border-color: var(--accent); }}
.guide.collapsed {{ display: none !important; }}
#guide-toggle {{
  margin: 24px 0 12px; padding: 8px 14px; border-radius: 6px; font-size: 13px;
  border: 1px solid var(--border); background: var(--surface); cursor: pointer;
  color: var(--text-muted); font-family: var(--font-body);
}}
#guide-toggle:hover {{ border-color: var(--accent); color: var(--text); }}
.guide-step {{ display: flex; gap: 14px; align-items: flex-start; }}
.step-num {{
  flex-shrink: 0; width: 28px; height: 28px; border-radius: 50%;
  background: var(--accent); color: #fff; font-weight: 700; font-size: 14px;
  display: flex; align-items: center; justify-content: center; margin-top: 2px;
}}
.step-body {{ flex: 1; min-width: 0; }}
.step-cap {{ margin: 4px 0 8px; font-size: 14px; }}
.step-body img {{ width: 100%; border: 1px solid var(--border-light); border-radius: 8px; }}
</style>
</head>
<body>
<header>
  <a href="{root}index.html"><img src="{root}brand/logo.png" alt="OpenVVVF"></a>
  <h1><span class="sep">/</span>BOM Tool</h1>
</header>
<main>
  <div class="controls">
    <div><label>Chassis</label><select id="chassis" onchange="onChassis()"></select></div>
    <div><label>Revision</label><select id="rev" onchange="onRev()"></select></div>
    <div><label>Variant</label><select id="variant" onchange="onVariant()"></select></div>
  </div>
  <div class="meta" id="meta"></div>
  <div class="vendors" id="vendors"></div>
  <div id="preview"><p class="empty">Pick a vendor BOM above to preview it.</p></div>
  <button id="guide-toggle" style="display:none" onclick="toggleGuide()">Hide ordering walkthrough</button>
  <div class="guide" id="guide" style="display:none"></div>
</main>
<script>
// Ordering walkthrough: hand-maintained files next to this page,
// ordering-<vendor>-<n>.png (screenshot) + ordering-<vendor>-<n>.txt
// (caption). Either may exist alone; the walkthrough stops at the first n
// where neither exists.
const ORDER_GUIDE_MAX_STEPS = 12;

function loadImg(src) {{
  return new Promise(res => {{
    const i = new Image();
    i.onload = () => res(i);
    i.onerror = () => res(null);
    i.src = src;
  }});
}}

async function renderGuide() {{
  const div = document.getElementById("guide");
  div.innerHTML = "";
  if (!state.vendor) {{ div.style.display = "none"; return; }}
  const vendor = state.vendor;
  for (let n = 1; n <= ORDER_GUIDE_MAX_STEPS; n++) {{
    const [img, cap] = await Promise.all([
      loadImg("ordering-" + vendor + "-" + n + ".png"),
      fetch("ordering-" + vendor + "-" + n + ".txt")
        .then(r => r.ok ? r.text() : null).catch(() => null),
    ]);
    if (!img && !cap) break;
    if (state.vendor !== vendor) return;  // switched vendors mid-load
    const step = document.createElement("div");
    step.className = "guide-step";
    const num = document.createElement("div");
    num.className = "step-num";
    num.textContent = n;
    step.appendChild(num);
    const body = document.createElement("div");
    body.className = "step-body";
    if (cap) {{
      const p = document.createElement("p");
      p.className = "step-cap";
      p.textContent = cap.trim();
      body.appendChild(p);
    }}
    if (img) body.appendChild(img);
    step.appendChild(body);
    div.appendChild(step);
  }}
  if (state.vendor === "mcmaster") {{
    const e = current();
    const map = boms();
    if (map.mcmaster_paste) {{
      const b = document.createElement("button");
      b.className = "copy-paste";
      b.textContent = "Copy McMaster order paste to clipboard";
      b.onclick = async () => {{
        const r = await fetch(ROOT + e.dir + "/" + map.mcmaster_paste);
        await navigator.clipboard.writeText(await r.text());
        b.textContent = "Copied!";
        setTimeout(() => b.textContent = "Copy McMaster order paste to clipboard", 2000);
      }};
      div.appendChild(b);
    }}
  }}
  div.style.display = div.children.length ? "flex" : "none";
  const toggle = document.getElementById("guide-toggle");
  toggle.style.display = div.children.length ? "inline-block" : "none";
  toggle.textContent = "Hide ordering walkthrough";
  div.classList.remove("collapsed");
}}

function toggleGuide() {{
  const div = document.getElementById("guide");
  const toggle = document.getElementById("guide-toggle");
  const collapsed = div.classList.toggle("collapsed");
  toggle.textContent = collapsed ? "Show ordering walkthrough" : "Hide ordering walkthrough";
}}

const MANIFEST = {manifest};
const ROOT = "{root}";
const VENDOR_LABELS = {{mouser: "Mouser", mcmaster: "McMaster-Carr", sendcutsend: "SendCutSend",
  digikey: "DigiKey", consolidated: "Consolidated", assembly: "Assembly", pcb: "PCBs"}};
const PRICE_NAMES = {{mouser: "Mouser", mcmaster: "McMaster-Carr", sendcutsend: "SendCutSend",
  digikey: "Digi-Key", assembly: "In-House Assembly", pcb: "PCB Fabrication"}};

let state = {{chassis: null, rev: null, variant: "base", vendor: null}};

function releases() {{
  return Object.values(MANIFEST).filter(e => !e.board && e.artifacts && e.artifacts.vendor_boms);
}}

function fill(sel, values, current) {{
  sel.innerHTML = "";
  for (const v of values) {{
    const o = document.createElement("option");
    o.value = v; o.textContent = v;
    if (v === current) o.selected = true;
    sel.appendChild(o);
  }}
}}

function current() {{
  return releases().find(e => e.chassis === state.chassis && e.rev === state.rev);
}}

function init() {{
  const rel = releases();
  if (!rel.length) {{
    document.getElementById("meta").textContent = "No chassis BOM exports yet — run: hwrelease update";
    return;
  }}
  state.chassis = state.chassis || rel[0].chassis;
  fill(document.getElementById("chassis"), [...new Set(rel.map(e => e.chassis))].sort(), state.chassis);
  onChassis();
  const h = location.hash.slice(1);
  if (VENDOR_LABELS[h]) {{
    state.vendor = h;
    renderVendors();
    renderGuide();
    loadPreview();
  }}
}}

window.addEventListener("hashchange", () => {{
  const h = location.hash.slice(1);
  if (VENDOR_LABELS[h] && h !== state.vendor) {{
    state.vendor = h;
    renderVendors();
    renderGuide();
    loadPreview();
  }}
}});

function onChassis() {{
  state.chassis = document.getElementById("chassis").value;
  const rel = releases().filter(e => e.chassis === state.chassis);
  state.rev = rel[0].rev;
  fill(document.getElementById("rev"), [...new Set(rel.map(e => e.rev))].sort(), state.rev);
  onRev();
}}

function onRev() {{
  state.rev = document.getElementById("rev").value;
  const e = current();
  const variants = ["base"].concat(Object.keys((e.artifacts || {{}}).variants || {{}}));
  state.variant = "base";
  fill(document.getElementById("variant"), variants, state.variant);
  onVariant();
}}

function onVariant() {{
  state.variant = document.getElementById("variant").value;
  state.vendor = null;
  renderVendors();
}}

function boms() {{
  const e = current();
  const a = (e && e.artifacts) || {{}};
  return state.variant === "base" ? (a.vendor_boms || {{}}) : ((a.variants || {{}})[state.variant] || {{}});
}}

function renderVendors() {{
  const e = current();
  const box = document.getElementById("vendors");
  box.innerHTML = "";
  const map = boms();
  const est = ((e.artifacts || {{}}).price_estimate) || {{}};
  const estVendors = est.vendors || {{}};
  const estVariants = est.variants || {{}};
  let meta = "Chassis " + e.chassis + " · Rev " + e.rev + " · source tag <code>" + e.source_tag + "</code>" +
    (e.source_url ? ' · <a href="' + e.source_url + '" target="_blank" rel="noopener">source \\u2197</a>' : "");
  const varTotal = state.variant === "base" ? (est.total || estVariants.base) : estVariants[state.variant];
  if (varTotal)
    meta += " · <strong>Est. total (" + (est.qty || 1) + " unit" + ((est.qty || 1) > 1 ? "s" : "") +
            ", " + state.variant + "): $" + varTotal + "</strong>";
  document.getElementById("meta").innerHTML = meta;
  const varVend = ((est.variant_vendors || {{}})[state.variant]) || null;
  const priceFor = key => state.variant === "base"
    ? estVendors[PRICE_NAMES[key]]
    : (varVend && varVend[key] !== undefined ? varVend[key] : estVendors[PRICE_NAMES[key]]);
  for (const [key, label] of Object.entries(VENDOR_LABELS)) {{
    if (!map[key]) continue;
    const b = document.createElement("button");
    b.textContent = label + (priceFor(key) ? " · $" + priceFor(key) : "");
    b.className = state.vendor === key ? "active" : "";
    b.onclick = () => {{ state.vendor = key; renderVendors(); renderGuide(); loadPreview(); }};
    box.appendChild(b);
  }}
  if (map.pcb) {{
    const pcb = document.createElement("a");
    pcb.href = "../PCB-Tool/pcb-tool.html";
    pcb.target = "_blank"; pcb.rel = "noopener";
    pcb.textContent = "View boards in PCB Tool \\u2197";
    box.appendChild(pcb);
    const jlc = document.createElement("a");
    jlc.href = "https://jlcpcb.com";
    jlc.target = "_blank"; jlc.rel = "noopener";
    jlc.textContent = "Order PCBs at JLCPCB \\u2197";
    box.appendChild(jlc);
  }}
  if (map.sendcutsend) {{
    const scs = document.createElement("a");
    scs.href = "https://sendcutsend.com";
    scs.target = "_blank"; scs.rel = "noopener";
    scs.textContent = "Order parts at SendCutSend \\u2197";
    box.appendChild(scs);
  }}
  if (state.vendor && map[state.vendor]) {{
    const a = document.createElement("a");
    a.className = "download";
    a.href = ROOT + e.dir + "/" + map[state.vendor];
    a.download = "";
    a.textContent = "Download CSV";
    box.appendChild(a);
  }}
}}

function parseCSV(text) {{
  const rows = []; let row = [], cur = "", q = false;
  for (let i = 0; i < text.length; i++) {{
    const c = text[i];
    if (q) {{
      if (c === '"') {{ if (text[i+1] === '"') {{ cur += '"'; i++; }} else q = false; }}
      else cur += c;
    }} else if (c === '"') q = true;
    else if (c === ",") {{ row.push(cur); cur = ""; }}
    else if (c === "\\n") {{ row.push(cur); rows.push(row); row = []; cur = ""; }}
    else if (c !== "\\r") cur += c;
  }}
  if (cur || row.length) {{ row.push(cur); rows.push(row); }}
  return rows;
}}

async function loadPreview() {{
  const e = current();
  const map = boms();
  const div = document.getElementById("preview");
  if (!state.vendor || !map[state.vendor]) return;
  const r = await fetch(ROOT + e.dir + "/" + map[state.vendor]);
  const rows = parseCSV(await r.text());
  let html = "<table><thead><tr>";
  for (const h of rows[0]) html += "<th>" + h + "</th>";
  html += "</tr></thead><tbody>";
  for (const row of rows.slice(1, 501)) {{
    html += "<tr>";
    for (const c of row) html += "<td>" + c + "</td>";
    html += "</tr>";
  }}
  html += "</tbody></table>";
  if (rows.length > 501) html += '<p class="meta">Showing 500 of ' + (rows.length - 1) + " rows.</p>";
  div.innerHTML = html;
}}

init();
</script>
</body>
</html>
"""


def render_bom_tool_html(manifest: Dict[str, dict], root: str = _ROOT) -> str:
    data = json.dumps(manifest, sort_keys=True)
    return _BOM_PAGE.format(root=root, manifest=data)


def build_viewer(manifest_path: Optional[Path] = None,
                 out_path: Optional[Path] = None) -> int:
    manifest_path = manifest_path or core.MANIFEST_PATH
    out_path = out_path or core.REPO_ROOT / VIEWER_REL
    manifest = core.load_manifest(manifest_path)
    if not manifest:
        print("Manifest is empty — run: hwrelease update")
        return 1
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(render_viewer_html(manifest))
    print(f"Wrote {out_path.relative_to(core.REPO_ROOT)} "
          f"({sum(1 for e in manifest.values() if 'board' in e)} board revision(s))")
    bom_path = out_path.parent.parent / "BOM-Tool" / "bom-tool.html"
    bom_path.parent.mkdir(parents=True, exist_ok=True)
    bom_path.write_text(render_bom_tool_html(manifest))
    print(f"Wrote {bom_path.relative_to(core.REPO_ROOT)} "
          f"({sum(1 for e in manifest.values() if 'board' not in e)} chassis release(s))")
    return 0
