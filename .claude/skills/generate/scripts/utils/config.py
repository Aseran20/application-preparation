# utils/config.py
"""Configuration for document generation."""

from pathlib import Path

# Paths — derived from skill directory structure
# __file__ = .claude/skills/generate/scripts/utils/config.py
SKILL_DIR = Path(__file__).resolve().parent.parent.parent  # -> .claude/skills/generate/
PROJECT_ROOT = SKILL_DIR.parent.parent.parent               # -> project root
TEMPLATES_DIR = SKILL_DIR / "assets"
JOBS_DIR = PROJECT_ROOT / "jobs"

# Author (personal skill - hardcoded)
AUTHOR_NAME  = "Adrian Turion"
AUTHOR_EMAIL = "turionadrian@gmail.com"
AUTHOR_PHONE = "+41 77 262 37 96"

# Templates
TEMPLATES = {
    "resume": TEMPLATES_DIR / f"Resume - {AUTHOR_NAME}.docx",
    "cover_letter": TEMPLATES_DIR / f"Cover Letter - {AUTHOR_NAME}.docx",
}

# Output file names
OUTPUT_NAMES = {
    "content": "content.json"
}

def get_output_names(company: str) -> dict:
    return {
        "resume_docx": f"{AUTHOR_NAME} - {company} - Resume.docx",
        "resume_pdf": f"{AUTHOR_NAME} - {company} - Resume.pdf",
        "cover_letter_docx": f"{AUTHOR_NAME} - {company} - Cover Letter.docx",
        "cover_letter_pdf": f"{AUTHOR_NAME} - {company} - Cover Letter.pdf",
    }

# Formatting
FONT_NAME = "Times New Roman"
FONT_SIZE_PT = 10

# Resume placeholders
RESUME_PLACEHOLDERS = {
    "introduction":          "{introduction}",
    "auraia_1":              "{auraia-bp1}",
    "auraia_2":              "{auraia-bp2}",
    "auraia_3":              "{auraia-bp3}",
    "auraia_4":              "{auraia-bp4}",
    "rc_1":                  "{rc-bp1}",
    "rc_2":                  "{rc-bp2}",
    "rc_3":                  "{rc-bp3}",
    "generali_1":            "{generali-bp1}",
    "generali_2":            "{generali-bp2}",
    "generali_3":            "{generali-bp3}",
    "extra_category_title":  "{extra-category-title}",
    "extra_bp1_title":       "{extra-bp1-title}",
    "extra_bp1_content":     "{extra-bp1-content}",
    "extra_bp2_title":       "{extra-bp2-title}",
    "extra_bp2_content":     "{extra-bp2-content}",
    "extra_bp3_title":       "{extra-bp3-title}",
    "extra_bp3_content":     "{extra-bp3-content}",
    "extra_bp4_title":       "{extra-bp4-title}",
    "extra_bp4_content":     "{extra-bp4-content}",
    "extra_bp5_title":       "{extra-bp5-title}",
    "extra_bp5_content":     "{extra-bp5-content}",
    "coursework":            "{coursework}",
    "tools":                 "{tools}",
    "skills":                "{skills}",
    "interests":             "{interests}",
}

# Cover letter placeholders
COVER_LETTER_PLACEHOLDERS = {
    "date":                  "{date}",
    "recipient_name":        "{recipient-name}",
    "street_number":         "{street-number}",
    "postal_city_country":   "{postal-city-country}",
    "company_name":          "{company-name}",
    "subject_line":          "{subject-line}",
    "salutation":            "{salutation}",
    "paragraph_1":           "{paragraph-1}",
    "paragraph_2":           "{paragraph-2}",
    "paragraph_3":           "{paragraph-3}",
    "closing":               "{closing}",
}
