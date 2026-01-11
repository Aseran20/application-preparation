"""
Workday ATS Form Filling Module.

Contains Workday-specific patterns and code generators.
"""

import json

from .base import (
    escape_js,
    get_label_regex,
    generate_fuzzy_select_code,
    generate_search_code,
)

# =============================================================================
# WORKDAY-SPECIFIC PATTERNS
# =============================================================================

PATTERNS = {
    "my_information": {
        "fields": {
            "prefix": ("role", "button", "name=Prefix Select One", "select"),
            "given_name": ("label", "Given Name(s)", "fill"),
            "family_name": ("label", "Family Name", "fill"),
            "address_line_1": ("label", "Address Line 1", "fill"),
            "city": ("label", "City", "fill"),
            "postal_code": ("label", "Postcode", "fill"),
            "email": ("label", "Email", "fill"),
            "phone_type": ("role", "button", "name=Phone Device Type Select One", "select"),
            "phone_country": ("role", "button", "name=Phone Country Code", "select"),
            "phone_number": ("label", "Phone Number", "fill"),
            "how_did_you_hear": ("role", "button", "name=How Did You Hear About Us", "select"),
            "canton": ("role", "button", "name=Canton Select One", "select"),
        },
        "dropdowns": {
            "prefix": {"Mr.": "Mr", "Mrs.": "Mrs", "Ms.": "Ms", "Dr.": "Dr"},
            "phone_type": {"Mobile": "Mobile", "Home": "Home", "Work": "Work"},
            "phone_country": {
                "+41": "Switzerland (+41)",
                "+33": "France (+33)",
                "+1": "United States of America (+1)",
                "+49": "Germany (+49)",
                "+34": "Spain (+34)",
            },
            "canton": {"Geneva": "Geneva", "Zurich": "Zurich", "Vaud": "Vaud", "Bern": "Bern"},
            "how_did_you_hear": {
                "LinkedIn": "LinkedIn",
                "Company Website": "Company Website",
                "Job Board": "Job Board",
                "Referral": "Referral",
            },
        },
    },
    "work_experience": {
        "fields": {
            "job_title": ("label", "Job Title", "fill"),
            "company": ("label", "Company", "fill"),
            "location": ("label", "Location", "fill"),
            "role_description": ("label", "Role Description", "fill"),
            "currently_work_here": ("label", "I currently work here", "click"),
        },
        "date_fields": {
            "from_month": ("spinbutton", "Month", "fill"),
            "from_year": ("spinbutton", "Year", "fill"),
            "to_month": ("spinbutton", "Month", "fill"),
            "to_year": ("spinbutton", "Year", "fill"),
        },
    },
    "education": {
        "fields": {
            "school": ("label", "School or University", "search"),
            "degree": ("role", "button", "name=Degree", "select"),
        },
        "dropdowns": {
            "degree": {
                "Master": "Master Degree",
                "Bachelor": "Bachelor Degree",
                "PhD": "Doctorate Degree",
                "MBA": "Master of Business Administration (M.B.A.)",
            },
        },
    },
    "languages": {
        "fields": {
            "language": ("role", "button", "name=Language Select One", "select"),
            "overall": ("role", "button", "name=Overall Select One", "select"),
            "fluent": ("label", "I am fluent in this language.", "click"),
        },
        "dropdowns": {
            "overall": {
                "Native": "4 - Native",
                "C2": "4 - Native",
                "Fluent": "3 - Fluent",
                "C1": "3 - Fluent",
                "Advanced": "2 - Advanced",
                "Business proficient": "2 - Advanced",
                "B2": "2 - Advanced",
                "B2-C1": "2 - Advanced",
                "Intermediate": "1 - Intermediate",
                "B1": "1 - Intermediate",
            },
        },
    },
}


# =============================================================================
# AUTH GENERATORS
# =============================================================================

def generate_create_account(data: dict) -> dict:
    """Generate code for Workday account creation.

    data format:
    {
        "email": "user@example.com",
        "password": "SecurePass123!"
    }
    """
    email = data.get("email", "")
    password = data.get("password", "")

    if not email or not password:
        return {"code": "", "filled": [], "error": "email and password required"}

    code = f"""async (page) => {{
  // Fill account creation form
  await page.getByRole('textbox', {{ name: /Email Address/i }}).fill('{escape_js(email)}');
  await page.getByRole('textbox', {{ name: /^Password/i }}).first().fill('{escape_js(password)}');
  await page.getByRole('textbox', {{ name: /Verify.*Password/i }}).fill('{escape_js(password)}');

  // Accept terms
  const agreeCheckbox = page.getByRole('checkbox', {{ name: /I Agree/i }});
  if (await agreeCheckbox.count() > 0) {{
    await agreeCheckbox.click();
  }}

  // Click Create Account
  await page.getByRole('button', {{ name: /Create Account/i }}).first().click();

  return 'Account creation submitted';
}}"""

    return {
        "code": code,
        "filled": ["email", "password", "verify_password", "i_agree"],
        "notes": "After running, check for email verification requirement or proceed to next step."
    }


def generate_sign_in(data: dict) -> dict:
    """Generate code for Workday sign in.

    data format:
    {
        "email": "user@example.com",
        "password": "SecurePass123!"
    }
    """
    email = data.get("email", "")
    password = data.get("password", "")

    if not email or not password:
        return {"code": "", "filled": [], "error": "email and password required"}

    code = f"""async (page) => {{
  // Click Sign In button to show form (if needed)
  const signInBtn = page.getByRole('button', {{ name: /Sign In/i }});
  if (await signInBtn.count() > 0) {{
    await signInBtn.first().click();
    await page.waitForTimeout(500);
  }}

  // Fill sign in form
  await page.getByRole('textbox', {{ name: /Email/i }}).fill('{escape_js(email)}');
  await page.getByRole('textbox', {{ name: /Password/i }}).fill('{escape_js(password)}');

  // Submit
  const submitBtn = page.getByRole('button', {{ name: /Sign In/i }});
  await submitBtn.click();

  return 'Sign in submitted';
}}"""

    return {
        "code": code,
        "filled": ["email", "password"],
        "notes": "After running, wait for page to load and check if signed in successfully."
    }


# =============================================================================
# SECTION GENERATORS
# =============================================================================

def generate_my_information(data: dict) -> dict:
    """Generate code for Workday My Information section."""
    lines = []
    filled = []

    # Text fields - use regex for aliases
    # Email may be read-only when signed in, so check if editable
    text_fields = [
        ("given_name", get_label_regex("given_name")),
        ("family_name", get_label_regex("family_name")),
        ("address_line_1", get_label_regex("address_line_1")),
        ("city", get_label_regex("city")),
        ("postal_code", get_label_regex("postal_code")),
        ("phone_number", get_label_regex("phone_number")),
    ]

    for field_key, label_pattern in text_fields:
        if field_key in data and data[field_key]:
            lines.append(f"  await page.getByRole('textbox', {{ name: /{label_pattern}/i }}).first().fill('{escape_js(data[field_key])}');")
            filled.append(field_key)

    # Email - optional (read-only if signed in)
    if "email" in data and data["email"]:
        email_pattern = get_label_regex("email")
        lines.append(f"  // Email (optional if already set)")
        lines.append(f"  const emailField = page.getByRole('textbox', {{ name: /{email_pattern}/i }});")
        lines.append(f"  if (await emailField.count() > 0) {{")
        lines.append(f"    await emailField.first().fill('{escape_js(data['email'])}');")
        lines.append(f"  }}")
        filled.append("email")

    # Radio button: "Have you worked at [Company] before?" -> No
    if data.get("worked_at_company") is False:
        lines.append("  // Select 'No' for previous employment question if present")
        lines.append("  const noRadio = page.getByRole('radio', { name: 'No' });")
        lines.append("  if (await noRadio.count() > 0) await noRadio.click();")
        filled.append("worked_at_company")

    # Dropdowns with fuzzy matching
    if "prefix" in data and data["prefix"]:
        lines.append(generate_fuzzy_select_code(
            button_selector="Prefix.*Select One",
            value=data["prefix"],
            field_name="prefix"
        ))
        filled.append("prefix")

    if "canton" in data and data["canton"]:
        lines.append("  // Canton dropdown (if present)")
        lines.append("  const cantonBtn = page.getByRole('button', { name: /Canton.*Select One/i });")
        lines.append("  if (await cantonBtn.count() > 0) {")
        lines.append("    await cantonBtn.click();")
        lines.append(f"    await page.getByRole('option', {{ name: '{data['canton']}' }}).waitFor({{ state: 'visible' }});")
        lines.append(f"    await page.getByRole('option', {{ name: '{data['canton']}' }}).click();")
        lines.append("  }")
        filled.append("canton")

    if "how_did_you_hear" in data and data["how_did_you_hear"]:
        # How Did You Hear uses search field - auto-selects on Enter
        search_term = data["how_did_you_hear"].split()[0]
        lines.append("  // How Did You Hear - search field (auto-selects on Enter)")
        lines.append(f"  await page.getByRole('textbox', {{ name: /How Did You Hear/i }}).fill('{escape_js(search_term)}');")
        lines.append(f"  await page.getByRole('textbox', {{ name: /How Did You Hear/i }}).press('Enter');")
        lines.append(f"  await page.waitForTimeout(500);")
        filled.append("how_did_you_hear")

    if "phone_type" in data and data["phone_type"]:
        lines.append(generate_fuzzy_select_code(
            button_selector="Phone Device Type.*Select One|Phone.*Type",
            value=data["phone_type"],
            field_name="phone_type"
        ))
        filled.append("phone_type")

    code = "async (page) => {\n" + "\n".join(lines) + "\n  return 'Filled: " + ", ".join(filled) + "';\n}"

    return {
        "code": code,
        "filled": filled,
        "notes": "Execute via browser_run_code. Uses regex for label flexibility. Optional fields checked with count()."
    }


def generate_work_experience(data: dict) -> dict:
    """Generate code for Workday Work Experience section.

    data format:
    {
        "experiences": [
            {
                "job_title": "...",
                "company": "...",
                "location": "...",
                "role_description": "...",
                "currently_work_here": true/false,
                "from_month": "08",
                "from_year": "2024",
                "to_month": "12",  # optional if currently_work_here
                "to_year": "2024"
            },
            ...
        ]
    }
    """
    experiences = data.get("experiences", [])
    if not experiences:
        return {"code": "", "filled": [], "notes": "No experiences provided"}

    lines = []
    filled = []

    # Step 1: Add entries - "Add" creates first, "Add Another" for rest
    lines.append("  // Step 1: Create all entries")
    lines.append("  await page.getByLabel('Work Experience').getByRole('button', { name: 'Add' }).click();")
    for i in range(len(experiences) - 1):
        lines.append("  await page.getByLabel('Work Experience').getByRole('button', { name: 'Add Another' }).click();")

    # Step 2: Fill text fields
    lines.append("\n  // Step 2: Fill all text fields")
    for i, exp in enumerate(experiences):
        if "job_title" in exp:
            lines.append(f"  await page.getByLabel('Job Title').nth({i}).fill('{escape_js(exp['job_title'])}');")
            filled.append(f"job_title_{i}")
        if "company" in exp:
            lines.append(f"  await page.getByLabel('Company').nth({i}).fill('{escape_js(exp['company'])}');")
            filled.append(f"company_{i}")
        if "location" in exp:
            # Location is optional - not all Workday instances have this field
            lines.append(f"  // Location (optional - not all Workday instances have this)")
            lines.append(f"  const locationField_{i} = page.getByLabel('Location').nth({i});")
            lines.append(f"  if (await locationField_{i}.count() > 0) {{")
            lines.append(f"    await locationField_{i}.fill('{escape_js(exp['location'])}');")
            lines.append(f"  }}")
            filled.append(f"location_{i}")
        if "role_description" in exp:
            lines.append(f"  await page.getByLabel('Role Description').nth({i}).fill('{escape_js(exp['role_description'])}');")
            filled.append(f"role_description_{i}")

    # Step 3: Checkboxes for "currently work here"
    lines.append("\n  // Step 3: Currently work here checkboxes")
    for i, exp in enumerate(experiences):
        if exp.get("currently_work_here"):
            lines.append(f"  await page.getByRole('group', {{ name: 'Work Experience {i+1}' }}).getByLabel('I currently work here').click();")
            filled.append(f"currently_work_here_{i}")

    # Step 4: Dates - use group-based selectors (not nth()) because hidden To fields stay in DOM
    lines.append("\n  // Step 4: Date spinbuttons (using group selectors for reliability)")
    for i, exp in enumerate(experiences):
        currently = exp.get("currently_work_here", False)
        we_group = f"page.getByRole('group', {{ name: 'Work Experience {i+1}' }})"

        # From date - always present
        if "from_month" in exp:
            lines.append(f"  await {we_group}.getByRole('group', {{ name: 'From' }}).getByRole('spinbutton', {{ name: 'Month' }}).fill('{exp['from_month']}');")
            filled.append(f"from_month_{i}")
        if "from_year" in exp:
            lines.append(f"  await {we_group}.getByRole('group', {{ name: 'From' }}).getByRole('spinbutton', {{ name: 'Year' }}).fill('{exp['from_year']}');")
            filled.append(f"from_year_{i}")

        # To date (only if not currently working here)
        if not currently:
            if "to_month" in exp:
                lines.append(f"  await {we_group}.getByRole('group', {{ name: 'To' }}).getByRole('spinbutton', {{ name: 'Month' }}).fill('{exp['to_month']}');")
                filled.append(f"to_month_{i}")
            if "to_year" in exp:
                lines.append(f"  await {we_group}.getByRole('group', {{ name: 'To' }}).getByRole('spinbutton', {{ name: 'Year' }}).fill('{exp['to_year']}');")
                filled.append(f"to_year_{i}")

    code = "async (page) => {\n" + "\n".join(lines) + "\n  return 'Work Experience filled';\n}"

    return {
        "code": code,
        "filled": filled,
        "notes": "Creates entries first, then fills all in batch. Uses group-based selectors for dates (not nth()) because hidden To fields stay in DOM when 'currently work here' is checked."
    }


def generate_education(data: dict) -> dict:
    """Generate code for Workday Education section.

    data format:
    {
        "education": [
            {"school_search": "Lausanne", "school_name": "Université de Lausanne", "degree": "Master"},
            {"school_search": "Lausanne", "school_name": "Université de Lausanne", "degree": "Bachelor"}
        ]
    }
    """
    education = data.get("education", [])
    if not education:
        return {"code": "", "filled": [], "notes": "No education provided"}

    lines = []
    filled = []

    # Add entries (Education 1 exists by default)
    if len(education) > 1:
        lines.append("  // Create additional education entries")
        for i in range(len(education) - 1):
            lines.append("  await page.getByLabel('Education').getByRole('button', { name: 'Add Another' }).click();")

    # Fill each education
    for i, edu in enumerate(education):
        lines.append(f"\n  // Education {i+1}")

        # School search - support both formats
        school_search = edu.get("school_search")
        school_name = edu.get("school_name")

        # Fallback: derive from "school" field if school_search/school_name not provided
        if not school_search and not school_name and "school" in edu:
            school = edu["school"]
            school_search = school.split()[-1] if school else None
            school_name = school

        if school_search and school_name:
            group = f"Education {i+1}"
            lines.append(generate_search_code("school", school_search, school_name, group, use_fallback=True))
            filled.append(f"school_{i}")

        # Degree dropdown - FUZZY matching
        if "degree" in edu:
            group = f"Education {i+1}"
            lines.append(generate_fuzzy_select_code(
                button_selector="Degree.*Select One|Degree.*Required|Degree",
                value=edu["degree"],
                group=group,
                field_name=f"degree_{i}"
            ))
            filled.append(f"degree_{i}")

        # Optional dates
        if "from_year" in edu or "to_year" in edu or "dates" in edu:
            group = f"Education {i+1}"
            from_year = edu.get("from_year")
            to_year = edu.get("to_year")
            if not from_year and "dates" in edu:
                parts = edu["dates"].split(" - ")
                if len(parts) >= 1:
                    from_year = parts[0].strip()
                if len(parts) >= 2:
                    to_year = parts[1].strip()

            lines.append(f"""
  // Optional dates for Education {i+1} (only if spinbuttons exist)
  await (async () => {{
    const group = page.getByRole('group', {{ name: '{group}' }});
    const fromYear = group.getByRole('group', {{ name: 'From' }}).getByRole('spinbutton', {{ name: 'Year' }});
    const toYear = group.getByRole('group', {{ name: 'To' }}).getByRole('spinbutton', {{ name: 'Year' }});

    // Only fill if spinbuttons exist on this Workday instance
    if ({f"'{from_year}'" if from_year else "null"} && await fromYear.count() > 0) {{
      await fromYear.fill('{from_year or ""}');
    }}
    if ({f"'{to_year}'" if to_year else "null"} && await toYear.count() > 0) {{
      await toYear.fill('{to_year or ""}');
    }}
  }})();""")
            if from_year:
                filled.append(f"from_year_{i}")
            if to_year:
                filled.append(f"to_year_{i}")

    code = "async (page) => {\n" + "\n".join(lines) + "\n  return 'Education filled';\n}"

    return {
        "code": code,
        "filled": filled,
        "notes": "Uses label aliases for school field, fallback to 'Other/School Not Listed' if school not found, optional dates only filled if spinbuttons exist."
    }


def generate_languages(data: dict) -> dict:
    """Generate code for Workday Languages section.

    data format:
    {
        "languages": [
            {"language": "French", "level": "Native", "fluent": true},
            {"language": "Spanish", "level": "Native", "fluent": true},
            {"language": "English", "level": "Fluent", "fluent": true},
            {"language": "German", "level": "Advanced", "fluent": false}
        ]
    }
    """
    languages = data.get("languages", [])
    if not languages:
        return {"code": "", "filled": [], "notes": "No languages provided"}

    lines = []
    filled = []

    # Add entries (Language 1 exists by default)
    if len(languages) > 1:
        lines.append("  // Create additional language entries")
        for i in range(len(languages) - 1):
            lines.append("  await page.getByLabel('Languages').getByRole('button', { name: 'Add Another' }).click();")

    # First batch: all fluent checkboxes
    lines.append("\n  // Batch 1: Fluent checkboxes")
    for i, lang in enumerate(languages):
        if lang.get("fluent"):
            group = f"Languages {i+1}"
            lines.append(f"  await page.getByRole('group', {{ name: '{group}' }}).getByLabel('I am fluent in this language.').click();")
            filled.append(f"fluent_{i}")

    # Second batch: all dropdowns with fuzzy matching
    lines.append("\n  // Batch 2: Language and level dropdowns (with fuzzy matching)")
    for i, lang in enumerate(languages):
        group = f"Languages {i+1}"

        # Language dropdown - exact match
        if "language" in lang:
            lines.append(f"  await page.getByRole('group', {{ name: '{group}' }}).getByRole('button', {{ name: /Language.*Select One|Language.*Required/ }}).click();")
            lines.append(f"  await page.getByRole('option', {{ name: '{lang['language']}' }}).waitFor({{ state: 'visible' }});")
            lines.append(f"  await page.getByRole('option', {{ name: '{lang['language']}' }}).click();")
            filled.append(f"language_{i}")

        # Level dropdown - FUZZY matching
        if "level" in lang:
            lines.append(generate_fuzzy_select_code(
                button_selector="Overall.*Select One|Overall.*Required",
                value=lang["level"],
                group=group,
                field_name=f"level_{i}"
            ))
            filled.append(f"level_{i}")

    code = "async (page) => {\n" + "\n".join(lines) + "\n  return 'Languages filled';\n}"

    return {
        "code": code,
        "filled": filled,
        "notes": "Checkboxes batched first, then all dropdowns in sequence."
    }


# =============================================================================
# SECTION REGISTRY
# =============================================================================

SECTIONS = {
    # Auth
    "create_account": generate_create_account,
    "sign_in": generate_sign_in,
    # Form sections
    "my_information": generate_my_information,
    "work_experience": generate_work_experience,
    "education": generate_education,
    "languages": generate_languages,
}
