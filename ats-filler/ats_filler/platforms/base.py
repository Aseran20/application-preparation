"""Base class for platform adapters."""

from abc import ABC, abstractmethod
from typing import List
from playwright.async_api import Page
from pathlib import Path

from ats_filler.schemas.responses import SnapshotResponse, SnapshotField


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

    async def click_save_and_continue(self):
        """Click the 'Save and Continue' button."""
        # Default implementation - can be overridden
        await self.page.get_by_role("button", name="Save and Continue").click()
        await self.page.wait_for_load_state("networkidle")

    async def get_validation_errors(self) -> List[str]:
        """Return list of validation error messages."""
        # Default implementation - can be overridden
        errors = []
        error_elements = await self.page.locator("[role='alert']").all()
        for elem in error_elements:
            text = await elem.text_content()
            if text:
                errors.append(text.strip())
        return errors

    async def count_work_experiences(self) -> int:
        """Count existing work experience entries."""
        # Default implementation - override for platform-specific logic
        return 0

    async def click_add_work_experience(self):
        """Click 'Add Work Experience' button."""
        # Default implementation - override for platform-specific logic
        await self.page.get_by_role("button", name="Add Work Experience").click()

    async def upload_file(self, file_type: str, file_path: Path):
        """Upload a file."""
        # Default implementation - override for platform-specific logic
        async with self.page.expect_file_chooser() as fc_info:
            await self.page.get_by_label(f"Upload {file_type}").click()
        file_chooser = await fc_info.value
        await file_chooser.set_files(str(file_path))
