# ATS MCP Server - Architecture Design

**Date:** 2026-01-11
**Status:** Design Complete, Ready for Implementation
**Problem:** Token-heavy ATS form filling (5000+ tokens/page via JS generation)
**Solution:** Custom MCP server with session-based workflow (500 tokens/page, 90% reduction)

---

## Problem Statement

Current ATS automation workflow consumes excessive tokens:

```
profile.json → form_filler.py → generates JS code (2000+ tokens)
                                        ↓
                      Claude reads JS → executes via Playwright MCP
```

**Token breakdown per page:**
- Generating verbose JavaScript: ~2000 tokens
- Reading generated code: ~1500 tokens
- Execution responses: ~1500 tokens
- **Total: ~5000 tokens/page**

With 4 pages per application, this consumes ~20,000 tokens unnecessarily.

---

## Solution Overview

Custom MCP server with session-based workflow and normalized data models:

```
profile.json → MCP bulk_fill(session_id, normalized_data) → compact response
```

**Token breakdown with MCP:**
- Tool call with normalized data: ~200 tokens
- Structured response: ~300 tokens
- **Total: ~500 tokens/page (90% reduction)**

**Key innovations:**
- Session context (detect platform once, reuse)
- Normalized data models (platform-agnostic)
- Bulk operations (fill all fields in one call)
- Structured responses (typed, compact)
- Platform adapters (reuse existing Workday logic)
- Graceful degradation (skip optional fields)

---

## Architecture

### Component Structure

```
ats-filler/
├── server.py                 # FastMCP server with 9 tools
├── engine/
│   ├── session.py           # Session + platform detection
│   └── actions.py           # BulkFiller, macros
├── platforms/
│   ├── base.py              # PlatformAdapter interface
│   ├── workday.py           # Workday adapter (reuses form_filler logic)
│   └── generic.py           # Heuristic-based adapter for custom sites
├── schemas/
│   ├── profile.py           # PersonalInfo, WorkExperience, etc.
│   └── responses.py         # BulkFillResponse, SnapshotResponse
├── common/
│   └── field_matchers.py    # Fuzzy matching utilities
├── pyproject.toml
└── README.md
```

### Data Flow

```
1. START
   Claude: start(url, job_folder)
   Server: Browser → detect platform → return session_id

2. SNAPSHOT (optional, for debugging)
   Claude: snapshot(session_id)
   Server: Return available fields + validation errors

3. BULK FILL
   Claude: bulk_fill(session_id, {given_name: "Adrian", email: "..."}]
   Server: Fill all matching fields → return {applied, skipped, failed}

4. UPSERT EXPERIENCES
   Claude: upsert_experiences(session_id, [WorkExperience(...), ...])
   Server: Add/update work entries → return counts

5. NEXT PAGE
   Claude: next_page(session_id)
   Server: Click "Save and Continue" → detect new page
```

---

## 1. MCP Tools (API)

### Core Workflow

#### `start(url, job_folder) → {session_id, platform, current_page}`
- Launch browser (headless=False for debugging)
- Navigate to URL
- Auto-detect platform (workday, successfactors, oracle, generic)
- Load platform adapter
- Return session ID for subsequent calls

#### `snapshot(session_id) → SnapshotResponse`
- Introspect current page
- Return available fields (field_id, label, type, required, options)
- Return validation errors (if any)
- Return available buttons
- Used for debugging or manual filling

#### `bulk_fill(session_id, data) → BulkFillResponse`
- Fill multiple fields at once
- Data format: `{field_id: value}` using normalized field IDs
- Platform adapter handles mapping to actual labels/selectors
- Returns: `{applied: [...], skipped: [...], failed: [...]}`
- Graceful degradation: skip fields not present on page

### Macro Operations

#### `upsert_experiences(session_id, experiences) → {added, updated, skipped}`
- Add or update work experience entries
- Handles "Add Work Experience" button clicks
- Uses group-based selectors for dates (avoids nth() issues)
- Returns counts of added/updated/skipped entries

#### `upsert_education(session_id, education) → {added, updated, skipped}`
- Add or update education entries
- Handles school autocomplete with fallbacks
- Handles "I am currently studying here" checkbox
- Returns counts

#### `upload_file(session_id, file_type, file_path) → {success, message}`
- Upload files (CV, cover letter, transcript)
- Handles file chooser dialogs
- Validates file exists and size
- file_type: "resume", "cover_letter", "transcript"

### Navigation

#### `next_page(session_id) → {current_page, message}`
- Click "Save and Continue" button
- Wait for navigation
- Auto-detect new page type
- Update session.current_step

#### `validate(session_id) → {errors, warnings}`
- Check for validation errors on current page
- Return list of error messages
- Used before next_page() to ensure clean state

### Utility

#### `probe(session_id, selector) → {found, text, options}`
- Debug tool: check if selector exists
- Return element text or options (for dropdowns)
- Used for troubleshooting field detection

---

## 2. Data Schemas

### Normalized Models (schemas/profile.py)

Platform-agnostic data structures that adapt to any ATS:

```python
class PersonalInfo(BaseModel):
    """Maps to 'My Information' section across all platforms"""
    prefix: Optional[str] = None              # Some Workday instances have this
    given_name: str
    family_name: str
    email: str
    phone: str
    phone_type: Optional[str] = "Mobile"
    address_line_1: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    canton: Optional[str] = None              # Switzerland-specific
    linkedin_url: Optional[str] = None
    how_did_you_hear: Optional[str] = None    # Optional dropdown
    worked_at_company_before: bool = False

class WorkExperience(BaseModel):
    job_title: str
    company: str
    location: Optional[str] = None            # Some forms don't have this
    currently_work_here: bool = False
    from_month: str                           # "02" format
    from_year: str                            # "2020" format
    to_month: Optional[str] = None
    to_year: Optional[str] = None
    role_description: Optional[str] = None    # Some forms don't have this

class Education(BaseModel):
    school_name: str
    degree: str                               # "Master's Degree"
    field_of_study: str
    currently_studying_here: bool = False
    from_month: str
    from_year: str
    to_month: Optional[str] = None
    to_year: Optional[str] = None
    gpa: Optional[str] = None                 # Some forms don't have this

class Language(BaseModel):
    language: str                             # "English"
    proficiency: str                          # "Native"

class ApplicationProfile(BaseModel):
    """Complete profile - loaded from profile.json"""
    personal: PersonalInfo
    work_history: List[WorkExperience]
    education_history: List[Education]
    languages: List[Language]
```

**Design principle:** Graceful degradation
- Optional fields are automatically skipped if not present on page
- Platform adapter handles fuzzy matching for labels/options
- No need to maintain per-platform schemas

### Response Models (schemas/responses.py)

Compact, typed responses for token efficiency:

```python
class FieldStatus(str, Enum):
    APPLIED = "applied"    # Successfully filled
    SKIPPED = "skipped"    # Field not present or value is None
    FAILED = "failed"      # Error during filling

class FieldResult(BaseModel):
    field_id: str
    status: FieldStatus
    message: Optional[str] = None  # Error message if failed

class BulkFillResponse(BaseModel):
    applied: List[FieldResult]
    skipped: List[FieldResult]
    failed: List[FieldResult]
    warnings: List[str] = []

class SnapshotField(BaseModel):
    field_id: str           # Normalized ID (e.g., "given_name")
    label: str              # Actual label on page
    field_type: str         # "text", "select", "checkbox"
    required: bool
    options: Optional[List[str]] = None  # For dropdowns

class SnapshotResponse(BaseModel):
    step: str                          # "my_information", "work_experience"
    fields: List[SnapshotField]
    buttons: List[str]                 # ["Save and Continue", "Cancel"]
    validation_errors: List[str] = []
```

---

## 3. Server Implementation

### FastMCP Server (server.py)

```python
from mcp.server.fastmcp import FastMCP
from pydantic import Field

mcp = FastMCP("ATS Filler")

# Global session manager
sessions = SessionManager()

@mcp.tool()
async def start(
    url: str = Field(description="Application URL"),
    job_folder: str = Field(description="Path to job folder"),
) -> dict:
    """Start browser session and detect platform."""
    session_id = await sessions.create_session(url, job_folder)
    session = sessions.get(session_id)
    return {
        "session_id": session_id,
        "platform": session.platform,
        "current_page": session.current_step,
        "message": f"Session started. Platform: {session.platform}"
    }

@mcp.tool()
async def snapshot(session_id: str) -> SnapshotResponse:
    """Introspect current page for available fields."""
    session = sessions.get(session_id)
    return await session.adapter.snapshot()

@mcp.tool()
async def bulk_fill(
    session_id: str,
    data: dict = Field(description="Normalized data to fill"),
) -> BulkFillResponse:
    """Fill multiple fields at once."""
    session = sessions.get(session_id)
    filler = BulkFiller(session)
    return await filler.fill(data)

@mcp.tool()
async def upsert_experiences(
    session_id: str,
    experiences: List[dict],
) -> dict:
    """Add or update work experience entries."""
    session = sessions.get(session_id)
    manager = ExperienceManager(session)
    return await manager.upsert_work_experiences(experiences)

@mcp.tool()
async def upsert_education(
    session_id: str,
    education: List[dict],
) -> dict:
    """Add or update education entries."""
    session = sessions.get(session_id)
    manager = ExperienceManager(session)
    return await manager.upsert_education(education)

@mcp.tool()
async def upload_file(
    session_id: str,
    file_type: str = Field(description="'resume', 'cover_letter', or 'transcript'"),
    file_path: str = Field(description="Absolute path to file"),
) -> dict:
    """Upload a file to the application."""
    session = sessions.get(session_id)
    uploader = FileUploader(session)
    return await uploader.upload(file_type, Path(file_path))

@mcp.tool()
async def next_page(session_id: str) -> dict:
    """Click 'Save and Continue' and detect next page."""
    session = sessions.get(session_id)
    await session.adapter.click_save_and_continue()
    session.current_step = await session.adapter.detect_current_step()
    return {
        "current_page": session.current_step,
        "message": f"Navigated to: {session.current_step}"
    }

@mcp.tool()
async def validate(session_id: str) -> dict:
    """Check for validation errors on current page."""
    session = sessions.get(session_id)
    errors = await session.adapter.get_validation_errors()
    return {
        "errors": errors,
        "warnings": [] if not errors else ["Fix errors before proceeding"]
    }

@mcp.tool()
async def probe(
    session_id: str,
    selector: str = Field(description="Playwright selector to check"),
) -> dict:
    """Debug tool: check if selector exists."""
    session = sessions.get(session_id)
    element = session.page.locator(selector).first
    count = await element.count()
    if count == 0:
        return {"found": False}
    text = await element.text_content()
    return {"found": True, "text": text}

def main():
    import asyncio
    import signal

    # Graceful shutdown
    def shutdown(signum, frame):
        asyncio.create_task(sessions.cleanup_all())

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    mcp.run(transport="stdio")
```

---

## 4. Session Management

### Session Class (engine/session.py)

```python
from playwright.async_api import async_playwright, Browser, Page
from pathlib import Path

class Session:
    def __init__(self, session_id: str, url: str, job_folder: Path):
        self.session_id = session_id
        self.url = url
        self.job_folder = job_folder
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.platform: str = "unknown"
        self.adapter = None
        self.current_step: str = "not_started"

    async def initialize(self):
        """Launch browser and detect platform."""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=False)  # User wants to see browser
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()

        await self.page.goto(self.url)

        # Platform detection
        self.platform = await self._detect_platform()

        # Load appropriate adapter
        if self.platform == "workday":
            self.adapter = WorkdayAdapter(self.page)
        elif self.platform == "successfactors":
            self.adapter = SuccessFactorsAdapter(self.page)  # TODO
        elif self.platform == "oracle":
            self.adapter = OracleAdapter(self.page)  # TODO
        else:
            self.adapter = GenericAdapter(self.page)

        # Detect initial page
        self.current_step = await self.adapter.detect_current_step()

    async def _detect_platform(self) -> str:
        """Auto-detect ATS platform from URL and page content."""
        url = self.page.url.lower()

        # URL-based detection (fast)
        if "workday" in url or "myworkdayjobs" in url:
            return "workday"
        if "successfactors" in url or "jobs.sap.com" in url:
            return "successfactors"
        if "oracle" in url or "taleo" in url:
            return "oracle"

        # Content-based detection (fallback)
        page_content = await self.page.content()
        if "workday" in page_content.lower():
            return "workday"

        return "generic"

    async def cleanup(self):
        """Close browser and cleanup resources."""
        if self.browser:
            await self.browser.close()

class SessionManager:
    def __init__(self):
        self.sessions: dict[str, Session] = {}

    async def create_session(self, url: str, job_folder: str) -> str:
        """Create and initialize a new session."""
        session_id = f"session_{len(self.sessions) + 1}"
        session = Session(session_id, url, Path(job_folder))
        await session.initialize()
        self.sessions[session_id] = session
        return session_id

    def get(self, session_id: str) -> Session:
        """Get session by ID."""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        return self.sessions[session_id]

    async def cleanup_all(self):
        """Cleanup all sessions."""
        for session in self.sessions.values():
            await session.cleanup()
        self.sessions.clear()
```

---

## 5. Actions (Bulk Operations)

### BulkFiller (engine/actions.py)

```python
class BulkFiller:
    def __init__(self, session: Session):
        self.session = session
        self.adapter = session.adapter

    async def fill(self, data: dict) -> BulkFillResponse:
        """Fill multiple fields at once with graceful degradation."""
        results = BulkFillResponse(applied=[], skipped=[], failed=[])

        # Get available fields on current page
        snapshot = await self.adapter.snapshot()
        available_fields = {field.field_id: field for field in snapshot.fields}

        for field_id, value in data.items():
            # Skip None values
            if value is None:
                continue

            # Skip fields not present on page (graceful degradation)
            if field_id not in available_fields:
                results.skipped.append(FieldResult(
                    field_id=field_id,
                    status=FieldStatus.SKIPPED,
                    message="Field not present on page"
                ))
                continue

            # Fill field via adapter
            try:
                field_info = available_fields[field_id]
                await self.adapter.fill_field(field_info, value)
                results.applied.append(FieldResult(
                    field_id=field_id,
                    status=FieldStatus.APPLIED,
                    message=f"Filled: {field_info.label}"
                ))
            except Exception as e:
                results.failed.append(FieldResult(
                    field_id=field_id,
                    status=FieldStatus.FAILED,
                    message=str(e)
                ))

        return results

class ExperienceManager:
    """Macro operations for work experience and education."""

    def __init__(self, session: Session):
        self.session = session
        self.adapter = session.adapter

    async def upsert_work_experiences(self, experiences: List[dict]) -> dict:
        """Add or update work experience entries."""
        added = 0
        updated = 0
        skipped = 0

        # Get current experience count
        current_count = await self.adapter.count_work_experiences()

        for i, exp_data in enumerate(experiences):
            if i < current_count:
                # Update existing
                await self.adapter.fill_work_experience(i, exp_data)
                updated += 1
            else:
                # Add new
                await self.adapter.click_add_work_experience()
                await self.adapter.fill_work_experience(i, exp_data)
                added += 1

        return {"added": added, "updated": updated, "skipped": skipped}

    async def upsert_education(self, education: List[dict]) -> dict:
        """Add or update education entries."""
        # Similar logic to work experiences
        pass

class FileUploader:
    """Handle file uploads."""

    def __init__(self, session: Session):
        self.session = session
        self.adapter = session.adapter

    async def upload(self, file_type: str, file_path: Path) -> dict:
        """Upload a file."""
        if not file_path.exists():
            return {"success": False, "message": f"File not found: {file_path}"}

        # Delegate to adapter
        await self.adapter.upload_file(file_type, file_path)

        return {"success": True, "message": f"Uploaded: {file_path.name}"}
```

---

## 6. Platform Adapters

### Base Adapter (platforms/base.py)

```python
from abc import ABC, abstractmethod

class PlatformAdapter(ABC):
    """Base class for all platform adapters."""

    def __init__(self, page: Page):
        self.page = page

    @abstractmethod
    async def detect_current_step(self) -> str:
        """Detect current page/step (e.g., 'my_information', 'work_experience')."""
        pass

    @abstractmethod
    async def snapshot(self) -> SnapshotResponse:
        """Return available fields on current page."""
        pass

    @abstractmethod
    async def fill_field(self, field: SnapshotField, value: any):
        """Fill a single field."""
        pass

    @abstractmethod
    async def fill_work_experience(self, index: int, data: dict):
        """Fill work experience entry at given index."""
        pass

    @abstractmethod
    async def fill_education(self, index: int, data: dict):
        """Fill education entry at given index."""
        pass

    @abstractmethod
    async def click_save_and_continue(self):
        """Click the 'Save and Continue' button."""
        pass

    @abstractmethod
    async def get_validation_errors(self) -> List[str]:
        """Return list of validation error messages."""
        pass
```

### Workday Adapter (platforms/workday.py)

Reuses existing form_filler.py logic:

```python
class WorkdayAdapter(PlatformAdapter):
    """Workday-specific implementation."""

    # Field mappings from form_filler.py
    FIELD_MAPPINGS = {
        "prefix": {
            "labels": ["Prefix Select One"],
            "type": "select",
            "optional": True
        },
        "given_name": {
            "labels": ["Given Name(s)", "First Name"],
            "type": "text",
            "optional": False
        },
        "family_name": {
            "labels": ["Family Name(s)", "Last Name"],
            "type": "text",
            "optional": False
        },
        # ... all other fields from form_filler.py
    }

    async def detect_current_step(self) -> str:
        """Detect page by checking for specific headings."""
        if await self.page.get_by_role("heading", name="My Information").count() > 0:
            return "my_information"
        if await self.page.get_by_role("heading", name="My Experience").count() > 0:
            return "my_experience"
        if await self.page.get_by_role("heading", name="Voluntary Disclosures").count() > 0:
            return "voluntary_disclosures"
        if await self.page.get_by_role("heading", name="Review").count() > 0:
            return "review"
        return "unknown"

    async def snapshot(self) -> SnapshotResponse:
        """Introspect current page."""
        fields = []

        # Iterate through known field mappings
        for field_id, config in self.FIELD_MAPPINGS.items():
            for label in config["labels"]:
                element = self.page.get_by_label(label).first
                if await element.count() > 0:
                    field_info = SnapshotField(
                        field_id=field_id,
                        label=label,
                        field_type=config["type"],
                        required=not config.get("optional", False),
                        options=await self._get_options(element) if config["type"] == "select" else None
                    )
                    fields.append(field_info)
                    break

        return SnapshotResponse(
            step=await self.detect_current_step(),
            fields=fields,
            buttons=["Save and Continue", "Cancel"],
            validation_errors=await self.get_validation_errors()
        )

    async def fill_field(self, field: SnapshotField, value: any):
        """Fill a single field using Playwright."""
        if field.field_type == "text":
            await self.page.get_by_label(field.label).fill(str(value))
        elif field.field_type == "select":
            # Fuzzy matching for dropdown options
            await self._fill_select_fuzzy(field.label, value, field.options)
        elif field.field_type == "checkbox":
            if value:
                await self.page.get_by_label(field.label).check()

    async def fill_work_experience(self, index: int, data: dict):
        """Fill work experience using group-based selectors (from form_filler.py)."""
        group = f"Work Experience {index + 1}"

        # Basic fields
        if "job_title" in data:
            await self.page.get_by_label("Job Title").nth(index).fill(data["job_title"])
        if "company" in data:
            await self.page.get_by_label("Company").nth(index).fill(data["company"])

        # Location (optional)
        if "location" in data and data["location"]:
            await self.page.get_by_label("Location").nth(index).fill(data["location"])

        # Currently work here checkbox
        if data.get("currently_work_here", False):
            await self.page.get_by_label("I currently work here").nth(index).check()

        # Dates using GROUP-BASED selectors (critical for handling hidden To fields)
        we_group = self.page.get_by_role("group", name=group)

        if "from_month" in data:
            await we_group.get_by_role("group", name="From").get_by_role("spinbutton", name="Month").fill(data["from_month"])
        if "from_year" in data:
            await we_group.get_by_role("group", name="From").get_by_role("spinbutton", name="Year").fill(data["from_year"])

        # To dates (only if not currently working here)
        if not data.get("currently_work_here", False):
            if "to_month" in data:
                await we_group.get_by_role("group", name="To").get_by_role("spinbutton", name="Month").fill(data["to_month"])
            if "to_year" in data:
                await we_group.get_by_role("group", name="To").get_by_role("spinbutton", name="Year").fill(data["to_year"])

        # Description (optional)
        if "role_description" in data and data["role_description"]:
            await self.page.get_by_label("Description").nth(index).fill(data["role_description"])

    async def fill_education(self, index: int, data: dict):
        """Fill education with school autocomplete and fallbacks."""
        group = f"Education {index + 1}"

        # School autocomplete with fallback
        if "school_name" in data:
            await self.page.get_by_label("School or University").nth(index).fill(data["school_name"])
            await self.page.get_by_label("School or University").nth(index).press("Enter")
            await self.page.wait_for_timeout(800)

            # Try primary school name
            option = self.page.get_by_role("option", name=f"{data['school_name']} not checked")
            if await option.count() == 0:
                # Try fallback names (from SCHOOL_FALLBACKS dict)
                fallbacks = SCHOOL_FALLBACKS.get(data["school_name"], [])
                for fallback in fallbacks:
                    option = self.page.get_by_role("option", name=f"{fallback} not checked")
                    if await option.count() > 0:
                        break

                # Ultimate fallback: "Other/School Not Listed"
                if await option.count() == 0:
                    option = self.page.get_by_role("option", name="Other not checked")

            await option.click()

        # Degree (fuzzy matching)
        if "degree" in data:
            await self._fill_select_fuzzy("Degree", data["degree"], group=group)

        # Field of study
        if "field_of_study" in data:
            await self.page.get_by_label("Field of Study").nth(index).fill(data["field_of_study"])

        # Currently studying checkbox
        if data.get("currently_studying_here", False):
            await self.page.get_by_label("I am currently studying here").nth(index).check()

        # Dates (similar group-based logic)
        edu_group = self.page.get_by_role("group", name=group)
        # ... same pattern as work experience

        # GPA (optional)
        if "gpa" in data and data["gpa"]:
            await self.page.get_by_label("GPA").nth(index).fill(data["gpa"])

    async def _fill_select_fuzzy(self, label: str, value: str, options: List[str] = None):
        """Fill select with fuzzy matching for variations."""
        # Uses FUZZY_PATTERNS from common/field_matchers.py
        from common.field_matchers import fuzzy_match_option

        # Open dropdown
        await self.page.get_by_label(label).click()

        # Get all options
        option_elements = await self.page.get_by_role("option").all()

        # Try fuzzy match
        matched = await fuzzy_match_option(option_elements, value)
        if matched:
            await matched.click()
        else:
            # Fallback: exact match
            await self.page.get_by_role("option", name=value).click()

    async def click_save_and_continue(self):
        """Click 'Save and Continue' button."""
        await self.page.get_by_role("button", name="Save and Continue").click()
        await self.page.wait_for_load_state("networkidle")

    async def get_validation_errors(self) -> List[str]:
        """Return validation error messages."""
        errors = []
        error_elements = await self.page.locator("[role='alert']").all()
        for elem in error_elements:
            text = await elem.text_content()
            if text:
                errors.append(text.strip())
        return errors

# School fallbacks for autocomplete
SCHOOL_FALLBACKS = {
    "Université de Lausanne": ["University of Lausanne", "UNIL"],
    "Universität St. Gallen": ["University of St. Gallen", "HSG"],
    # ... more mappings
}
```

### Generic Adapter (platforms/generic.py)

Heuristic-based adapter for custom sites:

```python
class GenericAdapter(PlatformAdapter):
    """Generic adapter for unknown platforms using heuristics."""

    # Multilingual field patterns
    FIELD_PATTERNS = {
        "given_name": ["first name", "given name", "prénom", "vorname", "nome"],
        "family_name": ["last name", "family name", "surname", "nom", "nachname"],
        "email": ["email", "e-mail", "courriel", "mail"],
        "phone": ["phone", "telephone", "téléphone", "telefon"],
        "address": ["address", "adresse", "strasse"],
        "city": ["city", "ville", "stadt"],
        "postal_code": ["zip", "postal", "postleitzahl", "code postal"],
        # ... more patterns
    }

    async def detect_current_step(self) -> str:
        """Detect step by checking headings and form structure."""
        # Check for common heading patterns
        page_text = await self.page.text_content("body")

        if any(kw in page_text.lower() for kw in ["personal info", "about you", "contact"]):
            return "personal_information"
        if any(kw in page_text.lower() for kw in ["experience", "work history", "employment"]):
            return "work_experience"
        if any(kw in page_text.lower() for kw in ["education", "academic"]):
            return "education"

        return "unknown"

    async def snapshot(self) -> SnapshotResponse:
        """Detect fields using heuristics."""
        fields = []

        # Find all input fields
        inputs = await self.page.locator("input, select, textarea").all()

        for element in inputs:
            # Extract label
            label_text = await self._extract_label(element)
            if not label_text:
                continue

            # Detect input type
            input_type = await element.get_attribute("type") or "text"
            tag_name = await element.evaluate("el => el.tagName.toLowerCase()")

            field_type = "text"
            if tag_name == "select":
                field_type = "select"
            elif input_type == "checkbox":
                field_type = "checkbox"
            elif input_type == "email":
                field_type = "email"

            # Match to normalized field_id
            field_id = self._match_field_id(label_text, input_type)

            # Check if required
            required = await element.get_attribute("required") is not None or \
                       await element.get_attribute("aria-required") == "true"

            # Get options if select
            options = None
            if field_type == "select":
                option_elements = await element.locator("option").all()
                options = [await opt.text_content() for opt in option_elements]

            fields.append(SnapshotField(
                field_id=field_id,
                label=label_text,
                field_type=field_type,
                required=required,
                options=options
            ))

        return SnapshotResponse(
            step=await self.detect_current_step(),
            fields=fields,
            buttons=await self._detect_buttons(),
            validation_errors=[]
        )

    async def _extract_label(self, element) -> str:
        """Extract label using multiple strategies."""
        # 1. Associated <label> via for= attribute
        element_id = await element.get_attribute("id")
        if element_id:
            label = self.page.locator(f"label[for='{element_id}']").first
            if await label.count() > 0:
                text = await label.text_content()
                if text:
                    return text.strip()

        # 2. aria-label
        aria_label = await element.get_attribute("aria-label")
        if aria_label:
            return aria_label.strip()

        # 3. placeholder
        placeholder = await element.get_attribute("placeholder")
        if placeholder:
            return placeholder.strip()

        # 4. name attribute (last resort)
        name = await element.get_attribute("name")
        if name:
            return name.replace("_", " ").replace("-", " ").title()

        # 5. Parent <label> wrapping input
        parent = element.locator("xpath=ancestor::label[1]").first
        if await parent.count() > 0:
            text = await parent.text_content()
            if text:
                return text.strip()

        return ""

    def _match_field_id(self, label_text: str, input_type: str) -> str:
        """Match label to normalized field_id using patterns."""
        label_lower = label_text.lower()

        # Use input type as hint
        if input_type == "email":
            return "email"
        if input_type == "tel":
            return "phone"

        # Pattern matching
        for field_id, patterns in self.FIELD_PATTERNS.items():
            for pattern in patterns:
                if pattern in label_lower:
                    return field_id

        # Fallback: use sanitized label as field_id
        return label_text.lower().replace(" ", "_")

    async def fill_field(self, field: SnapshotField, value: any):
        """Fill field using label or aria-label."""
        # Try multiple selectors
        selectors = [
            f"label:has-text('{field.label}') >> xpath=following-sibling::*[1]",
            f"[aria-label='{field.label}']",
            f"[placeholder='{field.label}']",
            f"[name='{field.field_id}']"
        ]

        for selector in selectors:
            element = self.page.locator(selector).first
            if await element.count() > 0:
                if field.field_type == "text":
                    await element.fill(str(value))
                elif field.field_type == "select":
                    await element.select_option(label=str(value))
                elif field.field_type == "checkbox":
                    if value:
                        await element.check()
                return

        raise ValueError(f"Could not find element for field: {field.label}")

    async def fill_work_experience(self, index: int, data: dict):
        """Generic work experience filling."""
        # Less sophisticated than Workday, but works for most forms
        # Use nth() selectors based on index
        if "job_title" in data:
            await self._fill_by_pattern(["job title", "position"], data["job_title"], index)
        if "company" in data:
            await self._fill_by_pattern(["company", "employer"], data["company"], index)
        # ... similar for other fields

    async def _fill_by_pattern(self, patterns: List[str], value: str, index: int = 0):
        """Fill field matching any of the patterns."""
        for pattern in patterns:
            elements = await self.page.get_by_label(pattern, exact=False).all()
            if len(elements) > index:
                await elements[index].fill(value)
                return
        raise ValueError(f"Could not find field matching patterns: {patterns}")

    async def _detect_buttons(self) -> List[str]:
        """Detect available action buttons."""
        buttons = []
        button_elements = await self.page.locator("button, input[type='submit']").all()
        for btn in button_elements:
            text = await btn.text_content() or await btn.get_attribute("value")
            if text:
                buttons.append(text.strip())
        return buttons
```

---

## 7. Configuration

### pyproject.toml

```toml
[project]
name = "ats-filler"
version = "0.1.0"
description = "MCP server for automated ATS form filling"
requires-python = ">=3.10"
dependencies = [
    "mcp>=1.0.0",
    "playwright>=1.40.0",
    "pydantic>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
]

[project.scripts]
ats-filler = "server:main"

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"
```

### Installation

```bash
# From ats-filler/ directory
pip install -e .

# Install Playwright browsers
playwright install chromium
```

### Usage Example

```python
# In Claude Code, after connecting to MCP server
from mcp import ClientSession

# Start session
result = await start(
    url="https://company.wd1.myworkdayjobs.com/position",
    job_folder="jobs/Company - Position - 11.01.2026/"
)
session_id = result["session_id"]
platform = result["platform"]  # "workday"

# Fill personal info
await bulk_fill(session_id, {
    "given_name": "Adrian",
    "family_name": "Turion",
    "email": "adrian@example.com",
    "phone": "+41772623796",
    "phone_type": "Mobile",
    "address_line_1": "Rue Example 10",
    "city": "Lausanne",
    "postal_code": "1005",
    "canton": "Vaud"
})

# Add work experiences
await upsert_experiences(session_id, [
    {
        "job_title": "M&A Analyst",
        "company": "Auraia Partners",
        "location": "Geneva",
        "from_month": "02",
        "from_year": "2024",
        "currently_work_here": True
    },
    # ... more experiences
])

# Upload CV
await upload_file(
    session_id,
    file_type="resume",
    file_path="jobs/Company - Position - 11.01.2026/PDF/Adrian Turion - Company - Resume.pdf"
)

# Next page
await next_page(session_id)
```

---

## Token Efficiency Analysis

### Before (Current System)

```
Page 1: My Information
├── form_filler.py generates 450 lines JS (~2000 tokens)
├── Claude reads JS code (~1500 tokens)
├── browser_run_code executes
└── Response (~500 tokens)
Total: ~4000 tokens

Page 2: My Experience (3 scripts)
├── work_experience script: ~800 tokens
├── education script: ~600 tokens
├── languages script: ~400 tokens
├── Claude reads all: ~1500 tokens
└── Responses: ~700 tokens
Total: ~4000 tokens

Grand total: ~8000 tokens for 2 pages
```

### After (MCP Server)

```
Page 1: My Information
├── bulk_fill(session_id, {given_name: "Adrian", ...}) (~200 tokens)
└── Response: {applied: 12, skipped: 3, failed: 0} (~100 tokens)
Total: ~300 tokens

Page 2: My Experience
├── upsert_experiences(session_id, [exp1, exp2, exp3]) (~300 tokens)
├── upsert_education(session_id, [edu1]) (~150 tokens)
└── Responses: {added: 3}, {added: 1} (~100 tokens)
Total: ~550 tokens

Grand total: ~850 tokens for 2 pages (90% reduction)
```

---

## Implementation Phases

### Phase 1: Core Infrastructure ✅ (Design Complete)
- [x] Design architecture
- [ ] Implement Session + SessionManager
- [ ] Implement FastMCP server skeleton
- [ ] Test basic start() → snapshot() flow

### Phase 2: Workday Adapter ✅ (Reuse Existing)
- [ ] Port form_filler.py logic to WorkdayAdapter
- [ ] Implement bulk_fill() for My Information
- [ ] Implement upsert_experiences() with group-based selectors
- [ ] Implement upsert_education() with school fallbacks
- [ ] Test full application flow on real Workday site

### Phase 3: Generic Adapter
- [ ] Implement heuristic field detection
- [ ] Test on 2-3 custom sites
- [ ] Refine pattern matching

### Phase 4: Additional Platforms
- [ ] SuccessFactors adapter (if needed)
- [ ] Oracle/Taleo adapter (if needed)

### Phase 5: Production Hardening
- [ ] Error handling and retries
- [ ] Logging and debugging tools
- [ ] Performance optimization
- [ ] Documentation

---

## Design Decisions

### Why FastMCP over raw MCP?
- Higher-level API (decorator-based tools)
- Built-in stdio transport
- Less boilerplate
- Recommended by official docs

### Why session-based vs platform parameter?
- Avoid repeating platform detection on each call (80% Workday = waste)
- Store browser state (page, context)
- Enable stateful workflows (track current page)
- Reduce token usage (no need to pass context repeatedly)

### Why normalized data models?
- Platform-agnostic application code
- Graceful degradation (skip optional fields)
- Single source of truth (profile.json)
- Type safety with Pydantic

### Why bulk operations?
- Token efficiency (one call instead of 12)
- Atomic operations (all or nothing)
- Better error handling (partial success tracking)

### Why generic adapter?
- Handle 20% custom sites without writing adapters
- Fallback for unknown platforms
- Uses standard HTML semantics (labels, aria)
- Multilingual support

### Why headless=False?
- User wants to see browser during development
- Easier debugging
- Can watch form filling in real-time
- Production can override with headless=True

---

## Success Criteria

- [x] Design complete and validated
- [ ] 90% token reduction achieved in practice
- [ ] Successfully fills Workday applications end-to-end
- [ ] Generic adapter handles at least 2 custom sites
- [ ] No manual intervention needed for standard fields
- [ ] Clean error messages for failed fields
- [ ] Documentation complete

---

## Next Steps

1. **Document this design** to `docs/plans/2026-01-11-ats-mcp-server-design.md` ✅
2. **Commit design document** to git
3. **Create ats-filler/ directory structure**
4. **Implement Phase 1** (Session + FastMCP skeleton)
5. **Port Workday logic** from form_filler.py to WorkdayAdapter
6. **Test on real Workday application**
