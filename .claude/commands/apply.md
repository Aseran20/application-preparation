Fill job application forms using Playwright MCP Local with batched execution.

---

## CRITICAL: PAGE-BASED APPROACH

**Run all scripts for a page at once, then fix errors via MCP.**

```
PAGE 1: My Information
├── Run form_filler.py my_information
├── Snapshot → fix via MCP if errors
└── Save and Continue

PAGE 2: My Experience (all scripts at once)
├── Run form_filler.py work_experience
├── Run form_filler.py education
├── Run form_filler.py languages
├── Upload CV + add LinkedIn
├── Snapshot → identify ALL errors
├── Fix errors via MCP (or user resets section → fix script → re-run)
└── Save and Continue

PAGE 3: Voluntary Disclosures
├── Fill date of birth + accept T&C
└── Save and Continue

PAGE 4: Review
└── User clicks Submit
```

## Two Modes

### Testing/Debugging Mode (current)
When scripts fail:
1. User resets the broken section manually
2. I fix the script
3. Re-run the script to verify fix works

### Autonomous Mode (future)
When scripts fail:
1. I fix directly via MCP (no user intervention)
2. Scripts are already optimized from testing phase

## Pre-authorized Actions

The user gives **permanent consent** for:
- Accepting Terms and Conditions / Privacy Policy checkboxes
- Accepting cookies (decline when possible, accept if required)

Do NOT ask for permission for these. Just do it.

## Input

The user provides:
1. An application URL (or navigates there manually)
2. The job folder path (e.g., `jobs/Richemont - Finance Accelerator - 10.01.2026/`)

## Prerequisite

Use Playwright MCP Local (`mcp__playwright-local__*` tools). NOT Claude in Chrome.

## Phase 1: Preparation

### 1.1 Detect platform

Read `data/ats_platforms.json` and match URL against `detect` patterns:

| Platform | URL patterns |
|----------|--------------|
| Workday | workday.com, myworkdayjobs.com |
| SuccessFactors | successfactors.com, jobs.sap.com |
| Greenhouse | greenhouse.io, boards.greenhouse.io |
| Lever | lever.co, jobs.lever.co |
| LinkedIn | linkedin.com/jobs |

Load platform-specific quirks. If unknown platform, use `default_quirks`.

### 1.2 Read source data

```
profile.json                     // Personal info, languages, auth
data/work_experiences.json       // Work history
```

### 1.3 Locate CV

Structure fixe :
```
jobs/[Company] - [Position] - [DD.MM.YYYY]/PDF/Adrian Turion - [Company] - Resume.pdf
```

Pattern glob :
```bash
jobs/*[Company]*/PDF/*Resume.pdf
```

Navigate to URL, handle login if needed, take initial snapshot.

## Phase 2: Fill Pages

### Page 1: My Information

```bash
py scripts/form_filler.py workday my_information --data '<json from profile.json>'
```

Execute returned code → Snapshot → Fix if needed → Save and Continue

### Page 2: My Experience (batch all)

Run ALL scripts, then verify:

```bash
# 1. Work Experience
py scripts/form_filler.py workday work_experience --data '<json>'

# 2. Education
py scripts/form_filler.py workday education --data '<json>'

# 3. Languages
py scripts/form_filler.py workday languages --data '<json>'

# 4. Upload CV (manual via browser_file_upload)
# 5. Add LinkedIn URL (manual)
```

After running all:
1. Take snapshot
2. Check for validation errors
3. If errors on a section:
   - **Testing mode:** User resets section → I fix script → re-run
   - **Autonomous mode:** Fix directly via MCP
4. Save and Continue

### Page 3: Voluntary Disclosures

Simple fields, no script needed:
- Date of birth (spinbuttons)
- Accept Terms and Conditions (checkbox - pre-authorized)

### Page 4: Review

User reviews and clicks Submit manually.

## Form Filler Usage

```bash
py scripts/form_filler.py <platform> <section> --data '<json>'
```

Sections:
- `my_information` - Personal info, address, phone
- `work_experience` - Jobs with dates
- `education` - Schools and degrees
- `languages` - Languages with levels

Returns:
```json
{
  "code": "async (page) => { ... }",
  "filled": ["field_0", "field_1"],
  "notes": "..."
}
```

Execute `code` via `browser_run_code`.

## Key Patterns

### Date Spinbuttons (use group selectors)

```javascript
// ✅ CORRECT: Group-based (handles hidden To fields)
await page.getByRole('group', { name: 'Work Experience 2' })
  .getByRole('group', { name: 'From' })
  .getByRole('spinbutton', { name: 'Month' }).fill('02');

// ❌ WRONG: nth() fails when "currently work here" hides To fields
await page.getByRole('spinbutton', { name: 'Month' }).nth(1).fill('02');
```

### Search Fields (Workday)

```javascript
// Fill + Enter + wait + select option
await page.getByLabel('School or University').fill('Lausanne');
await page.getByLabel('School or University').press('Enter');
await page.waitForTimeout(800);
await page.getByRole('option', { name: 'Université de Lausanne not checked' }).click();
```

### Dropdowns with Fuzzy Matching

Scripts use fuzzy patterns to handle label variations between Workday instances:
- "4 - Native" vs "Native or Bilingual" vs "C2"
- "Master Degree" vs "Master's Degree" vs "MSc"

### Batching Rules

| ONE browser_run_code | Separate tool calls |
|---------------------|---------------------|
| All text fields | File uploads (need modal) |
| All date spinbuttons | |
| All checkboxes | |
| All dropdowns (sequential inside) | |

## Error Recovery

### Script Error
```
Error in work_experience script
     │
     ▼
Testing: User deletes Work Experience entries
Autonomous: I delete via MCP
     │
     ▼
I fix form_filler.py
     │
     ▼
Re-run script → verify fix
```

### Unknown Field
If form has fields not in script:
1. Fill manually via MCP
2. Consider adding to form_filler.py if common

## Learning New Quirks

When a platform behaves unexpectedly:
1. Note the issue and solution
2. Fix the script (form_filler.py)
3. Add to `data/ats_platforms.json` if platform-specific
4. Test on next application

## Final Checklist

Before user submits:
- [ ] No validation errors visible
- [ ] Work experiences match source data
- [ ] Dates correct (check format)
- [ ] CV uploaded
- [ ] LinkedIn added (if field exists)
