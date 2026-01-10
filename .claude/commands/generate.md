Génère un CV et une lettre de motivation personnalisés à partir d'une description de poste.

---

## Input

L'utilisateur fournit la job description en argument.

## Workflow

### 1. Analyse de la job description
- Extraire : company, position, position_exact
- Identifier 10-15 keywords exacts (pour ATS)
- Détecter secteur et tone (trading/M&A/consulting/tech)
- Rédiger job_summary (2-3 phrases pour rappel avant entretien)

### 2. Recherche web (WebSearch)
Effectuer les recherches pertinentes selon le contexte :
- Valeurs/culture de l'entreprise
- Actualités récentes
- Secteur d'activité / concurrents
- Projets ou initiatives spécifiques mentionnés dans l'offre

Objectif : trouver des éléments concrets pour personnaliser les documents.

### 3. Sélection du contenu
Depuis `data/*.json`, sélectionner :
- 3 bullets Auraïa (sur 9 disponibles)
- 1 bullet RC Group (sur 6)
- 1 bullet Europ Assistance (sur 7)
- 3 leadership (sur 5)
- 3-4 courses, 5-7 skills

Critères : keywords match, secteur, tone adapté.

### 4. Rédaction
**CV :**
- Professional summary : 2-3 lignes, mentionne le nom de l'entreprise

**Lettre de motivation :**
- Intro : 60-80 mots, hook basé sur la recherche web
- Body 1/2/3 : 60-80 mots chacun, format "**Titre** — contenu"
- Closing : 50-70 mots

### 5. Génération
1. Créer le dossier `jobs/[Company]_[Position]_[DD-MM-YYYY]/`
2. Sauvegarder `content.json` avec tout le contenu
3. Sauvegarder `job_description.md`
4. Appeler `scripts/generate.py` pour générer DOCX + PDF

### 6. Validation
- Vérifier qu'aucun placeholder ne reste
- Confirmer que les PDFs sont générés

## Structure du content.json

```json
{
  "metadata": {
    "company": "...",
    "position": "...",
    "position_exact": "...",
    "date_created": "...",
    "job_keywords": [...],
    "job_summary": "..."
  },
  "research": {
    "company_values": [...],
    "company_mission": "...",
    "recent_news": "...",
    "used_in": [...]
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
    "recipient": "...",
    "street": "...",
    "postal": "...",
    "intro": "...",
    "body_1": "**Titre** — ...",
    "body_2": "**Titre** — ...",
    "body_3": "**Titre** — ...",
    "additional": "",
    "attraction": "",
    "closing": "..."
  }
}
```

## Modifications post-génération

Si l'utilisateur demande un changement :
1. Lire `content.json` du dossier
2. Modifier le champ concerné
3. Régénérer uniquement le document impacté :
   - `python scripts/generate.py <folder>` pour tout
   - Ou modifier et régénérer via les fonctions Python

Exemples :
- "CV trop long" → raccourcir bullets dans content.json, régénérer CV
- "Change le résumé pro" → modifier `resume.professional_summary`
- "Intro lettre trop générique" → modifier `cover_letter.intro`

## Style d'écriture

**À FAIRE :**
- Utiliser les EXACT keywords de la job description (ATS)
- Adapter le tone au secteur
- Inclure des métriques quantifiables
- Mentionner le nom de l'entreprise dans le summary

**À ÉVITER :**
- Phrases génériques ("passionate about", "excited to leverage")
- Em-dashes (utiliser tirets ou deux-points)
- Répéter le contenu du CV dans la lettre
- Dépasser 1 page
