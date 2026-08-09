"""PDF generation for OpenVVVF documentation pages."""

import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

from .frontmatter import Document, load_docs
from .site import _is_menu_only, url_path


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
            generated.append(output_path)
            print(f"Wrote {output_path}")
        except RuntimeError as e:
            print(f"ERROR generating PDF for {doc_id}: {e}", file=sys.stderr)
    return generated
