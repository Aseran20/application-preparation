"""Base class for platform adapters."""

import re
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
        """Click next page button, trying multiple variations."""
        button_names = [
            "Save and Continue",
            "Save & Continue",
            "Next",
            "Continue",
            "Submit",
            "Apply",
        ]

        for name in button_names:
            btn = self.page.get_by_role("button", name=re.compile(name, re.I))
            if await btn.count() > 0 and await btn.first.is_visible():
                await btn.first.click()
                await self.page.wait_for_load_state("networkidle")
                return {"clicked": name}

        # Fallback: Workday data-automation-id
        workday_next = self.page.locator("[data-automation-id='bottom-navigation-next-button']")
        if await workday_next.count() > 0:
            await workday_next.click()
            await self.page.wait_for_load_state("networkidle")
            return {"clicked": "workday-next-button"}

        raise ValueError("No next/continue button found")

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
        """Upload a file with multiple selector fallbacks."""
        # Try direct file input first (most reliable)
        file_input = self.page.locator("input[type='file']")
        if await file_input.count() > 0:
            await file_input.first.set_input_files(str(file_path))
            return {"uploaded": file_path.name, "method": "input_file"}

        # Try label-based selection
        labels = [
            f"Upload {file_type}",
            f"Upload {file_type.replace('_', ' ')}",
            "Select file",
            "Drop file",
            "Upload",
        ]

        for label in labels:
            trigger = self.page.get_by_text(re.compile(label, re.I))
            if await trigger.count() > 0:
                async with self.page.expect_file_chooser() as fc_info:
                    await trigger.first.click()
                file_chooser = await fc_info.value
                await file_chooser.set_files(str(file_path))
                return {"uploaded": file_path.name, "method": "file_chooser"}

        raise ValueError(f"No file upload element found for {file_type}")
