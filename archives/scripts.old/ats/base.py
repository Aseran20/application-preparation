"""
Base module with shared code for all ATS platforms.

Contains:
- Fuzzy matching patterns for dropdown options
- Label aliases for field name variations
- School fallback mappings
- Helper functions for code generation
"""

import json
import re

# =============================================================================
# FUZZY MATCHING PATTERNS
# =============================================================================
# Maps our intent to keywords that might appear in dropdown options
# Order matters - first match wins, so put most specific patterns first

FUZZY_PATTERNS = {
    # Language levels - different ATS instances use different scales
    "level_native": [
        r"4\s*[-–]\s*native",      # "4 - Native"
        r"native",                  # "Native", "Native or Bilingual"
        r"bilingual",               # "Bilingual"
        r"mother\s*tongue",         # "Mother tongue"
        r"c2",                      # "C2"
    ],
    "level_fluent": [
        r"3\s*[-–]\s*fluent",       # "3 - Fluent"
        r"full\s*professional",     # "Full Professional Proficiency"
        r"fluent",                  # "Fluent"
        r"c1",                      # "C1"
    ],
    "level_advanced": [
        r"2\s*[-–]\s*advanced",     # "2 - Advanced"
        r"professional\s*working",  # "Professional Working Proficiency"
        r"advanced",                # "Advanced"
        r"business",                # "Business proficient"
        r"b2",                      # "B2"
    ],
    "level_intermediate": [
        r"1\s*[-–]\s*intermediate", # "1 - Intermediate"
        r"limited\s*working",       # "Limited Working Proficiency"
        r"intermediate",            # "Intermediate"
        r"b1",                      # "B1"
    ],
    "level_basic": [
        r"0\s*[-–]",                # "0 - Basic"
        r"elementary",              # "Elementary"
        r"basic",                   # "Basic"
        r"beginner",                # "Beginner"
        r"a[12]",                   # "A1", "A2"
    ],

    # Degrees
    "degree_master": [
        r"master",                  # "Master Degree", "Master's Degree"
        r"msc",                     # "MSc"
        r"m\.?s\.?",                # "M.S.", "MS"
        r"mba",                     # "MBA"
        r"graduate",                # "Graduate Degree"
    ],
    "degree_bachelor": [
        r"bachelor",                # "Bachelor Degree", "Bachelor's Degree"
        r"bsc",                     # "BSc"
        r"b\.?s\.?",                # "B.S.", "BS"
        r"bba",                     # "BBA"
        r"undergraduate",           # "Undergraduate Degree"
    ],
    "degree_phd": [
        r"doctorate",               # "Doctorate Degree"
        r"ph\.?d",                  # "PhD", "Ph.D."
        r"doctoral",                # "Doctoral"
    ],

    # Prefixes/Titles
    "prefix_mr": [r"^mr\.?$", r"^m\.$", r"^monsieur$"],
    "prefix_mrs": [r"^mrs\.?$", r"^mme\.?$", r"^madame$"],
    "prefix_ms": [r"^ms\.?$", r"^mlle\.?$"],
    "prefix_dr": [r"^dr\.?$", r"^docteur$"],

    # Phone types
    "phone_mobile": [r"mobile", r"cell", r"portable"],
    "phone_home": [r"home", r"domicile", r"personal"],
    "phone_work": [r"work", r"office", r"business", r"professionnel"],

    # How did you hear
    "source_linkedin": [r"linkedin"],
    "source_website": [r"website", r"career\s*(page|site)", r"company\s*site"],
    "source_referral": [r"referral", r"employee", r"friend"],
    "source_jobboard": [r"job\s*board", r"indeed", r"glassdoor"],
}

# Maps user-friendly values to fuzzy pattern keys
VALUE_TO_FUZZY = {
    # Levels
    "Native": "level_native",
    "C2": "level_native",
    "Fluent": "level_fluent",
    "C1": "level_fluent",
    "Advanced": "level_advanced",
    "Business proficient": "level_advanced",
    "B2": "level_advanced",
    "B2-C1": "level_advanced",
    "Intermediate": "level_intermediate",
    "B1": "level_intermediate",
    "Basic": "level_basic",
    "A1": "level_basic",
    "A2": "level_basic",

    # Degrees
    "Master": "degree_master",
    "Master Degree": "degree_master",
    "Bachelor": "degree_bachelor",
    "Bachelor Degree": "degree_bachelor",
    "PhD": "degree_phd",
    "Doctorate": "degree_phd",

    # Prefixes
    "Mr.": "prefix_mr",
    "Mr": "prefix_mr",
    "Mrs.": "prefix_mrs",
    "Mrs": "prefix_mrs",
    "Ms.": "prefix_ms",
    "Ms": "prefix_ms",
    "Dr.": "prefix_dr",
    "Dr": "prefix_dr",

    # Phone types
    "Mobile": "phone_mobile",
    "Home": "phone_home",
    "Work": "phone_work",

    # Sources
    "LinkedIn": "source_linkedin",
    "Company Website": "source_website",
    "Referral": "source_referral",
    "Job Board": "source_jobboard",
}

# =============================================================================
# LABEL ALIASES
# =============================================================================
# Different ATS instances use different labels for the same fields

LABEL_ALIASES = {
    # My Information
    "given_name": ["Given Name(s)", "First Name", "Given Name"],
    "family_name": ["Family Name", "Last Name"],
    "address_line_1": ["Street and House Number", "Address Line 1"],
    "postal_code": ["Postcode", "Postal Code", "ZIP Code"],
    "city": ["City"],
    "email": ["Email", "Email Address"],
    "phone_number": ["Phone Number"],
    "canton": ["Canton", "State", "Province", "Region"],
    # Education
    "school": ["School or University", "School", "University", "Institution"],
    "degree": ["Degree", "Degree Level", "Education Level"],
    "field_of_study": ["Field of Study", "Major", "Specialization", "Program"],
}

# =============================================================================
# SCHOOL FALLBACKS
# =============================================================================
# When exact school isn't found, try alternatives

SCHOOL_FALLBACKS = {
    "Université de Lausanne": ["University of Lausanne", "UNIL"],
    "HEC Lausanne": ["Université de Lausanne", "University of Lausanne"],
    "HEC Lausanne (Faculty of Business and Economics of the University of Lausanne)": ["Université de Lausanne", "University of Lausanne"],
    "EPFL": ["École Polytechnique Fédérale de Lausanne", "Swiss Federal Institute"],
    "ETH Zurich": ["ETH Zürich", "Swiss Federal Institute of Technology"],
    "_default": "Other/School Not Listed",
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def escape_js(s: str) -> str:
    """Escape string for JavaScript."""
    return s.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n")


def escape_regex(s: str) -> str:
    """Escape string for use in JavaScript regex inside f-string."""
    return re.sub(r'([/.*+?^${}[\]()|\-])', r'\\\1', s)


def get_label_regex(field_key: str) -> str:
    """Get regex pattern matching all aliases for a field."""
    aliases = LABEL_ALIASES.get(field_key, [field_key])
    if len(aliases) == 1:
        return aliases[0]
    escaped = [a.replace("(", "\\(").replace(")", "\\)") for a in aliases]
    return f"({"|".join(escaped)})"


def get_fuzzy_patterns_js(fuzzy_key: str) -> str:
    """Get JS array of regex patterns for fuzzy matching."""
    if fuzzy_key not in FUZZY_PATTERNS:
        return "[]"
    patterns = FUZZY_PATTERNS[fuzzy_key]
    js_patterns = [f"/{p}/i" for p in patterns]
    return "[" + ", ".join(js_patterns) + "]"


# =============================================================================
# CODE GENERATORS
# =============================================================================

def generate_fuzzy_select_code(button_selector: str, value: str, group: str = None, field_name: str = "option") -> str:
    """Generate Playwright code that does fuzzy matching for dropdown options."""
    fuzzy_key = VALUE_TO_FUZZY.get(value)

    if fuzzy_key:
        patterns_js = get_fuzzy_patterns_js(fuzzy_key)

        if group:
            return f'''  // Fuzzy select {field_name}: looking for "{value}"
  await (async () => {{
    const patterns = {patterns_js};
    const btn = page.getByRole('group', {{ name: '{group}' }}).getByRole('button', {{ name: /{button_selector}/i }});
    await btn.click();
    await page.waitForTimeout(200);
    const options = await page.getByRole('option').all();
    for (const pattern of patterns) {{
      for (const opt of options) {{
        const text = await opt.textContent();
        if (pattern.test(text)) {{
          await opt.click();
          return;
        }}
      }}
    }}
    // Fallback: try exact match
    const fallback = page.getByRole('option', {{ name: '{escape_js(value)}' }});
    if (await fallback.count() > 0) await fallback.click();
    else throw new Error(`No option found for {field_name}="{value}"`);
  }})();'''
        else:
            return f'''  // Fuzzy select {field_name}: looking for "{value}"
  await (async () => {{
    const patterns = {patterns_js};
    const btn = page.getByRole('button', {{ name: /{button_selector}/i }});
    if (await btn.count() === 0) return; // Optional field not present
    await btn.click();
    await page.waitForTimeout(200);
    const options = await page.getByRole('option').all();
    for (const pattern of patterns) {{
      for (const opt of options) {{
        const text = await opt.textContent();
        if (pattern.test(text)) {{
          await opt.click();
          return;
        }}
      }}
    }}
    // Fallback: try exact match
    const fallback = page.getByRole('option', {{ name: '{escape_js(value)}' }});
    if (await fallback.count() > 0) await fallback.click();
    else throw new Error(`No option found for {field_name}="{value}"`);
  }})();'''
    else:
        # No fuzzy patterns - use simple exact match
        if group:
            return f'''  await page.getByRole('group', {{ name: '{group}' }}).getByRole('button', {{ name: /{button_selector}/i }}).click();
  await page.getByRole('option', {{ name: '{escape_js(value)}' }}).waitFor({{ state: 'visible' }});
  await page.getByRole('option', {{ name: '{escape_js(value)}' }}).click();'''
        else:
            return f'''  const btn_{field_name} = page.getByRole('button', {{ name: /{button_selector}/i }});
  if (await btn_{field_name}.count() > 0) {{
    await btn_{field_name}.click();
    await page.getByRole('option', {{ name: '{escape_js(value)}' }}).waitFor({{ state: 'visible' }});
    await page.getByRole('option', {{ name: '{escape_js(value)}' }}).click();
  }}'''


def generate_search_code(label: str, search_term: str, option_name: str, group: str = None, use_fallback: bool = True) -> str:
    """Generate Playwright code for search fields.

    Uses 'not checked' pattern to avoid matching already-selected pills.
    """
    if group:
        prefix = f"page.getByRole('group', {{ name: '{group}' }})"
    else:
        prefix = "page"

    label_regex = get_label_regex(label) if label in LABEL_ALIASES else label

    if not use_fallback:
        return f"""  await {prefix}.getByLabel(/{label_regex}/i).fill('{escape_js(search_term)}');
  await {prefix}.getByLabel(/{label_regex}/i).press('Enter');
  await page.waitForTimeout(800);
  await page.getByRole('option', {{ name: /{escape_js(option_name)}.*not checked/i }}).click();"""

    fallbacks = SCHOOL_FALLBACKS.get(option_name, [])
    default_fallback = SCHOOL_FALLBACKS.get("_default", "Other")

    return f"""  await (async () => {{
    const searchField = {prefix}.getByLabel(/{label_regex}/i);
    await searchField.fill('{escape_js(search_term)}');
    await searchField.press('Enter');
    await page.waitForTimeout(800);

    // Try primary option
    const primaryOption = page.getByRole('option', {{ name: /{escape_js(option_name)}.*not checked/i }});
    if (await primaryOption.count() > 0) {{
      await primaryOption.click();
      return;
    }}

    // Try fallback patterns: {fallbacks}
    const fallbackPatterns = {json.dumps([f"{fb}.*not checked" for fb in fallbacks])};
    for (const pattern of fallbackPatterns) {{
      const opt = page.getByRole('option', {{ name: new RegExp(pattern, 'i') }});
      if (await opt.count() > 0) {{
        await opt.click();
        return;
      }}
    }}

    // Ultimate fallback: "Other/School Not Listed"
    const otherOption = page.getByRole('option', {{ name: /{escape_regex(default_fallback)}.*not checked/i }});
    if (await otherOption.count() > 0) {{
      await otherOption.click();
      console.warn('School "{option_name}" not found, selected "{default_fallback}"');
      return;
    }}

    throw new Error('No school option found for "{option_name}"');
  }})();"""
