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
.fabspec table {{ border-collapse: collapse; margin: 10px 0; }}
.fabspec th, .fabspec td {{
  border: 1px solid var(--border-light); padding: 6px 12px; text-align: left;
}}
.fabspec th {{ background: var(--surface-2); font-family: var(--font-brand);
  text-transform: capitalize; }}
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
  if (a.fab_spec) {{
    const spec = a.fab_spec;
    const rows = Object.entries(spec.options || {{}});
    const notes = (spec.notes || []).concat(spec.default_notes || []);
    if (rows.length || notes.length) {{
      html += '<h3 style="margin-top:24px">Ordering specifications</h3><div class="fabspec">';
      if (rows.length) {{
        html += "<table>";
        for (const [k, v] of rows)
          html += "<tr><th>" + k.replace(/_/g, " ") + "</th><td>" + v + "</td></tr>";
        html += "</table>";
      }}
      if (notes.length) {{
        html += "<ul>";
        for (const n of notes) html += "<li>" + n + "</li>";
        html += "</ul>";
      }}
      html += "</div>";
    }}
  }}
  main.innerHTML = html;
  renderList();
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
.layout {{ display: flex; min-height: calc(100vh - 54px); }}
aside {{
  width: 300px; flex-shrink: 0; border-right: 1px solid var(--border-light);
  background: var(--surface); padding: 12px; overflow-y: auto;
}}
.sel {{ margin-bottom: 12px; }}
.sel label {{
  display: block; font-family: var(--font-brand); font-weight: 700; font-size: 12px;
  text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-muted); margin-bottom: 4px;
}}
.sel select {{
  width: 100%; padding: 8px 10px; border: 1px solid var(--border);
  border-radius: 6px; font-size: 14px; background: #fff;
}}
.vendors-label {{
  font-family: var(--font-brand); font-weight: 700; font-size: 12px;
  text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-muted); margin: 16px 4px 6px;
}}
.vn {{
  display: block; width: 100%; text-align: left; cursor: pointer;
  padding: 8px 10px; margin-bottom: 4px; border: 1px solid var(--border-light);
  border-radius: 6px; background: #fff; font-size: 13px;
}}
.vn small {{ display: block; color: var(--text-muted); }}
.vn:hover {{ border-color: var(--accent); }}
.vn.active {{ border-color: var(--accent); background: #fff5f6; box-shadow: inset 3px 0 0 var(--accent); }}
main {{ flex: 1; padding: 24px 28px; overflow-y: auto; }}
.meta {{ color: var(--text-muted); font-size: 14px; margin-bottom: 16px; }}
.actions {{ display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 20px; }}
.actions a, .actions button {{
  display: inline-block; padding: 9px 16px; border-radius: 6px; font-size: 14px;
  text-decoration: none; border: 1px solid var(--border); color: var(--text);
  background: #fff; cursor: pointer; font-family: var(--font-body);
}}
.actions a:hover, .actions button:hover {{ border-color: var(--accent); }}
.actions a.download {{ background: var(--accent); border-color: var(--accent); color: #fff; font-weight: 600; }}
.actions a.download:hover {{ background: var(--accent-dark); }}
table {{ border-collapse: collapse; width: 100%; font-size: 13px; }}
th, td {{ border: 1px solid var(--border-light); padding: 6px 10px; text-align: left; }}
th {{ background: var(--surface); font-family: var(--font-brand); position: sticky; top: 0; }}
tr:nth-child(even) {{ background: var(--surface); }}
.empty {{ color: var(--text-muted); margin-top: 40px; }}
#content {{ display: flex; gap: 24px; align-items: flex-start; }}
#preview {{ flex: 1; min-width: 0; }}
.guide-col {{ width: 560px; flex-shrink: 0; }}
.guide {{
  flex-direction: column; gap: 14px; display: flex;
  position: sticky; top: 16px; max-height: calc(100vh - 110px); overflow-y: auto;
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
  margin: 0 0 12px; padding: 8px 14px; border-radius: 6px; font-size: 13px;
  border: 1px solid var(--border); background: var(--surface); cursor: pointer;
  color: var(--text-muted); font-family: var(--font-body);
}}
#guide-toggle:hover {{ border-color: var(--accent); color: var(--text); }}
.guide-bar {{ display: flex; gap: 10px; align-items: center; margin-bottom: 12px; }}
.guide-bar #guide-toggle {{ margin: 0; }}
#guide-order-link {{
  padding: 8px 14px; border-radius: 6px; font-size: 13px; font-weight: 600;
  background: var(--accent); border: 1px solid var(--accent); color: #fff; text-decoration: none;
}}
#guide-order-link:hover {{ background: var(--accent-dark); }}
.guide-step {{ display: flex; gap: 14px; align-items: flex-start; }}
.step-num {{
  flex-shrink: 0; width: 28px; height: 28px; border-radius: 50%;
  background: var(--accent); color: #fff; font-weight: 700; font-size: 14px;
  display: flex; align-items: center; justify-content: center; margin-top: 2px;
}}
.step-body {{ flex: 1; min-width: 0; }}
.step-cap {{ margin: 4px 0 8px; font-size: 14px; }}
.step-body img {{ width: 100%; border: 1px solid var(--border-light); border-radius: 8px; }}
.mech-cards {{ display: flex; flex-wrap: wrap; gap: 14px; margin-bottom: 20px; }}
.mech-card {{
  width: 300px; border: 1px solid var(--border-light); border-radius: 8px;
  background: var(--surface); padding: 12px 14px; font-size: 13px;
}}
.mech-card img {{ width: 100%; border-radius: 6px; background: #fff;
  border: 1px solid var(--border-light); }}
.mech-card h4 {{ margin: 10px 0 4px; font-family: var(--font-brand); }}
.mech-meta {{ color: var(--text-muted); margin-bottom: 8px; }}
.mech-card ul {{ margin: 0 0 8px; padding-left: 18px; }}
.mech-notes {{ color: var(--text-muted); margin-bottom: 8px; }}
.mech-links {{ display: flex; gap: 12px; align-items: center; }}
.mech-links a {{ color: var(--accent); }}
@media (max-width: 800px) {{
  .layout {{ flex-direction: column; }}
  aside {{ width: 100%; border-right: none; border-bottom: 1px solid var(--border-light); }}
}}
@media (max-width: 1200px) {{
  #content {{ flex-direction: column; }}
  .guide-col {{ width: 100%; }}
  .guide {{ position: static; max-height: none; }}
}}
</style>
</head>
<body>
<header>
  <a href="{root}index.html"><img src="{root}brand/logo.png" alt="OpenVVVF"></a>
  <h1><span class="sep">/</span>BOM Tool</h1>
</header>
<div class="layout">
  <aside>
    <div class="sel"><label>Chassis</label><select id="chassis" onchange="onChassis()"></select></div>
    <div class="sel"><label>Revision</label><select id="rev" onchange="onRev()"></select></div>
    <div class="sel"><label>Variant</label><select id="variant" onchange="onVariant()"></select></div>
    <div class="vendors-label">Vendors</div>
    <div id="vendors"></div>
  </aside>
  <main>
    <div class="meta" id="meta"></div>
    <div class="actions" id="actions"></div>
    <div id="content">
      <div id="preview"><p class="empty">Select a vendor on the left to preview its BOM.</p></div>
      <div class="guide-col" id="guide-col" style="display:none">
        <div class="guide-bar">
          <button id="guide-toggle" onclick="toggleGuide()">Hide walkthrough</button>
          <a id="guide-order-link" target="_blank" rel="noopener" style="display:none"></a>
        </div>
        <div class="guide" id="guide"></div>
      </div>
    </div>
  </main>
</div>
<script>
// Ordering walkthrough: hand-maintained files next to this page,
// ordering-<vendor>-<n>.png (screenshot) + ordering-<vendor>-<n>.txt
// (caption). Either may exist alone; the walkthrough stops at the first n
// where neither exists.
const ORDER_GUIDE_MAX_STEPS = 12;
// Walkthrough file key per vendor (files are ordering-<key>-<n>.png/.txt).
const GUIDE_KEYS = {{pcb: "jlc"}};

function guideKey() {{ return GUIDE_KEYS[state.vendor] || state.vendor; }}

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
  const col = document.getElementById("guide-col");
  div.innerHTML = "";
  if (!state.vendor) {{ col.style.display = "none"; return; }}
  const vendor = guideKey();
  const selected = state.vendor;
  for (let n = 1; n <= ORDER_GUIDE_MAX_STEPS; n++) {{
    const [img, cap] = await Promise.all([
      loadImg("ordering-" + vendor + "-" + n + ".png"),
      fetch("ordering-" + vendor + "-" + n + ".txt")
        .then(r => r.ok ? r.text() : null).catch(() => null),
    ]);
    if (!img && !cap) break;
    if (state.vendor !== selected) return;  // switched vendors mid-load
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
  div.style.display = "flex";
  col.style.display = div.children.length ? "block" : "none";
  const toggle = document.getElementById("guide-toggle");
  toggle.textContent = "Hide walkthrough";
  div.classList.remove("collapsed");
  const orderLink = document.getElementById("guide-order-link");
  const ext = (ORDER_LINKS[state.vendor] || []).find(([, url]) => url.startsWith("http"));
  if (ext) {{
    orderLink.textContent = ext[0];
    orderLink.href = ext[1];
    orderLink.style.display = "inline-block";
  }} else {{
    orderLink.style.display = "none";
  }}
}}

function toggleGuide() {{
  const div = document.getElementById("guide");
  const toggle = document.getElementById("guide-toggle");
  const collapsed = div.classList.toggle("collapsed");
  toggle.textContent = collapsed ? "Show walkthrough" : "Hide walkthrough";
}}

const MANIFEST = {manifest};
const ROOT = "{root}";
const VENDOR_LABELS = {{mouser: "Mouser", mcmaster: "McMaster-Carr", sendcutsend: "SendCutSend",
  digikey: "DigiKey", pcb: "PCBs", printed: "3D Printed"}};
const PRICE_NAMES = {{mouser: "Mouser", mcmaster: "McMaster-Carr", sendcutsend: "SendCutSend",
  digikey: "Digi-Key", assembly: "In-House Assembly", pcb: "PCB Fabrication"}};

const ORDER_LINKS = {{
  mouser: [["Upload at the Mouser BOM Tool \\u2197", "https://www.mouser.com/bom/"]],
  digikey: [["Upload at DigiKey Lists \\u2197", "https://www.digikey.com/en/mylists/"]],
  mcmaster: [["Order at McMaster-Carr \\u2197", "https://www.mcmaster.com/"]],
  sendcutsend: [["Order parts at SendCutSend \\u2197", "https://sendcutsend.com/"]],
  pcb: [["View boards in PCB Tool \\u2197", "../PCB-Tool/pcb-tool.html"],
        ["Order PCBs at JLCPCB \\u2197", "https://jlcpcb.com/"]],
}};

let state = {{chassis: null, rev: null, variant: "base", vendor: null}};

function releases() {{
  // Chassis releases with vendor BOMs, plus boardless chassis whose content
  // is only mech parts (the parts live on separate mech manifest entries).
  const mechRevs = new Set(Object.values(MANIFEST).filter(e => e.mech)
    .map(e => e.chassis + "|" + e.rev));
  return Object.values(MANIFEST).filter(e => !e.board && !e.mech && e.artifacts &&
    (e.artifacts.vendor_boms || mechRevs.has(e.chassis + "|" + e.rev)));
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
    document.getElementById("meta").textContent = "No chassis BOM exports yet - run: hwrelease update";
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
  renderGuide();
  document.getElementById("preview").innerHTML =
    '<p class="empty">Select a vendor on the left to preview its BOM.</p>';
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
  const varVend = ((est.variant_vendors || {{}})[state.variant]) || null;
  const priceFor = key => state.variant === "base"
    ? estVendors[PRICE_NAMES[key]]
    : (varVend && varVend[key] !== undefined ? varVend[key] : estVendors[PRICE_NAMES[key]]);
  let meta = "Chassis " + e.chassis + " · Rev " + e.rev + " · source tag <code>" + e.source_tag + "</code>" +
    (e.source_url ? ' · <a href="' + e.source_url + '" target="_blank" rel="noopener">source \\u2197</a>' : "");
  const varTotal = state.variant === "base" ? (est.total || estVariants.base) : estVariants[state.variant];
  if (varTotal)
    meta += " · <strong>Est. total (" + (est.qty || 1) + " unit" + ((est.qty || 1) > 1 ? "s" : "") +
            ", " + state.variant + "): $" + varTotal + "</strong>";
  document.getElementById("meta").innerHTML = meta;
  for (const [key, label] of Object.entries(VENDOR_LABELS)) {{
    if (!map[key] && !(key === "printed" && mechParts("3d_print").length)) continue;
    const b = document.createElement("button");
    b.className = "vn" + (state.vendor === key ? " active" : "");
    b.innerHTML = label + (priceFor(key) ? "<small>$" + priceFor(key) + "</small>" : "");
    b.onclick = () => {{ state.vendor = key; renderVendors(); renderGuide(); loadPreview(); }};
    box.appendChild(b);
  }}
  const actions = document.getElementById("actions");
  actions.innerHTML = "";
  for (const [label, url] of (ORDER_LINKS[state.vendor] || [])) {{
    const a = document.createElement("a");
    a.href = url;
    a.target = "_blank"; a.rel = "noopener";
    a.textContent = label;
    actions.appendChild(a);
  }}
  if (state.vendor && map[state.vendor]) {{
    const a = document.createElement("a");
    a.className = "download";
    a.href = ROOT + e.dir + "/" + map[state.vendor];
    a.download = "";
    a.textContent = "Download CSV";
    actions.appendChild(a);
  }}
  if (state.vendor === "mcmaster" && map.mcmaster_paste) {{
    const b = document.createElement("button");
    b.textContent = "Copy order paste";
    b.onclick = async () => {{
      const r = await fetch(ROOT + e.dir + "/" + map.mcmaster_paste);
      await navigator.clipboard.writeText(await r.text());
      b.textContent = "Copied!";
      setTimeout(() => b.textContent = "Copy order paste", 2000);
    }};
    actions.appendChild(b);
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
  if (!state.vendor) return;
  if (state.vendor === "sendcutsend" || state.vendor === "printed") {{
    // Spec cards carry everything for fabricated/printed parts; skip the
    // CSV table (it stays available via Download CSV).
    div.innerHTML = mechCards(state.vendor === "printed" ? "3d_print" : "laser_cut") ||
      '<p class="empty">No part exports for this revision.</p>';
    return;
  }}
  if (!map[state.vendor]) return;
  const r = await fetch(ROOT + e.dir + "/" + map[state.vendor]);
  const rows = parseCSV(await r.text());
  // On the PCBs view, append a gerber-zip download column and a notes column.
  let gerberFor = null, notesFor = {{}}, stepFor = null;
  if (state.vendor === "pcb") {{
    gerberFor = {{}};
    for (const b of Object.values(MANIFEST)) {{
      if (b.board && b.chassis === state.chassis && b.rev === state.rev &&
          b.artifacts) {{
        if (b.artifacts.gerber_zip)
          gerberFor[b.part_number] = ROOT + b.dir + "/" + b.artifacts.gerber_zip;
        const spec = b.artifacts.fab_spec;
        if (spec && (spec.notes || []).length)
          notesFor[b.part_number] = spec.notes.join(" ");
      }}
    }}
  }}
  // On the SendCutSend view, append a STEP download column per mech part row.
  if (state.vendor === "sendcutsend") {{
    stepFor = [];
    for (const p of Object.values(MANIFEST)) {{
      if (p.mech && p.chassis === state.chassis && p.rev === state.rev &&
          p.artifacts && p.artifacts.step)
        stepFor.push([p.part_number, ROOT + p.dir + "/" + p.artifacts.step]);
    }}
  }}
  let html = "<table><thead><tr>";
  for (const h of rows[0]) html += "<th>" + h + "</th>";
  if (gerberFor) html += "<th>Gerbers</th><th>Notes</th>";
  if (stepFor) html += "<th>STEP</th>";
  html += "</tr></thead><tbody>";
  for (const row of rows.slice(1, 501)) {{
    html += "<tr>";
    for (const c of row) html += "<td>" + c + "</td>";
    if (gerberFor) {{
      const url = gerberFor[row[1]];
      html += "<td>" + (url ? '<a href="' + url + '" download>Download zip</a>' : "") + "</td>";
      html += "<td>" + (notesFor[row[1]] || "") + "</td>";
    }}
    if (stepFor) {{
      const hit = stepFor.find(([pn]) => row.includes(pn));
      html += "<td>" + (hit ? '<a href="' + hit[1] + '" download>Download STEP</a>' : "") + "</td>";
    }}
    html += "</tr>";
  }}
  html += "</tbody></table>";
  if (rows.length > 501) html += '<p class="meta">Showing 500 of ' + (rows.length - 1) + " rows.</p>";
  div.innerHTML = html;
}}

function mechParts(proc) {{
  // proc: "laser_cut" | "3d_print" | null (all)
  return Object.values(MANIFEST).filter(x => {{
    if (!x.mech || x.chassis !== state.chassis || x.rev !== state.rev) return false;
    if (!proc) return true;
    const p = (x.artifacts.fab_spec || {{}}).process ||
              (x.artifacts.info_fields || {{}}).Process || "";
    const is3d = p === "3d_print" || p === "3D Printing" ||
                 x.part_number.includes("-PRINTED-");
    return proc === "3d_print" ? is3d : !is3d;
  }});
}}

function mechCards(proc) {{
  const parts = mechParts(proc);
  if (!parts.length) return "";
  let html = '<div class="mech-cards">';
  for (const p of parts) {{
    const a = p.artifacts || {{}};
    const f = a.info_fields || {{}};
    const spec = a.fab_spec || {{}};
    const services = spec.services || {{}};
    const base = ROOT + p.dir + "/";
    html += '<div class="mech-card">';
    if (a.image) html += '<img src="' + base + a.image + '" alt="' + p.part_number + '">';
    html += "<h4>" + p.part_number + "</h4>";
    const bits = [];
    if (f.Qty) bits.push("Qty " + f.Qty);
    const mat = spec.material || a.material || f.Material;
    if (mat) bits.push(mat);
    if (spec.thickness_mm || f.Thickness_mm) bits.push((spec.thickness_mm || f.Thickness_mm) + " mm");
    if (spec.process) bits.push(spec.process);
    else if (f.Process) bits.push(f.Process);
    if (bits.length) html += '<div class="mech-meta">' + bits.join(" · ") + "</div>";
    const svc = [];
    for (const [name, val] of Object.entries(services)) {{
      if (val === true) svc.push(name);
      else if (Array.isArray(val))
        for (const item of val)
          svc.push(name + ": " + (typeof item === "string" ? item :
            (item.thread || item.for || "") + " - " + (item.holes || "")));
    }}
    if (svc.length) html += "<ul>" + svc.map(s => "<li>" + s + "</li>").join("") + "</ul>";
    const notes = spec.notes || [];
    if (notes.length) html += '<div class="mech-notes">' + notes.join(" ") + "</div>";
    html += '<div class="mech-links">';
    if (a.stl) html += '<a href="stl-viewer.html?file=' + ROOT + p.dir + "/" + a.stl +
                       '" target="_blank" rel="noopener">3D view \\u2197</a>';
    if (a.step) html += '<a href="' + base + a.step + '" download>STEP</a>';
    if (f.UnitPrice) html += "<span>$" + f.UnitPrice + " ea</span>";
    html += "</div></div>";
  }}
  return html + "</div>";
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
        print("Manifest is empty - run: hwrelease update")
        return 1
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(render_viewer_html(manifest))
    print(f"Wrote {out_path.relative_to(core.REPO_ROOT)} "
          f"({sum(1 for e in manifest.values() if 'board' in e)} board revision(s))")
    bom_path = out_path.parent.parent / "BOM-Tool" / "bom-tool.html"
    bom_path.parent.mkdir(parents=True, exist_ok=True)
    bom_path.write_text(render_bom_tool_html(manifest))
    print(f"Wrote {bom_path.relative_to(core.REPO_ROOT)} "
          f"({sum(1 for e in manifest.values() if 'board' not in e and 'mech' not in e)} chassis release(s))")
    return 0
