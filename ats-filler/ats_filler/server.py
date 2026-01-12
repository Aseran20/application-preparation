"""ATS Filler MCP Server - Simplified Architecture.

6 tools only:
- start(url, job_folder) → Opens browser, returns session_id
- snapshot(session_id) → Returns real selectors from page
- bulk_fill(session_id, data) → Fills text/checkbox/radio fields
- click(session_id, target) → Clicks by text or selector
- dropdown_select(session_id, selector, value) → Handles Workday custom dropdowns
- autocomplete(session_id, selector, search) → Type + wait + Enter
"""

import asyncio
import re
import signal
from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from pydantic import Field


# Initialize FastMCP
mcp = FastMCP(
    "ATS Filler",
    instructions="Automated ATS form filling with session-based workflow"
)


# =============================================================================
# Session Management (simplified - no adapters)
# =============================================================================

class Session:
    """Simple browser session - just page + job_folder."""

    def __init__(self, session_id: str, url: str, job_folder: Path):
        self.session_id = session_id
        self.url = url
        self.job_folder = job_folder
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self._playwright = None

    async def initialize(self):
        """Launch browser and navigate to URL."""
        self._playwright = await async_playwright().start()
        self.browser = await self._playwright.chromium.launch(headless=False)
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
        await self.page.goto(self.url)
        await self._dismiss_cookies()

    async def _dismiss_cookies(self):
        """Auto-dismiss cookie popups (decline when possible)."""
        decline_texts = ["Decline", "Reject", "Reject All", "Only necessary", "Deny"]
        accept_texts = ["Accept", "Accept All", "OK", "Got it"]

        for text in decline_texts + accept_texts:
            try:
                btn = self.page.get_by_role("button", name=re.compile(f"^{text}$", re.I))
                if await btn.count() > 0:
                    await btn.first.click(timeout=2000)
                    await self.page.wait_for_timeout(500)
                    return
            except:
                continue

    async def cleanup(self):
        """Close browser."""
        if self.browser:
            await self.browser.close()
        if self._playwright:
            await self._playwright.stop()


class SessionManager:
    """Manages browser sessions."""

    def __init__(self):
        self.sessions: dict[str, Session] = {}
        self._counter = 0

    async def create(self, url: str, job_folder: str) -> str:
        self._counter += 1
        session_id = f"session_{self._counter}"
        session = Session(session_id, url, Path(job_folder))
        await session.initialize()
        self.sessions[session_id] = session
        return session_id

    def get(self, session_id: str) -> Session:
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        return self.sessions[session_id]

    async def cleanup_all(self):
        for session in self.sessions.values():
            await session.cleanup()
        self.sessions.clear()


sessions = SessionManager()


# =============================================================================
# JavaScript for snapshot (extracts real selectors from page)
# =============================================================================

SNAPSHOT_JS = """() => {
    const fields = [];
    const seen = new Set();

    function addField(field) {
        if (field.selector && !seen.has(field.selector)) {
            seen.add(field.selector);
            fields.push(field);
        }
    }

    // 1. Standard inputs, selects, textareas
    document.querySelectorAll('input, select, textarea').forEach(el => {
        // Skip hidden elements (except file inputs which are always hidden)
        if (el.offsetParent === null && el.type !== 'file') return;

        const field = {
            selector: null,
            label: null,
            type: el.type || el.tagName.toLowerCase(),
            tag: el.tagName.toLowerCase(),
            isDropdown: el.tagName.toLowerCase() === 'select'
        };

        // Build selector (prefer data-automation-id, then id, then name)
        if (el.getAttribute('data-automation-id')) {
            field.selector = `[data-automation-id="${el.getAttribute('data-automation-id')}"]`;
        } else if (el.id) {
            field.selector = `#${el.id}`;
        } else if (el.name) {
            field.selector = `[name="${el.name}"]`;
        }

        // Get label
        field.label = el.getAttribute('aria-label')
            || el.getAttribute('placeholder')
            || el.getAttribute('data-automation-id')
            || null;

        if (!field.label && el.id) {
            const labelEl = document.querySelector(`label[for="${el.id}"]`);
            if (labelEl) field.label = labelEl.textContent.trim();
        }

        addField(field);
    });

    // 2. Workday custom dropdowns (buttons with aria-haspopup)
    document.querySelectorAll('button[aria-haspopup="listbox"], [role="combobox"], [role="listbox"]').forEach(el => {
        if (el.offsetParent === null) return;

        const field = {
            selector: null,
            label: null,
            type: 'dropdown',
            tag: el.tagName.toLowerCase(),
            isDropdown: true,
            currentValue: el.textContent.trim().substring(0, 50)
        };

        if (el.getAttribute('data-automation-id')) {
            field.selector = `[data-automation-id="${el.getAttribute('data-automation-id')}"]`;
        } else if (el.id) {
            field.selector = `#${el.id}`;
        }

        // Try to find label from parent container or aria-label
        field.label = el.getAttribute('aria-label');
        if (!field.label) {
            const container = el.closest('[data-automation-id*="formField"]');
            const labelEl = container?.querySelector('label');
            if (labelEl) field.label = labelEl.textContent.trim();
        }
        if (!field.label && el.id) {
            // Extract label from ID like "country--country" -> "country"
            field.label = el.id.split('--').pop();
        }

        addField(field);
    });

    // 3. Workday prompt icons (another dropdown pattern)
    document.querySelectorAll('[data-automation-id$="promptIcon"]').forEach(el => {
        if (el.offsetParent === null) return;

        const container = el.closest('[data-automation-id*="formField"]');
        const labelEl = container?.querySelector('label');

        const field = {
            selector: `[data-automation-id="${el.getAttribute('data-automation-id')}"]`,
            label: labelEl?.textContent.trim() || el.getAttribute('aria-label'),
            type: 'dropdown-prompt',
            tag: 'button',
            isDropdown: true
        };

        addField(field);
    });

    return fields;
}"""


# =============================================================================
# MCP Tools
# =============================================================================

@mcp.tool()
async def start(
    url: str = Field(description="Application URL to navigate to"),
    job_folder: str = Field(description="Path to job folder containing resume/cover letter"),
) -> dict:
    """Start a new browser session and detect the ATS platform.

    Returns session_id for use in subsequent calls.
    """
    session_id = await sessions.create(url, job_folder)
    session = sessions.get(session_id)

    # Detect platform from URL
    platform = "unknown"
    if "workday" in url.lower() or "myworkdayjobs" in url.lower():
        platform = "workday"

    return {
        "session_id": session_id,
        "platform": platform,
        "url": session.page.url,
        "message": f"Browser opened. Platform: {platform}"
    }


@mcp.tool()
async def snapshot(
    session_id: str = Field(description="Session ID from start()"),
) -> dict:
    """Introspect current page for available fields and validation errors.

    Useful for debugging or manual field inspection.
    """
    session = sessions.get(session_id)
    page = session.page

    # Extract fields using JavaScript
    fields = await page.evaluate(SNAPSHOT_JS)

    # Get validation errors
    errors = []
    error_elements = page.locator('[data-automation-id="errorMessage"], .error-message, [role="alert"]')
    count = await error_elements.count()
    for i in range(min(count, 10)):  # Limit to 10 errors
        text = await error_elements.nth(i).text_content()
        if text and text.strip():
            errors.append(text.strip())

    return {
        "fields": fields,
        "field_count": len(fields),
        "errors": errors,
        "url": page.url
    }


@mcp.tool()
async def bulk_fill(
    session_id: str = Field(description="Session ID from start()"),
    data: dict = Field(description="Normalized data to fill (field_id: value)"),
) -> dict:
    """Fill multiple fields at once using normalized data.

    Fields not present on page are automatically skipped (graceful degradation).
    Returns applied/skipped/failed fields.
    """
    session = sessions.get(session_id)
    page = session.page

    filled = []
    failed = []

    for selector, value in data.items():
        try:
            el = page.locator(selector).first

            # Check element exists
            if await el.count() == 0:
                failed.append({"selector": selector, "error": "not found"})
                continue

            # Get element type
            tag = await el.evaluate("el => el.tagName.toLowerCase()")
            input_type = await el.evaluate("el => el.type || ''")

            # Fill based on type
            if tag == "select":
                await el.select_option(value)
            elif input_type == "checkbox":
                if value:
                    await el.check()
                else:
                    await el.uncheck()
            elif input_type == "radio":
                await el.check()
            elif input_type == "file":
                await el.set_input_files(value)
            else:
                await el.fill(str(value))

            filled.append(selector)

        except Exception as e:
            failed.append({"selector": selector, "error": str(e)})

    return {
        "filled": filled,
        "filled_count": len(filled),
        "failed": failed,
        "failed_count": len(failed)
    }


@mcp.tool()
async def click(
    session_id: str = Field(description="Session ID from start()"),
    target: str = Field(description="Text to click OR CSS/XPath selector"),
) -> dict:
    """Click element by visible text OR selector.

    Tries in order:
    1. Exact text match
    2. Button with matching name
    3. Link with matching name
    4. CSS/XPath selector fallback
    """
    session = sessions.get(session_id)
    page = session.page

    # Try exact text match
    text_locator = page.get_by_text(target, exact=True)
    if await text_locator.count() > 0:
        await text_locator.first.click()
        return {"clicked": target, "method": "text"}

    # Try button role
    btn = page.get_by_role("button", name=target)
    if await btn.count() > 0:
        await btn.first.click()
        return {"clicked": target, "method": "button_role"}

    # Try link role
    link = page.get_by_role("link", name=target)
    if await link.count() > 0:
        await link.first.click()
        return {"clicked": target, "method": "link_role"}

    # Fallback to selector
    selector = page.locator(target)
    if await selector.count() > 0:
        await selector.first.click()
        return {"clicked": target, "method": "selector"}

    raise ValueError(f"Element not found: {target}")


@mcp.tool()
async def dropdown_select(
    session_id: str = Field(description="Session ID from start()"),
    selector: str = Field(description="Selector for the dropdown button/trigger"),
    value: str = Field(description="Value to select (fuzzy matched)"),
) -> dict:
    """Handle Workday custom dropdowns (click to open, then select option).

    Uses fuzzy matching to find the option.
    """
    session = sessions.get(session_id)
    page = session.page

    # Click to open dropdown
    trigger = page.locator(selector).first
    await trigger.click()
    await page.wait_for_timeout(300)

    # Wait for dropdown options to appear
    # Workday uses various patterns for dropdown items
    option_selectors = [
        f'[data-automation-id="promptOption"]:has-text("{value}")',
        f'[role="option"]:has-text("{value}")',
        f'li:has-text("{value}")',
        f'[data-automation-id*="option"]:has-text("{value}")',
    ]

    for opt_selector in option_selectors:
        option = page.locator(opt_selector).first
        if await option.count() > 0:
            await option.click()
            return {"selected": value, "method": opt_selector.split(":")[0]}

    # Fuzzy fallback: find any option containing the value
    all_options = page.locator('[data-automation-id="promptOption"], [role="option"], li[role="option"]')
    count = await all_options.count()

    for i in range(count):
        text = await all_options.nth(i).text_content()
        if text and value.lower() in text.lower():
            await all_options.nth(i).click()
            return {"selected": text.strip(), "method": "fuzzy"}

    # Close dropdown if nothing found
    await page.keyboard.press("Escape")
    raise ValueError(f"Option '{value}' not found in dropdown")


@mcp.tool()
async def autocomplete(
    session_id: str = Field(description="Session ID from start()"),
    selector: str = Field(description="Selector for the autocomplete input"),
    search: str = Field(description="Text to type and search for"),
    fallbacks: list = Field(default=[], description="Fallback values to try if main search fails"),
) -> dict:
    """Handle autocomplete fields (type + wait for suggestions + Enter).

    Used for school names, cities, etc. that require typing then selecting.
    """
    session = sessions.get(session_id)
    page = session.page

    searches_to_try = [search] + (fallbacks or [])

    for attempt, search_text in enumerate(searches_to_try):
        # Click and clear field
        field = page.locator(selector).first
        await field.click()
        await field.fill("")
        await page.wait_for_timeout(200)

        # Type search text
        await field.fill(search_text)
        await page.wait_for_timeout(500)  # Wait for suggestions

        # Press Enter to select first suggestion (don't click - it might navigate away)
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(300)

        # Check if field was accepted
        current_value = await field.input_value()
        if current_value:
            return {
                "selected": current_value,
                "method": "enter",
                "attempt": attempt + 1
            }

    return {
        "selected": None,
        "error": f"Could not find match for: {searches_to_try}",
        "method": "failed"
    }


@mcp.tool()
async def next_page(
    session_id: str = Field(description="Session ID from start()"),
) -> dict:
    """Click 'Save and Continue' and detect next page."""
    session = sessions.get(session_id)
    page = session.page

    # Try common button names
    button_names = ["Save and Continue", "Next", "Continue", "Submit"]

    for name in button_names:
        btn = page.get_by_role("button", name=re.compile(f"^{name}$", re.I))
        if await btn.count() > 0:
            await btn.first.click()
            await page.wait_for_load_state("networkidle", timeout=10000)
            return {
                "clicked": name,
                "new_url": page.url
            }

    raise ValueError(f"No navigation button found. Tried: {button_names}")


@mcp.tool()
async def upload_file(
    session_id: str = Field(description="Session ID from start()"),
    file_path: str = Field(description="Absolute path to file"),
    file_type: str = Field(default="resume", description="Type: 'resume', 'cover_letter', 'transcript'"),
) -> dict:
    """Upload a file to the application."""
    session = sessions.get(session_id)
    page = session.page

    # Find file input (they're usually hidden)
    file_input = page.locator('input[type="file"]').first

    if await file_input.count() == 0:
        raise ValueError("No file input found on page")

    await file_input.set_input_files(file_path)
    await page.wait_for_timeout(1000)  # Wait for upload

    return {
        "uploaded": file_path,
        "file_type": file_type
    }


# =============================================================================
# Main entry point
# =============================================================================

def main():
    """Main entry point with graceful shutdown."""

    def shutdown(signum, frame):
        asyncio.create_task(sessions.cleanup_all())

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
