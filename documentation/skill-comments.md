# Skill Comments - Issues restantes

## Bugs connus

### 1. docx2pdf COM instability (Windows)
Quand on enchaîne `regenerate_resume()` + `regenerate_cover_letter()` dans le même script Python, la deuxième conversion PDF peut crasher (AttributeError: Word.Application.Documents). Le COM object de Word ne se libère pas proprement entre les deux appels.
**Workaround actuel** : lancer les deux régénérations séparément.
**Fix potentiel** : ajouter un `gc.collect()` + délai entre les conversions, ou réutiliser la même instance COM.

### 2. Validation des limites de caractères non bloquante
`limits.md` définit des min/max par champ, mais `generate_all()` ne bloque pas la génération si les limites sont dépassées. Le resume peut dépasser 1 page et être trimmed silencieusement par PyPDF2.
**Fix potentiel** : ajouter une validation pre-generation qui warn explicitement quel champ dépasse, avec le nombre de chars actuel vs max.

## Améliorations futures

### 3. Cover letter `street_number` naming
Le champ s'appelle `street_number` mais contient en réalité l'adresse complète (ex: "Route des Acacias 60"). Renommer en `address_line` serait plus clair.

### 4. Email subject encore avec ref
Le template SKILL.md pour l'email dit `"subject": "Application - [Position] - Adrian Turion"` mais le skill ne donne pas d'instruction claire sur quand inclure ou non la référence dans l'email (vs jamais dans le subject_line de la cover letter).

### 5. Pas de fallback si web research échoue
L'étape 2 (web research) dépend de WebSearch/WebFetch. Si pas de connexion ou pas de résultats, le skill ne donne pas de guidance sur quoi mettre dans `paragraph_1` et `research`.

### 6. Nombre d'extra entries pas dynamique dans le template
Le template Word a exactement 5 slots (bp1-bp5). Si on veut 6+ entries un jour, il faudra modifier le template. Le script supprime les lignes vides pour < 5 entries, mais ne peut pas en ajouter au-delà de 5.
