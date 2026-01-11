"""Fuzzy matching utilities for dropdown options."""

import re
from typing import List, Optional
from playwright.async_api import Locator


# Fuzzy patterns from ats/scripts/base.py
FUZZY_PATTERNS = {
    "level_native": [r"native", r"bilingual", r"c2", r"mother\s*tongue"],
    "level_fluent": [r"fluent", r"proficient", r"c1", r"advanced"],
    "level_intermediate": [r"intermediate", r"conversational", r"b2"],
    "level_beginner": [r"beginner", r"basic", r"b1", r"a2"],
    "degree_bachelor": [r"bachelor", r"b\.?sc", r"undergraduate"],
    "degree_master": [r"master", r"msc", r"m\.?s\.?", r"mba", r"graduate"],
    "degree_phd": [r"phd", r"doctorate", r"doctoral"],
}

# Map values to fuzzy keys
VALUE_TO_FUZZY = {
    "Native": "level_native",
    "Fluent": "level_fluent",
    "Intermediate": "level_intermediate",
    "Beginner": "level_beginner",
    "Bachelor's Degree": "degree_bachelor",
    "Master's Degree": "degree_master",
    "PhD": "degree_phd",
}


async def fuzzy_match_option(options: List[Locator], value: str) -> Optional[Locator]:
    """Find dropdown option using fuzzy patterns.

    Args:
        options: List of Playwright option elements
        value: Value to match (e.g., "Native", "Master's Degree")

    Returns:
        Matched option element or None
    """
    # Get fuzzy key for this value
    fuzzy_key = VALUE_TO_FUZZY.get(value)

    if fuzzy_key and fuzzy_key in FUZZY_PATTERNS:
        patterns = FUZZY_PATTERNS[fuzzy_key]

        # Try each pattern
        for pattern in patterns:
            regex = re.compile(pattern, re.IGNORECASE)
            for opt in options:
                text = await opt.text_content()
                if text and regex.search(text):
                    return opt

    # Fallback: exact match
    for opt in options:
        text = await opt.text_content()
        if text and text.strip() == value:
            return opt

    return None
