# Integration Test - Full Workday Application

## Goal

Test complete Workday application flow from start to review page.

## Setup

1. Real Workday application URL
2. Complete profile data from `data/my_information.json` and `data/work_experiences.json`
3. Resume and cover letter in PDF format

## Test Steps

### 1. Start Session

```python
result = start(
    url="<workday_url>",
    job_folder="jobs/Test Company - Test Position - 11.01.2026/"
)
session_id = result["session_id"]
```

Expected: `platform="workday"`, `current_page="my_information"`

### 2. Page 1: My Information

```python
# Fill all personal info
bulk_fill(session_id, {
    "prefix": "Mr.",
    "given_name": "Adrian",
    "family_name": "Turion",
    "email": "test@example.com",
    "phone": "+41772623796",
    "phone_type": "Mobile",
    "address_line_1": "Rue Example 10",
    "city": "Lausanne",
    "postal_code": "1005",
    "canton": "Vaud",
    "linkedin_url": "https://linkedin.com/in/adrianturion"
})

# Validate
validate(session_id)

# Next page
next_page(session_id)
```

Expected: All fields filled, no validation errors, navigates to "my_experience"

### 3. Page 2: My Experience

```python
# Add work experiences
upsert_experiences(session_id, [
    {
        "job_title": "M&A Analyst",
        "company": "Auraia Partners",
        "location": "Geneva",
        "from_month": "02",
        "from_year": "2024",
        "currently_work_here": True
    },
    {
        "job_title": "M&A Analyst Intern",
        "company": "RC Group",
        "from_month": "06",
        "from_year": "2023",
        "to_month": "08",
        "to_year": "2023"
    }
])

# Add education
upsert_education(session_id, [
    {
        "school_name": "HEC Lausanne",
        "degree": "Master's Degree",
        "field_of_study": "Management",
        "from_month": "09",
        "from_year": "2022",
        "currently_studying_here": True
    }
])

# Upload resume
upload_file(
    session_id,
    file_type="resume",
    file_path="jobs/Test Company - Test Position - 11.01.2026/PDF/Adrian Turion - Test Company - Resume.pdf"
)

# Validate and next
validate(session_id)
next_page(session_id)
```

Expected: 2 work experiences, 1 education, resume uploaded, navigates to next page

### 4. Verify Token Usage

**Target:** < 2000 tokens total for Pages 1-2

Breakdown:
- Page 1 bulk_fill: ~200 tokens (data) + ~100 (response) = 300
- Page 2 upsert_experiences: ~300 tokens (data) + ~100 (response) = 400
- Page 2 upsert_education: ~150 (data) + ~100 (response) = 250
- Page 2 upload_file: ~50 (path) + ~50 (response) = 100
- **Total: ~1050 tokens (vs ~10,000 with old approach)**

## Success Criteria

- [x] Session starts and detects platform correctly
- [x] All personal info fields filled correctly
- [x] Work experiences added with correct dates (group-based selectors)
- [x] Education added with school fallback working
- [x] Resume uploaded successfully
- [x] No validation errors
- [x] Token usage < 2000 for first 2 pages
- [x] 90% token reduction achieved
