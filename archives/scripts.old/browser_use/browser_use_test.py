"""
Browser Use Test with Gemini 3 Flash
Simple test to verify browser automation works.
"""

import asyncio
from dotenv import load_dotenv

load_dotenv()

from browser_use import Agent, Browser, BrowserProfile
from browser_use import ChatGoogle


async def test_simple_search():
    """Test basic browser navigation and search."""

    # Gemini 3 Flash - fast and cheap
    llm = ChatGoogle(model='gemini-3-flash-preview')

    # Browser config - visible window
    browser_profile = BrowserProfile(
        headless=False,
        minimum_wait_page_load_time=0.5,
        wait_between_actions=0.3,
    )

    browser = Browser(browser_profile=browser_profile)

    agent = Agent(
        task="Go to google.com and search for 'Richemont careers graduate program'. Tell me what you find.",
        llm=llm,
        browser=browser,
        use_vision=True,
    )

    history = await agent.run(max_steps=15)
    print("\n" + "="*50)
    print("RESULT:")
    print("="*50)
    print(f"Completed in {len(history.history)} steps")
    if history.final_result():
        print(f"Final result: {history.final_result()}")


async def test_job_application_navigation():
    """Test navigating to a job application page."""

    llm = ChatGoogle(model='gemini-3-flash-preview')

    browser_profile = BrowserProfile(
        headless=False,
        minimum_wait_page_load_time=0.5,
    )

    browser = Browser(browser_profile=browser_profile)

    # Read profile data
    import json
    from pathlib import Path

    profile_path = Path(__file__).parent.parent / "profile.json"
    with open(profile_path, "r", encoding="utf-8") as f:
        profile = json.load(f)

    task = f"""
    Go to https://www.richemont.com/careers/ and:
    1. Find the 'Graduate Programs' or 'Early Careers' section
    2. Look for finance-related positions in Switzerland
    3. Report what positions are available

    Candidate info (for context):
    - Name: {profile['personal']['given_name']} {profile['personal']['family_name']}
    - Education: {profile['education'][0]['school']} - {profile['education'][0]['degree']}
    """

    agent = Agent(
        task=task,
        llm=llm,
        browser=browser,
        use_vision=True,
    )

    history = await agent.run(max_steps=20)
    print("\n" + "="*50)
    print("RESULT:")
    print("="*50)
    if history.final_result():
        print(history.final_result())


if __name__ == "__main__":
    print("="*50)
    print("Browser Use Test - Gemini 3 Flash")
    print("="*50)

    # Run simple test first
    asyncio.run(test_simple_search())
