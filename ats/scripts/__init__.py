"""
ATS Form Filling Module

Provides platform-specific code generators for filling job application forms.

Usage:
    from ats.scripts import workday, detector

    platform = detector.detect_platform(url)
    if platform == "workday":
        result = workday.SECTIONS["my_information"](data)

Or via the main entry point:
    from ats.scripts import fill_section

    result = fill_section("workday", "my_information", data)
"""

from . import base
from . import detector
from . import workday
# from . import oracle  # TODO
# from . import successfactors  # TODO

# Platform registry - maps platform name to module with SECTIONS dict
PLATFORMS = {
    "workday": workday,
    # "oracle": oracle,  # TODO
    # "successfactors": successfactors,  # TODO
}


def fill_section(platform: str, section: str, data: dict) -> dict:
    """Main entry point - generates Playwright code for a section.

    Args:
        platform: ATS platform name (e.g., "workday")
        section: Form section (e.g., "my_information")
        data: Data to fill in the form

    Returns:
        dict with keys:
            - code: Playwright JS code to execute
            - filled: list of fields that will be filled
            - notes: any platform-specific notes
            - error: (only if failed) error message
    """
    if platform not in PLATFORMS:
        return {
            "code": "",
            "filled": [],
            "error": f"Unknown platform: {platform}",
            "supported_platforms": list(PLATFORMS.keys())
        }

    platform_module = PLATFORMS[platform]

    if section not in platform_module.SECTIONS:
        return {
            "code": "",
            "filled": [],
            "error": f"Unknown section: {section}",
            "supported_sections": list(platform_module.SECTIONS.keys())
        }

    return platform_module.SECTIONS[section](data)
