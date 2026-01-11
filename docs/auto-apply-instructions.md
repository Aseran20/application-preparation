# /apply Automation - Problèmes & Solutions

## Comparaison des approches testées

| Aspect | Claude in Chrome | Playwright MCP Docker | Playwright MCP Local |
|--------|-----------------|----------------------|---------------------|
| Fenêtre visible | ✅ Oui | ❌ Headless | ✅ Oui |
| File upload | ❌ Impossible | ✅ Oui | ✅ Oui |
| Vitesse | Lent (~15-20 min pour 4 langues) | Rapide | Rapide (~2 min) |
| Stabilité | Extensions conflicts | Stable | Stable |
| Intervention user | Chat naturel | Screenshots | Chat naturel |

**Verdict : Playwright MCP Local = meilleure solution pour le semi-auto**

---

## Session de test : Richemont Finance Accelerator (Workday)

### Problèmes rencontrés

#### 1. Extensions Chrome qui bloquent
**Erreur:** `Cannot access a chrome-extension:// URL of different extension`

**Cause:** D'autres extensions Chrome injectent du contenu sur la page et Claude in Chrome essaie d'interagir avec ces éléments au lieu de la vraie page.

**Extensions problématiques identifiées:**
- Apollo.io (sales prospecting)
- Password managers (Bitwarden, 1Password, LastPass)
- Notification "Claude is active in this tab group"

**Solution:** Désactiver TOUTES les autres extensions sauf Claude in Chrome avant d'utiliser `/apply`

---

#### 2. Checkbox grisée après remplissage
**Problème:** La checkbox "I consent to privacy policy" apparaissait cochée mais était grisée/inactive

**Cause:** Probablement un état intermédiaire du formulaire Workday

**Solution:** Décocher puis recocher manuellement

---

#### 3. Recherche d'université - nom exact requis
**Problème:** "HEC Lausanne" → "No Items"

**Cause:** Workday utilise les noms officiels complets, pas les abréviations

**Solution:**
- "HEC Lausanne" → "Université de Lausanne"
- "EPFL" → "École Polytechnique Fédérale de Lausanne"
- Ajouter un mapping dans `profile.json` :

```json
{
  "education": [
    {
      "school": "HEC Lausanne",
      "school_official_names": [
        "Université de Lausanne",
        "University of Lausanne",
        "UNIL"
      ]
    }
  ]
}
```

---

#### 4. Dropdowns Workday
**Problème:** Les dropdowns nécessitent un clic pour ouvrir, puis un clic sur l'option

**Solution:**
1. `click` sur le bouton dropdown
2. `find` l'option souhaitée
3. `click` sur l'option

---

#### 5. Authentification requise
**Problème:** Workday demande de créer un compte avant de postuler

**Solution:**
- Stocker email + password dédié dans `profile.json`
- Gérer la création de compte automatiquement
- Pour 2FA : ouvrir Gmail et récupérer le code

---

---

### Leçons Playwright MCP Local (11 jan 2026)

#### 6. Toujours vérifier à la fin
**Problème:** Oubli de cocher "I am fluent in this language" pour les langues natives

**Solution:** Avant de cliquer "Save and Continue", faire un snapshot et vérifier :
- Tous les champs obligatoires sont remplis
- Les checkboxes sont cochées (ex: fluent pour Native languages)
- Les données correspondent à ce qui est dans les fichiers source

---

#### 7. Utiliser les bonnes données sources
**Problème:** Données inventées (ex: "Auraia" au lieu de "Auraïa Capital Advisory", mauvais titre de poste)

**Solution:** Toujours lire les fichiers de données AVANT de remplir :
```
data/work_experiences.json  → Job Title, Company, Location, Description
data/leadership.json        → Leadership experiences
profile.json                → Personal info, languages, education
```

**Champs critiques à vérifier:**
- `company`: nom exact avec accents (ex: "Auraïa Capital Advisory")
- `title`: titre exact (ex: "Mergers & Acquisitions Analyst")
- `location`: ville correcte (ex: "Geneva" pas "Lausanne")
- `dates`: format correct (ex: "Aug 2024" → mois 08)

---

#### 8. Localisation des fichiers PDF
**Problème:** Ne pas savoir où trouver le CV à uploader

**Solution:** Les PDFs sont dans le dossier du job :
```
jobs/[Company] - [Position] - [DD.MM.YYYY]/
├── PDF/
│   ├── Adrian Turion - [Company] - Resume.pdf    ← CV à uploader
│   └── Adrian Turion - [Company] - Cover Letter.pdf
```

Pour trouver le bon dossier :
```bash
# Glob pattern
jobs/*Richemont*/**/*.pdf
```

---

#### 9. Checkboxes "fluent" pour les langues
**Problème:** Les checkboxes "I am fluent in this language" ne sont pas cochées automatiquement même si le niveau est Native

**Solution:** Pour chaque langue avec niveau "Native" ou "Fluent", cocher manuellement la checkbox fluent

---

#### 14. browser_run_code - Actions parallèles
**Problème:** On veut accélérer en faisant plusieurs actions par call (comme Browser Use)

**Cause:** `browser_run_code` permet d'exécuter plusieurs commandes Playwright, mais les locators complexes (spinbuttons Workday) échouent souvent

**Solution:**
```javascript
// ✅ Marche - locators simples
await page.getByLabel('Job Title').fill('Analyst');
await page.getByLabel('Company').fill('RC Group');
await page.getByLabel('Location').fill('Paris');

// ❌ Échoue - locators complexes (spinbuttons, nested groups)
await page.getByLabel('Work Experience 2').locator('group:has-text("From")').getByRole('spinbutton').fill('02');
```

**Règle:** Pour formulaires complexes (Workday), préférer les actions séquentielles avec refs

---

#### 15. Refs vs Locators - Fiabilité
**Problème:** Les locators Playwright échouent sur les composants custom Workday

**Solution:** Utiliser les refs du snapshot pour une fiabilité maximale :
```
# Snapshot montre:
spinbutton "Month" [ref=e852]: "2"

# Action fiable:
browser_type ref=e852 text="08"
```

**Avantage:** Les refs pointent exactement vers l'élément, pas de recherche DOM

---

#### 16. Session persistence Workday
**Observation:** Workday préserve les données du formulaire entre sessions

**Implication:**
- Si on ferme le browser et revient, les champs restent remplis
- Permet de reprendre une candidature interrompue
- Les credentials sont aussi sauvés (auto-login)

---

#### 17. Champs de recherche - Appuyer sur Enter
**Problème:** Les champs de recherche (School or University) affichent "No Items" même avec le bon texte

**Cause:** Workday ne déclenche pas la recherche API automatiquement après `fill()`. Il faut simuler l'action utilisateur complète.

**Solution:**
```javascript
// ❌ Ne marche pas - pas de résultats
await page.getByLabel('School or University').fill('Lausanne');

// ✅ Marche - déclenche la recherche
await page.getByLabel('School or University').fill('Lausanne');
await page.getByLabel('School or University').press('Enter');
```

**Avec Playwright MCP:**
```
browser_type ref=e894 text="Lausanne" submit=true
```

Le paramètre `submit=true` ajoute automatiquement un `press('Enter')` après le fill.

---

### Leçons Browser Use (11 jan 2026)

#### 10. Login - Utiliser Enter au lieu de cliquer
**Problème:** L'agent clique 6+ fois sur le bouton "Sign In" sans que la page ne change

**Cause:** Le bouton Sign In de Workday ne répond pas toujours aux clics programmatiques

**Solution:**
- Après avoir entré les credentials, appuyer sur **Enter** dans le champ password
- Ne pas cliquer sur "Sign In" plus de 2 fois - passer au clavier

---

#### 11. Checkboxes Workday - Cliquer sur les SPAN, pas les DIV
**Problème:** Les checkboxes ne se cochent pas malgré des clics répétés

**Cause:** Workday utilise des composants custom où :
- Le `div` affiche le composant visuellement
- Le `span` (avec le texte du label) reçoit l'événement de clic
- Cliquer sur le `div` ne toggle pas l'état

**Solution:**
```
❌ click: div (ne marche pas)
✅ click: span (marche)
```

Pour identifier le bon élément :
- Chercher le `span` qui contient le texte du label ("I am fluent", "I currently work here")
- Éviter les `div` parents même s'ils semblent être le checkbox

---

#### 12. File Upload - Nécessite une liste de fichiers autorisés
**Problème:** L'agent voit le chemin du fichier dans les instructions mais ne peut pas l'uploader

**Cause:** Browser Use requiert explicitement `available_file_paths` pour autoriser l'accès aux fichiers

**Solution (Browser Use):**
```python
agent = Agent(
    task=task,
    available_file_paths=["/chemin/vers/cv.pdf"],
    ...
)
```

**Solution (Playwright MCP):** Utiliser le chemin absolu directement avec `browser_file_upload`

---

#### 13. Composants custom - Principes généraux
**Leçon clé:** Les interfaces modernes (Workday, Salesforce, Greenhouse) utilisent des composants JavaScript custom où l'élément visible n'est pas l'élément interactif.

| Ce qu'on voit | Ce qu'il faut cibler |
|---------------|---------------------|
| Checkbox visuelle | `span` avec le label text |
| Bouton Submit | Touche Enter dans le dernier champ |
| Dropdown | Clic sur le bouton, puis clic sur l'option `span` |

**Règle générale:** Si un clic ne marche pas après 2 tentatives, changer de stratégie :
1. Essayer un élément enfant (`span`, `label`)
2. Essayer le clavier (Tab + Space, Enter)
3. Ne pas répéter la même action plus de 2 fois

---

### Comparaison Browser Use vs Playwright MCP

| Aspect | Browser Use | Playwright MCP |
|--------|-------------|----------------|
| Contrôle | L'agent décide | Tu décides |
| Debugging | Difficile (agent loop) | Facile (step by step) |
| Apprentissage | Par essai/erreur (coûte des steps) | Tu codes les quirks une fois |
| Multi-plateforme | Doit réapprendre chaque plateforme | Tu adaptes le script |
| Maturité | Encore immature pour formulaires complexes | Production-ready |
| Actions parallèles | Oui (natif) | Limité (`browser_run_code` pour locators simples) |
| Fiabilité Workday | ~60% (checkboxes, spinbuttons) | ~95% (avec refs) |

**Verdict:** Playwright MCP pour le contrôle, Browser Use pour l'exploration

---

### Améliorations à implémenter

- [ ] Script de pré-vol qui désactive les extensions problématiques
- [ ] Mapping des noms d'universités (abréviation → nom officiel)
- [x] Retry logic pour les checkboxes → cliquer sur span, pas div
- [ ] Détection automatique du type de formulaire (Workday, Greenhouse, Lever, etc.)
- [ ] Fallback manuel avec instructions claires quand l'automation échoue
- [x] Validation finale avant "Save and Continue" (snapshot + checklist)
- [x] Lire data/*.json avant de remplir les champs
- [ ] Auto-cocher "fluent" pour Native/Fluent languages
- [x] Login → Enter au lieu de cliquer sur Sign In (Browser Use) / Click direct (Playwright MCP)
- [x] File upload → chemin absolu obligatoire
- [x] Utiliser refs pour fiabilité maximale sur Workday
- [x] Champs de recherche → Enter après fill() pour déclencher l'API
- [ ] Optimiser avec browser_run_code pour champs simples (Job Title, Company, Location)

---

### Flux validé

```
1. LinkedIn job page
   └─> Click "Apply" (external link)

2. Workday landing page
   └─> Decline cookies
   └─> Click "Apply Manually"

3. Create Account page
   └─> Fill email (from profile.json)
   └─> Fill password (from profile.json)
   └─> Check consent checkbox
   └─> Click "Create Account"

4. My Information (Step 1/4)
   └─> Radio: "No" for previous employment
   └─> Dropdown: Country, Prefix, Canton
   └─> Text: Name, Address, Phone
   └─> Click "Save and Continue"

5. My Experience (Step 2/4)
   └─> Work Experience 1: Auraïa (from data/work_experiences.json)
   └─> Work Experience 2+: Add Another → RC Group, Europ Assistance...
   └─> Education: Search university (nom officiel!)
   └─> Languages: Dropdown selections + fluent checkboxes
   └─> Upload CV (from jobs/[Company]/PDF/)
   └─> Snapshot + vérification avant de continuer
   └─> Click "Save and Continue"

6. Voluntary Disclosures (Step 3/4)
   └─> TBD

7. Review (Step 4/4)
   └─> USER clicks Submit (pas l'IA)
```
