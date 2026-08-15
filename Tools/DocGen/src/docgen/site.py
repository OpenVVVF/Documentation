"""Static site generator for OpenVVVF documentation."""

import re
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

import markdown
import yaml

from .frontmatter import Document, load_docs
from .product import assemble_manual, list_products, load_product


MD = markdown.Markdown(
    extensions=[
        "tables",
        "fenced_code",
        "toc",
        "nl2br",
    ]
)


def template_dir() -> Path:
    """Return the directory containing HTML/CSS templates."""
    return Path(__file__).resolve().parent / "templates"


def repo_root() -> Path:
    """Return the repository root.

    This module lives at Tools/DocGen/src/docgen/site.py.
    """
    return Path(__file__).resolve().parent.parent.parent.parent.parent


def load_template(name: str) -> str:
    """Load a template file as a string."""
    return (template_dir() / name).read_text(encoding="utf-8")


def rel_root(doc_path: Path, output_dir: Path) -> str:
    """Return the relative path from an output HTML file to the site root."""
    try:
        relative = doc_path.parent.relative_to(output_dir)
    except ValueError:
        return "./"
    if relative == Path("."):
        return "./"
    return "../" * len(relative.parts)


_MD_LINK_RE = re.compile(r'href="([^"#?]+?)\.md([#?][^"]*)?"')


def _rewrite_md_links(html: str) -> str:
    """Rewrite relative links to .md sources so they point at built pages.

    `Name.md` becomes `Name.html`; `Index.md` becomes `index.html`, matching
    the directory-index URLs used by the built site. This lets source
    documents interlink with source paths that also work on GitHub.
    """

    def repl(match: re.Match) -> str:
        target, suffix = match.group(1), match.group(2) or ""
        if "://" in target or target.startswith("/"):
            return match.group(0)
        if target.lower() == "index" or target.lower().endswith("/index"):
            base = target[:-5] + "index"
            return f'href="{base}.html{suffix}"'
        return f'href="{target}.html{suffix}"'

    return _MD_LINK_RE.sub(repl, html)


def md_to_html(text: str) -> str:
    """Convert Markdown text to HTML."""
    MD.reset()
    html = MD.convert(text)
    html = _rewrite_md_links(html)
    html = _apply_callout_classes(html)
    html = _wrap_figures(html)
    return html


_FIGURE_RE = re.compile(r'<p><img alt="([^"]*)" src="([^"]+)"\s*/></p>')


def _wrap_figures(html: str) -> str:
    """Wrap standalone images in <figure> with a <figcaption> from the alt text."""

    def repl(m: re.Match) -> str:
        alt, src = m.group(1), m.group(2)
        caption = f"<figcaption>{alt}</figcaption>" if alt else ""
        return f'<figure><img alt="{alt}" src="{src}" />{caption}</figure>'

    return _FIGURE_RE.sub(repl, html)


_CHAPTER_RE = re.compile(r"<(h[12])(\b[^>]*)>(\d+)(\.\d+)?\s+(.+?)</\1>", re.S)


def _apply_chapter_attributes(html: str) -> str:
    """Add data-chapter attributes to headings that start with chapter numbers.

    Examples:
      <h1>1 Preparation</h1> -> <h1 data-chapter="1">1 Preparation</h1>
      <h2>1.2 Substep</h2> -> <h2 data-chapter="1.2">1.2 Substep</h2>
    """

    def repl(match: re.Match) -> str:
        tag = match.group(1)
        attrs = (match.group(2) or "").strip()
        number = match.group(3)
        decimal = match.group(4) or ""
        rest = match.group(5)
        if 'data-chapter' not in attrs:
            attrs = f'{attrs} data-chapter="{number}{decimal}"'.strip()
        if attrs:
            attrs = " " + attrs
        return f"<{tag}{attrs}>{number}{decimal} {rest}</{tag}>"

    return _CHAPTER_RE.sub(repl, html)


_CALLOUT_CLASSES = {
    "danger": "callout-danger",
    "warning": "callout-warning",
    "caution": "callout-warning",
    "note": "callout-note",
    "tip": "callout-tip",
}


def _apply_callout_classes(html: str) -> str:
    """Add callout classes to blockquotes whose first strong tag is a known label."""
    for label, cls in _CALLOUT_CLASSES.items():
        html = re.sub(
            rf'<blockquote>\s*<p>\s*<strong>{label}</strong>',
            f'<blockquote class="{cls}"><p><strong>{label.capitalize()}</strong>',
            html,
            flags=re.IGNORECASE,
        )
    return html


def frontmatter_table(doc: Document) -> str:
    """Render document frontmatter as a collapsible metadata panel."""
    if not doc.frontmatter:
        return ""

    skip_keys = {"prepared", "title"}
    # Hide opaque doc_id when a friendly test_id is present.
    if doc.frontmatter.get("test_id") is not None:
        skip_keys = skip_keys | {"doc_id"}
    skip_values = {"", "N/A", "n/a", "TBD", "tbd", "TODO", "todo", "(not yet reviewed)"}
    rows = []
    for key, value in doc.frontmatter.items():
        if key in skip_keys:
            continue
        if isinstance(value, list):
            value = ", ".join(str(v) for v in value)
        else:
            value = str(value)
        if value in skip_values:
            continue
        label = key.replace("_", " ").capitalize()
        rows.append(f"<tr><th>{label}</th><td>{value}</td></tr>")

    if not rows:
        return ""

    # Compact summary line shown when the panel is collapsed.
    fm = doc.frontmatter
    id_bit = fm.get("test_id") if fm.get("test_id") is not None else fm.get("doc_id")
    summary_bits = [
        id_bit,
        f"v{fm.get('version')}" if fm.get("version") else None,
        fm.get("date"),
    ]
    summary = " · ".join(str(b) for b in summary_bits if b is not None)

    return (
        '<details class="frontmatter">'
        f'<summary><span class="frontmatter-summary">{summary}</span></summary>'
        '<table>'
        + "".join(rows)
        + "</table></details>"
    )


def copy_brand_assets(output_dir: Path) -> None:
    """Copy brand assets (logo, icons, fonts) into the built site."""
    src = template_dir() / "brand"
    shutil.copytree(src, output_dir / "brand", dirs_exist_ok=True)


def cover_page(doc: Optional[Document], root: str = "./") -> str:
    """Render a print-only cover page from document frontmatter."""
    brand = "OpenVVVF"
    if doc is None or not doc.frontmatter:
        return "".join([
            '<div class="print-cover">',
            '<div class="print-cover-accent print-cover-accent-top"></div>',
            '<div class="print-cover-inner">',
            '<header class="print-cover-header">',
            f'<img class="print-cover-logo" src="{root}brand/logo.svg" alt="{brand}">',
            '<div class="print-cover-header-text">',
            '<span class="print-cover-header-doctype">Documentation</span>',
            '</div>',
            '</header>',
            '<div class="print-cover-main">',
            f'<h1 class="print-cover-title">{brand} Documentation</h1>',
            '</div>',
            '</div>',
            '<div class="print-cover-accent print-cover-accent-bottom"></div>',
            '</div>',
        ])

    fm = doc.frontmatter
    doctype = doc.doctype or "Document"
    title = doc.title or doc.path.stem
    description = fm.get("description", "")
    product_line = fm.get("product_line", brand)

    rows = []

    def add_row(label: str, value: Any) -> None:
        if value is None or value == "":
            return
        if isinstance(value, list):
            value = ", ".join(str(v) for v in value)
        rows.append(f"<tr><th>{label}</th><td>{value}</td></tr>")

    add_row("Document ID", fm.get("doc_id"))
    if fm.get("test_id") is not None:
        add_row("Test ID", fm.get("test_id"))
    add_row("Version", fm.get("version"))
    add_row("Date", fm.get("date"))
    add_row("Applies to", fm.get("applies_to"))
    add_row("Product line", product_line)
    add_row("Normative references", fm.get("normative_refs"))

    meta_table = f'<table class="print-cover-meta">{"".join(rows)}</table>' if rows else ""

    info_page = ""
    if meta_table:
        info_page = "".join([
            '<div class="print-info">',
            '<h2 class="print-info-title">Document Information</h2>',
            meta_table,
            '</div>',
        ])

    return "".join([
        '<div class="print-cover">',
        '<div class="print-cover-accent print-cover-accent-top"></div>',
        '<div class="print-cover-inner">',
        '<header class="print-cover-header">',
        f'<img class="print-cover-logo" src="{root}brand/logo.svg" alt="{brand}">',
        '<div class="print-cover-header-text">',
        f'<span class="print-cover-header-doctype">{doctype}</span>',
        '</div>',
        '</header>',
        '<div class="print-cover-main">',
        f'<h1 class="print-cover-title">{title}</h1>',
        (f'<p class="print-cover-description">{description}</p>' if description else ""),
        '</div>',
        '<footer class="print-cover-footer">',
        '<div class="print-cover-sponsors">',
        '<div class="print-cover-sponsors-label">Supported by</div>',
        '<div class="print-cover-sponsor-logos">',
        '<img src="https://cdn.trustedparts.com/company/dd042a20-7bd6-4e96-92c0-203775acde0d-mouser-logo.svg" alt="Mouser Electronics">',
        '<img src="https://upload.wikimedia.org/wikipedia/commons/1/10/Mitsubishi_Electric_logo.svg" alt="Mitsubishi Electric">',
        '<img src="https://sendcutsend.com/wp-content/uploads/2022/11/scs-logo-text-1-1.svg" alt="SendCutSend">',
        '</div>',
        '</div>',
        '</footer>',
        '</div>',
        '<div class="print-cover-accent print-cover-accent-bottom"></div>',
        '</div>',
        info_page,
    ])


def _doc_sort_key(doc: Document) -> tuple:
    """Sort key: nav_order first, then title, then filename."""
    return (doc.nav_order, doc.title or doc.path.stem, doc.path.name)


def _display_name(name: str) -> str:
    """Convert a kebab-case directory/file name to a human-readable title.

    Splits a leading `<N>_` number prefix, replaces dashes with spaces, and
    title-cases the result while preserving obvious acronyms.
    """
    prefix = ""
    body = name
    if "_" in body:
        first, rest = body.split("_", 1)
        if first.isdigit():
            prefix = f"{first} "
            body = rest

    words = body.replace("-", " ").split()
    formatted = []
    for word in words:
        if len(word) > 1 and word.isupper():
            formatted.append(word)
        else:
            formatted.append(word.capitalize())
    return prefix + " ".join(formatted)


def _dir_sort_key(
    rel_dir: Path,
    index_docs: Dict[Path, Document],
) -> tuple:
    """Sort key for directories: index nav_order, then directory name."""
    index_doc = index_docs.get(rel_dir)
    order = index_doc.nav_order if index_doc else 9999
    return (order, rel_dir.name)


_PLACEHOLDER_HINTS = re.compile(
    r"(?i)(content to be|placeholder|under revision|to be added|to be migrated|stub|planned content|will be added|coming soon)"
)


def _is_placeholder_doc(doc: Optional[Document]) -> bool:
    """Return True if a document looks like a placeholder or is marked as one."""
    if doc is None:
        return False
    if doc.frontmatter.get("placeholder"):
        return True
    body = doc.body or ""
    if len(body) < 200:
        return True
    return bool(_PLACEHOLDER_HINTS.search(body))


def _is_menu_only(doc: Optional[Document]) -> bool:
    """Return True if an index document should act as a nav group, not a page."""
    return doc is not None and bool(doc.frontmatter.get("menu_only"))


def _nav_tree(
    docs: List[Document],
    current_doc_id: Optional[str],
    root: str,
    docs_dir: Path,
) -> str:
    """Build a nested sidebar tree from the real Docs/ directory structure.

    Sections with children are rendered as collapsible accordions. Placeholder
    documents are flagged with a WIP marker so users know which links are empty.
    """
    tree: Dict[Path, List[Document]] = {}
    index_docs: Dict[Path, Document] = {}
    all_dirs: set[Path] = set()

    for doc in docs:
        if doc.doc_id == "OV-DOCS-INDEX":
            continue
        rel_parent = doc.path.parent.relative_to(docs_dir)
        tree.setdefault(rel_parent, []).append(doc)
        if doc.path.stem.lower() == "index":
            index_docs[rel_parent] = doc
        # Register this directory and all ancestors so the tree is complete.
        all_dirs.add(rel_parent)
        for ancestor in rel_parent.parents:
            if ancestor != Path("."):
                all_dirs.add(ancestor)

    for rel_parent in tree:
        tree[rel_parent].sort(key=_doc_sort_key)

    docs_by_id = {doc.doc_id: doc for doc in docs}
    current_doc = docs_by_id.get(current_doc_id)

    def _dir_contains_active(rel_dir: Path) -> bool:
        if current_doc is None:
            return False
        current_rel = current_doc.path.parent.relative_to(docs_dir)
        return current_rel == rel_dir or current_rel.is_relative_to(rel_dir)

    def _link_classes(doc: Optional[Document], is_active: bool) -> str:
        classes = []
        if is_active:
            classes.append("active")
        if _is_placeholder_doc(doc):
            classes.append("nav-placeholder")
        return ' class="' + " ".join(classes) + '"' if classes else ""

    def _wip_marker(doc: Optional[Document]) -> str:
        return ' <span class="nav-wip">WIP</span>' if _is_placeholder_doc(doc) else ""

    def render_dir(rel_dir: Path, depth: int) -> str:
        indent = "  " * depth
        items: List[str] = []

        index_doc = index_docs.get(rel_dir)
        dir_docs = [d for d in tree.get(rel_dir, []) if d.path.stem.lower() != "index"]
        child_dirs = sorted(
            [d for d in all_dirs if d != rel_dir and d.parent == rel_dir],
            key=lambda p: _dir_sort_key(p, index_docs),
        )
        has_children = bool(dir_docs or child_dirs)
        is_open = has_children and _dir_contains_active(rel_dir)

        if has_children:
            li_class = "nav-section"
            if not is_open:
                li_class += " nav-section-collapsed"
            li_open = f'{indent}<li class="{li_class}">'
        else:
            li_open = f'{indent}<li>'
        items.append(li_open)

        if has_children:
            items.append(
                f'{indent}  <button class="nav-section-toggle" '
                f'aria-expanded="{str(is_open).lower()}" '
                f'aria-label="Toggle {_display_name(rel_dir.name)}"></button>'
            )

        if index_doc is not None and not _is_menu_only(index_doc):
            href = index_doc.url_path if hasattr(index_doc, "url_path") else "#"
            active = index_doc.doc_id == current_doc_id
            cls = _link_classes(index_doc, active)
            title = index_doc.title or _display_name(rel_dir.name)
            wip = _wip_marker(index_doc)
            items.append(f'{indent}<a href="{root}{href}"{cls}>{title}{wip}</a>')
        elif index_doc is not None:
            title = index_doc.title or _display_name(rel_dir.name)
            wip = _wip_marker(index_doc)
            items.append(f'{indent}<span class="group-label">{title}{wip}</span>')
        else:
            items.append(f'{indent}<span class="group-label">{_display_name(rel_dir.name)}</span>')

        if dir_docs or child_dirs:
            items.append(f'{indent}  <ul>')
            for doc in dir_docs:
                href = doc.url_path if hasattr(doc, "url_path") else "#"
                active = doc.doc_id == current_doc_id
                cls = _link_classes(doc, active)
                title = doc.title or _display_name(doc.path.stem)
                wip = _wip_marker(doc)
                items.append(
                    f'{indent}    <li><a href="{root}{href}"{cls}>{title}{wip}</a></li>'
                )
            for child in child_dirs:
                items.append(render_dir(child, depth + 2))
            items.append(f'{indent}  </ul>')

        items.append(f'{indent}</li>')
        return "\n".join(items)

    top_dirs = sorted(
        [d for d in all_dirs if len(d.parts) == 1],
        key=lambda p: _dir_sort_key(p, index_docs),
    )

    out = ['<h2 class="sidebar-title">Documents</h2>', '<ul class="nav-tree">']
    out.append(f'  <li><a href="{root}index.html">Documentation Index</a></li>')
    for top_dir in top_dirs:
        out.append(render_dir(top_dir, 1))
    out.append('</ul>')
    return "\n".join(out)


def nav_html(
    docs: List[Document],
    current_doc_id: Optional[str],
    root: str,
    docs_dir: Path,
) -> str:
    """Build a sidebar navigation tree from the Docs/ directory structure."""
    return _nav_tree(docs, current_doc_id, root, docs_dir)


def breadcrumbs_html(doc: Document, root: str, docs_dir: Path, docs: List[Document]) -> str:
    """Build breadcrumb links for a document relative to the docs root.

    Uses the index document title for each directory when available, falling
    back to a display-friendly directory name.
    """
    index_by_dir: Dict[Path, Document] = {}
    for d in docs:
        if d.path.stem.lower() == "index":
            rel = d.path.parent.relative_to(docs_dir)
            index_by_dir[rel] = d

    crumbs = [f'<a href="{root}index.html">Index</a>']
    current = Path()
    rel_parent = doc.path.parent.relative_to(docs_dir)
    for part in rel_parent.parts:
        if part in ("Docs", "."):
            continue
        current = current / part
        index_doc = index_by_dir.get(current)
        label = index_doc.title if index_doc else _display_name(part)
        if index_doc is not None and _is_menu_only(index_doc):
            crumbs.append(label)
        else:
            crumbs.append(f'<a href="{root}{current.as_posix()}/index.html">{label}</a>')
    title = doc.title or _display_name(doc.path.stem)
    crumbs.append(title)
    return " / ".join(crumbs)


def url_path(doc_path: Path, docs_dir: Path) -> str:
    """Return the URL path for a document relative to the site root.

    Section Index.md files become lowercase index.html so they act as directory
    index pages.
    """
    rel = doc_path.relative_to(docs_dir)
    if rel.stem.lower() == "index":
        rel = rel.with_name("index.html")
    else:
        rel = rel.with_suffix(".html")
    return str(rel)


def _wip_badge(doc: Document) -> str:
    """Render a small WIP badge for placeholder documents in cards/listings."""
    if not _is_placeholder_doc(doc):
        return ""
    return '<span class="status-badge status-draft">WIP</span>'


def _placeholder_banner(doc: Optional[Document]) -> str:
    """Render a prominent banner if the document is marked as a placeholder."""
    if doc is None or not doc.frontmatter.get("placeholder"):
        return ""
    return (
        '<div class="placeholder-banner">'
        '<strong>Placeholder / Under Revision</strong> - '
        'This page is incomplete or out of date and will be revised.'
        '</div>'
    )


def copy_assets(doc: Document, docs_dir: Path, output_dir: Path) -> None:
    """Copy image/asset files referenced by a Markdown document."""
    src_dir = doc.path.parent
    dst_dir = output_dir / doc.path.parent.relative_to(docs_dir)
    for asset in src_dir.iterdir():
        if asset.is_file() and asset.suffix.lower() in {
            ".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp", ".pdf",
            ".txt", ".csv", ".jsonl", ".html",
        }:
            dst = dst_dir / asset.name
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(asset, dst)


def render_page(
    title: str,
    body_html: str,
    doc: Optional[Document],
    docs: List[Document],
    output_path: Path,
    output_dir: Path,
    docs_dir: Path,
    frontmatter: str = "",
) -> str:
    """Render a full HTML page from the template."""
    root = rel_root(output_path, output_dir)
    if doc:
        nav = nav_html(docs, doc.doc_id, root, docs_dir)
        if doc.doc_id == "OV-DOCS-INDEX":
            # Landing page: no breadcrumbs, no metadata strip.
            crumbs = ""
        else:
            crumbs = breadcrumbs_html(doc, root, docs_dir, docs)
    else:
        nav = nav_html(docs, None, root, docs_dir)
        crumbs = '<a href="{root}index.html">Index</a>'.format(root=root)

    banner = _placeholder_banner(doc)
    body = banner + body_html if banner else body_html

    content_class = ""
    if doc and "Assembly-Guide" in doc.path.parts:
        content_class = "assembly-guide"
    elif doc and doc.doc_id == "OV-DOCS-INDEX":
        content_class = "landing"

    cover = cover_page(doc, root)
    pdf_url = f"{root}pdfs/{doc.doc_id}.pdf" if doc and doc.doc_id else ""

    page = load_template("page.html")
    return page.format(
        title=title,
        body=body,
        nav=nav,
        breadcrumbs=crumbs,
        root=root,
        frontmatter=frontmatter,
        content_class=content_class,
        cover=cover,
        pdf_url=pdf_url,
    )


def build_site(docs_dir: Path, output_dir: Path) -> None:
    """Build a static HTML site from the Markdown documentation tree."""
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    copy_brand_assets(output_dir)

    by_id = load_docs(docs_dir)
    docs = list(by_id.values())

    # Attach URL paths and copy assets.
    for doc in docs:
        doc.url_path = url_path(doc.path, docs_dir)
        copy_assets(doc, docs_dir, output_dir)

    # Render each document (skip the root index; it becomes the landing page).
    # Skip menu-only index documents; they act as navigation groups, not pages.
    for doc in docs:
        if doc.doc_id == "OV-DOCS-INDEX" or _is_menu_only(doc):
            continue
        body = md_to_html(doc.body)
        fm = frontmatter_table(doc)
        output_path = output_dir / doc.url_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        title = doc.title or doc.path.stem
        html = render_page(
            title=title,
            body_html=body,
            doc=doc,
            docs=docs,
            output_path=output_path,
            output_dir=output_dir,
            docs_dir=docs_dir,
            frontmatter=fm,
        )
        output_path.write_text(html, encoding="utf-8")

    # Build directory index pages for directories that do not have an Index.md.
    directories = {doc.path.parent for doc in docs}
    index_dirs = {doc.path.parent for doc in docs if doc.path.stem.lower() == "index"}
    for directory in directories:
        if directory in index_dirs:
            continue
        rel_dir = directory.relative_to(docs_dir)
        dir_docs = [d for d in docs if d.path.parent == directory]
        if not dir_docs:
            continue
        items = []
        for doc in sorted(dir_docs, key=_doc_sort_key):
            title = doc.title or _display_name(doc.path.stem)
            blurb = doc.description or doc.path.name
            # Link is relative to the directory index page itself.
            href = f"{doc.path.stem}.html"
            badge = _wip_badge(doc)
            items.append(
                f'<div class="card"><h3><a href="{href}">{title}</a> {badge}</h3>'
                f'<p>{blurb}</p></div>'
            )
        body = f"<h1>{_display_name(rel_dir.name) or 'Documentation'}</h1>\n<div class=\"landing-grid\">\n" + "\n".join(items) + "\n</div>"
        output_path = output_dir / rel_dir / "index.html"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        html = render_page(
            title=_display_name(rel_dir.name) or "Documentation",
            body_html=body,
            doc=None,
            docs=docs,
            output_path=output_path,
            output_dir=output_dir,
            docs_dir=docs_dir,
        )
        output_path.write_text(html, encoding="utf-8")

    # Build product manual pages.
    products_dir = repo_root() / "Data" / "Products"
    if products_dir.is_dir():
        for product in list_products(products_dir):
            output_path = output_dir / "Manuals" / f"{product.product_id}.html"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            md = assemble_manual(product, docs_dir)
            body = md_to_html(md)
            html = render_page(
                title=product.name,
                body_html=body,
                doc=None,
                docs=docs,
                output_path=output_path,
                output_dir=output_dir,
                docs_dir=docs_dir,
            )
            output_path.write_text(html, encoding="utf-8")

    # Copy CSS.
    shutil.copy2(template_dir() / "style.css", output_dir / "style.css")
    shutil.copy2(template_dir() / "print.css", output_dir / "print.css")

    # Build landing page from Docs/Index.md if available, otherwise synthesize one.
    index_doc = by_id.get("OV-DOCS-INDEX")
    if index_doc:
        index_doc.url_path = "index.html"
        output_path = output_dir / "index.html"
        body = md_to_html(index_doc.body)
        html = render_page(
            title=index_doc.title or "OpenVVVF Documentation",
            body_html=body,
            doc=index_doc,
            docs=docs,
            output_path=output_path,
            output_dir=output_dir,
            docs_dir=docs_dir,
            frontmatter="",
        )
    else:
        landing_body = build_landing_body(docs)
        html = render_page(
            title="OpenVVVF Documentation",
            body_html=landing_body,
            doc=None,
            docs=docs,
            output_path=output_dir / "index.html",
            output_dir=output_dir,
            docs_dir=docs_dir,
        )
    (output_dir / "index.html").write_text(html, encoding="utf-8")

    print(f"Wrote site to {output_dir}")


def build_landing_body(docs: List[Document]) -> str:
    """Build the body HTML for the site landing page."""
    sections: Dict[str, List[Document]] = {}
    for doc in docs:
        if doc.doc_id == "OV-DOCS-INDEX":
            continue
        parts = doc.path.parent.parts
        section = "General"
        if "Control-Assembly" in parts:
            section = "Control Assembly"
        elif "Power-Stages" in parts:
            section = "Power Stages"
        elif "Safety-and-Compliance" in parts:
            section = "Safety and Compliance"
        elif "Software" in parts:
            section = "Software"
        elif "Testing" in parts:
            section = "Testing"
        elif "Tools" in parts:
            section = "Tools"
        sections.setdefault(section, []).append(doc)

    out = ['<h1>OpenVVVF Documentation</h1>']
    out.append(
        '<p>Static site for OpenVVVF product documentation, safety analyses, '
        'power-stage guides, software targets, and test evidence.</p>'
    )
    for section in sorted(sections.keys()):
        out.append(f"<h2>{section}</h2>")
        out.append('<div class="landing-grid">')
        for doc in sorted(sections[section], key=_doc_sort_key):
            href = doc.url_path
            title = doc.title or _display_name(doc.path.stem)
            blurb = doc.description or doc.path.name
            badge = _wip_badge(doc)
            out.append(
                f'<div class="card"><h3><a href="{href}">{title}</a> {badge}</h3>'
                f'<p>{blurb}</p></div>'
            )
        out.append("</div>")
    return "\n".join(out)
