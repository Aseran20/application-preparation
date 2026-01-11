# Design: Batched /apply Automation

## Problème

L'approche step-by-step actuelle est trop lente (~10-15 min par candidature):
- Chaque action = 1 round-trip API
- ~50-80 tours pour remplir un formulaire complet
- L'utilisateur doit attendre

## Solution

**Batched par section** - Générer et exécuter plusieurs actions d'un coup via `browser_run_code`.

## Architecture

```
/apply [URL]
     │
     ▼
┌─────────────────────────────────────────┐
│ 1. PRÉPARATION (1 tour)                 │
│    - Lire profile.json                  │
│    - Lire data/work_experiences.json    │
│    - Trouver CV: jobs/[Company]/PDF/    │
│    - Naviguer vers URL                  │
│    - Snapshot initial                   │
└─────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────┐
│ 2. BATCH PAR SECTION (1 tour/section)   │
│                                         │
│    Pour chaque step du formulaire:      │
│    1. Analyser le snapshot              │
│    2. Générer toutes les actions JS     │
│    3. browser_run_code (tout d'un coup) │
│    4. Snapshot résultat                 │
│    5. Click "Save and Continue"         │
└─────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────┐
│ 3. VÉRIFICATION + FIX (si nécessaire)   │
│    - Comparer snapshot vs attendu       │
│    - Si erreurs: re-batch corrections   │
│    - Sinon: passer à la suite           │
└─────────────────────────────────────────┘
     │
     ▼
         User review + Submit
```

## Exemple de batch généré

Pour Step 1 "My Information":

```javascript
async (page) => {
  // Radio button
  await page.getByRole('radio', { name: 'No' }).click();

  // Country dropdown
  await page.getByRole('button', { name: 'Country' }).click();
  await page.getByRole('option', { name: 'Switzerland' }).click();

  // Text fields
  await page.getByLabel('Given Name').fill('Adrian');
  await page.getByLabel('Family Name').fill('Turion');
  await page.getByLabel('Street and House Number').fill('Avenue de Sainte Clotilde 9');
  await page.getByLabel('Postcode').fill('1205');
  await page.getByLabel('City').fill('Geneva');

  // Canton dropdown
  await page.getByRole('button', { name: 'Canton' }).click();
  await page.getByRole('option', { name: 'Geneva' }).click();

  // Phone
  await page.getByRole('button', { name: 'Phone Device Type' }).click();
  await page.getByRole('option', { name: 'Mobile' }).click();
  await page.getByLabel('Phone Number').fill('77 262 37 96');
}
```

## Règles de génération

### Ce qui marche en batch
- `fill()` sur les textbox
- `click()` sur radio, checkbox, buttons
- `getByLabel()`, `getByRole()` avec noms exacts
- Dropdowns: click button → click option

### Ce qui nécessite des pauses
- Champs de recherche: `fill()` + `press('Enter')` + wait + click option
- File upload: action séparée avec `browser_file_upload`
- Spinbuttons (dates): parfois fragiles, préférer refs si problème

### Fallback
Si le batch échoue sur un élément:
1. Identifier l'élément problématique dans l'erreur
2. Générer un mini-batch sans cet élément
3. Traiter l'élément problématique en step-by-step

## Gains attendus

| Métrique | Step-by-step | Batched |
|----------|--------------|---------|
| Tours API | ~50-80 | ~8-12 |
| Temps total | ~10-15 min | ~2-3 min |
| Fiabilité | ~95% | ~90% |
| Flexibilité | 100% | 90% |

## Prochaines étapes

1. [ ] Implémenter le flow batched dans `/apply`
2. [ ] Tester sur Workday (Richemont)
3. [ ] Ajouter la logique de vérification/fix
4. [ ] Documenter les patterns qui marchent/échouent
