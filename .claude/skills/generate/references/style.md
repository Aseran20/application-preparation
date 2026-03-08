# Writing Style Guide

## Introduction (`{introduction}`)

**Pattern:** `[current positioning] + [sector-specific exposure]. [directional sentence]. Available from May 2026.`

**Rules:**
- No company name, no role title explicitly named
- No first person ("I")
- ~2 lines in Word (~150-230 chars)
- Factual tone — no "passionate", "dynamic", "excited"
- Sector vocabulary naturally woven in (not forced)

**Sector examples:**
- Commodity trading: "Commodity-focused M&A analyst with exposure to physical trade finance, cross-border logistics and counterparty structuring across energy and metals. Moving into physical trading operations. Available from May 2026."
- M&A: "M&A analyst with full deal cycle experience across energy, commodities and industrials — sourcing to close across 9 live mandates in a 5-person boutique. Looking to develop within a larger advisory platform. Available from May 2026."
- Private equity: "M&A analyst with hands-on deal execution, financial modelling and due diligence across energy and industrials. Combining transactional rigour with sector analysis to move into direct investment and value creation. Available from May 2026."
- Wealth management: "Multilingual finance professional combining analytical background in derivatives and portfolio management with cross-border M&A deal exposure. Moving into client-facing wealth advisory and structured solutions. Available from May 2026."

---

## Bullets — Auraia / RC / Generali

**Pattern:** `[Action verb] + [what/scope] + [context or metric]`

**Rules:**
- No subject ("I") — starts directly with verb
- Include metrics when available (CHF amounts, %, counts)
- Auraia: up to 2 lines per bullet (more detail, data points encouraged)
- RC / Generali: max 1 line per bullet (keep concise)
- No period at end
- Never use em dash (—) anywhere in resume or cover letter; use commas, semicolons, or hyphens instead
- Vocabulary adapted to sector (e.g. "counterparty structuring", "margin sensitivity" for trading; "LBO", "quality of earnings" for PE)
- Auraia: 4 bullets | RC: 3 bullets | Generali: 3 bullets (fixed counts)

**Selection criteria:** keyword match with JD first, sector vocabulary second, strongest metrics third.

**Quality rules:**
- Never repeat the same data point (e.g. "7 mandates") across multiple bullets
- Reframe bullets for the target sector — don't just select, adapt the vocabulary (e.g. "sourcing to close" for M&A, "client engagement through advisory" for WM)
- Every bullet should have at least one concrete element: metric, scope, outcome, or named context
- Avoid generic filler like "Analyzed market trends and competitive landscape" without specifics

---

## Extra section

**Title:** `ENTREPRENEURIAL & INDEPENDENT PROJECTS` (default)
Use `COMMODITY & ENTREPRENEURIAL EXPOSURE` for physical trading / commodity roles.

**Entry format:** `**Title (context):** One-sentence description with action + outcome.`

Each entry stored as `{"title": "...", "sentence": "..."}` in content.json.
The script renders it as `**Title:** sentence` with markdown bold.

**Available pool:** see `references/profile.md` > Entrepreneurial & Independent Projects — select 3 most relevant entries for the sector.

---

## Cover letter

**Structure:**
- `paragraph_1` — Why this company: use research finding (company values, recent news, specific initiative). 3-5 sentences. Hook immediately.
- `paragraph_2` — Why me: max 2 experiences, concrete evidence, avoid repeating resume bullets verbatim. 4-6 sentences.
- `paragraph_3` — Why us: trajectory alignment, what you bring + what you want to learn. 2-4 sentences.
- `closing` — Standard: "I would welcome the opportunity to discuss my application further."

**Tone rules:**
- Confident but not over-the-top
- Never: "I am excited to leverage", "I have always been passionate about", "I am thrilled"
- Narrative prose — no bold titles, no bullet points
- Always English
- All 3 paragraphs + closing must fit on 1 page

---

## Skills section fields

- `{tools}`: comma-separated, mostly fixed — Excel (advanced), VBA, Python, SQL, Bloomberg Terminal — reorder by relevance to JD
- `{skills}`: comma-separated, adapted to JD keywords, based on real experience
- `{interests}`: comma-separated, from personal data (Energy geopolitics, Physical commodity flows, Fitness (strength & endurance), Applied AI tools)
- `{coursework}`: 3-4 courses from `references/profile.md` > Course pool, comma-separated, most relevant to JD
