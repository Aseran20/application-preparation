"""Generic adapter for unknown platforms using heuristics."""

from typing import List
from ats_filler.platforms.base import PlatformAdapter
from ats_filler.schemas.responses import SnapshotResponse, SnapshotField


class GenericAdapter(PlatformAdapter):
    """Generic adapter for unknown platforms."""

    async def detect_current_step(self) -> str:
        """Detect step by checking headings and form structure."""
        page_text = await self.page.text_content("body")
        if not page_text:
            return "unknown"

        page_text_lower = page_text.lower()

        if any(kw in page_text_lower for kw in ["personal info", "about you", "contact"]):
            return "personal_information"
        if any(kw in page_text_lower for kw in ["experience", "work history", "employment"]):
            return "work_experience"
        if any(kw in page_text_lower for kw in ["education", "academic"]):
            return "education"

        return "unknown"

    async def snapshot(self) -> SnapshotResponse:
        """Detect fields using heuristics."""
        # Minimal implementation for now
        return SnapshotResponse(
            step=await self.detect_current_step(),
            fields=[],
            buttons=[],
            validation_errors=[]
        )

    async def fill_field(self, field: SnapshotField, value: any):
        """Fill field using label."""
        # Minimal implementation
        await self.page.get_by_label(field.label).fill(str(value))

    async def fill_work_experience(self, index: int, data: dict):
        """Generic work experience filling."""
        # Minimal implementation
        pass

    async def fill_education(self, index: int, data: dict):
        """Generic education filling."""
        # Minimal implementation
        pass
