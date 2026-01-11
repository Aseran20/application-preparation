"""
Browser Use - Profile Initialization Script
Opens the Browser Use profile and lets you log into Gmail and LinkedIn manually.
After login, cookies are saved for future sessions.
"""

import asyncio
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from browser_use import Agent, Browser, BrowserProfile
from browser_use import ChatGoogle


# Browser Use profile directory
BROWSER_USE_PROFILE_DIR = Path.home() / ".browseruse" / "profiles" / "job-apply"


async def init_gmail():
    """Open Gmail for manual login."""
    print("=" * 60)
    print("STEP 1: Gmail Login")
    print("=" * 60)
    print("Opening Gmail... Please log in manually.")
    print("Once logged in, the agent will confirm and move on.")
    print("=" * 60)

    llm = ChatGoogle(model='gemini-3-flash-preview')

    browser_profile = BrowserProfile(
        headless=False,
        minimum_wait_page_load_time=1,
        wait_between_actions=0.5,
    )

    browser = Browser(
        browser_profile=browser_profile,
        user_data_dir=str(BROWSER_USE_PROFILE_DIR),
    )

    agent = Agent(
        task="""
        Go to https://mail.google.com

        Check if the user is logged in:
        - If you see an inbox with emails, report "Gmail: Already logged in"
        - If you see a login page, wait for the user to log in manually (they will do it themselves)
        - Once the inbox is visible, report "Gmail: Login successful"

        IMPORTANT: Do NOT try to fill in any login credentials. Just navigate and observe.
        Wait up to 2 minutes for the user to complete manual login.
        """,
        llm=llm,
        browser=browser,
        use_vision=True,
    )

    history = await agent.run(max_steps=30)

    if history.final_result():
        print(f"\nResult: {history.final_result()}")

    return browser


async def init_linkedin(browser=None):
    """Open LinkedIn for manual login."""
    print("\n" + "=" * 60)
    print("STEP 2: LinkedIn Login")
    print("=" * 60)
    print("Opening LinkedIn... Please log in manually if needed.")
    print("=" * 60)

    llm = ChatGoogle(model='gemini-3-flash-preview')

    if browser is None:
        browser_profile = BrowserProfile(
            headless=False,
            minimum_wait_page_load_time=1,
            wait_between_actions=0.5,
        )

        browser = Browser(
            browser_profile=browser_profile,
            user_data_dir=str(BROWSER_USE_PROFILE_DIR),
        )

    agent = Agent(
        task="""
        Go to https://www.linkedin.com

        Check if the user is logged in:
        - If you see a feed or profile page, report "LinkedIn: Already logged in"
        - If you see a login page, wait for the user to log in manually
        - Once logged in, report "LinkedIn: Login successful"

        IMPORTANT: Do NOT try to fill in any login credentials. Just navigate and observe.
        Wait up to 2 minutes for the user to complete manual login.
        """,
        llm=llm,
        browser=browser,
        use_vision=True,
    )

    history = await agent.run(max_steps=30)

    if history.final_result():
        print(f"\nResult: {history.final_result()}")


async def verify_logins():
    """Verify that both Gmail and LinkedIn are accessible."""
    print("\n" + "=" * 60)
    print("VERIFICATION: Checking saved logins")
    print("=" * 60)

    llm = ChatGoogle(model='gemini-3-flash-preview')

    browser_profile = BrowserProfile(
        headless=False,
        minimum_wait_page_load_time=1,
    )

    browser = Browser(
        browser_profile=browser_profile,
        user_data_dir=str(BROWSER_USE_PROFILE_DIR),
    )

    agent = Agent(
        task="""
        Verify login status for both Gmail and LinkedIn:

        1. Go to https://mail.google.com - check if logged in (should see inbox)
        2. Go to https://www.linkedin.com - check if logged in (should see feed)

        Report the status of each:
        - Gmail: [Logged in / Not logged in]
        - LinkedIn: [Logged in / Not logged in]
        """,
        llm=llm,
        browser=browser,
        use_vision=True,
    )

    history = await agent.run(max_steps=20)

    if history.final_result():
        print(f"\nVerification Result:\n{history.final_result()}")


async def main():
    """Run the full initialization process."""
    print("=" * 60)
    print("Browser Use - Profile Initialization")
    print("=" * 60)
    print(f"Profile directory: {BROWSER_USE_PROFILE_DIR}")
    print()
    print("This script will help you set up your Browser Use profile")
    print("with Gmail and LinkedIn access for job applications.")
    print()
    print("You will need to log in manually to each service.")
    print("After that, cookies will be saved for future sessions.")
    print("=" * 60)

    # Ensure profile directory exists
    BROWSER_USE_PROFILE_DIR.mkdir(parents=True, exist_ok=True)

    # Step 1: Gmail
    await init_gmail()

    print("\nContinuing to LinkedIn login...")

    # Step 2: LinkedIn
    await init_linkedin()

    print("\nVerifying logins...")

    # Verify
    await verify_logins()

    print("\n" + "=" * 60)
    print("DONE!")
    print("=" * 60)
    print("Your Browser Use profile is now set up with:")
    print("- Gmail access (for OTP verification)")
    print("- LinkedIn access (for job applications)")
    print()
    print("You can now use: py scripts/browser_use_apply.py <job_url>")
    print("=" * 60)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "--gmail":
            asyncio.run(init_gmail())
        elif sys.argv[1] == "--linkedin":
            asyncio.run(init_linkedin())
        elif sys.argv[1] == "--verify":
            asyncio.run(verify_logins())
        else:
            print("Usage:")
            print("  py scripts/browser_use_init_profile.py          # Full setup")
            print("  py scripts/browser_use_init_profile.py --gmail   # Gmail only")
            print("  py scripts/browser_use_init_profile.py --linkedin # LinkedIn only")
            print("  py scripts/browser_use_init_profile.py --verify  # Verify logins")
    else:
        asyncio.run(main())
