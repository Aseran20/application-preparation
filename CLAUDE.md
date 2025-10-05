# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI-powered resume and cover letter generation system for tailored job applications. The system analyzes job descriptions, extracts requirements, selects relevant experiences from a structured database, and generates professionally formatted Word documents using customizable templates.

## Architecture

### Core Workflow

**Resume Generation Flow:**
1. Read `job_description.md` from root directory
2. Analyze job requirements, extract keywords, identify company culture/tone
3. Select relevant content from JSON databases in `data/`:
   - `work_experiences.json` - Professional experience with multiple accomplishments per role
   - `leadership.json` - Entrepreneurial and leadership experiences
   - `courses_and_other.json` - Coursework and technical skills
4. Call `scripts/generate_resume.py` with selected content
5. Validate with `scripts/validate_resume.py`
6. Output to `jobs/[Company]_[Position]_[DD-MM-YYYY]/`

**Cover Letter Generation Flow:**
1. Read `job_description.md` from root directory
2. **CRITICAL:** Use Tavily MCP to research company mission, recent news, and industry context
3. Select 2-3 key experiences that tell a compelling story
4. Call `scripts/generate_cover_letter.py` with crafted paragraphs
5. Validate with `scripts/validate_cover_letter.py`
6. Output to same folder as resume

### Data Architecture

**Experience Database (`data/`):**
- Each role has multiple accomplishments with quantifiable metrics
- Content is reusable and can be framed differently for different job types
- Accomplishments include specific actions, outcomes, and industry context

**Template System (`templates/`):**
- Word templates with placeholders for dynamic content
- Formatting preserved through special replacement functions
- Fixed structure with strict formatting rules (Times New Roman 10pt)

### Document Generation Core

**Key Scripts:**

`scripts/generate_resume.py`:
- Main function: `generate_resume(professional_summary, auraia_bullets, rc_group_bullet, europ_assistance_bullet, leadership_bullets, courses, skills, company, position)`
- Uses `replace_paragraph_text()` to preserve formatting while replacing placeholders
- NEVER use `paragraph.text = ...` (destroys formatting)
- Handles multi-run placeholders correctly
- Returns `(folder_name, output_path)`

`scripts/generate_cover_letter.py`:
- Main function: `generate_cover_letter(company_name, recipient_name, street_number, postal_city_country, intro_paragraph, body_paragraph_1, body_paragraph_2, body_paragraph_3, additional_context, company_attraction, closing_paragraph, output_folder)`
- Uses `replace_paragraph_text_cl()` to preserve template formatting
- Optional paragraphs (additional_context, company_attraction) can be empty strings
- Automatically formats date and salutation

**Validation Scripts:**
- Check for remaining placeholders (regex patterns for `[...]`, `W\d-B\d`, `L-B\d`)
- Verify Times New Roman 10pt formatting
- Ensure 1-page layout compliance

## Common Commands

### Generate Resume
```bash
/c/Users/Adrian/AppData/Local/Programs/Python/Python313/python.exe scripts/generate_resume.py
```

### Validate Resume
```bash
/c/Users/Adrian/AppData/Local/Programs/Python/Python313/python.exe scripts/validate_resume.py "jobs/[Company]_[Position]_[Date]/Resume_Adrian_Turion.docx"
```

### Validate Cover Letter
```bash
/c/Users/Adrian/AppData/Local/Programs/Python/Python313/python.exe scripts/validate_cover_letter.py "jobs/[Company]_[Position]_[Date]/Cover_Letter_Adrian_Turion.docx"
```

## Claude Code Slash Commands

Two primary slash commands configured in `.claude/commands/`:

### `/resume_create`
Generates a tailored resume based on `job_description.md`. The command:
- Deeply analyzes job description for keywords, tone, culture, industry-specific lingo
- Intelligently selects 3 bullets for Auraïa, 1 for RC Group, 1 for Europ Assistance
- Selects 3 leadership experiences
- Chooses 3-4 relevant courses (NOT 5)
- Crafts company-specific professional summary with exact keywords
- Decides skills format (subdivided vs simple list) based on role requirements
- Maintains 1-page CV constraint

**Critical Requirements:**
- Use EXACT keywords/phrases from job description (for ATS systems)
- Adapt tone to sector (trading = confident/action, consulting = strategic, M&A = technical)
- Professional summary MUST mention company name
- Keep coursework section SHORT (3-4 courses max)
- Skills section must fit on ONE line
- NO generic content - everything tailored to specific role

### `/cover_letter_create`
Generates a compelling cover letter. The command:
- **MUST use Tavily MCP** to search for:
  - Company mission/values/culture
  - Recent company news (2025)
  - Industry trends and context
- Crafts narrative around 3 core questions: Why this role? Why Adrian? Why this company?
- Selects 2-3 experiences that tell a progression story
- Formats with numbered strengths (1., 2., 3.)
- Keeps within 1 page (350-450 words ideal)

**Critical Requirements:**
- Web research is MANDATORY before writing
- Use exact keywords from job description
- NO repetition of resume content (expand stories, don't list)
- Show genuine research through specific company references
- Tone adapted to sector

## Content Selection Philosophy

**Be Intelligent & Adaptive:**
- Same experience can be framed differently for different roles:
  - M&A role: "Led valuation analysis and financial modeling..."
  - Trading role: "Executed analysis on 7 high-stakes deals under tight deadlines..."
  - Consulting role: "Delivered strategic insights across 7 client engagements..."
- Quality over quantity - select fewer, highly relevant bullets
- Match industry language organically
- Think like the recruiter - what persona are they seeking?

**Job Description Signals:**
- "Fast-paced" → Highlight concurrent projects, tight deadlines, execution speed
- "Entrepreneurial" → Emphasize startup experience, ownership, builder mindset
- "Data-driven" → Show quantitative skills, metrics-based achievements
- "Resilience/Pressure" → Demonstrate performance in high-stakes environments
- "Commercial acumen" → Focus on deal-making, negotiation, business judgment
- "Global/International" → Mention cross-border exposure

## Important Technical Details

### Formatting Preservation
- All body text MUST be Times New Roman 10pt
- Use `replace_paragraph_text()` functions in generation scripts
- Reference `templates/cv_formatting_reference.md` for exact specifications
- Validation scripts catch formatting violations

### File Structure
```
resume.ai/
├── .claude/
│   ├── commands/
│   │   ├── resume_create.md (detailed resume generation instructions)
│   │   └── cover_letter_create.md (detailed cover letter instructions)
│   └── settings.local.json
├── data/
│   ├── work_experiences.json (3 roles with multiple accomplishments each)
│   ├── leadership.json (5 experiences with outcomes)
│   └── courses_and_other.json (bachelor + master coursework)
├── jobs/
│   └── [Company]_[Position]_[DD-MM-YYYY]/
│       ├── job_description.md
│       ├── Resume_Adrian_Turion.docx
│       └── Cover_Letter_Adrian_Turion.docx
├── scripts/
│   ├── generate_resume.py (core resume generation)
│   ├── generate_cover_letter.py (core cover letter generation)
│   ├── validate_resume.py (format/placeholder validation)
│   └── validate_cover_letter.py (format/placeholder validation)
├── templates/
│   ├── Resume - Adrian Turion.docx (template with placeholders)
│   ├── Cover Letter - Adrian Turion v2.docx (template with placeholders)
│   └── cv_formatting_reference.md (exact formatting specs)
└── job_description.md (input for generation)
```

### Placeholder System

**Resume Placeholders:**
- `[Your professional summary here...]` → Professional summary
- `[...W1-B1]`, `[...W1-B2]`, `[...W1-B3]` → Auraïa bullets
- `[...W2-B1]` → RC Group bullet
- `[...W3-B1]` → Europ Assistance bullet
- `[...L-B1]`, `[...L-B2]`, `[...L-B3]` → Leadership bullets
- `[Relevant coursework here]` → Comma-separated courses
- `[Relevant software here]` → Technical skills (may include `|` separator)

**Cover Letter Placeholders:**
- `[DATE]`, `[RECIPIENT_NAME]`, `[STREET_NUMBER]`, `[POSTAL_CITY_COUNTRY]`
- `[COMPANY_NAME]`, `[SALUTATION]`
- `[INTRO_PARAGRAPH]`, `[BODY_PARAGRAPH_1]`, `[BODY_PARAGRAPH_2]`, `[BODY_PARAGRAPH_3]`
- `[ADDITIONAL_CONTEXT]`, `[COMPANY_ATTRACTION]`, `[CLOSING_PARAGRAPH]`

## Error Handling

- If `job_description.md` is missing/empty, ask user to provide it
- If validation fails, report specific errors and regenerate
- If templates are missing, alert immediately
- If JSON files are malformed, report parsing errors

## Success Criteria

**Resume:**
- Content highly relevant to specific job
- Professional summary tailored with company name
- All placeholders replaced
- Formatting identical to template
- 1 page maximum
- Passes validation

**Cover Letter:**
- Compelling narrative showing genuine research
- Uses exact job description keywords
- 2-3 specific examples with metrics
- Explains cultural fit beyond skills
- 1 page (350-450 words ideal)
- No resume repetition
- Passes validation
