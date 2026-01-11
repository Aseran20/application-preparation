"""ATS Filler MCP Server."""

import asyncio
import signal
from pathlib import Path
from typing import List, Optional

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from ats_filler.engine.session import SessionManager
from ats_filler.engine.actions import BulkFiller, ExperienceManager, FileUploader
from ats_filler.schemas.responses import BulkFillResponse, SnapshotResponse

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
