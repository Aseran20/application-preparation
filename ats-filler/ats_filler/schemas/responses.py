"""Response models for MCP tool results."""

from typing import Optional, List
from enum import Enum
from pydantic import BaseModel


class FieldStatus(str, Enum):
    """Status of field filling operation."""
    APPLIED = "applied"
    SKIPPED = "skipped"
    FAILED = "failed"


class FieldResult(BaseModel):
    """Result of filling a single field."""
    field_id: str
    status: FieldStatus
    message: Optional[str] = None


class BulkFillResponse(BaseModel):
    """Response from bulk_fill operation."""
    applied: List[FieldResult]
    skipped: List[FieldResult]
    failed: List[FieldResult]
    warnings: List[str] = []


class SnapshotField(BaseModel):
    """Field detected on current page."""
    field_id: str  # Normalized ID (e.g., "given_name")
    label: str  # Actual label on page
    field_type: str  # "text", "select", "checkbox"
    required: bool
    options: Optional[List[str]] = None


class SnapshotResponse(BaseModel):
    """Response from snapshot operation."""
    step: str  # "my_information", "work_experience"
    fields: List[SnapshotField]
    buttons: List[str]
    validation_errors: List[str] = []
