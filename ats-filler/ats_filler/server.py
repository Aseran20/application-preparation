"""ATS Filler MCP Server."""

import asyncio
import re
import signal
from pathlib import Path
from typing import List

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from ats_filler.engine.session import SessionManager
from ats_filler.engine.actions import BulkFiller, ExperienceManager, FileUploader

# Initialize FastMCP
mcp = FastMCP(
    "ATS Filler",
    instructions="Automated ATS form filling with session-based workflow"
)

# Global session manager
sessions = SessionManager()


@mcp.tool()
async def start(
    url: str = Field(description="Application URL to navigate to"),
    job_folder: str = Field(description="Path to job folder containing resume/cover letter"),
) -> dict:
    """Start a new browser session and detect the ATS platform.

    Returns session_id for use in subsequent calls.
    """
    session_id = await sessions.create_session(url, job_folder)
    session = sessions.get(session_id)

    return {
        "session_id": session_id,
        "platform": session.platform,
        "current_page": session.current_step,
        "message": f"Session started. Platform detected: {session.platform}"
    }


@mcp.tool()
async def snapshot(
    session_id: str = Field(description="Session ID from start()"),
) -> dict:
    """Introspect current page for available fields and validation errors.

    Useful for debugging or manual field inspection.
    """
    session = sessions.get(session_id)
    result = await session.adapter.snapshot()

    # Convert Pydantic model to dict for MCP response
    return result.model_dump()


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
    filler = BulkFiller(session)
    result = await filler.fill(data)

    return result.model_dump()


@mcp.tool()
async def upsert_experiences(
    session_id: str = Field(description="Session ID from start()"),
    experiences: List[dict] = Field(description="List of work experience entries"),
) -> dict:
    """Add or update work experience entries.

    Handles 'Add Work Experience' button clicks automatically.
    """
    session = sessions.get(session_id)
    manager = ExperienceManager(session)
    return await manager.upsert_work_experiences(experiences)


@mcp.tool()
async def upsert_education(
    session_id: str = Field(description="Session ID from start()"),
    education: List[dict] = Field(description="List of education entries"),
) -> dict:
    """Add or update education entries."""
    session = sessions.get(session_id)
    manager = ExperienceManager(session)
    return await manager.upsert_education(education)


@mcp.tool()
async def upload_file(
    session_id: str = Field(description="Session ID from start()"),
    file_type: str = Field(description="Type of file: 'resume', 'cover_letter', or 'transcript'"),
    file_path: str = Field(description="Absolute path to file"),
) -> dict:
    """Upload a file to the application."""
    session = sessions.get(session_id)
    uploader = FileUploader(session)
    return await uploader.upload(file_type, Path(file_path))


@mcp.tool()
async def next_page(
    session_id: str = Field(description="Session ID from start()"),
) -> dict:
    """Click 'Save and Continue' and detect next page."""
    session = sessions.get(session_id)
    await session.adapter.click_save_and_continue()
    session.current_step = await session.adapter.detect_current_step()

    return {
        "current_page": session.current_step,
        "message": f"Navigated to: {session.current_step}"
    }


@mcp.tool()
async def validate(
    session_id: str = Field(description="Session ID from start()"),
) -> dict:
    """Check for validation errors on current page."""
    session = sessions.get(session_id)
    errors = await session.adapter.get_validation_errors()

    return {
        "errors": errors,
        "warnings": [] if not errors else ["Fix errors before proceeding"]
    }


@mcp.tool()
async def probe(
    session_id: str = Field(description="Session ID from start()"),
    selector: str = Field(description="Playwright selector to check"),
) -> dict:
    """Debug tool: check if selector exists and get its text/options."""
    session = sessions.get(session_id)
    element = session.page.locator(selector).first
    count = await element.count()

    if count == 0:
        return {"found": False}

    text = await element.text_content()
    return {"found": True, "text": text}


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
async def sign_in(
    session_id: str = Field(description="Session ID from start()"),
    email: str = Field(description="Email address"),
    password: str = Field(description="Password"),
) -> dict:
    """Sign in to existing account."""
    session = sessions.get(session_id)
    page = session.page

    # Click Sign In button if exists (opens modal)
    sign_in_btn = page.get_by_role("button", name=re.compile(r"Sign In", re.I))
    if await sign_in_btn.count() > 0:
        await sign_in_btn.first.click()
        await page.wait_for_timeout(500)

    # Fill credentials
    email_field = page.get_by_role("textbox", name=re.compile(r"Email", re.I))
    if await email_field.count() > 0:
        await email_field.fill(email)

    password_field = page.get_by_role("textbox", name=re.compile(r"Password", re.I))
    if await password_field.count() > 0:
        await password_field.fill(password)

    # Submit
    submit = page.get_by_role("button", name=re.compile(r"Sign In", re.I))
    await submit.click()
    await page.wait_for_load_state("networkidle")

    return {"status": "signed_in", "email": email}


@mcp.tool()
async def create_account(
    session_id: str = Field(description="Session ID from start()"),
    email: str = Field(description="Email address"),
    password: str = Field(description="Password"),
) -> dict:
    """Create new account with auto T&C acceptance."""
    session = sessions.get(session_id)
    page = session.page

    # Click Create Account if exists
    create_btn = page.get_by_role("button", name=re.compile(r"Create Account", re.I))
    if await create_btn.count() > 0:
        await create_btn.first.click()
        await page.wait_for_timeout(500)

    # Fill email
    email_field = page.get_by_role("textbox", name=re.compile(r"Email", re.I)).first
    if await email_field.count() > 0:
        await email_field.fill(email)

    # Fill password
    password_field = page.get_by_role("textbox", name=re.compile(r"^Password", re.I)).first
    if await password_field.count() > 0:
        await password_field.fill(password)

    # Verify password
    verify_field = page.get_by_role("textbox", name=re.compile(r"Verify.*Password|Confirm.*Password", re.I))
    if await verify_field.count() > 0:
        await verify_field.fill(password)

    # Accept terms (auto-agree per CLAUDE.md policy)
    agree_checkbox = page.get_by_role("checkbox", name=re.compile(r"I Agree|Accept|Terms", re.I))
    if await agree_checkbox.count() > 0:
        await agree_checkbox.check()

    # Submit
    submit = page.get_by_role("button", name=re.compile(r"Create Account", re.I))
    await submit.click()
    await page.wait_for_load_state("networkidle")

    return {"status": "account_created", "email": email}


def main():
    """Main entry point with graceful shutdown."""

    # Graceful shutdown handler
    def shutdown(signum, frame):
        asyncio.create_task(sessions.cleanup_all())

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    # Run MCP server
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
