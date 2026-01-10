# scripts/generate.py
"""Orchestrateur principal pour la génération de candidatures."""

import json
import shutil
from pathlib import Path
from datetime import datetime

from scripts.utils.config import JOBS_DIR, OUTPUT_NAMES
from scripts.resume import generate_resume
from scripts.cover_letter import generate_cover_letter


def create_project_folder(company: str, position: str) -> Path:
    """
    Crée le dossier de projet pour une candidature.

    Args:
        company: Nom de l'entreprise
        position: Nom du poste

    Returns:
        Path vers le dossier créé
    """
    date_str = datetime.now().strftime("%d.%m.%Y")

    # Nettoyer les caractères interdits dans les noms de dossiers Windows
    invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    company_clean = company
    position_clean = position
    for char in invalid_chars:
        company_clean = company_clean.replace(char, "-")
        position_clean = position_clean.replace(char, "-")

    folder_name = f"{company_clean} - {position_clean} - {date_str}"
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


def generate_email_draft(content: dict, folder: Path) -> Path:
    """
    Génère un brouillon d'email pour candidature par mail.

    Args:
        content: Dict contenant les données
        folder: Dossier de destination

    Returns:
        Path vers le fichier email_draft.txt
    """
    metadata = content.get("metadata", {})
    email_data = content.get("email", {})

    company = metadata.get("company", "Company")
    position = metadata.get("position", "Position")
    recipient = email_data.get("recipient", "Hiring Team")
    subject = email_data.get("subject", f"Application - {position} - Adrian Turion")
    body = email_data.get("body", "")

    # Si pas de body personnalisé, générer un template par défaut
    if not body:
        body = f"""Dear {recipient},

Please find attached my resume and cover letter for the {position} position at {company}.

I would welcome the opportunity to discuss my application further.

Best regards,
Adrian Turion
+41 77 262 37 96
turionadrian@gmail.com"""

    email_content = f"""Subject: {subject}

{body}
"""

    email_path = folder / "email_draft.txt"
    with open(email_path, 'w', encoding='utf-8') as f:
        f.write(email_content)
    print(f"[EMAIL] {email_path}")

    return email_path


def generate_all(folder: Path) -> dict:
    """
    Génère CV, lettre de motivation et brouillon email depuis content.json.

    Args:
        folder: Dossier contenant content.json

    Returns:
        Dict avec les chemins générés
    """
    content = load_content(folder)

    resume_docx, resume_pdf = generate_resume(content, folder)
    cl_docx, cl_pdf = generate_cover_letter(content, folder)
    email_path = generate_email_draft(content, folder)

    return {
        "resume_docx": str(resume_docx),
        "resume_pdf": str(resume_pdf) if resume_pdf else None,
        "cover_letter_docx": str(cl_docx),
        "cover_letter_pdf": str(cl_pdf) if cl_pdf else None,
        "email_draft": str(email_path)
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
