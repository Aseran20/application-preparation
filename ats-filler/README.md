# ATS Filler MCP Server

Custom MCP server for automated ATS form filling. Achieves 90% token reduction compared to JavaScript code generation.

## Installation

```bash
cd ats-filler
pip install -e .
playwright install chromium
```

## Usage

### Connecting via MCP Inspector

```bash
# Install MCP inspector
npm install -g @modelcontextprotocol/inspector

# Run server via inspector
mcp-inspector python -m ats_filler.server
```

### Connecting from Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ats-filler": {
      "command": "python",
      "args": ["-m", "ats_filler.server"]
    }
  }
}
```

## Example Workflow

```python
# 1. Start session
result = start(
    url="https://company.wd1.myworkdayjobs.com/position",
    job_folder="jobs/Company - Position - 11.01.2026/"
)
session_id = result["session_id"]  # "session_1"
platform = result["platform"]  # "workday"

# 2. Fill personal info
bulk_fill(session_id, {
    "given_name": "Adrian",
    "family_name": "Turion",
    "email": "adrian@example.com",
    "phone": "+41772623796",
    "city": "Lausanne"
})

# 3. Add work experiences
upsert_experiences(session_id, [
    {
        "job_title": "M&A Analyst",
        "company": "Auraia Partners",
        "from_month": "02",
        "from_year": "2024",
        "currently_work_here": True
    }
])

# 4. Next page
next_page(session_id)
```

## Architecture

- **Session-based workflow**: Platform detected once, reused across calls
- **Normalized data models**: Platform-agnostic PersonalInfo, WorkExperience, etc.
- **Graceful degradation**: Optional fields automatically skipped if not present
- **Platform adapters**: Workday adapter reuses existing form_filler.py logic

## Token Efficiency

- **Before**: ~5000 tokens/page (JS generation + reading + execution)
- **After**: ~500 tokens/page (tool calls + structured responses)
- **Reduction**: 90%
