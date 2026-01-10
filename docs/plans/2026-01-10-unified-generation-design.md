# Design : Génération unifiée CV + Lettre de motivation

**Date** : 2026-01-10
**Statut** : Validé

---

## Problème

L'architecture actuelle présente plusieurs limitations :

1. **Deux commandes séparées** (`/resume_create`, `/cover_letter_create`) - workflow fragmenté
2. **Pas de parallélisme** - un seul `job_description.md` à la racine, impossible de travailler sur plusieurs candidatures en même temps
3. **Code dupliqué** - ~150 lignes identiques entre les deux scripts (PDF, placeholders)
4. **Modifications difficiles** - éditer un DOCX généré nécessite des scripts ad-hoc
5. **Dépendance externe** - Tavily MCP pour la recherche, seulement pour la lettre

---

## Solution

### Commande unique

```
/generate "job description..."
```

Génère CV + lettre de motivation en une seule commande.

### Architecture par projet

Chaque candidature dans son propre dossier, permettant le parallélisme :

```
jobs/
├── Glencore_Commercial_10-01-2026/
│   ├── job_description.md
│   ├── content.json
│   ├── Resume_Adrian_Turion.docx
│   ├── Cover_Letter_Adrian_Turion.docx
│   └── PDF/
│       ├── Resume_Adrian_Turion.pdf
│       └── Cover_Letter_Adrian_Turion.pdf
│
├── Shell_Graduate_10-01-2026/
│   └── ...
```

### JSON intermédiaire

`content.json` centralise tout le contenu, facilitant les modifications :

```json
{
  "metadata": {
    "company": "Glencore",
    "position": "Commercial Graduate",
    "position_exact": "Commercial Graduate Programme - Metals (LME Desk)",
    "date_created": "2026-01-10",
    "job_keywords": ["commercial aptitude", "resilience", "data analysis"],
    "job_summary": "Programme de 2 ans avec rotations sur les desks métaux..."
  },

  "research": {
    "company_values": ["entrepreneurialism", "integrity"],
    "company_mission": "Responsibly sourcing commodities...",
    "recent_news": "Expansion copper production to 1M tons by 2028",
    "used_in": ["cover_letter_intro", "resume_summary"]
  },

  "resume": {
    "professional_summary": "...",
    "auraia_bullets": ["...", "...", "..."],
    "rc_bullet": "...",
    "europ_bullet": "...",
    "leadership_bullets": ["...", "...", "..."],
    "courses": "...",
    "skills": "..."
  },

  "cover_letter": {
    "recipient": "Hiring Manager",
    "intro": "...",
    "body_1": "**Commercial Execution** — ...",
    "body_2": "**Entrepreneurial Drive** — ...",
    "body_3": "**Analytical Rigor** — ...",
    "closing": "..."
  }
}
```

---

## Structure des fichiers

```
resume.ai/
├── scripts/
│   ├── generate.py              # Orchestrateur principal
│   ├── resume.py                # Génération CV (JSON → DOCX)
│   ├── cover_letter.py          # Génération lettre (JSON → DOCX)
│   └── utils/
│       ├── config.py            # Chemins, fonts, constantes
│       ├── docx.py              # Remplacement placeholders + markdown
│       └── pdf.py               # Conversion DOCX → PDF (1 page)
│
├── templates/
│   ├── Resume - Adrian Turion.docx
│   └── Cover Letter - Adrian Turion.docx
│
├── data/
│   ├── work_experiences.json
│   ├── leadership.json
│   └── courses_and_other.json
│
├── jobs/                        # Un dossier par candidature
│
└── .claude/
    └── commands/
        └── generate.md          # Commande unique
```

---

## Flow de génération

```
/generate "job description..."
         │
         ▼
┌─────────────────────────────────────┐
│  1. ANALYSE JOB DESCRIPTION         │
│  - Extraire company, position       │
│  - Identifier 10-15 keywords        │
│  - Détecter secteur/tone            │
│  - Rédiger job_summary              │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  2. RECHERCHE WEB                   │
│  - Recherches pertinentes selon     │
│    contexte (valeurs, news, deals,  │
│    produit, secteur...)             │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  3. SÉLECTION CONTENU               │
│  - Lire data/*.json                 │
│  - Choisir bullets pertinents       │
│  - Adapter au secteur/tone          │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  4. RÉDACTION                       │
│  - Professional summary (CV)        │
│  - Paragraphes lettre               │
│  - Intégrer research où pertinent   │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  5. CRÉER DOSSIER + content.json    │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  6. GÉNÉRER DOCUMENTS               │
│  - JSON → Resume.docx → PDF         │
│  - JSON → Cover_Letter.docx → PDF   │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  7. VALIDATION                      │
│  - Placeholders remplacés ?         │
│  - Fonts corrects ?                 │
│  - 1 page ?                         │
└─────────────────────────────────────┘
```

---

## Flow de modification

```
Utilisateur: "Le 2ème bullet Auraia est trop long"
         │
         ▼
┌─────────────────────────────────────┐
│  1. LIRE content.json               │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  2. MODIFIER le champ concerné      │
│  auraia_bullets[1] = version courte │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  3. RÉGÉNÉRER seulement le CV       │
│  (lettre pas impactée = pas refaite)│
└─────────────────────────────────────┘
```

**Exemples de modifications :**

| Demande | Action |
|---------|--------|
| "CV trop long" | Raccourcir les bullets les plus longs |
| "Change le résumé pro" | Modifier `resume.professional_summary` |
| "Plus d'accent sur l'IA" | Ajuster bullets + summary |
| "Intro lettre trop générique" | Réécrire `cover_letter.intro` |
| "Remplace le 3ème leadership" | Sélectionner un autre de `data/leadership.json` |

---

## Scripts Python

### `scripts/utils/config.py`
```python
TEMPLATES = {
    "resume": "templates/Resume - Adrian Turion.docx",
    "cover_letter": "templates/Cover Letter - Adrian Turion.docx"
}
FONT = "Times New Roman"
FONT_SIZE = 10
OUTPUT_NAMES = {
    "resume": "Resume_Adrian_Turion",
    "cover_letter": "Cover_Letter_Adrian_Turion"
}
```

### `scripts/utils/docx.py`
```python
def replace_placeholders(doc, replacements: dict) -> None
def apply_markdown_bold(paragraph, text: str) -> None
def remove_empty_paragraphs(doc) -> None
```

### `scripts/utils/pdf.py`
```python
def convert_to_pdf(docx_path: str, output_folder: str) -> str
def trim_to_one_page(pdf_path: str) -> None
```

### `scripts/resume.py`
```python
def generate_resume(content: dict, output_folder: str) -> tuple[str, str]
```

### `scripts/cover_letter.py`
```python
def generate_cover_letter(content: dict, output_folder: str) -> tuple[str, str]
```

### `scripts/generate.py`
```python
def create_project(company: str, position: str) -> str
def save_content(content: dict, folder: str) -> None
def load_content(folder: str) -> dict
def generate_all(folder: str) -> None
def regenerate_resume(folder: str) -> None
def regenerate_cover_letter(folder: str) -> None
```

---

## Commande /generate

**Fichier** : `.claude/commands/generate.md`

Remplace les deux commandes actuelles (`resume_create.md`, `cover_letter_create.md`).

**Contenu simplifié** :
- Analyse job description
- Recherche web (flexible selon contexte)
- Sélection contenu depuis data/*.json
- Rédaction (summary CV + paragraphes lettre)
- Génération content.json + DOCX + PDF
- Support modifications post-génération

---

## Avantages

| Avant | Après |
|-------|-------|
| 2 commandes séparées | 1 commande unique |
| Pas de parallélisme | Multi-projets simultanés |
| ~150 lignes dupliquées | Code factorisé dans utils/ |
| Modifications = galère | Modifier JSON → régénérer |
| Tavily externe | WebSearch intégré |
| 600+ lignes de prompts | Prompts simplifiés |

---

## Implémentation

### Phase 1 : Utils partagés
- [ ] Créer `scripts/utils/config.py`
- [ ] Créer `scripts/utils/docx.py` (extraire logique existante)
- [ ] Créer `scripts/utils/pdf.py` (extraire logique existante)

### Phase 2 : Scripts refactorisés
- [ ] Refactoriser `scripts/resume.py` (utiliser utils, lire JSON)
- [ ] Refactoriser `scripts/cover_letter.py` (utiliser utils, lire JSON)
- [ ] Créer `scripts/generate.py` (orchestrateur)

### Phase 3 : Commande unifiée
- [ ] Créer `.claude/commands/generate.md`
- [ ] Supprimer `resume_create.md` et `cover_letter_create.md`

### Phase 4 : Nettoyage
- [ ] Supprimer code dupliqué
- [ ] Mettre à jour CLAUDE.md
- [ ] Tester sur une candidature réelle
