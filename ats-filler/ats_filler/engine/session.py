"""Session management for browser automation."""

import re
from typing import Optional
from pathlib import Path
from playwright.async_api import async_playwright, Browser, Page, BrowserContext


class Session:
    """Manages a single browser session for an application."""

    def __init__(self, session_id: str, url: str, job_folder: Path):
        self.session_id = session_id
        self.url = url
        self.job_folder = job_folder
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.platform: str = "unknown"
        self.adapter = None
        self.current_step: str = "not_started"
        self._playwright = None

    async def initialize(self):
        """Launch browser and detect platform."""
        from ats_filler.platforms.workday import WorkdayAdapter
        from ats_filler.platforms.generic import GenericAdapter

        self._playwright = await async_playwright().start()
        self.browser = await self._playwright.chromium.launch(headless=False)
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()

        await self.page.goto(self.url)

        # Auto-dismiss cookie consent popups
        await self._dismiss_cookies()

        # Platform detection
        self.platform = await self._detect_platform()

        # Load appropriate adapter
        if self.platform == "workday":
            self.adapter = WorkdayAdapter(self.page)
        else:
            self.adapter = GenericAdapter(self.page)

        # Detect initial page
        self.current_step = await self.adapter.detect_current_step()

    async def _dismiss_cookies(self):
        """Auto-dismiss cookie consent popups (decline when possible)."""
        decline_buttons = [
            "Decline",
            "Reject",
            "Reject All",
            "Reject all",
            "Only necessary",
            "Decline optional cookies",
            "Deny",
        ]

        for text in decline_buttons:
            btn = self.page.get_by_role("button", name=re.compile(f"^{text}$", re.I))
            if await btn.count() > 0 and await btn.first.is_visible():
                await btn.first.click()
                await self.page.wait_for_timeout(500)
                return True

        # If no decline button, try generic cookie dismiss buttons
        accept_buttons = ["Accept", "Accept All", "OK", "Got it"]
        for text in accept_buttons:
            btn = self.page.get_by_role("button", name=re.compile(f"^{text}$", re.I))
            if await btn.count() > 0 and await btn.first.is_visible():
                await btn.first.click()
                await self.page.wait_for_timeout(500)
                return True

        return False

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
        if self._playwright:
            await self._playwright.stop()


class SessionManager:
    """Manages multiple browser sessions."""

    def __init__(self):
        self.sessions: dict[str, Session] = {}
        self._session_counter = 0

    async def create_session(self, url: str, job_folder: str) -> str:
        """Create and initialize a new session."""
        self._session_counter += 1
        session_id = f"session_{self._session_counter}"
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
