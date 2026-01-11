# Plan: Architecture Modulaire ATS

## Objectif

Refactorer `form_filler.py` monolithique en architecture modulaire + séparer `/apply` (production) de `/improve` (développement).

---

## 1. Structure des fichiers

```
scripts/ats/
├── __init__.py
├── base.py              # Code partagé (fuzzy matching, helpers)
├── workday.py           # Générateurs Workday
├── oracle.py            # (futur) Générateurs Oracle
├── successfactors.py    # (futur) Générateurs SuccessFactors
└── detector.py          # Détection plateforme par URL

scripts/form_filler.py   # Entry point CLI (garde le même usage)

.claude/commands/
├── apply.md             # Production: exécute scripts, MCP fix si erreur
└── improve.md           # Dev: teste + améliore scripts
```

---

## 2. Contenu de chaque fichier

### `base.py` - Code partagé (~200 lignes)
```python
# Constantes
LABEL_ALIASES = {...}
SCHOOL_FALLBACKS = {...}
FUZZY_PATTERNS = {...}

# Helpers
def escape_js(s: str) -> str
def escape_regex(s: str) -> str
def get_label_regex(field_key: str) -> str

# Générateurs génériques
def generate_fuzzy_select_code(button_selector, value, group, field_name) -> str
def generate_search_code(label, search_term, option_name, group, use_fallback) -> str
```

### `workday.py` - Spécifique Workday (~400 lignes)
```python
from .base import *

# Patterns Workday
WORKDAY_PATTERNS = {...}

# Générateurs par section
def generate_my_information(data: dict) -> dict
def generate_work_experience(data: dict) -> dict
def generate_education(data: dict) -> dict
def generate_languages(data: dict) -> dict

# Registry
SECTIONS = {
    "my_information": generate_my_information,
    "work_experience": generate_work_experience,
    "education": generate_education,
    "languages": generate_languages,
}
```

### `detector.py` - Détection plateforme (~30 lignes)
```python
PLATFORM_PATTERNS = {
    "workday": ["workday.com", "myworkdayjobs.com"],
    "oracle": ["oracle.com", "taleo.net"],
    "successfactors": ["successfactors.com", "jobs.sap.com"],
}

def detect_platform(url: str) -> str | None
```

### `form_filler.py` - Entry point (simplifié)
```python
from scripts.ats import workday, oracle, detector

def fill_section(platform: str, section: str, data: dict) -> dict:
    if platform == "workday":
        return workday.SECTIONS[section](data)
    elif platform == "oracle":
        return oracle.SECTIONS[section](data)
    # ...

# CLI reste identique
if __name__ == "__main__":
    # python scripts/form_filler.py workday my_information --data '{...}'
```

---

## 3. Les deux modes

### `/apply` - Production
```
Workflow:
1. Détecte plateforme (URL)
2. Charge profile.json + work_experiences.json
3. Pour chaque page:
   a. Génère script via form_filler.py
   b. Exécute via browser_run_code
   c. Si erreur → FIX VIA MCP (ne touche pas au code source)
   d. Continue
4. User review + submit

Règle: JAMAIS modifier workday.py ou base.py
```

### `/improve` - Développement
```
Workflow:
1. User donne une URL de test
2. Tente d'appliquer les scripts existants
3. Quand ça casse:
   a. Analyse l'erreur
   b. Modifie workday.py / base.py pour fix
   c. Re-teste
4. Itère jusqu'à succès
5. Commit les améliorations

Règle: Le but est d'AMÉLIORER le code pour que /apply marche mieux
```

### Différence clé

| Situation | `/apply` | `/improve` |
|-----------|----------|------------|
| Script fail sur un champ | Fix via MCP | Modifie le script |
| Nouveau type de champ | Skip ou manual | Ajoute support |
| Plateforme inconnue | Erreur | Crée nouveau fichier |

---

## 4. Ordre d'implémentation

1. **Créer structure** - `scripts/ats/` avec `__init__.py`
2. **Extraire base.py** - Fuzzy matching, helpers, aliases
3. **Créer workday.py** - Déplacer générateurs Workday
4. **Créer detector.py** - Détection plateforme
5. **Simplifier form_filler.py** - Juste le dispatch
6. **Tester** - Vérifier que `/apply` marche toujours
7. **Créer improve.md** - Nouveau skill pour mode dev

---

## 5. Validation

- [ ] `py scripts/form_filler.py workday my_information --data '{...}'` fonctionne
- [ ] `/apply` sur Richemont fonctionne comme avant
- [ ] Structure claire et modulaire
