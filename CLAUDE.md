# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Resume.ai generates personalized, ATS-optimized resumes and cover letters. It analyzes job descriptions, selects relevant experiences from JSON databases, and produces formatted Word/PDF documents.

## Commands

### Primary Slash Commands

```bash
/resume_create      # Generate tailored resume from job_description.md
/cover_letter_create  # Generate cover letter with Tavily research
```

### Validation

```bash
python scripts/validate_resume.py "jobs/[Folder]/Resume_Adrian_Turion.docx"
python scripts/validate_cover_letter.py "jobs/[Folder]/Cover_Letter_Adrian_Turion.docx"
```

### Dependencies

```bash
pip install python-docx PyPDF2 docx2pdf
```

## Architecture

### Generation Flow

```
job_description.md (paste job posting here)
        │
        ▼
/resume_create or /cover_letter_create
        │
        ▼
Read data/*.json → Select relevant content
        │
        ▼ (cover letter only)
Tavily web search: company values, recent news
        │
        ▼
scripts/generate_*.py → Replace template placeholders
        │
        ▼
jobs/[Company]_[Position]_[DD-MM-YYYY]/
```

### Key Script Functions

**`scripts/generate_resume.py`**
```python
generate_resume(
    professional_summary,      # 2-3 lines, mention company name
    auraia_bullets,           # List[str] - 3 items
    rc_group_bullet,          # str
    europ_assistance_bullet,  # str
    leadership_bullets,       # List[str] - 3 items
    courses,                  # str - comma-separated, 3-4 max
    skills,                   # str - one line, 5-7 tools max
    company, position
) -> (folder_name, docx_path, pdf_path)
```

**`scripts/generate_cover_letter.py`**
```python
generate_cover_letter(
    company_name, recipient_name,
    street_number, postal_city_country,
    intro_paragraph,          # 60-80 words, Tavily hook required
    body_paragraph_1,         # "**Title** — content" format
    body_paragraph_2,
    body_paragraph_3,
    additional_context,       # "" to skip
    company_attraction,       # "" to skip
    closing_paragraph,
    output_folder
) -> (folder_name, docx_path, pdf_path)
```

### Data Files

| File | Content |
|------|---------|
| `data/work_experiences.json` | 3 roles: Auraia (9), RC Group (6), Europ Assistance (7 accomplishments) |
| `data/leadership.json` | 5 experiences: McKinsey finalist, AIESEC, Startup, Screeny.ai, Portfolio |
| `data/courses_and_other.json` | Bachelor (17) + Master (15) courses |

## Content Selection

### Resume Requirements
- **Auraia**: 3 bullets from 9 accomplishments
- **RC Group**: 1 bullet from 6
- **Europ Assistance**: 1 bullet from 7
- **Leadership**: 3 from 5 experiences
- **Courses**: 3-4 MAX (comma-separated)
- **Skills**: 5-7 MAX (one line, may use `|` separator)

### Cover Letter Requirements
- **MANDATORY**: 2 Tavily searches before writing
  - `"[Company] mission values culture"`
  - `"[Company] news 2025"`
- **Intro**: Must reference specific Tavily finding
- **Body**: `**Bold Title** — content` format
- **Word count**: 250-550 (ideal 350-450)

## Formatting Rules

- **Font**: Times New Roman, 10pt body (11-22pt headings)
- **Output**: 1-page PDF (trimmed via PyPDF2)
- **Cover letter markdown**: `**bold**` syntax supported

## Placeholder Reference

**Resume:**
- `[Your professional summary...]` → Professional summary
- `[...W1-B1/B2/B3]` → Auraia bullets
- `[...W2-B1]` → RC Group bullet
- `[...W3-B1]` → Europ Assistance bullet
- `[...L-B1/B2/B3]` → Leadership bullets
- `[Relevant coursework here]` / `[Relevant software here]`

**Cover Letter:**
- `[DATE]`, `[COMPANY_NAME]`, `[SALUTATION]`
- `[INTRO_PARAGRAPH]`, `[BODY_PARAGRAPH_1/2/3]`
- `[ADDITIONAL_CONTEXT]`, `[COMPANY_ATTRACTION]` (optional, removed if empty)
- `[CLOSING_PARAGRAPH]`

## Writing Style

**DO:**
- Use EXACT keywords from job description (ATS optimization)
- Adapt tone to sector (trading=action, consulting=strategic, M&A=technical)
- Include quantifiable metrics from JSON data
- Mention company name in professional summary

**DON'T:**
- Generic phrases ("passionate about", "excited to leverage")
- Em-dashes (use hyphens or colons)
- Repeat resume content in cover letter
- Exceed 1 page

## Output Structure

```
jobs/[Company]_[Position]_[DD-MM-YYYY]/
├── Resume_Adrian_Turion.docx
├── Cover_Letter_Adrian_Turion.docx
├── job_description.md
├── tavily_research.md (cover letter only)
└── PDF/
    ├── Resume_Adrian_Turion.pdf
    └── Cover_Letter_Adrian_Turion.pdf
```
