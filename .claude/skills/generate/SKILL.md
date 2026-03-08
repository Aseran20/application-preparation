---
name: generate
description: This skill should be used when the user asks to "generate a resume", "create a cover letter", "apply to a job", or provides a job description for application document creation. Generates personalized ATS-optimized resume and cover letter from job postings.
allowed-tools: Bash(python *), Bash(py *), Read, Write, Edit, WebSearch, WebFetch
---

## References

Read before selecting content:
- [references/profile.md](references/profile.md) — bullet pools, extra entries, courses, personal background, positioning strategy
- [references/style.md](references/style.md) — writing rules and tone
- [references/limits.md](references/limits.md) — character limits per field
- [references/Resume - Adrian Turion.pdf](references/Resume%20-%20Adrian%20Turion.pdf) — example CV styled for commodity trading (use as tone/vocabulary reference when sector is commodity-trading)

## Prerequisites

Python packages (install once if missing): `pip install python-docx docx2pdf PyPDF2`

## Workflow

### 1. Analyze job description
- Extract: `company`, `position`, `position_exact`
- Identify 10-15 exact keywords (for ATS)
- Detect sector: `commodity-trading` / `M&A` / `PE` / `wealth-management` / `etc.`
- Write `job_summary` (2-3 sentences)

### 2. Web research
Search for company values, recent news, key differentiators.
Goal: 1-2 concrete findings for `paragraph_1` of the cover letter.

### 3. Select content
From `references/profile.md`, pick:
- 4 Auraia bullets
- 3 C10Play / RC Group bullets
- 3 Europ Assistance / Generali bullets
- 3-5 extra entries (Entrepreneurial & Independent Projects)
- 3-4 courses, tools, skills, interests

### 4. Write content

**Resume:**
- `introduction`: Show trajectory/movement into the sector, not "Seeking [position]". E.g., "Transitioning from X into Y to leverage Z" or "Moving into [field] to apply [skills]". Sector-adapted, ~2 lines, no company name, ends with "Available from May 2026"
- All bullets: action verb + what + metric/context
- `extra_category_title`: "ENTREPRENEURIAL & INDEPENDENT PROJECTS" (default) or "COMMODITY & ENTREPRENEURIAL EXPOSURE" (trading)

**Cover letter** (narrative prose, no bold titles, English, 1 page max):
- `paragraph_1`: Why this company — hook from research
- `paragraph_2`: Why me — max 2 experiences
- `paragraph_3`: Why us — trajectory + fit
- `closing`: "I would welcome the opportunity to discuss my application further."

### 5. Generate

```python
import sys
from pathlib import Path
sys.path.insert(0, "${CLAUDE_SKILL_DIR}/scripts")

from generate import create_project_folder, save_content, generate_all

folder = create_project_folder(company, position)
save_content(content, folder)
results = generate_all(Path(folder))
```

### 6. Validate
- Both PDFs generated, 1 page each
- No `{placeholder}` text remaining

## content.json schema

```json
{
  "metadata": {
    "company": "...",
    "position": "...",
    "position_exact": "...",
    "date_created": "YYYY-MM-DD",
    "job_keywords": ["..."],
    "job_summary": "..."
  },
  "research": {
    "company_values": ["..."],
    "company_mission": "...",
    "recent_news": "...",
    "used_in": ["paragraph_1"]
  },
  "resume": {
    "introduction": "...",
    "auraia_bullets": ["...", "...", "...", "..."],
    "rc_bullets": ["...", "...", "..."],
    "generali_bullets": ["...", "...", "..."],
    "extra_category_title": "ENTREPRENEURIAL & INDEPENDENT PROJECTS",
    "extra_entries": [
      {"title": "...", "sentence": "..."},
      {"title": "...", "sentence": "..."},
      {"title": "...", "sentence": "..."},
      {"title": "...", "sentence": "..."},
      {"title": "...", "sentence": "..."}
    ],
    "coursework": "...",
    "tools": "...",
    "skills": "...",
    "interests": "..."
  },
  "cover_letter": {
    "recipient_name": "Hiring Manager",
    "street_number": "Company Name",
    "postal_city_country": "City, Country",
    "company_name": "...",
    "subject_line": "[Position] - [Company Full Name]",
    "salutation": "Dear Hiring Manager,",
    "paragraph_1": "...",
    "paragraph_2": "...",
    "paragraph_3": "...",
    "closing": "I would welcome the opportunity to discuss my application further."
  },
  "email": {
    "subject": "Application - [Position] - Adrian Turion",
    "body": "..."
  }
}
```

## Modifications

1. Read `content.json` from the job folder
2. Edit the relevant field(s)
3. Regenerate only the impacted document:

```python
import sys
sys.path.insert(0, "${CLAUDE_SKILL_DIR}/scripts")

from generate import regenerate_resume, regenerate_cover_letter

regenerate_resume(folder)        # resume only
regenerate_cover_letter(folder)  # cover letter only
```
