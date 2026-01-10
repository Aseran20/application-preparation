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
- Professional summary: 2-3 lines, mention company name

**Cover letter:**
- Subject line: position title
- Intro: 60-80 words, hook based on web research
- Body 1/2/3: 60-80 words each, format "**Title** - content"
- Closing: 50-70 words

### 5. Generation
1. Create folder `jobs/[Company] - [Position] - [DD.MM.YYYY]/`
2. Save `content.json` with all content
3. Save `job_description.md`
4. Call Python scripts to generate DOCX + PDF

```python
from scripts.generate import create_project_folder, save_content, save_job_description, generate_all

folder = create_project_folder(company, position)
save_content(content, folder)
save_job_description(job_description_text, folder)
results = generate_all(folder)
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
    "subject": "...",
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
| Field | Max characters |
|-------|----------------|
| professional_summary | 300 |
| auraia_bullets (each) | 220 |
| rc_bullet | 280 |
| europ_bullet | 250 |
| leadership_bullets (each) | 180 |
| courses | 100 |
| skills | 120 |

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
├── job_description.md
├── email_draft.txt                              ← For email applications
├── Adrian Turion - [Company] - Resume.docx
├── Adrian Turion - [Company] - Cover Letter.docx
└── PDF/
    ├── Adrian Turion - [Company] - Resume.pdf
    └── Adrian Turion - [Company] - Cover Letter.pdf
```

## Email draft

Always generated for email applications. Format:

```
Subject: Application - [Position] - Adrian Turion

Dear [Recipient],

Please find attached my resume and cover letter for the [Position] position at [Company].

[1-2 sentences with hook from cover letter intro - company-specific]

I would welcome the opportunity to discuss my application further.

Best regards,
Adrian Turion
+41 77 262 37 96
turionadrian@gmail.com
```

**Keep it short** (5-7 sentences max). The cover letter has the details.
