# scripts/utils/config.py
"""Configuration centralisée pour la génération de documents."""

import json
from pathlib import Path

# Chemins
PROJECT_ROOT = Path(__file__).parent.parent.parent
TEMPLATES_DIR = PROJECT_ROOT / "templates"
JOBS_DIR = PROJECT_ROOT / "jobs"
DATA_DIR = PROJECT_ROOT / "data"
CONFIG_LOCAL = PROJECT_ROOT / "config.local.json"

# Charger config locale si elle existe
_local_config = {}
if CONFIG_LOCAL.exists():
    with open(CONFIG_LOCAL, 'r', encoding='utf-8') as f:
        _local_config = json.load(f)

# Données personnelles (depuis config.local.json ou défaut)
AUTHOR_NAME = _local_config.get("author_name", "Your Name")
AUTHOR_EMAIL = _local_config.get("email", "your.email@example.com")
AUTHOR_PHONE = _local_config.get("phone", "+00 00 000 00 00")

# Templates
TEMPLATES = {
    "resume": TEMPLATES_DIR / f"Resume - {AUTHOR_NAME}.docx",
    "cover_letter": TEMPLATES_DIR / f"Cover Letter - {AUTHOR_NAME}.docx"
}

# Noms des fichiers de sortie (statiques)
OUTPUT_NAMES = {
    "content": "content.json"
}

def get_output_names(company: str) -> dict:
    """Génère les noms de fichiers avec le nom de l'entreprise."""
    return {
        "resume_docx": f"{AUTHOR_NAME} - {company} - Resume.docx",
        "resume_pdf": f"{AUTHOR_NAME} - {company} - Resume.pdf",
        "cover_letter_docx": f"{AUTHOR_NAME} - {company} - Cover Letter.docx",
        "cover_letter_pdf": f"{AUTHOR_NAME} - {company} - Cover Letter.pdf",
    }

# Formatting
FONT_NAME = "Times New Roman"
FONT_SIZE_PT = 10

# Placeholders CV
RESUME_PLACEHOLDERS = {
    "introduction": "[INTRODUCTION]",
    "auraia_1": "[W1-B1]",
    "auraia_2": "[W1-B2]",
    "auraia_3": "[W1-B3]",
    "rc": "[W2-B1]",
    "europ": "[W3-B1]",
    "leadership_1": "[L-B1]",
    "leadership_2": "[L-B2]",
    "leadership_3": "[L-B3]",
    "courses": "[COURSEWORK]",
    "skills": "[SOFTWARE]"
}

# Placeholders lettre
COVER_LETTER_PLACEHOLDERS = {
    "date": "[DATE]",
    "recipient": "[RECIPIENT_NAME]",
    "street": "[STREET_NUMBER]",
    "postal": "[POSTAL_CITY_COUNTRY]",
    "company": "[COMPANY_NAME]",
    "subject": "[SUBJECT_LINE]",
    "salutation": "[SALUTATION]",
    "intro": "[INTRO_PARAGRAPH]",
    "body_1": "[BODY_PARAGRAPH_1]",
    "body_2": "[BODY_PARAGRAPH_2]",
    "body_3": "[BODY_PARAGRAPH_3]",
    "additional": "[ADDITIONAL_CONTEXT]",
    "attraction": "[COMPANY_ATTRACTION]",
    "closing": "[CLOSING_PARAGRAPH]"
}
