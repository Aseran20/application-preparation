"""
Browser Use - Job Application Agent
Uses Gemini 3 Flash with persistent Chrome profile for job applications.
"""

import asyncio
import json
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from browser_use import Agent, Browser, BrowserProfile
from browser_use import ChatGoogle


# Paths
PROJECT_ROOT = Path(__file__).parent.parent
PROFILE_PATH = PROJECT_ROOT / "profile.json"
WORK_EXP_PATH = PROJECT_ROOT / "data" / "work_experiences.json"
LEADERSHIP_PATH = PROJECT_ROOT / "data" / "leadership.json"

# Browser Use profile directory (separate from your main Chrome)
BROWSER_USE_PROFILE_DIR = Path.home() / ".browseruse" / "profiles" / "job-apply"


def load_profile():
    """Load candidate profile data."""
    with open(PROFILE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_work_experiences():
    """Load work experiences data."""
    with open(WORK_EXP_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_leadership():
    """Load leadership experiences data."""
    with open(LEADERSHIP_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_sensitive_data(profile: dict) -> dict:
    """
    Extract sensitive data for secure form filling.
    The LLM only sees placeholders (keys), real values are injected into DOM.
    """
    return {
        "job_email": profile["auth"]["job_portals_email"],
        "job_password": profile["auth"]["job_portals_password"],
    }


def format_work_experience(exp: dict) -> str:
    """Format work experience for the agent task."""
    return f"""
    Company: {exp['company']}
    Title: {exp['title']}
    Location: {exp['location']}
    Dates: {exp['dates']}
    Description: {exp.get('description', '')}
    """


def format_languages(languages: list) -> str:
    """Format languages for the agent task."""
    return "\n".join([
        f"- {lang['language']}: {lang['level']} (fluent: {lang.get('fluent', False)})"
        for lang in languages
    ])


def find_cv_path(job_folder: str) -> Path | None:
    """Find the CV PDF in the job folder."""
    jobs_dir = PROJECT_ROOT / "jobs"

    # Try exact match first
    folder_path = jobs_dir / job_folder
    if folder_path.exists():
        pdf_dir = folder_path / "PDF"
        for pdf in pdf_dir.glob("*Resume*.pdf"):
            return pdf

    # Try partial match (e.g., "Richemont" matches "Richemont - Finance...")
    for folder in jobs_dir.iterdir():
        if folder.is_dir() and job_folder.lower() in folder.name.lower():
            pdf_dir = folder / "PDF"
            if pdf_dir.exists():
                for pdf in pdf_dir.glob("*Resume*.pdf"):
                    return pdf

    return None


async def apply_to_job(job_url: str, job_folder: str = None, debug: bool = False):
    """
    Apply to a job using Browser Use agent.

    Args:
        job_url: URL of the job application page
        job_folder: Folder name in jobs/ containing CV (e.g., "Richemont" or full name)
        debug: If True, shows more verbose output
    """
    # Load all data
    profile = load_profile()
    work_exp = load_work_experiences()

    # Find CV path
    cv_path = None
    if job_folder:
        cv_path = find_cv_path(job_folder)
        if cv_path:
            print(f"CV found: {cv_path}")
        else:
            print(f"WARNING: CV not found for '{job_folder}'")

    # Sensitive data - LLM sees placeholders, real values injected at DOM level
    sensitive_data = get_sensitive_data(profile)

    # Format candidate info for the task
    personal = profile["personal"]
    address = profile["address"]
    education = profile["education"][0]  # Most recent
    languages = format_languages(profile["languages"])

    # Get current work experience (Auraia)
    current_job = work_exp["work_experiences"][0]
    current_job_formatted = format_work_experience(current_job)

    # LLM setup - Gemini 3 Flash
    llm = ChatGoogle(model='gemini-3-flash-preview')

    # Browser profile - persistent, separate from main Chrome
    browser_profile = BrowserProfile(
        headless=False,
        minimum_wait_page_load_time=0.8,
        wait_between_actions=0.5,  # More time for Workday forms
    )

    # Browser with persistent profile
    browser = Browser(
        browser_profile=browser_profile,
        user_data_dir=str(BROWSER_USE_PROFILE_DIR),
    )

    # Build the task prompt
    task = f"""
    Apply to the job at: {job_url}

    CANDIDATE INFORMATION:
    ----------------------
    Name: {personal['prefix']} {personal['given_name']} {personal['family_name']}
    Email: Use placeholder 'job_email'
    Phone: {personal['phone']}
    Nationality: {personal['nationality']}
    Date of Birth: {personal['date_of_birth']}

    Address:
    {address['street']}
    {address['postcode']} {address['city']}, {address['canton']}
    {address['country']}

    Education:
    {education['school']} - {education['degree']}
    {education['dates']} | GPA: {education['gpa']}

    Languages:
    {languages}

    Current Position:
    {current_job_formatted}

    CV FILE PATH:
    {str(cv_path) if cv_path else "NOT PROVIDED - skip CV upload"}

    INSTRUCTIONS:
    -------------
    1. If login is required, use 'job_email' and 'job_password' placeholders
    2. Fill all required fields with the information above
    3. For languages marked as fluent=True, check the "I am fluent" checkbox
    4. Upload CV using the EXACT path above (copy-paste it)
    5. STOP before clicking Submit - ask for confirmation
    6. Take a screenshot before final submission for review

    LOGIN HANDLING:
    - After entering credentials, press ENTER key instead of clicking Sign In button
    - If page doesn't transition after 1 attempt, try Enter key in password field
    - Don't click Sign In more than twice - use keyboard instead

    CHECKBOX HANDLING (Workday forms):
    - Workday checkboxes are tricky - clicking div elements does NOT work
    - SOLUTION: Click on the SPAN element inside or next to the checkbox
    - Look for span elements with the checkbox label text
    - Do NOT click on div elements for checkboxes - they won't toggle
    - After clicking the span, verify the checkbox is actually checked

    IMPORTANT:
    - Use EXACT company names and job titles from the data
    - For university searches, try "Université de Lausanne" if "HEC Lausanne" doesn't work
    - Check all checkboxes for required consents
    - Verify all fields before proceeding to next step
    """

    # Available files for upload
    available_files = [str(cv_path)] if cv_path else []

    agent = Agent(
        task=task,
        llm=llm,
        browser=browser,
        sensitive_data=sensitive_data,
        available_file_paths=available_files,  # Required for file uploads
        use_vision=True,  # Better for complex forms
        max_failures=3,
    )

    print("=" * 60)
    print("Browser Use - Job Application Agent")
    print("=" * 60)
    print(f"Target: {job_url}")
    print(f"Candidate: {personal['given_name']} {personal['family_name']}")
    print(f"Profile dir: {BROWSER_USE_PROFILE_DIR}")
    print("=" * 60)

    # Run the agent
    history = await agent.run(max_steps=25)

    print("\n" + "=" * 60)
    print("RESULT:")
    print("=" * 60)
    print(f"Completed in {len(history.history)} steps")
    if history.final_result():
        print(f"\n{history.final_result()}")


async def test_login_persistence():
    """
    Test that the browser profile persists logins.
    First run: Log into a job portal
    Second run: Should already be logged in
    """
    llm = ChatGoogle(model='gemini-3-flash-preview')

    browser_profile = BrowserProfile(
        headless=False,
        minimum_wait_page_load_time=0.5,
    )

    browser = Browser(
        browser_profile=browser_profile,
        user_data_dir=str(BROWSER_USE_PROFILE_DIR),
    )

    agent = Agent(
        task="Go to linkedin.com and check if I'm logged in. Report what you see.",
        llm=llm,
        browser=browser,
        use_vision=True,
    )

    print("Testing login persistence...")
    print(f"Profile dir: {BROWSER_USE_PROFILE_DIR}")

    history = await agent.run(max_steps=10)

    if history.final_result():
        print(f"\nResult: {history.final_result()}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            # Test login persistence
            asyncio.run(test_login_persistence())
        else:
            # Apply to job URL
            job_url = sys.argv[1]
            job_folder = sys.argv[2] if len(sys.argv) > 2 else None
            asyncio.run(apply_to_job(job_url, job_folder))
    else:
        print("Usage:")
        print("  py scripts/browser_use_apply.py <job_url> <job_folder>")
        print("  py scripts/browser_use_apply.py --test")
        print("")
        print("Examples:")
        print("  py scripts/browser_use_apply.py https://careers.richemont.com/... Richemont")
        print("  py scripts/browser_use_apply.py https://careers.cargill.com/... Cargill")
        print("  py scripts/browser_use_apply.py --test  # Test login persistence")
