"""Workday-specific platform adapter."""

from typing import List, Optional
from ats_filler.platforms.base import PlatformAdapter
from ats_filler.schemas.responses import SnapshotResponse, SnapshotField
from ats_filler.common.field_matchers import fuzzy_match_option


class WorkdayAdapter(PlatformAdapter):
    """Workday-specific implementation."""

    # Field mappings from ats/scripts/workday.py
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
        "email": {
            "labels": ["Email Address", "E-mail Address"],
            "type": "text",
            "optional": False
        },
        "phone": {
            "labels": ["Phone Number"],
            "type": "text",
            "optional": False
        },
        "phone_type": {
            "labels": ["Phone Device Type"],
            "type": "select",
            "optional": True
        },
        "address_line_1": {
            "labels": ["Address Line 1"],
            "type": "text",
            "optional": True
        },
        "city": {
            "labels": ["City"],
            "type": "text",
            "optional": True
        },
        "postal_code": {
            "labels": ["Postal Code"],
            "type": "text",
            "optional": True
        },
        "canton": {
            "labels": ["Canton"],
            "type": "select",
            "optional": True
        },
        "linkedin_url": {
            "labels": ["LinkedIn Profile"],
            "type": "text",
            "optional": True
        },
        "how_did_you_hear": {
            "labels": ["How Did You Hear About Us?"],
            "type": "select",
            "optional": True
        },
        "worked_at_company_before": {
            "labels": ["Have you previously worked at"],
            "type": "checkbox",
            "optional": True
        },
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

    async def _get_options(self, element) -> List[str]:
        """Get dropdown options."""
        # Click to open dropdown
        await element.click()
        # Get all options
        option_elements = await self.page.get_by_role("option").all()
        options = []
        for opt in option_elements:
            text = await opt.text_content()
            if text:
                options.append(text.strip())
        # Close dropdown by pressing Escape
        await self.page.keyboard.press("Escape")
        return options

    async def fill_field(self, field: SnapshotField, value: any):
        """Fill a single field using Playwright."""
        if field.field_type == "text":
            await self.page.get_by_label(field.label).fill(str(value))
        elif field.field_type == "select":
            # Open dropdown
            await self.page.get_by_label(field.label).click()

            # Get all options
            option_elements = await self.page.get_by_role("option").all()

            # Try fuzzy match
            matched = await fuzzy_match_option(option_elements, str(value))
            if matched:
                await matched.click()
            else:
                # Fallback: exact match
                await self.page.get_by_role("option", name=str(value)).click()
        elif field.field_type == "checkbox":
            if value:
                await self.page.get_by_label(field.label).check()

    async def fill_work_experience(self, index: int, data: dict):
        """Fill work experience using group-based selectors."""
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

        # Dates using GROUP-BASED selectors
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
        """Fill education entry."""
        # Minimal implementation for now - will expand later
        if "school_name" in data:
            await self.page.get_by_label("School or University").nth(index).fill(data["school_name"])
        if "field_of_study" in data:
            await self.page.get_by_label("Field of Study").nth(index).fill(data["field_of_study"])
