# Character Limits

Validated automatically by `generate_all()`. MAX limits block generation to guarantee 1-page fit.

## Resume

| Field | Min | Max |
|-------|-----|-----|
| `introduction` | 180 | 220 |
| `auraia_bullet` (each of 4) | 150 | 280 |
| `rc_bullet` (each of 3) | 110 | 150 |
| `generali_bullet` (each of 3) | 110 | 150 |
| `extra_sentence` (each of 3-5) | 120 | 160 |
| `coursework` | 60 | 100 |
| `tools` | 50 | 80 |
| `skills` | 50 | 110 |
| `interests` | 50 | 110 |

## Cover letter

No hard validation — fit is visual. Guidelines:

| Field | Target |
|-------|--------|
| `paragraph_1` | 200–400 chars |
| `paragraph_2` | 300–500 chars |
| `paragraph_3` | 150–300 chars |
| `closing` | 50–120 chars |

**If PDF exceeds 1 page:** shorten the longest resume bullets first, then cover letter paragraphs.
Run `regenerate_resume()` or `regenerate_cover_letter()` after editing content.json.
