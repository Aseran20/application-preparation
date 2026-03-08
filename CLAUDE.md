# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Resume.ai is a specialized resume and cover letter generation system for rotational programmes and graduate roles. It uses Python scripts to generate ATS-optimized, sector-specific documents from structured JSON data and professional Word templates.

## Architecture

### Skill System
The generate skill (.claude/skills/generate/) is the primary interface encapsulating:
- SKILL.md: Workflow documentation
- scripts/: Python generation logic  
- references/: Content pools and guidelines

### Project Structure
```
jobs/
  └── month-yy/
      └── Company - Role - DD.MM.YYYY/
          ├── content.json
          ├── additional_responses.md
          ├── job_description.md
          ├── PDF/ (generated)
          ├── *.docx (generated)
          └── email_draft.txt (generated)

.claude/skills/generate/
  ├── SKILL.md
  ├── scripts/
  │   ├── generate.py
  │   ├── resume.py
  │   ├── cover_letter.py
  │   └── utils/
  ├── references/
  │   ├── profile.md
  │   ├── style.md
  │   └── limits.md
  └── templates/
```

## Common Tasks

### Generate Job Application Documents
1. Extract job description
2. Run `/generate` skill (6-step workflow: analysis → research → selection → writing → generation → validation)
3. Output: content.json, resume PDF, cover letter PDF, email draft

### Regenerate Resume or Cover Letter Only
After editing content.json:
```python
from generate import regenerate_resume, regenerate_cover_letter
regenerate_resume(folder)
regenerate_cover_letter(folder)
```

## Critical Implementation Details

### Placeholder Replacement
Resume template has 6 separate placeholders per extra entry ({extra-bp1-title}, {extra-bp1-content}). Code maps them as title/content pairs for up to 5 entries. utils/docx.py implements run-level replacement to preserve formatting (bold/non-bold).

### Character Limits (Auto-Enforced)
Validated by generate.py against limits.md:
- Introduction: 180-220 chars (trajectory pattern, not "seeking [position]")
- Auraia bullets: 150-280 chars each (max 2 lines)
- RC/Generali bullets: 110-150 chars each (1 line only)
- Extra entries: 120-160 chars each
- Cover letter: 200-500 chars per paragraph (advisory only)

Generation errors if limits exceeded.

### Sector-Specific Content Selection
profile.md consolidates all work experiences, extra entries, and skills. For each sector:
1. Select 4 Auraia bullets for sector fit
2. Select 3 RC/Generali bullets highlighting context
3. Select 3-5 extra entries showing entrepreneurship
4. Adapt introduction as trajectory ("Moving into X to Y")

### Email Generation
Auto-generated from content.json["email"] section. If no body provided, default template used. Always personalize subject and opening.

## Known Limitations

1. docx2pdf COM crashes on consecutive conversions (workaround: regenerate separately)
2. Character limit validation non-blocking
3. Template hardcoded to max 5 extra entries
4. Cover letter page limits advisory (not auto-trimmed)
5. Web research not automated (manual entry required)

## File Relationships

- profile.md: Source for all bullet pools and projects
- limits.md: Character limits (synced with generate.py CHAR_LIMITS_MAX/MIN)
- style.md: Writing rules and tone guidance
- SKILL.md: User-facing workflow
- content.json: Schema in SKILL.md
- generate.py: Orchestrator (calls resume.py, cover_letter.py, validates)
- resume.py/cover_letter.py: Call utils/docx.py for placeholder replacement
- utils/docx.py: Run-level placeholder replacement core logic

## Notes for Future Development

- Automate company research with MCP server or WebFetch integration
- Add cover letter auto-trim to 1 page
- Move character limits to separate config file
- Document sector-specific vocabulary mappings
