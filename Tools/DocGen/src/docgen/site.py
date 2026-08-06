"""Static site generator for OpenVVVF documentation."""

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


def md_to_html(text: str) -> str:
    """Convert Markdown text to HTML."""
    MD.reset()
    return MD.convert(text)


def frontmatter_table(doc: Document) -> str:
    """Render document frontmatter as a small HTML table, if present."""
    if not doc.frontmatter:
        return ""
    rows = []
    for key, value in doc.frontmatter.items():
        if isinstance(value, list):
            value = ", ".join(str(v) for v in value)
        rows.append(f"<tr><th>{key}</th><td>{value}</td></tr>")
    return (
        '<div class="frontmatter">'
        '<table>'
        + "".join(rows)
        + "</table></div>"
    )


def nav_html(docs: List[Document], current_doc_id: Optional[str], root: str) -> str:
    """Build a sidebar navigation grouped by parent directory."""
    groups: Dict[str, List[Document]] = {}
    for doc in docs:
        if doc.doc_id == "OV-DOCS-INDEX":
            continue
        group = "General"
        parts = doc.path.parent.parts
        if "Platform" in parts:
            group = "Platform"
        elif "PowerStages" in parts:
            group = "Power Stages"
        elif "Software" in parts:
            group = "Software"
        elif "Manuals" in parts:
            group = "Manuals"
        groups.setdefault(group, []).append(doc)

    out = []
    out.append('<h2 class="sidebar-title">Documents</h2>')
    out.append("<ul>")
    out.append(f'<li><a href="{root}index.html">Documentation Index</a></li>')
    out.append("</ul>")

    for group in sorted(groups.keys()):
        out.append(f'<div class="group"><div class="group-label">{group}</div><ul>')
        for doc in sorted(groups[group], key=lambda d: d.title or d.path.name):
            href = doc.url_path if hasattr(doc, "url_path") else "#"
            active = ' class="active"' if doc.doc_id == current_doc_id else ""
            title = doc.title or doc.path.stem
            out.append(f'<li><a href="{root}{href}"{active}>{title}</a></li>')
        out.append("</ul></div>")

    return "\n".join(out)


def breadcrumbs_html(doc: Document, root: str) -> str:
    """Build breadcrumb links for a document."""
    crumbs = [f'<a href="{root}index.html">Index</a>']
    current = ""
    for part in doc.path.parent.parts:
        if part in ("Docs", "."):
            continue
        current += part + "/"
        crumbs.append(f'<a href="{root}{current}index.html">{part}</a>')
    title = doc.title or doc.path.stem
    crumbs.append(title)
    return " / ".join(crumbs)


def url_path(doc_path: Path, docs_dir: Path) -> str:
    """Return the URL path for a document relative to the site root."""
    rel = doc_path.relative_to(docs_dir)
    return str(rel.with_suffix(".html"))


def copy_assets(doc: Document, docs_dir: Path, output_dir: Path) -> None:
    """Copy image/asset files referenced by a Markdown document."""
    src_dir = doc.path.parent
    dst_dir = output_dir / doc.path.parent.relative_to(docs_dir)
    for asset in src_dir.iterdir():
        if asset.is_file() and asset.suffix.lower() in {
            ".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp", ".pdf"
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
        nav = nav_html(docs, doc.doc_id, root)
        crumbs = breadcrumbs_html(doc, root)
    else:
        nav = nav_html(docs, None, root)
        crumbs = '<a href="{root}index.html">Index</a>'.format(root=root)

    page = load_template("page.html")
    return page.format(
        title=title,
        body=body_html,
        nav=nav,
        breadcrumbs=crumbs,
        root=root,
        frontmatter=frontmatter,
    )


def build_site(docs_dir: Path, output_dir: Path) -> None:
    """Build a static HTML site from the Markdown documentation tree."""
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    by_id = load_docs(docs_dir)
    docs = list(by_id.values())

    # Attach URL paths and copy assets.
    for doc in docs:
        doc.url_path = url_path(doc.path, docs_dir)
        copy_assets(doc, docs_dir, output_dir)

    # Render each document (skip the root index; it becomes the landing page).
    for doc in docs:
        if doc.doc_id == "OV-DOCS-INDEX":
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

    # Build directory index pages.
    directories = {doc.path.parent for doc in docs}
    for directory in directories:
        rel_dir = directory.relative_to(docs_dir)
        dir_docs = [d for d in docs if d.path.parent == directory]
        if not dir_docs:
            continue
        items = []
        for doc in sorted(dir_docs, key=lambda d: d.title or d.path.name):
            title = doc.title or doc.path.stem
            items.append(
                f'<div class="card"><h3><a href="{doc.path.stem}.html">{title}</a></h3>'
                f'<p>{doc.path.name}</p></div>'
            )
        body = f"<h1>{rel_dir.name or 'Documentation'}</h1>\n<div class=\"landing-grid\">\n" + "\n".join(items) + "\n</div>"
        output_path = output_dir / rel_dir / "index.html"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        html = render_page(
            title=rel_dir.name or "Documentation",
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

    # Build landing page from Docs/Index.md if available, otherwise synthesize one.
    index_doc = by_id.get("OV-DOCS-INDEX")
    if index_doc:
        index_doc.url_path = "index.html"
        output_path = output_dir / "index.html"
        body = md_to_html(index_doc.body)
        fm = frontmatter_table(index_doc)
        html = render_page(
            title=index_doc.title or "OpenVVVF Documentation",
            body_html=body,
            doc=index_doc,
            docs=docs,
            output_path=output_path,
            output_dir=output_dir,
            docs_dir=docs_dir,
            frontmatter=fm,
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
        if "Platform" in parts:
            section = "Platform"
        elif "PowerStages" in parts:
            section = "Power Stages"
        elif "Software" in parts:
            section = "Software"
        elif "Manuals" in parts:
            section = "Manuals"
        sections.setdefault(section, []).append(doc)

    out = ['<h1>OpenVVVF Documentation</h1>']
    out.append(
        '<p>Static site for OpenVVVF product documentation, safety analyses, '
        'power-stage guides, and software targets.</p>'
    )
    for section in sorted(sections.keys()):
        out.append(f"<h2>{section}</h2>")
        out.append('<div class="landing-grid">')
        for doc in sorted(sections[section], key=lambda d: d.title or d.path.name):
            href = doc.url_path
            title = doc.title or doc.path.stem
            out.append(
                f'<div class="card"><h3><a href="{href}">{title}</a></h3>'
                f'<p>{doc.path.name}</p></div>'
            )
        out.append("</div>")
    return "\n".join(out)
