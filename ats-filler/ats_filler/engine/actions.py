"""Actions for bulk operations."""

from typing import List
from pathlib import Path

from ats_filler.engine.session import Session
from ats_filler.schemas.responses import BulkFillResponse, FieldResult, FieldStatus


class BulkFiller:
    """Handles bulk field filling operations."""

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
        # Similar logic to work experiences - implement when needed
        return {"added": 0, "updated": 0, "skipped": 0}


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
