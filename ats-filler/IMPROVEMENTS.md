# ATS Filler - Limitations & Improvements

## Testing Session: 2026-01-12

### Fixed Issues

1. **~~No generic click tool~~** - FIXED
   - Added `click(session_id, target)` tool in server.py
   - Tries: text match → button role → link role → CSS selector

2. **~~Upload file selector hardcoded~~** - FIXED
   - Workday adapter now uses `[data-automation-id="file-upload-input-ref"]`
   - Base adapter uses `input[type="file"]` fallback
   - Multiple label variations tried

3. **~~No authentication handling~~** - FIXED
   - Added `sign_in(session_id, email, password)` tool
   - Added `create_account(session_id, email, password)` tool with auto T&C

4. **~~next_page() button selector too specific~~** - FIXED
   - Now tries: "Save and Continue", "Save & Continue", "Next", "Continue", "Submit", "Apply"
   - Falls back to Workday `data-automation-id` selector

5. **~~Cookie consent not handled~~** - FIXED
   - Auto-dismiss on `start()` - tries decline buttons first, then accept

### Remaining Issues

1. **Snapshot returns empty fields**
   - Problem: On autofillWithResume page, snapshot shows no fields
   - Current: Only detects buttons, not the upload area
   - Solution: Improve field detection for file upload zones
   - Priority: MEDIUM

2. **probe() returns only first match**
   - Problem: Can only see one element at a time
   - Current: Hard to debug page state
   - Solution: Add `probe_all(session_id, selector)` to return all matches
   - Priority: LOW

### Notes

- Cookie consent appears before form loads → now auto-dismissed
- Julius Baer Workday requires Sign In before accessing application form
- Platform detection works correctly (detected "workday")
- `autofillWithResume` URL flow: Login → Upload Resume → Form

### Testing URLs

- Julius Baer: `https://juliusbaer.wd3.myworkdayjobs.com/en-US/External/job/Zurich/GPS-Associate-Programme--Private-Markets-Analyst-----Zurich-100---f-m-d-_r-17260/apply/autofillWithResume?source=LinkedIn`

---

## Backlog (Future Improvements)

- [x] Add `click(session_id, selector_or_text)` tool
- [x] Add `sign_in()` and `create_account()` tools
- [x] Improve file upload detection with Workday selectors
- [x] Auto-dismiss cookie popups on session start
- [x] Better button detection with multiple fallbacks
- [ ] Better page state detection (login, resume upload, form, review)
- [ ] Add `probe_all()` for debugging
