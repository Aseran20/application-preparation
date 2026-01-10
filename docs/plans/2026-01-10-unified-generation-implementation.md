# Unified Generation Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Refactoriser le système de génération CV/lettre en une commande unique `/generate` avec architecture modulaire et content.json intermédiaire.

**Architecture:** Extraire le code dupliqué (PDF, DOCX) dans `scripts/utils/`, créer un orchestrateur `generate.py` qui lit/écrit `content.json`, et une seule commande Claude qui fait tout.

**Tech Stack:** Python 3.13, python-docx, PyPDF2, docx2pdf

---

## Phase 1 : Utils partagés

### Task 1: Créer config.py

**Files:**
- Create: `scripts/utils/__init__.py`
- Create: `scripts/utils/config.py`

**Step 1: Créer le dossier utils**

```bash
mkdir -p scripts/utils
```

**Step 2: Créer __init__.py vide**

```python
# scripts/utils/__init__.py
```

**Step 3: Créer config.py avec les constantes**

```python
# scripts/utils/config.py
"""Configuration centralisée pour la génération de documents."""

from pathlib import Path

# Chemins
PROJECT_ROOT = Path(__file__).parent.parent.parent
TEMPLATES_DIR = PROJECT_ROOT / "templates"
JOBS_DIR = PROJECT_ROOT / "jobs"
DATA_DIR = PROJECT_ROOT / "data"

# Templates
TEMPLATES = {
    "resume": TEMPLATES_DIR / "Resume - Adrian Turion.docx",
    "cover_letter": TEMPLATES_DIR / "Cover Letter - Adrian Turion.docx"
}

# Noms des fichiers de sortie
OUTPUT_NAMES = {
    "resume_docx": "Resume_Adrian_Turion.docx",
    "resume_pdf": "Resume_Adrian_Turion.pdf",
    "cover_letter_docx": "Cover_Letter_Adrian_Turion.docx",
    "cover_letter_pdf": "Cover_Letter_Adrian_Turion.pdf",
    "content": "content.json"
}

# Formatting
FONT_NAME = "Times New Roman"
FONT_SIZE_PT = 10

# Placeholders CV
RESUME_PLACEHOLDERS = {
    "summary": "[Your professional summary here - describe your background, expertise, and career goals]",
    "auraia_1": "[Describe your key responsibility or achievement here W1-B1]",
    "auraia_2": "[Describe your key responsibility or achievement here W1-B2]",
    "auraia_3": "[Describe your key responsibility or achievement here W1-B3]",
    "rc": "[Describe your key responsibility or achievement here W2-B1]",
    "europ": "[Describe your key responsibility or achievement here W3-B1]",
    "leadership_1": "[Describe your key responsibility or achievement here L-B1]",
    "leadership_2": "[Describe your key responsibility or achievement here L-B2]",
    "leadership_3": "[Describe your key responsibility or achievement here L-B3]",
    "courses": "[Relevant coursework here]",
    "skills": "[Relevant software here]"
}

# Placeholders lettre
COVER_LETTER_PLACEHOLDERS = {
    "date": "[DATE]",
    "recipient": "[RECIPIENT_NAME]",
    "street": "[STREET_NUMBER]",
    "postal": "[POSTAL_CITY_COUNTRY]",
    "company": "[COMPANY_NAME]",
    "salutation": "[SALUTATION]",
    "intro": "[INTRO_PARAGRAPH]",
    "body_1": "[BODY_PARAGRAPH_1]",
    "body_2": "[BODY_PARAGRAPH_2]",
    "body_3": "[BODY_PARAGRAPH_3]",
    "additional": "[ADDITIONAL_CONTEXT]",
    "attraction": "[COMPANY_ATTRACTION]",
    "closing": "[CLOSING_PARAGRAPH]"
}
```

**Step 4: Commit**

```bash
git add scripts/utils/
git commit -m "feat: add config.py with centralized constants"
```

---

### Task 2: Créer pdf.py

**Files:**
- Create: `scripts/utils/pdf.py`

**Step 1: Créer pdf.py avec la logique de conversion**

```python
# scripts/utils/pdf.py
"""Conversion DOCX vers PDF avec trim à 1 page."""

import subprocess
import shutil
from pathlib import Path


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


def convert_and_trim(docx_path: str | Path, output_folder: str | Path) -> Path | None:
    """
    Convertit DOCX en PDF et garde uniquement la première page.

    Args:
        docx_path: Chemin vers le fichier DOCX
        output_folder: Dossier de destination pour le PDF

    Returns:
        Path vers le PDF généré (1 page), ou None si échec
    """
    pdf_path = convert_to_pdf(docx_path, output_folder)
    if pdf_path and pdf_path.exists():
        trim_to_one_page(pdf_path)
        return pdf_path
    return None
```

**Step 2: Commit**

```bash
git add scripts/utils/pdf.py
git commit -m "feat: add pdf.py with convert and trim functions"
```

---

### Task 3: Créer docx.py

**Files:**
- Create: `scripts/utils/docx.py`

**Step 1: Créer docx.py avec la logique de manipulation Word**

```python
# scripts/utils/docx.py
"""Manipulation de documents Word - remplacement de placeholders."""

import re
from docx import Document
from docx.shared import Pt
from .config import FONT_NAME, FONT_SIZE_PT


def replace_placeholder(paragraph, placeholder: str, replacement: str, support_markdown: bool = False) -> bool:
    """
    Remplace un placeholder dans un paragraphe en préservant le formatting.

    Args:
        paragraph: Paragraphe python-docx
        placeholder: Texte à remplacer
        replacement: Texte de remplacement
        support_markdown: Si True, parse **bold** syntax

    Returns:
        True si remplacement effectué, False sinon
    """
    full_text = paragraph.text

    if placeholder not in full_text:
        return False

    # Récupérer le formatting original
    original_font_name = FONT_NAME
    original_font_size = Pt(FONT_SIZE_PT)

    for run in paragraph.runs:
        if run.text.strip():
            if run.font.name:
                original_font_name = run.font.name
            if run.font.size:
                original_font_size = run.font.size
            break

    # Remplacer le texte
    new_text = full_text.replace(placeholder, replacement)

    # Appliquer le nouveau texte
    if support_markdown and '**' in new_text:
        _apply_markdown_formatting(paragraph, new_text, original_font_name, original_font_size)
    else:
        _apply_simple_text(paragraph, new_text, original_font_name, original_font_size)

    return True


def _apply_simple_text(paragraph, text: str, font_name: str, font_size):
    """Applique du texte simple sans markdown."""
    # Clear all runs
    for run in paragraph.runs:
        run.text = ""

    # Add text to first run
    if paragraph.runs:
        first_run = paragraph.runs[0]
    else:
        first_run = paragraph.add_run()

    first_run.text = text
    first_run.font.name = font_name
    first_run.font.size = font_size
    first_run.font.bold = None
    first_run.font.italic = None


def _apply_markdown_formatting(paragraph, text: str, font_name: str, font_size):
    """Parse **bold** syntax et applique le formatting Word."""
    # Clear all runs
    for run in paragraph.runs:
        run.text = ""

    # Split by **text** pattern
    parts = re.split(r'(\*\*.*?\*\*)', text)

    for part in parts:
        if not part:
            continue

        if part.startswith('**') and part.endswith('**'):
            # Bold text
            bold_text = part[2:-2]
            run = paragraph.add_run(bold_text)
            run.font.name = font_name
            run.font.size = font_size
            run.font.bold = True
        else:
            # Normal text
            run = paragraph.add_run(part)
            run.font.name = font_name
            run.font.size = font_size
            run.font.bold = None


def replace_all_placeholders(doc: Document, replacements: dict, support_markdown: bool = False):
    """
    Remplace tous les placeholders dans un document.

    Args:
        doc: Document python-docx
        replacements: Dict {placeholder: replacement}
        support_markdown: Si True, parse **bold** syntax
    """
    # Process tables
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    for placeholder, replacement in replacements.items():
                        if replacement:  # Skip empty replacements
                            replace_placeholder(paragraph, placeholder, replacement, support_markdown)

    # Process regular paragraphs
    for paragraph in doc.paragraphs:
        for placeholder, replacement in replacements.items():
            if replacement:
                replace_placeholder(paragraph, placeholder, replacement, support_markdown)


def remove_empty_paragraphs(doc: Document, placeholders_to_remove: list[str] = None):
    """
    Supprime les paragraphes vides ou contenant certains placeholders.

    Args:
        doc: Document python-docx
        placeholders_to_remove: Liste de placeholders dont les paragraphes doivent être supprimés
    """
    if placeholders_to_remove:
        # Remove paragraphs containing specific placeholders
        paragraphs_to_remove = []
        for paragraph in doc.paragraphs:
            for placeholder in placeholders_to_remove:
                if placeholder in paragraph.text:
                    paragraphs_to_remove.append(paragraph)
                    break

        for paragraph in paragraphs_to_remove:
            p_element = paragraph._element
            p_element.getparent().remove(p_element)

    # Remove trailing empty paragraphs
    while len(doc.paragraphs) > 0:
        last_para = doc.paragraphs[-1]
        if not last_para.text.strip():
            p_element = last_para._element
            p_element.getparent().remove(p_element)
        else:
            break
```

**Step 2: Commit**

```bash
git add scripts/utils/docx.py
git commit -m "feat: add docx.py with placeholder replacement and markdown support"
```

---

## Phase 2 : Refactoriser les scripts de génération

### Task 4: Créer resume.py (nouvelle version)

**Files:**
- Create: `scripts/resume.py`

**Step 1: Créer le nouveau resume.py qui lit content.json**

```python
# scripts/resume.py
"""Génération de CV depuis content.json."""

import json
from pathlib import Path
from docx import Document

from utils.config import TEMPLATES, OUTPUT_NAMES, RESUME_PLACEHOLDERS
from utils.docx import replace_all_placeholders, remove_empty_paragraphs
from utils.pdf import convert_and_trim


def generate_resume(content: dict, output_folder: str | Path) -> tuple[Path, Path | None]:
    """
    Génère un CV depuis le content.json.

    Args:
        content: Dict contenant les données (depuis content.json)
        output_folder: Dossier de destination

    Returns:
        Tuple (docx_path, pdf_path)
    """
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)

    # Charger le template
    doc = Document(TEMPLATES["resume"])

    # Construire les remplacements depuis content.json
    resume_data = content.get("resume", {})

    replacements = {
        RESUME_PLACEHOLDERS["summary"]: resume_data.get("professional_summary", ""),
        RESUME_PLACEHOLDERS["auraia_1"]: resume_data.get("auraia_bullets", ["", "", ""])[0],
        RESUME_PLACEHOLDERS["auraia_2"]: resume_data.get("auraia_bullets", ["", "", ""])[1],
        RESUME_PLACEHOLDERS["auraia_3"]: resume_data.get("auraia_bullets", ["", "", ""])[2],
        RESUME_PLACEHOLDERS["rc"]: resume_data.get("rc_bullet", ""),
        RESUME_PLACEHOLDERS["europ"]: resume_data.get("europ_bullet", ""),
        RESUME_PLACEHOLDERS["leadership_1"]: resume_data.get("leadership_bullets", ["", "", ""])[0],
        RESUME_PLACEHOLDERS["leadership_2"]: resume_data.get("leadership_bullets", ["", "", ""])[1],
        RESUME_PLACEHOLDERS["leadership_3"]: resume_data.get("leadership_bullets", ["", "", ""])[2],
        RESUME_PLACEHOLDERS["courses"]: resume_data.get("courses", ""),
        RESUME_PLACEHOLDERS["skills"]: resume_data.get("skills", "")
    }

    # Remplacer les placeholders
    replace_all_placeholders(doc, replacements, support_markdown=False)

    # Supprimer les paragraphes vides trailing
    remove_empty_paragraphs(doc)

    # Sauvegarder le DOCX
    docx_path = output_folder / OUTPUT_NAMES["resume_docx"]
    doc.save(docx_path)
    print(f"[DOCX] {docx_path}")

    # Générer le PDF
    pdf_folder = output_folder / "PDF"
    pdf_path = convert_and_trim(docx_path, pdf_folder)
    if pdf_path:
        print(f"[PDF] {pdf_path} (1 page)")

    return docx_path, pdf_path


def generate_resume_from_file(content_path: str | Path, output_folder: str | Path = None) -> tuple[Path, Path | None]:
    """
    Génère un CV depuis un fichier content.json.

    Args:
        content_path: Chemin vers content.json
        output_folder: Dossier de destination (défaut: même dossier que content.json)

    Returns:
        Tuple (docx_path, pdf_path)
    """
    content_path = Path(content_path)

    with open(content_path, 'r', encoding='utf-8') as f:
        content = json.load(f)

    if output_folder is None:
        output_folder = content_path.parent

    return generate_resume(content, output_folder)
```

**Step 2: Commit**

```bash
git add scripts/resume.py
git commit -m "feat: add new resume.py reading from content.json"
```

---

### Task 5: Créer cover_letter.py (nouvelle version)

**Files:**
- Create: `scripts/cover_letter.py`

**Step 1: Créer le nouveau cover_letter.py qui lit content.json**

```python
# scripts/cover_letter.py
"""Génération de lettre de motivation depuis content.json."""

import json
from pathlib import Path
from datetime import datetime
from docx import Document

from utils.config import TEMPLATES, OUTPUT_NAMES, COVER_LETTER_PLACEHOLDERS
from utils.docx import replace_all_placeholders, remove_empty_paragraphs
from utils.pdf import convert_and_trim


def generate_cover_letter(content: dict, output_folder: str | Path) -> tuple[Path, Path | None]:
    """
    Génère une lettre de motivation depuis le content.json.

    Args:
        content: Dict contenant les données (depuis content.json)
        output_folder: Dossier de destination

    Returns:
        Tuple (docx_path, pdf_path)
    """
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)

    # Charger le template
    doc = Document(TEMPLATES["cover_letter"])

    # Extraire les données
    metadata = content.get("metadata", {})
    cl_data = content.get("cover_letter", {})

    # Date et salutation
    current_date = datetime.now().strftime("%B %d, %Y")
    recipient = cl_data.get("recipient", "Hiring Manager")
    salutation = f"Dear {recipient},"

    # Construire les remplacements
    replacements = {
        COVER_LETTER_PLACEHOLDERS["date"]: current_date,
        COVER_LETTER_PLACEHOLDERS["recipient"]: recipient,
        COVER_LETTER_PLACEHOLDERS["street"]: cl_data.get("street", ""),
        COVER_LETTER_PLACEHOLDERS["postal"]: cl_data.get("postal", ""),
        COVER_LETTER_PLACEHOLDERS["company"]: metadata.get("company", ""),
        COVER_LETTER_PLACEHOLDERS["salutation"]: salutation,
        COVER_LETTER_PLACEHOLDERS["intro"]: cl_data.get("intro", ""),
        COVER_LETTER_PLACEHOLDERS["body_1"]: cl_data.get("body_1", ""),
        COVER_LETTER_PLACEHOLDERS["body_2"]: cl_data.get("body_2", ""),
        COVER_LETTER_PLACEHOLDERS["body_3"]: cl_data.get("body_3", ""),
        COVER_LETTER_PLACEHOLDERS["additional"]: cl_data.get("additional", ""),
        COVER_LETTER_PLACEHOLDERS["attraction"]: cl_data.get("attraction", ""),
        COVER_LETTER_PLACEHOLDERS["closing"]: cl_data.get("closing", "")
    }

    # Identifier les placeholders optionnels vides à supprimer
    placeholders_to_remove = []
    if not cl_data.get("additional"):
        placeholders_to_remove.append(COVER_LETTER_PLACEHOLDERS["additional"])
    if not cl_data.get("attraction"):
        placeholders_to_remove.append(COVER_LETTER_PLACEHOLDERS["attraction"])

    # Supprimer les paragraphes optionnels vides
    remove_empty_paragraphs(doc, placeholders_to_remove)

    # Remplacer les placeholders (avec support markdown pour **bold**)
    replace_all_placeholders(doc, replacements, support_markdown=True)

    # Supprimer les paragraphes vides trailing
    remove_empty_paragraphs(doc)

    # Sauvegarder le DOCX
    docx_path = output_folder / OUTPUT_NAMES["cover_letter_docx"]
    doc.save(docx_path)
    print(f"[DOCX] {docx_path}")

    # Générer le PDF
    pdf_folder = output_folder / "PDF"
    pdf_path = convert_and_trim(docx_path, pdf_folder)
    if pdf_path:
        print(f"[PDF] {pdf_path} (1 page)")

    return docx_path, pdf_path


def generate_cover_letter_from_file(content_path: str | Path, output_folder: str | Path = None) -> tuple[Path, Path | None]:
    """
    Génère une lettre depuis un fichier content.json.

    Args:
        content_path: Chemin vers content.json
        output_folder: Dossier de destination (défaut: même dossier que content.json)

    Returns:
        Tuple (docx_path, pdf_path)
    """
    content_path = Path(content_path)

    with open(content_path, 'r', encoding='utf-8') as f:
        content = json.load(f)

    if output_folder is None:
        output_folder = content_path.parent

    return generate_cover_letter(content, output_folder)
```

**Step 2: Commit**

```bash
git add scripts/cover_letter.py
git commit -m "feat: add new cover_letter.py reading from content.json"
```

---

### Task 6: Créer generate.py (orchestrateur)

**Files:**
- Create: `scripts/generate.py`

**Step 1: Créer l'orchestrateur principal**

```python
# scripts/generate.py
"""Orchestrateur principal pour la génération de candidatures."""

import json
import shutil
from pathlib import Path
from datetime import datetime

from utils.config import JOBS_DIR, OUTPUT_NAMES
from resume import generate_resume
from cover_letter import generate_cover_letter


def create_project_folder(company: str, position: str) -> Path:
    """
    Crée le dossier de projet pour une candidature.

    Args:
        company: Nom de l'entreprise
        position: Nom du poste

    Returns:
        Path vers le dossier créé
    """
    date_str = datetime.now().strftime("%d-%m-%Y")
    # Nettoyer les noms (remplacer espaces par underscore)
    company_clean = company.replace(" ", "_").replace("/", "-")
    position_clean = position.replace(" ", "_").replace("/", "-")

    folder_name = f"{company_clean}_{position_clean}_{date_str}"
    folder_path = JOBS_DIR / folder_name
    folder_path.mkdir(parents=True, exist_ok=True)

    return folder_path


def save_content(content: dict, folder: Path) -> Path:
    """
    Sauvegarde le content.json dans le dossier.

    Args:
        content: Dict avec toutes les données
        folder: Dossier de destination

    Returns:
        Path vers le fichier content.json
    """
    content_path = folder / OUTPUT_NAMES["content"]
    with open(content_path, 'w', encoding='utf-8') as f:
        json.dump(content, f, indent=2, ensure_ascii=False)
    print(f"[JSON] {content_path}")
    return content_path


def load_content(folder: Path) -> dict:
    """
    Charge le content.json depuis le dossier.

    Args:
        folder: Dossier contenant content.json

    Returns:
        Dict avec les données
    """
    content_path = folder / OUTPUT_NAMES["content"]
    with open(content_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_job_description(job_description: str, folder: Path) -> Path:
    """
    Sauvegarde la description de poste dans le dossier.

    Args:
        job_description: Texte de la description
        folder: Dossier de destination

    Returns:
        Path vers le fichier
    """
    jd_path = folder / "job_description.md"
    with open(jd_path, 'w', encoding='utf-8') as f:
        f.write(job_description)
    print(f"[MD] {jd_path}")
    return jd_path


def generate_all(folder: Path) -> dict:
    """
    Génère CV et lettre de motivation depuis content.json.

    Args:
        folder: Dossier contenant content.json

    Returns:
        Dict avec les chemins générés
    """
    content = load_content(folder)

    resume_docx, resume_pdf = generate_resume(content, folder)
    cl_docx, cl_pdf = generate_cover_letter(content, folder)

    return {
        "resume_docx": str(resume_docx),
        "resume_pdf": str(resume_pdf) if resume_pdf else None,
        "cover_letter_docx": str(cl_docx),
        "cover_letter_pdf": str(cl_pdf) if cl_pdf else None
    }


def regenerate_resume(folder: Path) -> dict:
    """
    Régénère uniquement le CV.

    Args:
        folder: Dossier contenant content.json

    Returns:
        Dict avec les chemins générés
    """
    content = load_content(folder)
    resume_docx, resume_pdf = generate_resume(content, folder)

    return {
        "resume_docx": str(resume_docx),
        "resume_pdf": str(resume_pdf) if resume_pdf else None
    }


def regenerate_cover_letter(folder: Path) -> dict:
    """
    Régénère uniquement la lettre de motivation.

    Args:
        folder: Dossier contenant content.json

    Returns:
        Dict avec les chemins générés
    """
    content = load_content(folder)
    cl_docx, cl_pdf = generate_cover_letter(content, folder)

    return {
        "cover_letter_docx": str(cl_docx),
        "cover_letter_pdf": str(cl_pdf) if cl_pdf else None
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python generate.py <folder_path>")
        print("  Regenerates CV and cover letter from content.json in the folder")
        sys.exit(1)

    folder = Path(sys.argv[1])
    if not folder.exists():
        print(f"Error: Folder {folder} does not exist")
        sys.exit(1)

    results = generate_all(folder)
    print("\nGeneration complete:")
    for key, path in results.items():
        if path:
            print(f"  {key}: {path}")
```

**Step 2: Commit**

```bash
git add scripts/generate.py
git commit -m "feat: add generate.py orchestrator"
```

---

## Phase 3 : Commande unifiée

### Task 7: Créer la commande /generate

**Files:**
- Create: `.claude/commands/generate.md`

**Step 1: Créer le fichier de commande**

```markdown
Génère un CV et une lettre de motivation personnalisés à partir d'une description de poste.

---

## Input

L'utilisateur fournit la job description en argument.

## Workflow

### 1. Analyse de la job description
- Extraire : company, position, position_exact
- Identifier 10-15 keywords exacts (pour ATS)
- Détecter secteur et tone (trading/M&A/consulting/tech)
- Rédiger job_summary (2-3 phrases pour rappel avant entretien)

### 2. Recherche web (WebSearch)
Effectuer les recherches pertinentes selon le contexte :
- Valeurs/culture de l'entreprise
- Actualités récentes
- Secteur d'activité / concurrents
- Projets ou initiatives spécifiques mentionnés dans l'offre

Objectif : trouver des éléments concrets pour personnaliser les documents.

### 3. Sélection du contenu
Depuis `data/*.json`, sélectionner :
- 3 bullets Auraïa (sur 9 disponibles)
- 1 bullet RC Group (sur 6)
- 1 bullet Europ Assistance (sur 7)
- 3 leadership (sur 5)
- 3-4 courses, 5-7 skills

Critères : keywords match, secteur, tone adapté.

### 4. Rédaction
**CV :**
- Professional summary : 2-3 lignes, mentionne le nom de l'entreprise

**Lettre de motivation :**
- Intro : 60-80 mots, hook basé sur la recherche web
- Body 1/2/3 : 60-80 mots chacun, format "**Titre** — contenu"
- Closing : 50-70 mots

### 5. Génération
1. Créer le dossier `jobs/[Company]_[Position]_[DD-MM-YYYY]/`
2. Sauvegarder `content.json` avec tout le contenu
3. Sauvegarder `job_description.md`
4. Appeler `scripts/generate.py` pour générer DOCX + PDF

### 6. Validation
- Vérifier qu'aucun placeholder ne reste
- Confirmer que les PDFs sont générés

## Structure du content.json

```json
{
  "metadata": {
    "company": "...",
    "position": "...",
    "position_exact": "...",
    "date_created": "...",
    "job_keywords": [...],
    "job_summary": "..."
  },
  "research": {
    "company_values": [...],
    "company_mission": "...",
    "recent_news": "...",
    "used_in": [...]
  },
  "resume": {
    "professional_summary": "...",
    "auraia_bullets": ["...", "...", "..."],
    "rc_bullet": "...",
    "europ_bullet": "...",
    "leadership_bullets": ["...", "...", "..."],
    "courses": "...",
    "skills": "..."
  },
  "cover_letter": {
    "recipient": "...",
    "street": "...",
    "postal": "...",
    "intro": "...",
    "body_1": "**Titre** — ...",
    "body_2": "**Titre** — ...",
    "body_3": "**Titre** — ...",
    "additional": "",
    "attraction": "",
    "closing": "..."
  }
}
```

## Modifications post-génération

Si l'utilisateur demande un changement :
1. Lire `content.json` du dossier
2. Modifier le champ concerné
3. Régénérer uniquement le document impacté :
   - `python scripts/generate.py <folder>` pour tout
   - Ou modifier et régénérer via les fonctions Python

Exemples :
- "CV trop long" → raccourcir bullets dans content.json, régénérer CV
- "Change le résumé pro" → modifier `resume.professional_summary`
- "Intro lettre trop générique" → modifier `cover_letter.intro`

## Style d'écriture

**À FAIRE :**
- Utiliser les EXACT keywords de la job description (ATS)
- Adapter le tone au secteur
- Inclure des métriques quantifiables
- Mentionner le nom de l'entreprise dans le summary

**À ÉVITER :**
- Phrases génériques ("passionate about", "excited to leverage")
- Em-dashes (utiliser tirets ou deux-points)
- Répéter le contenu du CV dans la lettre
- Dépasser 1 page
```

**Step 2: Commit**

```bash
git add .claude/commands/generate.md
git commit -m "feat: add unified /generate command"
```

---

## Phase 4 : Nettoyage

### Task 8: Archiver les anciens fichiers

**Files:**
- Move: `scripts/generate_resume.py` → `scripts/archive/generate_resume_old.py`
- Move: `scripts/generate_cover_letter.py` → `scripts/archive/generate_cover_letter_old.py`
- Delete: `.claude/commands/resume_create.md`
- Delete: `.claude/commands/cover_letter_create.md`

**Step 1: Créer le dossier archive et déplacer les anciens scripts**

```bash
mkdir -p scripts/archive
mv scripts/generate_resume.py scripts/archive/generate_resume_old.py
mv scripts/generate_cover_letter.py scripts/archive/generate_cover_letter_old.py
```

**Step 2: Supprimer les anciennes commandes**

```bash
rm .claude/commands/resume_create.md
rm .claude/commands/cover_letter_create.md
```

**Step 3: Commit**

```bash
git add -A
git commit -m "chore: archive old scripts and remove old commands"
```

---

### Task 9: Mettre à jour CLAUDE.md

**Files:**
- Modify: `CLAUDE.md`

**Step 1: Remplacer le contenu de CLAUDE.md**

```markdown
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Resume.ai génère des CV et lettres de motivation personnalisés et optimisés ATS. Une seule commande `/generate` analyse la job description, fait de la recherche web, et produit les documents.

## Commande principale

```bash
/generate "job description..."
```

Génère CV + lettre de motivation en une fois.

## Architecture

```
jobs/[Company]_[Position]_[Date]/
├── job_description.md      # Input original
├── content.json            # Tout le contenu (modifiable)
├── Resume_Adrian_Turion.docx
├── Cover_Letter_Adrian_Turion.docx
└── PDF/
    ├── Resume_Adrian_Turion.pdf
    └── Cover_Letter_Adrian_Turion.pdf
```

## Modification rapide

1. Modifier `content.json` (champ concerné)
2. Régénérer : `python scripts/generate.py jobs/[folder]`

Ou demander directement : "Raccourcis le 2ème bullet Auraia"

## Scripts

| Script | Usage |
|--------|-------|
| `scripts/generate.py` | Orchestrateur principal |
| `scripts/resume.py` | Génération CV depuis content.json |
| `scripts/cover_letter.py` | Génération lettre depuis content.json |
| `scripts/utils/config.py` | Constantes et chemins |
| `scripts/utils/docx.py` | Manipulation Word |
| `scripts/utils/pdf.py` | Conversion PDF |

## Données

| Fichier | Contenu |
|---------|---------|
| `data/work_experiences.json` | 3 rôles (Auraia, RC, Europ) |
| `data/leadership.json` | 5 expériences leadership |
| `data/courses_and_other.json` | Cours Bachelor + Master |

## Sélection contenu

- **Auraia**: 3 bullets sur 9
- **RC Group**: 1 bullet sur 6
- **Europ**: 1 bullet sur 7
- **Leadership**: 3 sur 5
- **Courses**: 3-4 max
- **Skills**: 5-7 max (une ligne)

## Style

**DO:** Keywords exacts, tone adapté au secteur, métriques, nom entreprise dans summary

**DON'T:** Phrases génériques, em-dashes, répétition CV/lettre, >1 page
```

**Step 2: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: update CLAUDE.md for new architecture"
```

---

### Task 10: Test end-to-end

**Step 1: Créer un content.json de test**

```bash
mkdir -p jobs/Test_Company_10-01-2026
```

Créer `jobs/Test_Company_10-01-2026/content.json` :

```json
{
  "metadata": {
    "company": "Test Company",
    "position": "Graduate",
    "position_exact": "Graduate Programme - Test",
    "date_created": "2026-01-10",
    "job_keywords": ["analytical", "teamwork"],
    "job_summary": "Test position for validation."
  },
  "research": {
    "company_values": ["innovation"],
    "company_mission": "Test mission",
    "recent_news": "Test news",
    "used_in": ["cover_letter_intro"]
  },
  "resume": {
    "professional_summary": "Finance graduate with M&A experience seeking to join Test Company.",
    "auraia_bullets": [
      "Led valuation for 7 M&A transactions across healthcare and tech sectors",
      "Managed 7 concurrent mandates in a lean 3-person team",
      "Built AI-powered buyer sourcing tool reducing research time by 90%"
    ],
    "rc_bullet": "Worked with CEO on evaluating acquisition targets in France",
    "europ_bullet": "Built automated dashboards in Excel and PowerBI",
    "leadership_bullets": [
      "Founded Screeny.ai, adopted by 3 M&A firms",
      "Drove business development at AIESEC",
      "Finalist in McKinsey case competition"
    ],
    "courses": "Risk Management, Derivatives, Data Science",
    "skills": "Excel, Bloomberg, Python, SQL"
  },
  "cover_letter": {
    "recipient": "Hiring Manager",
    "street": "",
    "postal": "",
    "intro": "Test Company's commitment to innovation aligns with my experience in M&A.",
    "body_1": "**Analytical Skills** — At Auraia, I developed strong analytical capabilities.",
    "body_2": "**Teamwork** — Working in lean teams taught me collaboration.",
    "body_3": "**Innovation** — I built AI tools to improve efficiency.",
    "additional": "",
    "attraction": "",
    "closing": "I look forward to discussing how I can contribute to Test Company."
  }
}
```

**Step 2: Lancer la génération**

```bash
cd scripts
python generate.py ../jobs/Test_Company_10-01-2026
```

**Step 3: Vérifier les fichiers générés**

```bash
ls -la ../jobs/Test_Company_10-01-2026/
ls -la ../jobs/Test_Company_10-01-2026/PDF/
```

Expected output:
- `Resume_Adrian_Turion.docx`
- `Cover_Letter_Adrian_Turion.docx`
- `PDF/Resume_Adrian_Turion.pdf`
- `PDF/Cover_Letter_Adrian_Turion.pdf`

**Step 4: Commit le test (optionnel)**

```bash
git add jobs/Test_Company_10-01-2026/content.json
git commit -m "test: add test content.json for validation"
```

---

## Résumé des commits

1. `feat: add config.py with centralized constants`
2. `feat: add pdf.py with convert and trim functions`
3. `feat: add docx.py with placeholder replacement and markdown support`
4. `feat: add new resume.py reading from content.json`
5. `feat: add new cover_letter.py reading from content.json`
6. `feat: add generate.py orchestrator`
7. `feat: add unified /generate command`
8. `chore: archive old scripts and remove old commands`
9. `docs: update CLAUDE.md for new architecture`
10. `test: add test content.json for validation` (optionnel)
