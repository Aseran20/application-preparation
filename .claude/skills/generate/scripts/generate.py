# generator/scripts/generate.py
"""Orchestrateur principal pour la génération de candidatures."""

import json
import shutil
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from utils.config import JOBS_DIR, OUTPUT_NAMES, AUTHOR_NAME, AUTHOR_EMAIL, AUTHOR_PHONE
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
    now = datetime.now()
    date_str = now.strftime("%d.%m.%Y")
    month_dir = now.strftime("%b-%y").lower()  # e.g. "mar-26"

    # Nettoyer les caractères interdits dans les noms de dossiers Windows
    invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    company_clean = company
    position_clean = position
    for char in invalid_chars:
        company_clean = company_clean.replace(char, "-")
        position_clean = position_clean.replace(char, "-")

    folder_name = f"{company_clean} - {position_clean} - {date_str}"
    folder_path = JOBS_DIR / month_dir / folder_name
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


def visual_check(content: dict) -> list[str]:
    """
    Analyse visuelle des bullets pour vérifier qu'ils tiennent sur les bonnes lignes.

    Args:
        content: Dict avec les données

    Returns:
        List de warnings si problèmes détectés
    """
    warnings = []
    resume = content.get("resume", {})

    # Vérifier que RC et Generali tiennent sur 1 ligne (< 150 chars recommandé)
    for i, bullet in enumerate(resume.get("rc_bullets", []), 1):
        if len(bullet) > 140:
            warnings.append(f"RC bullet {i} semble dépasser 1 ligne ({len(bullet)} chars) - à vérifier visuellement")

    for i, bullet in enumerate(resume.get("generali_bullets", []), 1):
        if len(bullet) > 140:
            warnings.append(f"Generali bullet {i} semble dépasser 1 ligne ({len(bullet)} chars) - à vérifier visuellement")

    return warnings


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

    # Analyse visuelle post-génération
    visual_warnings = visual_check(content)
    if visual_warnings:
        print("[VISUAL CHECK] Vérifiez manuellement:")
        for warn in visual_warnings:
            print(f"  - {warn}")
        print("")

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

# Character limits - keep in sync with .claude/generate/limits.md
CHAR_LIMITS_MAX = {
    "introduction":   220,
    "auraia_bullet":  280,
    "rc_bullet":      160,
    "generali_bullet": 160,
    "extra_sentence": 160,
    "coursework":     100,
    "tools":           80,
    "skills":         110,
    "interests":       80,
}

CHAR_LIMITS_MIN = {
    "introduction":   150,
    "auraia_bullet":  100,
    "rc_bullet":      100,
    "generali_bullet": 100,
    "extra_sentence":  60,
    "coursework":      40,
    "tools":           30,
    "skills":          50,
    "interests":       30,
}


def validate_content_structure(content: dict) -> list[str]:
    errors = []
    resume = content.get("resume", {})

    auraia = resume.get("auraia_bullets", [])
    if len(auraia) != 4:
        errors.append(f"auraia_bullets must have 4 items, found {len(auraia)}")

    rc = resume.get("rc_bullets", [])
    if len(rc) != 3:
        errors.append(f"rc_bullets must have 3 items, found {len(rc)}")

    generali = resume.get("generali_bullets", [])
    if len(generali) != 3:
        errors.append(f"generali_bullets must have 3 items, found {len(generali)}")

    extra = resume.get("extra_entries", [])
    if not (3 <= len(extra) <= 5):
        errors.append(f"extra_entries must have 3-5 items, found {len(extra)}")

    return errors


def validate_content_length(content: dict) -> tuple[list[str], list[str]]:
    errors = []
    warnings = []
    resume = content.get("resume", {})

    def check_field(value: str, field_name: str, display_name: str = None):
        display = display_name or field_name
        min_len = CHAR_LIMITS_MIN.get(field_name, 0)
        max_len = CHAR_LIMITS_MAX.get(field_name, 9999)
        tolerance = int(min_len * 0.05)
        effective_min = min_len - tolerance

        if len(value) < effective_min:
            errors.append(f"{display} too short: {len(value)}/{min_len} chars min")
        elif len(value) > max_len:
            errors.append(f"{display} too long: {len(value)}/{max_len} chars max")

    check_field(resume.get("introduction", ""), "introduction")

    for i, bullet in enumerate(resume.get("auraia_bullets", []), 1):
        check_field(bullet, "auraia_bullet", f"auraia_bullet {i}")

    for i, bullet in enumerate(resume.get("rc_bullets", []), 1):
        check_field(bullet, "rc_bullet", f"rc_bullet {i}")

    for i, bullet in enumerate(resume.get("generali_bullets", []), 1):
        check_field(bullet, "generali_bullet", f"generali_bullet {i}")

    for i, entry in enumerate(resume.get("extra_entries", []), 1):
        check_field(entry.get("sentence", ""), "extra_sentence", f"extra_sentence {i}")

    check_field(resume.get("coursework", ""),  "coursework")
    check_field(resume.get("tools", ""),       "tools")
    check_field(resume.get("skills", ""),      "skills")
    check_field(resume.get("interests", ""),   "interests")

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
