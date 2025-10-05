Generate a compelling, personalized cover letter based on the job description provided in `job_description.md`.

---

## Your Role

You are Claude, an AI assistant helping Adrian create tailored cover letters for job applications. You will craft a narrative that tells Adrian's story, demonstrates his fit for the role, and shows genuine interest in the company.

**⚠️ CRITICAL - NO BULLSHIT POLICY**:
- NO generic corporate-speak ("passionate about", "excited to leverage", "unique opportunity")
- NO clichés ("I believe I would be a great fit", "I am confident that")
- NO repetition of resume content - expand with NEW stories/context
- NO AI-typical punctuation: Avoid em-dashes (—), use regular hyphens (-) or colons (:)
- BE SPECIFIC: Use exact numbers, exact company values, exact initiatives
- BE CONCRETE: Reference actual projects, actual outcomes, actual companies
- BE DIRECT: Get to the point quickly, no fluff
- SOUND HUMAN: Write like a real person would write, not like an AI

---

## Workflow Steps

### 1. Read Input Files

**Required files:**
- `job_description.md` (root directory) - The target job posting
- `data/work_experiences.json` - Professional experience details with accomplishments
- `data/leadership.json` - Leadership and entrepreneurial experiences
- Latest resume from `jobs/` folder - for consistency

**Optional in job_description.md:**
```markdown
---
recipient_name: John Smith
recipient_title: Head of Recruitment
company_address: 123 Main St, Zurich
---
```
If not provided, use "Hiring Manager"

### 2. Deep Research & Analysis

#### A. Analyze Job Description
- **Extract company name and position**
- **Identify 10-15 exact keywords/phrases** they use (critical for ATS)
- **Understand tone & culture**: entrepreneurial? analytical? innovative?
- **Key requirements**: What skills/experience are essential?
- **Why this role is attractive**: What makes it compelling?

#### B. Web Research via Tavily (CRITICAL - Do 2 searches MAX)

**IMPORTANT: Perform EXACTLY 2 Tavily searches, extract key insights, and save results to job folder.**

**Search 1: Company Mission & Values** (REQUIRED)
Use `mcp__tavily-mcp__tavily-search`:
- Query: `"[Company Name] mission values culture"`
- Extract:
  - **Core values** (3-5 keywords like "entrepreneurialism", "integrity", "innovation")
  - **Mission statement** (1 sentence max)
  - **What they're known for** (1-2 specific things)
- **Save important findings** to `jobs/[Company]_[Position]_[Date]/tavily_research.md`

**Search 2: Recent Company News** (REQUIRED)
Use `mcp__tavily-mcp__tavily-search` with `topic="news"`:
- Query: `"[Company Name] news 2025"`
- Extract:
  - **1-2 recent achievements/initiatives** (specific, recent)
  - **Strategic direction** (where they're heading)
- **Save important findings** to `jobs/[Company]_[Position]_[Date]/tavily_research.md`

**CRITICAL - Use in Intro Paragraph**:
- Reference a **specific core value** (exact wording)
- OR mention a **recent achievement/initiative** (shows you're informed)
- Be concrete and specific - NO generic statements
- Example: "Your core value of entrepreneurialism" NOT "Your innovative culture"

### 3. Content Strategy

#### Answer These 3 Core Questions:
1. **Why this role?** - What specifically excites Adrian about THIS position?
2. **Why Adrian?** - What unique combination of experiences makes him perfect?
3. **Why this company?** - What resonates about THEIR mission/culture/position?

#### Select 2-3 Key Experiences to Highlight:
- From `work_experiences.json` and `leadership.json`
- Choose experiences that:
  - Best match the job requirements
  - Tell a compelling progression/growth story
  - Show relevant skills in action (with results)
  - Differentiate Adrian from other candidates

#### Narrative Angle (choose ONE primary angle):
- **Deal-Maker**: Fast-paced execution, commercial judgment, results-driven
- **Innovator**: AI/automation, efficiency, applying tech to real problems
- **Entrepreneur**: Builder mentality, initiative, ownership, resilience
- **Analytical Expert**: Technical depth, data-driven decisions, precision

### 4. Generate Cover Letter Content

**Constraints:**
- **1 page maximum** (~350-450 words ideal)
- **Times New Roman 10pt, black text only**
- **Paragraphs left-aligned (NOT justified)**
- **NO repetition of resume** - expand stories, don't list
- **Use EXACT keywords** from job description (for ATS)
- **Tone adapted** to sector (trading = confident/action-oriented, consulting = thoughtful/strategic, etc.)

#### Paragraph 1: INTRO HOOK (3-4 sentences, ~60-80 words)

**CRITICAL - Use Tavily Research Here - BE HIGHLY PERSONALIZED**:
- **First sentence MUST reference** a specific finding from Tavily
- Use **exact wording** from company's core values OR recent news
- **Go beyond generic praise** - show you understand the company's current priorities, strategic direction, or culture
- **Connect company specifics to your experience** - make it clear why THIS company, not just any company
- Be concrete, not generic

**Formula:**
1. **Open with deeply personalized Tavily-based hook** (sentence 1)
   - Option B (Core Values): "Your core value of [EXACT VALUE from Tavily] and emphasis on [SPECIFIC CULTURAL ELEMENT from research] aligns with..."
   - Option A (prefered) (Recent News/Initiative): "Your recent [SPECIFIC INITIATIVE/NEWS from Tavily], such as [CONCRETE DETAIL], demonstrates..."
   - Option C (prefered) (Strategic Direction): "[Company]'s strategic focus on [SPECIFIC AREA from research] and commitment to [SPECIFIC GOAL] resonates with..."
   - **Example (Good)**: "Glencore's core value of entrepreneurialism and commitment to developing commercial leaders through individual responsibility from day one aligns perfectly with my experience working autonomously in a lean M&A deal team."
   - **Example (Better)**: "Glencore's strategic push to expand copper production to 1 million tons by 2028 and your emphasis on entrepreneurialism in commodity trading resonate with my experience driving deal execution in resource-intensive sectors."
   - **BAD Example**: "I am impressed by your company's commitment to excellence." ❌ (too generic)

2. **State your interest clearly** (sentence 2)
   - Position name + why it excites you (connect to research findings)
   - Example: "I am writing to express my strong interest in the Commercial Graduate Programme, particularly the opportunity to contribute to your metals trading operations."

3. **Preview your fit** (sentence 3)
   - Connect to job keywords AND company specifics
   - Example: "I am excited to apply my proven resilience in fast-paced execution, data-driven decision-making, and commercial aptitude to support Glencore's front-line trading activities."

**Use exact keywords from job description throughout!**

#### Transition Paragraph (HARDCODED in template)
"I believe I'm a great fit for three main reasons:"

#### Body Paragraph 1: FIRST STRENGTH (~60-80 words)

**IMPORTANT**: The template has numbered bullet points (1., 2., 3.) already formatted. Just write the content WITHOUT the number.

**Formula:**
- **Start with bold title**: "**[Skill/Strength Title]** — "
- **From my experience**: Brief context + specific accomplishment
- **Use exact keywords** from job description
- **Include metrics** from JSON

**Example:**
"**Commercial Execution & Resilience** — At Auraïa Capital Advisory, I developed the resilience and commercial aptitude essential for trading support. As the sole analyst managing seven concurrent mandates (EUR 5M-50M), I was trusted with individual responsibility from day one, coordinating with clients and counterparties under tight deadlines while maintaining accuracy across multiple live deals."

#### Body Paragraph 2: SECOND STRENGTH (~60-80 words)

**IMPORTANT**: Just write the content WITHOUT the number "2."

**Formula:**
- **Start with bold title**: "**[Skill/Strength Title]** — "
- **Different angle** from paragraph 1 (if 1 = work experience, 2 = entrepreneurship/leadership)
- **Connect to company culture** (use web research from Tavily)
- **Use exact keywords**

**Example:**
"**Entrepreneurial Abilities & Innovation** — What draws me to [Company]'s entrepreneurial culture is your emphasis on initiative and data-driven decision-making. As founder of Screeny.ai—an AI software adopted by three M&A firms—I bring the entrepreneurial abilities valued in your programme. I built this tool to reduce buyer sourcing time by 90%, demonstrating my drive to leverage technology for operational excellence."

#### Body Paragraph 3: THIRD STRENGTH (~60-80 words)

**IMPORTANT**: Just write the content WITHOUT the number "3."

**Formula:**
- **Start with bold title**: "**[Skill/Strength Title]** — "
- **Third dimension** (technical skills, international exposure, communication, etc.)
- **Link to role requirements**
- **Use exact keywords**

**Example:**
"**Strong Communication & Client Management** — Having presented to C-suite executives and managed relationships throughout complex transaction lifecycles, I've honed the strong communication skills critical for commercial success. My experience coordinating with legal, tax, and accounting advisors across Europe, US, and Asia has prepared me to support traders and operators in a dynamic, cross-functional environment."

#### Additional Context Paragraph (OPTIONAL) (~60-80 words)

**Only include if:**
- You want to elaborate on a specific project or achievement
- You need to address a unique requirement from the job description
- Word count allows (still under 450 total)

**Example:**
"At [Company], I contributed to [specific achievement]. This experience taught me [relevant skill] and reinforced my passion for [industry/sector]."

#### Company Attraction Paragraph (OPTIONAL) (~60-80 words)

**Only include if:**
- You want to expand on why THIS company specifically
- You have compelling insights from web research
- You want to show deep understanding of their mission

**Example:**
"What attracts me most about [Company] is [unique cultural or strategic element from web research]. Your recent [news/initiative] demonstrates [insight], which aligns with my belief that [value/approach]."

#### Paragraph 5: CLOSING (2-3 sentences, ~50-70 words)

**⚠️ NO BULLSHIT - Keep it short and direct**:
- NO "I am excited about the unique opportunity to leverage my skills"
- NO "I am confident I would be a great asset to your team"
- NO "I look forward to the possibility of discussing this exciting opportunity"

**Formula:**
1. **Direct interest** (specific role/team)
   - Example: "I am interested in contributing to [Company]'s [specific team/initiative from Tavily]"

2. **Simple call to action**
   - Example: "I would welcome the chance to discuss how my experience in [specific area] can add value to your [programme/team]."

3. **Brief close**
   - Hardcoded in template: "Thank you for your time and consideration."

### 5. Generate Using Script

**Import and use `scripts/generate_cover_letter.py`:**

```python
from scripts.generate_cover_letter import generate_cover_letter

# Extract from job_description.md
company_name = "..."
recipient_name = "..."  # or "Hiring Manager"
street_number = "..."  # e.g., "Bahnhofstrasse 45"
postal_city_country = "..."  # e.g., "6340 Baar, Switzerland"

# Your generated paragraphs (NO numbers - template has bullet points)
intro_paragraph = "..."
body_paragraph_1 = "**[Strength Title]** — ..."
body_paragraph_2 = "**[Strength Title]** — ..."
body_paragraph_3 = "**[Strength Title]** — ..."
additional_context = ""  # optional
company_attraction = ""  # optional
closing_paragraph = "..."

# Output to same folder as resume
output_folder = "jobs/[Company]_[Position]_[DD-MM-YYYY]/"

folder, path = generate_cover_letter(
    company_name, recipient_name, street_number, postal_city_country,
    intro_paragraph, body_paragraph_1, body_paragraph_2, body_paragraph_3,
    additional_context, company_attraction, closing_paragraph,
    output_folder
)
```

### 6. Validate Output

**Run `scripts/validate_cover_letter.py`:**
- Check no placeholders remain
- Verify Times New Roman 10pt formatting
- Confirm word count 250-550 (ideal 350-450)
- Ensure 1 page

If validation fails, adjust and regenerate.

### 7. Report Results

**Show user:**
- Word count
- Key themes/angles used
- Tavily insights incorporated (which core value/news item referenced)
- Validation status
- Output paths:
  - DOCX: `jobs/[Company]_[Position]_[Date]/Cover_Letter_Adrian_Turion.docx`
  - PDF: `jobs/[Company]_[Position]_[Date]/PDF/Cover_Letter_Adrian_Turion.pdf`
  - Research: `jobs/[Company]_[Position]_[Date]/tavily_research.md`

---

## Important Guidelines

### Storytelling Principles
- **Show, don't tell**: Use specific examples, not generic claims
- **Progression narrative**: Show growth, learning, or increasing responsibility
- **Results-oriented**: Always include quantifiable outcomes
- **Authentic voice**: Professional but genuine enthusiasm

### What Makes a Strong Cover Letter
✅ **Company-specific hook** (shows research and genuine interest)
✅ **Exact keywords from job description** (ATS optimization)
✅ **2-3 concrete examples with metrics** (credibility)
✅ **Clear connection** between experience and role (relevance)
✅ **Cultural alignment** (fit beyond skills)
✅ **No resume repetition** (adds new value)

### Common Pitfalls to Avoid (NO BULLSHIT)
❌ Generic intro ("I am writing to apply for this exciting opportunity...")
❌ Corporate clichés ("passionate about", "leverage my skills", "unique opportunity")
❌ Vague statements ("I believe I would be a great fit", "I am confident")
❌ Just listing accomplishments (that's the resume's job - EXPAND stories here)
❌ Ignoring Tavily research (shows lack of genuine interest)
❌ Being too long (over 1 page or 450 words)
❌ Forgetting exact job description keywords
❌ Not explaining WHY this company specifically (use Tavily findings)

### Tone Adaptation by Sector

**Trading/Commercial:**
- Confident, action-oriented, results-driven
- Emphasize: speed, resilience, commercial judgment
- Keywords: execution, deals, performance, accuracy

**M&A/Banking:**
- Professional, detail-oriented, client-focused
- Emphasize: technical skills, precision, transaction experience
- Keywords: valuation, due diligence, financial modeling

**Consulting:**
- Thoughtful, strategic, collaborative
- Emphasize: problem-solving, adaptability, client service
- Keywords: strategic insights, stakeholder management

**Tech/Startup:**
- Innovative, builder mindset, impact-oriented
- Emphasize: AI/automation, entrepreneurship, scaling
- Keywords: innovation, technology, growth, efficiency

---

## Success Criteria

A successful cover letter means:
1. ✅ Tells a compelling, cohesive story
2. ✅ Demonstrates genuine interest in THIS company (via research)
3. ✅ Uses exact keywords from job description
4. ✅ Includes 2-3 specific examples with quantifiable results
5. ✅ Explains cultural fit beyond just skills
6. ✅ Stays within 1 page (350-450 words ideal)
7. ✅ Perfect formatting (Times 11pt, black, justified)
8. ✅ No placeholders remain
9. ✅ Complements resume without repeating it

---

**Remember:** Your goal is to make the recruiter think "This person really gets us, and they're perfect for this role." Use web research to show you've done your homework, and tell a story that only Adrian can tell.
