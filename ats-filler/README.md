# ATS Filler MCP Server

Custom MCP server for automated ATS form filling. Achieves 90% token reduction compared to JavaScript code generation.

## Installation

```bash
cd ats-filler
pip install -e .
playwright install chromium
```

## Development Workflow

### Method 1: `uv run mcp dev` (Recommended)

**Best for rapid iteration during development:**

```bash
cd ats-filler

# Launch server + inspector in one command
uv run mcp dev server.py

# With editable mode (hot reload)
uv run mcp dev server.py --with-editable .

# Add dependencies on the fly
uv run mcp dev server.py --with playwright --with pydantic
```

**Workflow (30-second iteration):**
1. Edit code in `ats-filler/platforms/workday.py`
2. Ctrl+C in terminal
3. Up arrow + Enter (relaunch)
4. Test in browser inspector UI
5. Repeat

### Method 2: NPX Inspector (Fallback)

**If `uv` is unavailable:**

```bash
# Terminal 1: Launch inspector
npx -y @modelcontextprotocol/inspector

# Terminal 2: Run server
python -m ats_filler.server
```

### Method 3: Unit Tests (Automated)

**For regression prevention:**

```python
# ats-filler/tests/test_workday.py
import pytest
from mcp.shared.memory import create_connected_server_and_client_session

@pytest.mark.asyncio
async def test_bulk_fill():
    async with create_connected_server_and_client_session(app) as session:
        result = await session.call_tool("bulk_fill", {
            "session_id": "test",
            "data": {"given_name": "Adrian"}
        })
        assert result.status == "success"
```

Run tests:
```bash
uv run pytest
```

## Production Usage

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
