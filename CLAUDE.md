# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Resume.ai generates personalized, ATS-optimized resumes and cover letters. It analyzes job descriptions, performs web research, selects relevant experiences from JSON databases, and produces formatted Word/PDF documents.

## Commands

### Primary Slash Command

```bash
/generate "paste job description here"
```

Generates both resume AND cover letter in a single command. Creates a project folder with all documents.

### Validation

```bash
py scripts/validate_resume.py "jobs/[Folder]/Resume_Adrian_Turion.docx"
py scripts/validate_cover_letter.py "jobs/[Folder]/Cover_Letter_Adrian_Turion.docx"
```

Note: On Windows, use `py` instead of `python`.

### Dependencies

```bash
pip install -r requirements.txt
```

Or manually: `pip install python-docx PyPDF2 docx2pdf`

### Configuration

Personal data is stored in `config.local.json` (gitignored):
```json
{
  "author_name": "Your Name",
  "email": "your.email@example.com",
  "phone": "+00 00 000 00 00"
}
```

## Architecture

### Generation Flow

```
/generate "job description..."
        │
        ▼
┌─────────────────────────────────────┐
│  1. ANALYZE JOB DESCRIPTION         │
│  - Extract company, position        │
│  - Identify 10-15 keywords          │
│  - Detect sector/tone               │
│  - Write job_summary                │
└─────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────┐
│  2. WEB RESEARCH (WebSearch)        │
│  - Company values, mission          │
│  - Recent news, initiatives         │
│  - Flexible queries per context     │
└─────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────┐
│  3. SELECT CONTENT                  │
│  - Read data/*.json                 │
│  - Choose relevant bullets          │
│  - Adapt to sector/tone             │
└─────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────┐
│  4. WRITE CONTENT                   │
│  - Professional summary (CV)        │
│  - Cover letter paragraphs          │
│  - Integrate research findings      │
└─────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────┐
│  5. CREATE content.json             │
│  - Save all content to JSON         │
│  - Easy to modify later             │
└─────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────┐
│  6. GENERATE DOCUMENTS              │
│  - content.json → Resume.docx → PDF │
│  - content.json → Cover.docx → PDF  │
└─────────────────────────────────────┘
```

### Modification Flow

```
User: "Shorten the 2nd Auraia bullet"
        │
        ▼
1. Read content.json
2. Modify resume.auraia_bullets[1]
3. Regenerate only the resume (not cover letter)
```

### Script Structure

```
scripts/
├── generate.py           # Main orchestrator
├── resume.py             # Resume generation (content.json → DOCX)
├── cover_letter.py       # Cover letter generation (content.json → DOCX)
├── validate_resume.py    # Resume validation
├── validate_cover_letter.py  # Cover letter validation
└── utils/
    ├── config.py         # Paths, constants, placeholders
    ├── docx.py           # Placeholder replacement, markdown
    └── pdf.py            # DOCX → PDF conversion, 1-page trim
```

### Key Functions

**`scripts/generate.py`**
```python
create_project_folder(company, position) -> Path
save_content(content, folder) -> Path  # folder accepts str or Path
load_content(folder) -> dict           # folder accepts str or Path
generate_all(folder) -> dict           # Validates content, then generates
regenerate_resume(folder) -> dict
regenerate_cover_letter(folder) -> dict
validate_content(content) -> (errors, warnings)  # Pre-generation validation
```

**Validation** runs automatically in `generate_all()`:
- Errors if `auraia_bullets` or `leadership_bullets` != 3 elements
- Errors if content is too short (with 5% tolerance)
- Warnings if content exceeds max limits (risk of >1 page)

**Character limits** (defined in `scripts/generate.py`):
| Field | Min | Max |
|-------|-----|-----|
| professional_summary | 340 | 420 |
| auraia_bullets (each) | 210 | 260 |
| rc_bullet | 260 | 320 |
| europ_bullet | 260 | 320 |
| leadership_bullets (each) | 160 | 200 |
| courses | 60 | 100 |
| skills | 55 | 90 |

**`scripts/resume.py`**
```python
generate_resume(content: dict, output_folder) -> (docx_path, pdf_path)
```

**`scripts/cover_letter.py`**
```python
generate_cover_letter(content: dict, output_folder) -> (docx_path, pdf_path)
```

### Data Files

| File | Content |
|------|---------|
| `data/work_experiences.json` | 3 roles: Auraia (9), RC Group (6), Europ Assistance (7 accomplishments) |
| `data/leadership.json` | 5 experiences: McKinsey finalist, AIESEC, Startup, Screeny.ai, Portfolio |
| `data/courses_and_other.json` | Bachelor (17) + Master (15) courses |

## content.json Schema

```json
{
  "metadata": {
    "company": "Glencore",
    "position": "Commercial Graduate",
    "position_exact": "Commercial Graduate Programme - Metals (LME Desk)",
    "date_created": "2026-01-10",
    "job_keywords": ["commercial aptitude", "resilience", "data analysis"],
    "job_summary": "2-year program with rotations on metals desks..."
  },
  "research": {
    "company_values": ["entrepreneurialism", "integrity"],
    "company_mission": "Responsibly sourcing commodities...",
    "recent_news": "Expansion copper production to 1M tons by 2028",
    "used_in": ["cover_letter_intro", "resume_summary"]
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
    "recipient": "Hiring Manager",
    "street": "Company Address",
    "postal": "City, Country",
    "subject": "**Subject:** Application for [Position] Position",
    "intro": "...",
    "body_1": "**Title** - ...",
    "body_2": "**Title** - ...",
    "body_3": "**Title** - ...",
    "additional": "",
    "attraction": "",
    "closing": "..."
  },
  "email": {
    "recipient": "Hiring Team",
    "subject": "Application - [Position] - Adrian Turion",
    "body": "..."
  }
}
```

## Content Selection

### Resume Requirements
- **Auraia**: 3 bullets from 9 accomplishments
- **RC Group**: 1 bullet from 6
- **Europ Assistance**: 1 bullet from 7
- **Leadership**: 3 from 5 experiences
- **Courses**: 3-4 MAX (comma-separated)
- **Skills**: 5-7 MAX (one line, may use `|` separator)

### Cover Letter Requirements
- **Web research**: Use WebSearch for company values and recent news
- **Intro**: Must reference specific research finding
- **Body**: `**Bold Title** - content` format (use hyphen, not em-dash)
- **Word count**: 250-550 (ideal 350-450)

## Formatting Rules

- **Font**: Times New Roman, 10pt body (11-22pt headings)
- **Output**: 1-page PDF (trimmed via PyPDF2)
- **Cover letter markdown**: `**bold**` syntax supported in body paragraphs

## Writing Style

**DO:**
- Use EXACT keywords from job description (ATS optimization)
- Adapt tone to sector (trading=action, consulting=strategic, M&A=technical)
- Include quantifiable metrics from JSON data
- Mention company name in professional summary
- Reference specific company values/news in cover letter intro

**DON'T:**
- Generic phrases ("passionate about", "excited to leverage")
- Em-dashes (use hyphens or colons)
- Repeat resume content in cover letter
- Exceed 1 page

## Output Structure

```
jobs/[Company] - [Position] - [DD.MM.YYYY]/
├── content.json              # Intermediate data (easy to modify)
├── email_draft.txt           # For email applications
├── Adrian Turion - [Company] - Resume.docx
├── Adrian Turion - [Company] - Cover Letter.docx
└── PDF/
    ├── Adrian Turion - [Company] - Resume.pdf
    └── Adrian Turion - [Company] - Cover Letter.pdf
```

## Modification Examples

| Request | Action |
|---------|--------|
| "CV too long" | Shorten longest bullets in content.json, regenerate resume |
| "Change pro summary" | Edit `resume.professional_summary`, regenerate resume |
| "More AI focus" | Adjust relevant bullets + summary, regenerate resume |
| "Intro too generic" | Edit `cover_letter.intro`, regenerate cover letter |
| "Replace 3rd leadership" | Pick different one from `data/leadership.json`, regenerate resume |
