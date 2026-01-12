# ATS Filler MCP Server

Custom MCP server for automated ATS form filling. Achieves 90% token reduction compared to JavaScript code generation.

## Architecture

**Simplified 8-tool design:**

| Tool | Type | Purpose |
|------|------|---------|
| `start` | Setup | Opens browser, returns session_id |
| `snapshot` | Read | Returns real selectors from page |
| `bulk_fill` | Write | Fills text, checkbox, radio fields |
| `click` | Action | Clicks by text or selector |
| `dropdown_select` | Smart | Handles Workday custom dropdowns |
| `autocomplete` | Smart | Type + wait + Enter (schools, cities) |
| `next_page` | Navigation | Clicks Save/Continue/Next |
| `upload_file` | File | Uploads resume/cover letter |

**Philosophy:**
- `snapshot()` returns REAL selectors - Claude does the mapping
- `bulk_fill()` is dumb - just fills what you give it
- Smart helpers only for genuinely complex interactions (dropdowns, autocomplete)

## Installation

```bash
cd ats-filler
pip install -e .
playwright install chromium
```

## Usage

### From Claude Code

```bash
claude mcp add ats-filler -- uv run --directory C:/Users/Adrian/Downloads/devprojects/resume.ai/ats-filler ats-filler
```

### Workflow

```python
# 1. Start session
result = start(
    url="https://company.wd1.myworkdayjobs.com/position",
    job_folder="jobs/Company - Position - 11.01.2026/"
)
session_id = result["session_id"]

# 2. Take snapshot to see available fields
fields = snapshot(session_id)
# Returns: {"fields": [{"selector": "#name--firstName", "label": "Given Name", "type": "text"}, ...]}

# 3. Fill fields using real selectors from snapshot
bulk_fill(session_id, {
    "#name--legalName--firstName": "Adrian",
    "#name--legalName--lastName": "Turion",
    "#emailAddress--emailAddress": "adrian@example.com"
})

# 4. Handle dropdowns with smart helper
dropdown_select(session_id, "#country--country", "Switzerland")
dropdown_select(session_id, "#phoneNumber--phoneType", "Mobile")

# 5. Handle autocomplete fields (schools, cities)
autocomplete(session_id, "#education--school", "HEC Lausanne",
    fallbacks=["Université de Lausanne", "University of Lausanne"])

# 6. Navigate to next page
next_page(session_id)
```

## Development

### Quick Test with Inspector

```bash
cd ats-filler
uv run mcp dev ats_filler/server.py
```

### Verify Installation

```python
py -c "
from ats_filler.server import mcp
print([t for t in mcp._tool_manager._tools.keys()])
"
# Output: ['start', 'snapshot', 'bulk_fill', 'click', 'dropdown_select', 'autocomplete', 'next_page', 'upload_file']
```

## Token Efficiency

| Approach | Tokens/Page | Notes |
|----------|-------------|-------|
| Playwright MCP | ~3000 | 1 action at a time |
| JS Code Gen | ~5000 | Generate + read + execute |
| **ATS Filler** | **~500** | Bulk operations |

**90% reduction** vs code generation.
