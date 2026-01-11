# scripts/utils/pdf.py
"""Conversion DOCX vers PDF avec validation et trim à 1 page."""

import subprocess
import shutil
from pathlib import Path


class PageLimitExceeded(Exception):
    """Raised when a document exceeds the 1-page limit."""
    def __init__(self, pdf_path: Path, page_count: int):
        self.pdf_path = pdf_path
        self.page_count = page_count
        super().__init__(f"Document has {page_count} pages (limit: 1): {pdf_path.name}")


def get_page_count(pdf_path: str | Path) -> int:
    """
    Returns the number of pages in a PDF.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        Number of pages, or 0 if unable to read
    """
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(pdf_path)
        return len(reader.pages)
    except Exception:
        return 0


def convert_to_pdf(docx_path: str | Path, output_folder: str | Path) -> Path | None:
    """
    Convertit un DOCX en PDF dans le dossier spécifié.

    Args:
        docx_path: Chemin vers le fichier DOCX
        output_folder: Dossier de destination pour le PDF

    Returns:
        Path vers le PDF généré, ou None si échec
    """
    docx_path = Path(docx_path).resolve()
    output_folder = Path(output_folder).resolve()
    output_folder.mkdir(parents=True, exist_ok=True)

    pdf_name = docx_path.stem + ".pdf"
    pdf_path = output_folder / pdf_name

    # Essayer LibreOffice d'abord
    try:
        subprocess.run([
            "soffice", "--headless", "--convert-to", "pdf",
            "--outdir", str(output_folder), str(docx_path)
        ], check=True, capture_output=True)
        return pdf_path
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    # Fallback: docx2pdf (Windows)
    try:
        from docx2pdf import convert
        convert(str(docx_path), str(pdf_path))
        return pdf_path
    except ImportError:
        print("[WARNING] PDF conversion skipped (install LibreOffice or docx2pdf)")
        return None


def trim_to_one_page(pdf_path: str | Path) -> bool:
    """
    Garde uniquement la première page d'un PDF.

    Args:
        pdf_path: Chemin vers le PDF à trimmer

    Returns:
        True si succès, False sinon
    """
    try:
        from PyPDF2 import PdfReader, PdfWriter
    except ImportError:
        print("[WARNING] PyPDF2 not installed - PDF may contain extra pages")
        return False

    pdf_path = Path(pdf_path)
    temp_path = pdf_path.with_suffix(".temp.pdf")

    try:
        reader = PdfReader(pdf_path)
        writer = PdfWriter()

        if len(reader.pages) > 0:
            writer.add_page(reader.pages[0])

        with open(temp_path, 'wb') as f:
            writer.write(f)

        shutil.move(temp_path, pdf_path)
        return True
    except Exception as e:
        print(f"[WARNING] Page trimming failed: {e}")
        if temp_path.exists():
            temp_path.unlink()
        return False


def convert_and_trim(docx_path: str | Path, output_folder: str | Path) -> tuple[Path | None, int]:
    """
    Convertit DOCX en PDF et garde uniquement la première page.

    Args:
        docx_path: Chemin vers le fichier DOCX
        output_folder: Dossier de destination pour le PDF

    Returns:
        Tuple (pdf_path, original_page_count):
        - pdf_path: Path vers le PDF généré (1 page), ou None si échec
        - original_page_count: Nombre de pages avant trim (0 si échec)
    """
    pdf_path = convert_to_pdf(docx_path, output_folder)
    if pdf_path and pdf_path.exists():
        original_page_count = get_page_count(pdf_path)
        trim_to_one_page(pdf_path)
        return pdf_path, original_page_count
    return None, 0
