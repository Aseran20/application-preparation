Generate a personalized resume and cover letter from a job description.

---

## Input

The user provides the job description as an argument.

## Workflow

### 1. Analyze job description
- Extract: company, position, position_exact
- Identify 10-15 exact keywords (for ATS)
- Detect sector and tone (trading/M&A/consulting/tech)
- Write job_summary (2-3 sentences for interview prep recall)

### 2. Web research (WebSearch)
Perform relevant searches based on context:
- Company values/culture
- Recent news
- Industry / competitors
- Specific projects or initiatives mentioned in the posting

Goal: find concrete elements to personalize the documents.

### 3. Content selection
From `data/*.json`, select and adjust if needed:
- 3 Auraia bullets (from 9 available)
- 1 RC Group bullet (from 6)
- 1 Europ Assistance bullet (from 7)
- 3 leadership (from 5)
- 3-4 courses, 5-7 skills

Criteria: keyword match, sector relevance, adapted tone.

### 4. Writing
**Resume:**
- Professional summary: 3-4 lines, mention company name AND specific program/role details, personalize to job

**Cover letter:**
- Subject line: "**Subject:** Application for [Position] Position" (bold with prefix)
- Intro: 60-80 words, hook based on web research
- Body 1/2/3: 60-80 words each, format "**Title** - content"
- Closing: 50-70 words

### 5. Generation
1. Create folder `jobs/[Company] - [Position] - [DD.MM.YYYY]/`
2. Save `content.json` with all content
3. Call Python scripts to generate DOCX + PDF

**Note:** Do NOT save job_description.md - it wastes output tokens rewriting content already in the prompt.

```python
from pathlib import Path
from scripts.generate import create_project_folder, save_content, generate_all

folder = create_project_folder(company, position)
save_content(content, folder)
results = generate_all(Path(folder))  # Pass Path object to avoid str/Path error
```

### 6. Validation
- Verify no placeholders remain
- Confirm PDFs are generated (1 page each)

## content.json Structure

```json
{
  "metadata": {
    "company": "...",
    "position": "...",
    "position_exact": "...",
    "date_created": "...",
    "job_keywords": [...],
    "job_summary": "..."
  },
  "research": {
    "company_values": [...],
    "company_mission": "...",
    "recent_news": "...",
    "used_in": [...]
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
    "recipient": "...",
    "street": "...",
    "postal": "...",
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

## Post-generation modifications

If the user requests a change:
1. Read `content.json` from the folder
2. Modify the relevant field
3. Regenerate only the impacted document

Examples:
- "Resume too long" → shorten bullets in content.json, regenerate resume
- "Change the intro" → modify `cover_letter.intro`, regenerate cover letter
- "More focus on AI" → adjust relevant bullets + summary

## Character limits (1-page guardrail)

**CRITICAL: Documents must fit on 1 page. Respect these limits:**

**Resume:**
| Field | Min chars | Max chars |
|-------|-----------|-----------|
| professional_summary | 340 | 420 |
| auraia_bullets (each) | 210 | 260 |
| rc_bullet | 260 | 320 |
| europ_bullet | 260 | 320 |
| leadership_bullets (each) | 160 | 200 |
| courses | 60 | 100 |
| skills | 55 | 90 |

**Note:** rc_bullet and europ_bullet have higher limits since there's only 1 bullet each. Limits are validated in `scripts/generate.py` - too short = error, too long = warning.

**Cover letter:**
| Field | Max characters |
|-------|----------------|
| intro | 450 |
| body_1, body_2, body_3 (each) | 400 |
| closing | 350 |

**If PDF generation shows WARNING about exceeding 1 page:**
1. Check which fields are longest
2. Shorten them in content.json
3. Regenerate the document
4. Repeat until no warning

## Writing style

**DO:**
- Use EXACT keywords from job description (ATS optimization)
- Adapt tone to sector
- Include quantifiable metrics
- Mention company name in summary
- Reference specific company values/news in cover letter intro
- **Stay within character limits above**

**DON'T:**
- Generic phrases ("passionate about", "excited to leverage")
- Em-dashes (use hyphens or colons)
- Repeat resume content in cover letter
- Exceed 1 page

## Output files

```
jobs/[Company] - [Position] - [DD.MM.YYYY]/
├── content.json
├── email_draft.txt                              ← For email applications
├── Adrian Turion - [Company] - Resume.docx
├── Adrian Turion - [Company] - Cover Letter.docx
└── PDF/
    ├── Adrian Turion - [Company] - Resume.pdf
    └── Adrian Turion - [Company] - Cover Letter.pdf
```

## Email draft

**ALWAYS personalize the email body** - never use generic template.

Write the `email.body` in content.json with:
1. Brief intro mentioning the position
2. 1-2 sentences with the hook from cover letter intro (company-specific research)
3. Call to action

**Example:**
```json
{
  "email": {
    "recipient": "Hiring Team",
    "subject": "Application - Commercial Graduate Programme - Adrian Turion",
    "body": "Dear Hiring Team,\n\nPlease find attached my resume and cover letter for the Commercial Graduate Programme at Glencore.\n\nYour core value of entrepreneurialism and emphasis on individual responsibility from day one resonates with my experience leading deal execution autonomously in a lean M&A team. I am eager to bring this mindset to your trading operations.\n\nI would welcome the opportunity to discuss my application further.\n\nBest regards,\nAdrian Turion\n+41 77 262 37 96\nturionadrian@gmail.com"
  }
}
```

**Keep it short** (5-7 sentences max). The cover letter has the details.
