"""PDF generation for OpenVVVF documentation pages."""

import io
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

from .frontmatter import Document, load_docs
from .site import _is_menu_only, template_dir, url_path

# A4 page geometry matching the @page rule in print.css (2.4cm/2cm top/bottom,
# 1.8cm left/right margins).
_MARGIN_X = 1.8 * 28.3465  # left/right margin in pt
_LINE_Y = 2.0 * 28.3465 - 8  # footer divider, just below the content area
_TEXT_Y = _LINE_Y - 22  # footer baseline, roughly centered in the bottom margin
_HEADER_LINE_OFFSET = 16  # header divider sits this far above the content area
_FONT_SIZE = 10
_HEADER_FONT_SIZE = 8.5
_LOGO_H = 10.6
_LOGO_W = _LOGO_H * 1600 / 405  # brand logo aspect ratio
_GREY = (156 / 255, 163 / 255, 175 / 255)  # #9ca3af, same as the footer text
_DARK_GREY = (90 / 255, 90 / 255, 90 / 255)  # #5a5a5a, header text
_LINE_GREY = (233 / 255, 236 / 255, 239 / 255)  # #e9ecef


def _stamp_running(
    pdf_path: Path, footer_text: str, header_title: str, header_id: str
) -> None:
    """Stamp the running header (doc title/id + rule) and footer (logo,
    doc line, page number) onto the finished PDF.

    Chromium's page margin boxes cannot render images and glue their rules
    to the content edge, so all running elements are drawn directly onto
    the PDF instead of via CSS. The cover page only gets a page number.
    """
    from pypdf import PdfReader, PdfWriter
    from reportlab.pdfgen import canvas

    logo_path = template_dir() / "brand" / "logo-grey.png"
    reader = PdfReader(str(pdf_path))
    writer = PdfWriter()
    for index, page in enumerate(reader.pages):
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)
        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=(width, height))
        if index > 0:
            header_line_y = height - 2.4 * 28.3465 + _HEADER_LINE_OFFSET
            c.setStrokeColorRGB(*_LINE_GREY)
            c.setLineWidth(0.5)
            c.line(_MARGIN_X, header_line_y, width - _MARGIN_X, header_line_y)
            c.line(_MARGIN_X, _LINE_Y, width - _MARGIN_X, _LINE_Y)
            c.setFillColorRGB(*_DARK_GREY)
            c.setFont("Helvetica", _HEADER_FONT_SIZE)
            c.drawString(_MARGIN_X, header_line_y + 8, header_title)
            c.drawRightString(width - _MARGIN_X, header_line_y + 8, header_id)
            if logo_path.exists():
                c.drawImage(
                    str(logo_path),
                    _MARGIN_X,
                    _TEXT_Y - 2,
                    width=_LOGO_W,
                    height=_LOGO_H,
                    mask="auto",
                )
            c.setFillColorRGB(*_GREY)
            c.setFont("Helvetica", _FONT_SIZE)
            c.drawString(_MARGIN_X + _LOGO_W + 7, _TEXT_Y, footer_text)
        c.setFillColorRGB(*_GREY)
        c.setFont("Helvetica", _FONT_SIZE)
        c.drawRightString(width - _MARGIN_X, _TEXT_Y, str(index + 1))
        c.showPage()
        c.save()
        buf.seek(0)
        page.merge_page(PdfReader(buf).pages[0])
        writer.add_page(page)
    with open(pdf_path, "wb") as f:
        writer.write(f)


def _html_path_for_doc(doc: Document, docs_dir: Path, site_dir: Path) -> Path:
    """Return the rendered HTML path for a document.

    Uses the same path logic as the site generator so filenames always match.
    """
    return site_dir / url_path(doc.path, docs_dir)


def _find_chromium() -> Optional[str]:
    """Return the path to a Chromium/Chrome executable, or None."""
    for name in ("chromium", "chromium-browser", "google-chrome-stable", "google-chrome", "chrome"):
        path = shutil.which(name)
        if path:
            return path
    return None


def html_to_pdf(
    html_path: Path,
    output_path: Path,
    chromium_path: Optional[str] = None,
) -> None:
    """Render a local HTML file to a clean PDF using Chromium headless."""
    if chromium_path is None:
        chromium_path = _find_chromium()
    if chromium_path is None:
        raise RuntimeError(
            "No Chromium/Chrome executable found. "
            "Install Chromium or pass --chromium with the full path."
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    url = html_path.resolve().as_uri()
    cmd = [
        chromium_path,
        "--headless",
        "--disable-gpu",
        "--no-pdf-header-footer",
        "--run-all-compositor-stages-before-draw",
        f"--print-to-pdf={output_path}",
        url,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"Chromium failed to generate PDF (exit {result.returncode}):\n"
            f"{result.stderr}\n{result.stdout}"
        )


def build_pdf(
    doc_id: str,
    docs_dir: Path,
    site_dir: Path,
    output_dir: Path,
    chromium_path: Optional[str] = None,
) -> Path:
    """Generate a PDF for a single document by doc_id."""
    by_id = load_docs(docs_dir)
    if doc_id not in by_id:
        raise ValueError(f"Document not found: {doc_id}")

    doc = by_id[doc_id]
    html_path = _html_path_for_doc(doc, docs_dir, site_dir)
    if not html_path.exists():
        raise FileNotFoundError(
            f"HTML not found for {doc_id}: {html_path}\n"
            "Run 'docgen site' first."
        )

    output_path = output_dir / f"{doc_id}.pdf"
    html_to_pdf(html_path, output_path, chromium_path)
    _stamp_running(
        output_path,
        f"/  Documentation  /  {doc.doctype or 'Document'}",
        doc.title or doc_id,
        doc.doc_id or "",
    )
    return output_path


def build_all_pdfs(
    docs_dir: Path,
    site_dir: Path,
    output_dir: Path,
    chromium_path: Optional[str] = None,
) -> list[Path]:
    """Generate a PDF for every document in the docs tree."""
    by_id = load_docs(docs_dir)
    generated: list[Path] = []
    for doc_id, doc in by_id.items():
        # Skip navigation-only pages and the root landing page.
        if doc_id == "OV-DOCS-INDEX" or _is_menu_only(doc):
            continue
        html_path = _html_path_for_doc(doc, docs_dir, site_dir)
        if not html_path.exists():
            print(f"Skipping {doc_id}: HTML not found at {html_path}", file=sys.stderr)
            continue
        output_path = output_dir / f"{doc_id}.pdf"
        try:
            html_to_pdf(html_path, output_path, chromium_path)
            _stamp_running(
                output_path,
                f"/  Documentation  /  {doc.doctype or 'Document'}",
                doc.title or doc_id,
                doc.doc_id or "",
            )
            generated.append(output_path)
            print(f"Wrote {output_path}")
        except RuntimeError as e:
            print(f"ERROR generating PDF for {doc_id}: {e}", file=sys.stderr)
    return generated
