"""
Form Filler - CLI entry point for ATS form filling.

Generates Playwright code for known ATS platforms.

Usage:
    python scripts/form_filler.py <platform> <section> --data '<json>'

Example:
    python scripts/form_filler.py workday my_information --data '{"prefix": "Mr.", "given_name": "Adrian"}'

Returns JSON with:
    - code: Playwright JS code to execute via browser_run_code
    - filled: list of fields that will be filled
    - notes: any platform-specific notes

Supported platforms:
    - workday: My Information, Work Experience, Education, Languages
    - oracle: (coming soon)
    - successfactors: (coming soon)

See scripts/ats/ for platform-specific implementations.
"""

import argparse
import json
import sys
from pathlib import Path

# Add parent directory to path for imports when run directly
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.ats import fill_section, PLATFORMS


def main():
    parser = argparse.ArgumentParser(
        description="Generate Playwright code for ATS forms",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Supported platforms: {', '.join(PLATFORMS.keys())}

Example:
    py scripts/form_filler.py workday my_information --data '{{"given_name": "Adrian"}}'
"""
    )
    parser.add_argument("platform", help="ATS platform (e.g., workday)")
    parser.add_argument("section", help="Form section (e.g., my_information)")
    parser.add_argument("--data", required=True, help="JSON data to fill")

    args = parser.parse_args()

    try:
        data = json.loads(args.data)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON: {e}"}))
        sys.exit(1)

    result = fill_section(args.platform, args.section, data)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
