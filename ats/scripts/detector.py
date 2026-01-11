"""
ATS Platform Detector.

Detects which ATS platform is being used based on URL patterns.
"""

from typing import Optional


# URL patterns for each platform
PLATFORM_PATTERNS = {
    "workday": [
        "workday.com",
        "myworkdayjobs.com",
        "wd1.myworkdayjobs.com",
        "wd3.myworkdayjobs.com",
        "wd5.myworkdayjobs.com",
    ],
    "oracle": [
        "oracle.com",
        "taleo.net",
        "oraclecloud.com",
    ],
    "successfactors": [
        "successfactors.com",
        "successfactors.eu",
        "jobs.sap.com",
    ],
    "greenhouse": [
        "greenhouse.io",
        "boards.greenhouse.io",
    ],
    "lever": [
        "lever.co",
        "jobs.lever.co",
    ],
    "icims": [
        "icims.com",
    ],
    "smartrecruiters": [
        "smartrecruiters.com",
    ],
}


def detect_platform(url: str) -> Optional[str]:
    """Detect ATS platform from URL.

    Args:
        url: The job application URL

    Returns:
        Platform name (e.g., "workday") or None if unknown
    """
    url_lower = url.lower()

    for platform, patterns in PLATFORM_PATTERNS.items():
        for pattern in patterns:
            if pattern in url_lower:
                return platform

    return None


def get_supported_platforms() -> list[str]:
    """Get list of all supported platform names."""
    return list(PLATFORM_PATTERNS.keys())
