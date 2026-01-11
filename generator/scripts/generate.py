# generator/scripts/generate.py
"""Orchestrateur principal pour la génération de candidatures."""

import json
import shutil
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from generator.utils.config import JOBS_DIR, OUTPUT_NAMES, AUTHOR_NAME, AUTHOR_EMAIL, AUTHOR_PHONE
from generator.scripts.resume import generate_resume
from generator.scripts.cover_letter import generate_cover_letter


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


def save_content(content: dict, folder) -> Path:
    """
    Sauvegarde le content.json dans le dossier.

    Args:
        content: Dict avec toutes les données
        folder: Dossier de destination (str ou Path)

    Returns:
        Path vers le fichier content.json
    """
    folder = Path(folder)
    content_path = folder / OUTPUT_NAMES["content"]
    with open(content_path, 'w', encoding='utf-8') as f:
        json.dump(content, f, indent=2, ensure_ascii=False)
    print(f"[JSON] {content_path}")
    return content_path


def load_content(folder) -> dict:
    """
    Charge le content.json depuis le dossier.

    Args:
        folder: Dossier contenant content.json (str ou Path)

    Returns:
        Dict avec les données
    """
    folder = Path(folder)
    content_path = folder / OUTPUT_NAMES["content"]
    with open(content_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_job_description(job_description: str, folder) -> Path:
    """
    Sauvegarde la description de poste dans le dossier.

    Args:
        job_description: Texte de la description
        folder: Dossier de destination (str ou Path)

    Returns:
        Path vers le fichier
    """
    folder = Path(folder)
    jd_path = folder / "job_description.md"
    with open(jd_path, 'w', encoding='utf-8') as f:
        f.write(job_description)
    print(f"[MD] {jd_path}")
    return jd_path


def generate_email_draft(content: dict, folder) -> Path:
    """
    Génère un brouillon d'email pour candidature par mail.

    Args:
        content: Dict contenant les données
        folder: Dossier de destination (str ou Path)

    Returns:
        Path vers le fichier email_draft.txt
    """
    folder = Path(folder)
    metadata = content.get("metadata", {})
    email_data = content.get("email", {})

    company = metadata.get("company", "Company")
    position = metadata.get("position", "Position")
    recipient = email_data.get("recipient", "Hiring Team")
    subject = email_data.get("subject", f"Application - {position} - {AUTHOR_NAME}")
    body = email_data.get("body", "")

    # Si pas de body personnalisé, générer un template par défaut
    if not body:
        body = f"""Dear {recipient},

Please find attached my resume and cover letter for the {position} position at {company}.

I would welcome the opportunity to discuss my application further.

Best regards,
{AUTHOR_NAME}
{AUTHOR_PHONE}
{AUTHOR_EMAIL}"""

    email_content = f"""Subject: {subject}

{body}
"""

    email_path = folder / "email_draft.txt"
    with open(email_path, 'w', encoding='utf-8') as f:
        f.write(email_content)
    print(f"[EMAIL] {email_path}")

    return email_path


def generate_all(folder) -> dict:
    """
    Génère CV, lettre de motivation et brouillon email depuis content.json.

    Args:
        folder: Dossier contenant content.json (str ou Path)

    Returns:
        Dict avec les chemins générés
    """
    folder = Path(folder)
    content = load_content(folder)
    
    # Validation pré-génération
    errors, warnings = validate_content(content)
    
    if errors:
        print("[ERREUR] Problèmes dans content.json:")
        for err in errors:
            print(f"  - {err}")
        raise ValueError("content.json invalide - corrigez les erreurs ci-dessus")
    
    if warnings:
        print("[WARNING] Le CV risque de dépasser 1 page:")
        for warn in warnings:
            print(f"  - {warn}")
        print("")

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


def regenerate_resume(folder) -> dict:
    """
    Régénère uniquement le CV.

    Args:
        folder: Dossier contenant content.json (str ou Path)

    Returns:
        Dict avec les chemins générés
    """
    folder = Path(folder)
    content = load_content(folder)
    resume_docx, resume_pdf = generate_resume(content, folder)

    return {
        "resume_docx": str(resume_docx),
        "resume_pdf": str(resume_pdf) if resume_pdf else None
    }


def regenerate_cover_letter(folder) -> dict:
    """
    Régénère uniquement la lettre de motivation.

    Args:
        folder: Dossier contenant content.json (str ou Path)

    Returns:
        Dict avec les chemins générés
    """
    folder = Path(folder)
    content = load_content(folder)
    cl_docx, cl_pdf = generate_cover_letter(content, folder)

    return {
        "cover_letter_docx": str(cl_docx),
        "cover_letter_pdf": str(cl_pdf) if cl_pdf else None
    }




# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

# Character limits - keep in sync with .claude/commands/generate.md
# Note: rc_bullet and europ_bullet can be longer since there's only 1 bullet each
CHAR_LIMITS_MAX = {
    "professional_summary": 420,
    "auraia_bullet": 260,
    "rc_bullet": 320,
    "europ_bullet": 320,
    "leadership_bullet": 200,
    "courses": 100,
    "skills": 90,
}

CHAR_LIMITS_MIN = {
    "professional_summary": 340,
    "auraia_bullet": 210,
    "rc_bullet": 260,
    "europ_bullet": 260,
    "leadership_bullet": 160,
    "courses": 60,
    "skills": 55,
}


def validate_content_structure(content: dict) -> list[str]:
    """
    Valide la structure du content.json (nombre d'éléments dans les arrays).
    
    Args:
        content: Dict avec les données
        
    Returns:
        Liste d'erreurs (vide si tout est OK)
    """
    errors = []
    resume = content.get("resume", {})
    
    auraia = resume.get("auraia_bullets", [])
    if len(auraia) != 3:
        errors.append(f"auraia_bullets doit avoir 3 éléments, trouvé {len(auraia)}")
    
    leadership = resume.get("leadership_bullets", [])
    if len(leadership) != 3:
        errors.append(f"leadership_bullets doit avoir 3 éléments, trouvé {len(leadership)}")
    
    return errors


def validate_content_length(content: dict) -> tuple[list[str], list[str]]:
    """
    Valide les longueurs de contenu (min et max).

    Args:
        content: Dict avec les données

    Returns:
        Tuple (errors pour trop court, warnings pour trop long)
    """
    errors = []  # Trop court = erreur (page vide)
    warnings = []  # Trop long = warning (risque > 1 page)
    resume = content.get("resume", {})

    def check_field(value: str, field_name: str, display_name: str = None):
        display = display_name or field_name
        min_len = CHAR_LIMITS_MIN.get(field_name, 0)
        max_len = CHAR_LIMITS_MAX.get(field_name, 999)
        # 5% tolerance on minimum (don't be strict about a few chars)
        tolerance = int(min_len * 0.05)
        effective_min = min_len - tolerance

        if len(value) < effective_min:
            errors.append(f"{display} trop court: {len(value)}/{min_len} chars min")
        elif len(value) > max_len:
            warnings.append(f"{display} trop long: {len(value)}/{max_len} chars max")

    # Professional summary
    check_field(resume.get("professional_summary", ""), "professional_summary")

    # Auraia bullets
    for i, bullet in enumerate(resume.get("auraia_bullets", []), 1):
        check_field(bullet, "auraia_bullet", f"auraia_bullet {i}")

    # RC bullet
    check_field(resume.get("rc_bullet", ""), "rc_bullet")

    # Europ bullet
    check_field(resume.get("europ_bullet", ""), "europ_bullet")

    # Leadership bullets
    for i, bullet in enumerate(resume.get("leadership_bullets", []), 1):
        check_field(bullet, "leadership_bullet", f"leadership_bullet {i}")

    # Courses
    check_field(resume.get("courses", ""), "courses")

    # Skills
    check_field(resume.get("skills", ""), "skills")

    return errors, warnings


def validate_content(content: dict) -> tuple[list[str], list[str]]:
    """
    Valide le content.json (structure + longueurs).

    Args:
        content: Dict avec les données

    Returns:
        Tuple (errors, warnings)
    """
    errors = validate_content_structure(content)
    length_errors, length_warnings = validate_content_length(content)
    errors.extend(length_errors)
    return errors, length_warnings

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
