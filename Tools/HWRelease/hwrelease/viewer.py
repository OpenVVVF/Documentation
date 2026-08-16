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
@media (max-width: 800px) {{
  .layout {{ flex-direction: column; }}
  aside {{ width: 100%; border-right: none; border-bottom: 1px solid var(--border-light); }}
}}
</style>
</head>
<body>
<header>
  <img src="{root}brand/logo.png" alt="OpenVVVF">
  <h1>OpenVVVF<span class="sep">/</span>PCB Tool</h1>
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
  return Object.values(MANIFEST).sort((a, b) => a.part_number.localeCompare(b.part_number));
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
          f"({len(manifest)} board revision(s))")
    return 0
