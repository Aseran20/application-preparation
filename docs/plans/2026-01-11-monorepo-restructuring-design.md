# Monorepo Restructuring Design

**Date:** 2026-01-11
**Status:** Approved

## Problem Statement

The current codebase mixes two distinct projects:
1. **Document Generation:** CV and cover letter generation from job descriptions
2. **ATS Automation:** Workday form filling with Playwright

This creates confusion and makes the codebase harder to maintain and understand.

## Goals

1. **Separate concerns** - Clear separation between document generation and ATS automation
2. **Maintain data sharing** - Both projects use the same personal data (work_experiences.json, my_information.json, etc.)
3. **Keep it simple** - No over-engineering, no complex build systems, just clean Python structure
4. **Zero downtime** - Existing functionality continues to work during migration

## Solution: Clean Monorepo Structure

### Target Structure

```
resume.ai/
├── generator/
│   ├── scripts/
│   │   ├── generate.py
│   │   ├── resume.py
│   │   ├── cover_letter.py
│   │   ├── validate_resume.py
│   │   └── validate_cover_letter.py
│   ├── utils/
│   │   ├── config.py
│   │   ├── docx.py
│   │   └── pdf.py
│   └── templates/
│       ├── Resume - Adrian Turion.docx
│       └── Cover Letter - Adrian Turion v2.docx
├── ats/
│   ├── scripts/
│   │   ├── base.py
│   │   ├── workday.py
│   │   ├── form_filler.py
│   │   └── detector.py
│   └── browser_use/
├── data/              # SHARED
│   ├── work_experiences.json
│   ├── leadership.json
│   ├── courses_and_other.json
│   └── my_information.json
├── jobs/              # SHARED (output)
├── .claude/
│   └── commands/
│       ├── generate.md
│       └── apply.md
├── config.local.json
├── requirements.txt
└── CLAUDE.md
```

### Key Principles

1. **Independence:** `generator/` and `ats/` are completely independent (no cross-imports)
2. **Shared Resources:** Both use `data/` for input and `jobs/` for output
3. **Simple Imports:** Use sys.path manipulation instead of setuptools/pip install -e
4. **Backwards Compatible:** Existing `/generate` and `/apply` commands continue to work

## Technical Changes

### Path Resolution

**generator/utils/config.py:**
```python
PROJECT_ROOT = Path(__file__).parent.parent.parent  # generator/utils/ -> generator/ -> resume.ai/
TEMPLATES_DIR = PROJECT_ROOT / "generator" / "templates"
DATA_DIR = PROJECT_ROOT / "data"
JOBS_DIR = PROJECT_ROOT / "jobs"
```

### Import Pattern

All scripts use this pattern at the top:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Then normal imports work:
from generator.utils.config import ...
from ats.scripts.base import ...
```

### Command Updates

**.claude/commands/generate.md:**
```python
from pathlib import Path
import sys
sys.path.insert(0, str(Path.cwd()))

from generator.scripts.generate import create_project_folder, save_content, generate_all
```

**.claude/commands/apply.md:**
- Update paths to `py ats/scripts/form_filler.py`

## Migration Plan

### Phase 1: Create New Structure (No Breaking Changes)
1. Create `generator/` and `ats/` directories
2. **Copy** (not move) files to new locations
3. Adjust imports and paths in copied files
4. Update `.claude/commands/` to use new paths

### Phase 2: Validation
1. Test `/generate` with new structure
2. Test ATS form_filler.py with new structure
3. Generate a test CV/cover letter to confirm everything works

### Phase 3: Cleanup
1. Rename `scripts/` to `scripts.old/` (backup)
2. Update CLAUDE.md with new structure
3. Commit: "refactor: separate generator and ats into clean monorepo structure"

### Phase 4: Final Cleanup
1. Delete `scripts.old/` after confirming everything works
2. Archive or delete any unused files

## Success Criteria

- [ ] `/generate` command works with new structure
- [ ] `/apply` command works with new structure
- [ ] All validation scripts work
- [ ] No broken imports
- [ ] CLAUDE.md reflects new structure
- [ ] Can delete old `scripts/` directory without breaking anything

## Future Improvements (Out of Scope)

- Custom MCP server for ATS automation (reduces token usage)
- Package-based imports if project grows significantly
- Separate repos if projects diverge in purpose

## Trade-offs

**Chosen Approach (Monorepo):**
- ✅ Shared data between projects
- ✅ Single repo to maintain
- ✅ Natural workflow: generate → apply
- ❌ Slightly more complex than single project

**Rejected: Separate Repos**
- ❌ Data duplication or symlinks
- ❌ Two repos to maintain
- ✅ Complete independence

**Rejected: Single Package with setup.py**
- ❌ Over-engineering for personal tool
- ❌ Adds complexity without benefit
- ✅ "Proper" Python package structure
