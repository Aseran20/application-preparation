# Plan: Robustness Fixes for Resume.ai

**Date:** 2026-01-10
**Status:** In Progress
**Estimated effort:** ~1 hour

## Context

Critical analysis revealed several bugs and robustness issues affecting daily usage:
- CVs exceeding 1 page without warning (main pain point)
- TypeError when passing string instead of Path
- Empty address placeholders visible in output
- Missing dependency management
- Hardcoded personal data

## Fixes

### Fix #1: str → Path normalization
**File:** `scripts/generate.py`
**Issue:** `generate_all()` and other functions fail with TypeError when receiving a string path.
**Solution:** Add `folder = Path(folder)` at the start of all public functions.

### Fix #2: Empty address placeholders
**File:** `scripts/cover_letter.py`
**Issue:** `[STREET_NUMBER]` and `[POSTAL_CITY_COUNTRY]` appear in output when empty.
**Solution:** Remove paragraphs containing only empty placeholders after replacement.

### Fix #3: Pre-generation length validation
**File:** `scripts/generate.py`
**Issue:** CV exceeds 1 page, discovered only after generation.
**Solution:** Add `validate_content_length()` function that checks character counts against limits from `generate.md` before generating documents.

Character limits (from generate.md):
- professional_summary: 450 chars
- auraia_bullet: 190 chars each
- rc_bullet: 180 chars
- europ_bullet: 180 chars
- leadership_bullet: 150 chars each
- courses: 120 chars
- skills: 100 chars

### Fix #4: requirements.txt
**File:** `requirements.txt` (new)
**Issue:** No dependency management, installation not reproducible.
**Solution:** Create requirements.txt with pinned versions.

### Fix #5: Externalize personal config
**Files:** `config.local.json` (new), `scripts/utils/config.py`, `.gitignore`
**Issue:** Personal data (name, email, phone) hardcoded in source.
**Solution:** Load from `config.local.json` (gitignored) with fallback defaults.

### Fix #6: Array structure validation
**File:** `scripts/generate.py`
**Issue:** Silent failures when arrays have wrong number of elements.
**Solution:** Add `validate_content_structure()` that checks array lengths before generation.

## Implementation Order

1. Fix #4 (requirements.txt) - quick win
2. Fix #1 (str→Path) - eliminates TypeError
3. Fix #2 (empty placeholders) - visible bug
4. Fix #6 (array validation) - catches structure errors
5. Fix #3 (length validation) - main pain point
6. Fix #5 (config locale) - security improvement

## Success Criteria

- [ ] `generate_all("path/as/string")` works without TypeError
- [ ] Empty street/postal don't show placeholders in output
- [ ] Warning displayed before generation if content too long
- [ ] `pip install -r requirements.txt` works
- [ ] Personal data not in tracked files
- [ ] Clear error if auraia_bullets has != 3 elements
