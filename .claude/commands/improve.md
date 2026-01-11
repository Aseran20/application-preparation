Test and improve ATS form filling scripts on a new site.

---

## Purpose

Use this command to improve `scripts/ats/` code when testing on new Workday instances or other ATS platforms. Unlike `/apply` (production), this mode explicitly allows modifying source code.

## Input

The user provides:
1. A test URL (job application page)
2. Optionally: which section to focus on

## Prerequisite

Use Playwright MCP Local (`mcp__playwright-local__*` tools). NOT Claude in Chrome.

## Workflow

```
1. DETECT PLATFORM
   └── Match URL against detector.py patterns
   └── If unknown → create new platform file

2. FOR EACH SECTION (my_information, work_experience, education, languages):
   │
   ├── Generate script via form_filler.py
   ├── Execute via browser_run_code
   │
   ├── SUCCESS? → Next section
   │
   └── FAILURE? → Debug cycle:
       │
       ├── 1. Take snapshot, identify error
       ├── 2. User resets the section manually
       ├── 3. Analyze root cause
       ├── 4. Modify scripts/ats/*.py to fix
       ├── 5. Re-run script to verify
       └── 6. Repeat until success

3. ALL SECTIONS PASS
   └── Summarize changes made
   └── Offer to commit
```

## Key Difference from /apply

| Situation | `/apply` | `/improve` |
|-----------|----------|------------|
| Script fails | Fix via MCP browser actions | Modify the source code |
| New field type | Skip or manual | Add support to scripts |
| Unknown platform | Error | Create new platform file |

## Files I Can Modify

```
scripts/ats/
├── base.py          # Shared: fuzzy patterns, aliases, helpers
├── workday.py       # Workday-specific generators
├── detector.py      # Platform detection
└── [new_platform].py  # New platforms
```

## Common Fixes

### Selector Issues
- **Wrong nth()**: Use group-based selectors instead
- **Matches wrong element**: Add "not checked" pattern for Workday options
- **Label varies**: Add alias to `LABEL_ALIASES` in base.py

### Dropdown Issues
- **Option name differs**: Add pattern to `FUZZY_PATTERNS` in base.py
- **New value mapping**: Add to `VALUE_TO_FUZZY` in base.py

### Search Fields
- **School not found**: Add to `SCHOOL_FALLBACKS` in base.py
- **Field label varies**: Add alias to `LABEL_ALIASES`

## Testing Commands

```bash
# Test a specific section
py scripts/form_filler.py workday my_information --data '{"given_name": "Test"}'

# Test education with school
py scripts/form_filler.py workday education --data '{"education": [{"school_search": "Lausanne", "school_name": "HEC Lausanne", "degree": "Master"}]}'
```

## After Improvements

Once all sections work:
1. Summarize what was changed
2. Ask user if they want to commit
3. Commit with message describing the improvements

Example commit message:
```
fix(ats): improve Workday education selector robustness

- Add "not checked" pattern to avoid matching selected pills
- Use group-based selectors for education fields
- Add school fallbacks for Swiss universities
```
