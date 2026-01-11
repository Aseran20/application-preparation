# Manual Test Procedure

## Prerequisites

1. Have a real Workday application URL ready
2. Have profile data prepared (name, email, phone, etc.)
3. MCP Inspector installed: `npm install -g @modelcontextprotocol/inspector`

## Test 1: Start Session and Snapshot

```bash
# Start MCP inspector
mcp-inspector python -m ats_filler.server

# In inspector UI:
# 1. Call start()
#    - url: <your Workday URL>
#    - job_folder: "jobs/Test Company - Test Position - 11.01.2026"
#
# Expected result:
# {
#   "session_id": "session_1",
#   "platform": "workday",
#   "current_page": "my_information",
#   "message": "Session started. Platform detected: workday"
# }

# 2. Call snapshot()
#    - session_id: "session_1"
#
# Expected result:
# {
#   "step": "my_information",
#   "fields": [
#     {"field_id": "given_name", "label": "Given Name(s)", "field_type": "text", "required": true},
#     {"field_id": "family_name", "label": "Family Name(s)", "field_type": "text", "required": true},
#     ...
#   ],
#   "buttons": ["Save and Continue", "Cancel"],
#   "validation_errors": []
# }
```

## Test 2: Bulk Fill Personal Info

```bash
# Call bulk_fill()
#    - session_id: "session_1"
#    - data: {
#        "given_name": "Adrian",
#        "family_name": "Turion",
#        "email": "test@example.com",
#        "phone": "+41772623796",
#        "city": "Lausanne"
#      }
#
# Expected result:
# {
#   "applied": [
#     {"field_id": "given_name", "status": "applied", "message": "Filled: Given Name(s)"},
#     {"field_id": "family_name", "status": "applied", "message": "Filled: Family Name(s)"},
#     ...
#   ],
#   "skipped": [],
#   "failed": []
# }

# Verify in browser: All fields should be filled correctly
```

## Test 3: Add Work Experience

```bash
# Call upsert_experiences()
#    - session_id: "session_1"
#    - experiences: [
#        {
#          "job_title": "M&A Analyst",
#          "company": "Auraia Partners",
#          "location": "Geneva",
#          "from_month": "02",
#          "from_year": "2024",
#          "currently_work_here": true
#        }
#      ]
#
# Expected result:
# {
#   "added": 1,
#   "updated": 0,
#   "skipped": 0
# }

# Verify in browser: Work experience entry should be filled with all dates
```

## Success Criteria

- [x] Session starts and detects Workday platform
- [x] Snapshot returns all expected fields
- [x] Bulk fill successfully fills all personal info fields
- [x] Work experience macro adds entry with group-based date selectors
- [x] Browser shows filled data correctly
- [x] No token consumption issues (stay under 500 tokens/operation)
