# Resume & Cover Letter AI Generator

Automated system to generate personalized resumes and cover letters for job applications using Claude AI and Tavily web search.

## 📁 Project Structure

```
resume.ai/
├── .claude/
│   └── commands/
│       ├── resume_create.md          # /resume_create command prompt
│       └── cover_letter_create.md    # /cover_letter_create command prompt
├── data/
│   ├── work_experiences.json         # Professional experience with KPIs
│   ├── leadership.json               # Leadership & entrepreneurial experiences
│   └── courses_and_other.json        # Courses and technical skills
├── scripts/
│   ├── generate_resume.py            # Resume generation logic
│   ├── validate_resume.py            # Resume validation (formatting, placeholders)
│   ├── generate_cover_letter.py      # Cover letter generation logic
│   └── validate_cover_letter.py      # Cover letter validation
├── templates/
│   ├── Resume - Adrian Turion.docx           # Resume template
│   └── Cover Letter - Adrian Turion v2.docx  # Cover letter template
├── jobs/
│   └── [Company]_[Position]_[Date]/  # Generated outputs
│       ├── job_description.md
│       ├── Resume_Adrian_Turion.docx
│       └── Cover_Letter_Adrian_Turion.docx
└── job_description.md                # Current job description to target

```

## 🚀 Usage

### Resume Generation

1. **Paste job description** into `job_description.md`
2. **Run command**: `/resume_create`
3. **Claude will**:
   - Analyze job requirements
   - Extract exact keywords
   - Select relevant experiences from JSON databases
   - Generate personalized resume
   - Validate output
   - Save to `jobs/[Company]_[Position]_[Date]/`

**Output**: 1-page CV in Times New Roman 10pt with exact keyword matching for ATS optimization.

### Cover Letter Generation

1. **Paste job description** into `job_description.md`
2. **Run command**: `/cover_letter_create`
3. **Claude will**:
   - Analyze job requirements
   - **Use Tavily MCP** to research:
     - Company mission, values, culture
     - Recent news and initiatives
     - Industry trends
   - Select relevant experiences
   - Generate personalized cover letter with 1-2-3 structure
   - Validate output
   - Save to `jobs/[Company]_[Position]_[Date]/`

**Output**: 1-page cover letter in Times New Roman 10pt with company-specific insights.

## 📋 Key Features

### Resume (`/resume_create`)
- ✅ **1-page constraint** enforcement
- ✅ **ATS optimization** with exact keyword matching
- ✅ **Dynamic content selection** (3 bullets Auraïa, 1 RC, 1 Europ)
- ✅ **Quantifiable metrics** from JSON databases
- ✅ **3-4 courses MAX**, 5-7 skills MAX (one line)
- ✅ **AI/automation mentions** when relevant
- ✅ **Formatting validation** (Times 10pt, black text only)

### Cover Letter (`/cover_letter_create`)
- ✅ **Tavily web research integration** (company intel, news, trends)
- ✅ **1-2-3 punchy structure** with bullet points
- ✅ **Company-specific hooks** using research insights
- ✅ **Narrative storytelling** (deal-maker, innovator, entrepreneur)
- ✅ **Exact keyword matching** for ATS
- ✅ **Formatting validation** (Times 10pt, left-aligned)

## 🔧 Technical Details

### Resume Generation
- **Template**: Word .docx with placeholders
- **Formatting preservation**: Multi-run placeholder handling
- **Font**: Times New Roman 10pt (headings 11-22pt)
- **Validation**: Checks for placeholders, formatting, 1-page constraint

### Cover Letter Generation
- **Template**: Word .docx with numbered bullets (1., 2., 3.) pre-formatted
- **Web Research**: Tavily MCP integration for company/industry insights
- **Formatting preservation**: Preserves all original template formatting
- **Font**: Times New Roman 10pt throughout
- **Signature**: Includes image signature at bottom
- **Validation**: Checks for placeholders, formatting, word count (250-550)

### Data Structure

**work_experiences.json**:
```json
{
  "work_experiences": [
    {
      "id": "auraiacapital_mna",
      "company": "Auraïa Capital Advisory",
      "accomplishments": ["..."],
      "missions": [
        {
          "title": "...",
          "outcomes": "3 mandates; ~CHF 100M value; 30+ acquirers"
        }
      ]
    }
  ]
}
```

**leadership.json**:
```json
{
  "leadership_experiences": [
    {
      "id": "screeny_ai",
      "titre": "Founder & Developer - Screeny.ai",
      "outcomes": "3 clients; ~90% time reduction; +200% growth"
    }
  ]
}
```

## 🎯 Workflow Example

```bash
# 1. Add job description
echo "Commercial Graduate Programme - Glencore..." > job_description.md

# 2. Generate resume
/resume_create
# Output: jobs/Glencore_Commercial_Graduate_05-10-2025/Resume_Adrian_Turion.docx

# 3. Generate cover letter (with Tavily research)
/cover_letter_create
# Output: jobs/Glencore_Commercial_Graduate_05-10-2025/Cover_Letter_Adrian_Turion.docx
```

## 📊 Success Criteria

### Resume
- ✅ Exactly 1 page
- ✅ All placeholders replaced
- ✅ Times New Roman 10pt (resume), specific sizes for headings
- ✅ Contains 10-15 exact keywords from job description
- ✅ Quantifiable outcomes in every bullet
- ✅ Professional summary mentions company name

### Cover Letter
- ✅ 350-450 words (250-550 range)
- ✅ All placeholders replaced
- ✅ Times New Roman 10pt, left-aligned
- ✅ Incorporates Tavily research insights naturally
- ✅ Uses exact keywords from job description
- ✅ 1-2-3 punchy structure with bold titles
- ✅ Company-specific hook in intro

## 🛠️ Maintenance

### Updating Data
- Edit `data/work_experiences.json` to add new roles/accomplishments
- Edit `data/leadership.json` to add new ventures/leadership roles
- Edit `data/courses_and_other.json` to update skills/courses

### Updating Templates
- Templates preserve exact formatting - modify carefully
- Resume: `templates/Resume - Adrian Turion.docx`
- Cover Letter: `templates/Cover Letter - Adrian Turion v2.docx`

### Updating Prompts
- Resume prompt: `.claude/commands/resume_create.md`
- Cover Letter prompt: `.claude/commands/cover_letter_create.md`

## ATS MCP Server

**NEW:** Custom MCP server for automated ATS form filling with 90% token reduction.

See `ats-filler/README.md` for installation and usage.

**Key features:**
- Session-based workflow (detect platform once, reuse)
- 9 MCP tools (start, snapshot, bulk_fill, upsert_*, upload_file, next_page, validate, probe)
- Normalized data models (PersonalInfo, WorkExperience, Education)
- Platform adapters (Workday reuses existing form_filler.py logic, Generic uses heuristics)
- Graceful degradation (optional fields automatically skipped)
- Fuzzy matching for dropdown variations
- Token efficiency: ~500 tokens/page vs ~5000 before

**Architecture:**
```
ats-filler/
├── server.py           # FastMCP server with 9 tools
├── engine/
│   ├── session.py     # Session + platform detection
│   └── actions.py     # BulkFiller, macros
├── platforms/
│   ├── workday.py     # Workday adapter
│   └── generic.py     # Heuristic-based adapter
└── schemas/
    ├── profile.py     # PersonalInfo, WorkExperience, etc.
    └── responses.py   # BulkFillResponse, SnapshotResponse
```

---

**Built with**: Python, python-docx, Claude AI, Tavily MCP, FastMCP, Playwright
