# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Resume.ai generates personalized, ATS-optimized resumes and cover letters, then automates job application form filling. It analyzes job descriptions, performs web research, selects relevant experiences from JSON databases, produces formatted Word/PDF documents, and fills Workday ATS forms using Playwright automation.

## Commands

### Primary Workflow

```bash
/generate "paste job description here"
```

Generates both resume AND cover letter in a single command. Creates a project folder with all documents.

```bash
/apply
```

Automates Workday ATS form filling using Playwright MCP Local. Runs page-by-page with batch execution.

### Manual Generation/Regeneration

```python
# Generate all documents from content.json
py generator/scripts/generate.py "jobs/[Company] - [Position] - [DD.MM.YYYY]"

# Or programmatically:
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path.cwd()))

from generator.scripts.generate import create_project_folder, save_content, generate_all, regenerate_resume, regenerate_cover_letter

# Full generation
folder = create_project_folder(company, position)
save_content(content, folder)
results = generate_all(Path(folder))  # Pass Path object, not string

# Modify content.json, then regenerate only CV:
regenerate_resume(folder)

# Or only cover letter:
regenerate_cover_letter(folder)
```

### ATS Form Filling

```python
# Generate Playwright code for Workday sections
py ats/scripts/form_filler.py workday my_information --data '<json>'
py ats/scripts/form_filler.py workday work_experience --data '<json>'
py ats/scripts/form_filler.py workday education --data '<json>'
py ats/scripts/form_filler.py workday languages --data '<json>'

# Also supports auth:
py ats/scripts/form_filler.py workday create_account --data '<json>'
py ats/scripts/form_filler.py workday sign_in --data '<json>'
```

Outputs JavaScript code to run via Playwright MCP's `browser_run_code` tool.

### Validation

```bash
py generator/scripts/validate_resume.py "jobs/[Folder]/Adrian Turion - [Company] - Resume.docx"
py generator/scripts/validate_cover_letter.py "jobs/[Folder]/Adrian Turion - [Company] - Cover Letter.docx"
```

### Dependencies

```bash
pip install -r requirements.txt
```

Or manually: `pip install python-docx PyPDF2 docx2pdf`

### Configuration

Personal data is stored in `config.local.json` (gitignored):
```json
{
  "author_name": "Adrian Turion",
  "email": "turionadrian@gmail.com",
  "phone": "+41 77 262 37 96"
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
│  - Generate email_draft.txt         │
└─────────────────────────────────────┘
```

### ATS Automation Flow

```
/apply → Playwright MCP Local + Workday form filling
        │
        ▼
┌─────────────────────────────────────┐
│  PAGE 1: My Information             │
│  - Generate code via form_filler.py │
│  - Run via browser_run_code         │
│  - Snapshot → fix errors via MCP    │
│  - Save and Continue                │
└─────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────┐
│  PAGE 2: Experience (batch)         │
│  - Work experience                  │
│  - Education                        │
│  - Languages                        │
│  - Upload CV + LinkedIn             │
│  - Snapshot → fix ALL errors        │
│  - Save and Continue                │
└─────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────┐
│  PAGE 3: Voluntary Disclosures      │
│  - DOB + T&C acceptance             │
│  - Save and Continue                │
└─────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────┐
│  PAGE 4: Review                     │
│  - User clicks Submit               │
└─────────────────────────────────────┘
```

**Key principle:** Run all scripts for a page at once, then fix errors via MCP before moving to next page.

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
generator/               # Document generation
├── scripts/
│   ├── generate.py       # Main orchestrator
│   ├── resume.py         # Resume generation (content.json → DOCX)
│   ├── cover_letter.py   # Cover letter generation (content.json → DOCX)
│   ├── validate_resume.py
│   └── validate_cover_letter.py
├── utils/
│   ├── config.py         # Paths, constants, placeholders
│   ├── docx.py           # Placeholder replacement, markdown
│   └── pdf.py            # DOCX → PDF conversion, 1-page trim
└── templates/
    ├── Resume - Adrian Turion.docx
    └── Cover Letter - Adrian Turion v2.docx

ats/                     # ATS automation
├── scripts/
│   ├── base.py           # Shared fuzzy matching, code generators
│   ├── workday.py        # Workday-specific patterns and generators
│   ├── form_filler.py    # CLI to generate Playwright code
│   └── detector.py       # ATS platform detection (future)
└── browser_use/

data/                    # SHARED personal data
├── work_experiences.json
├── leadership.json
├── courses_and_other.json
└── my_information.json

jobs/                    # SHARED output folder
└── [Company] - [Position] - [Date]/
```

### Key Functions

**`generator/scripts/generate.py`**
```python
create_project_folder(company, position) -> Path
save_content(content, folder) -> Path  # folder accepts str or Path
load_content(folder) -> dict           # folder accepts str or Path
generate_all(folder) -> dict           # Validates content, then generates
regenerate_resume(folder) -> dict
regenerate_cover_letter(folder) -> dict
generate_email_draft(content, folder) -> Path
validate_content(content) -> (errors, warnings)  # Pre-generation validation
```

**Validation** runs automatically in `generate_all()` and BLOCKS generation if errors:
- Errors if `auraia_bullets` or `leadership_bullets` != 3 elements
- Errors if content is too short (with 5% tolerance on min)
- **Errors if content exceeds max limits (BLOCKS to guarantee 1-page fit)**

**Character limits** (defined in `scripts/generate.py`):
**CRITICAL: These are STRICT limits - exceeding max will block generation to ensure 1-page fit.**
| Field | Min | Max |
|-------|-----|-----|
| professional_summary | 340 | 400 |
| auraia_bullets (each) | 210 | 245 |
| rc_bullet | 260 | 300 |
| europ_bullet | 260 | 300 |
| leadership_bullets (each) | 160 | 190 |
| courses | 60 | 95 |
| skills | 55 | 85 |

**`generator/scripts/resume.py`**
```python
generate_resume(content: dict, output_folder) -> (docx_path, pdf_path)
```

**`generator/scripts/cover_letter.py`**
```python
generate_cover_letter(content: dict, output_folder) -> (docx_path, pdf_path)
```

**`ats/scripts/workday.py`**
```python
SECTIONS = {
    "create_account": generate_create_account,
    "sign_in": generate_sign_in,
    "my_information": generate_my_information,
    "work_experience": generate_work_experience,
    "education": generate_education,
    "languages": generate_languages,
}
```

Each generator returns `{"code": str, "filled": list, "notes": str}` with Playwright JavaScript to run via MCP.

**`ats/scripts/base.py`**
Contains:
- `FUZZY_PATTERNS`: Maps intent to dropdown option keywords (e.g., "level_native" → ["native", "bilingual", "c2"])
- `LABEL_ALIASES`: Maps field keys to ATS label variations (e.g., "given_name" → ["Given Name(s)", "First Name"])
- `SCHOOL_FALLBACKS`: Alternative school names when exact match fails
- `generate_fuzzy_select_code()`: Creates JavaScript for robust dropdown selection
- `generate_search_code()`: Creates JavaScript for search fields with fallbacks

### Data Files

| File | Content |
|------|---------|
| `data/work_experiences.json` | 3 roles: Auraia (9), RC Group (6), Europ Assistance (7 accomplishments) |
| `data/leadership.json` | 5 experiences: McKinsey finalist, AIESEC, Startup, Screeny.ai, Portfolio |
| `data/courses_and_other.json` | Bachelor (17) + Master (15) courses |
| `data/my_information.json` | Personal data for ATS forms (address, phone, etc.) |

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

## ATS Automation Details

### Workday Form Filling

The `/apply` command automates Workday application forms using Playwright MCP Local.

**Workflow:**
1. Generate Playwright code via `form_filler.py` for each section
2. Run code via Playwright MCP's `browser_run_code` tool
3. Take snapshot to verify success
4. Fix errors via MCP if needed
5. Move to next page

**Pre-authorized Actions:**
The user gives permanent consent for:
- Accepting Terms and Conditions / Privacy Policy checkboxes
- Accepting cookies (decline when possible, accept if required)

**Fuzzy Matching:**
The ATS system uses fuzzy pattern matching for robust dropdown selection across different Workday instances. For example:
- "Native" level matches "4 - Native", "Native or Bilingual", "C2"
- "Master Degree" matches "Master", "MSc", "M.S.", "Graduate Degree"

**School Fallbacks:**
If exact school name not found, tries alternatives:
- "HEC Lausanne" → "Université de Lausanne" → "University of Lausanne"
- Finally falls back to "Other/School Not Listed"

### Code Generation Pattern

```python
# Example: Generate code for My Information section
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from ats.scripts import fill_section

data = {
    "prefix": "Mr.",
    "given_name": "Adrian",
    "family_name": "Turion",
    # ... more fields
}

result = fill_section("workday", "my_information", data)
# result["code"] contains JavaScript for browser_run_code
# result["filled"] lists successfully mapped fields
```

## Modification Examples

| Request | Action |
|---------|--------|
| "CV too long" | Shorten longest bullets in content.json, regenerate resume |
| "Change pro summary" | Edit `resume.professional_summary`, regenerate resume |
| "More AI focus" | Adjust relevant bullets + summary, regenerate resume |
| "Intro too generic" | Edit `cover_letter.intro`, regenerate cover letter |
| "Replace 3rd leadership" | Pick different one from `data/leadership.json`, regenerate resume |
| "Fix My Information script" | Edit `ats/scripts/workday.py`, test via `py ats/scripts/form_filler.py workday my_information --data '<json>'` |

## Platform Notes

- **Windows**: Use `py` instead of `python` for all commands
- **Python version**: Python 3.13 (C:\Users\Adrian\AppData\Local\Programs\Python\Python313\python.exe)
- **Character encoding**: All files use UTF-8
