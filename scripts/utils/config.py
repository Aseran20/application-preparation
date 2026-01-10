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

# Nom de l'auteur
AUTHOR_NAME = "Adrian Turion"

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
