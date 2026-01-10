import sys
sys.path.insert(0, 'scripts')
from generate_resume import generate_resume

print("=== Generating SILEX Resume ===")

# Tailored content for SILEX [STAGE] Assistant Sales - produits structurés (Genève)
company = "SILEX"
position = "Assistant_Sales_Produits_Structures"

professional_summary = (
    "Commercially minded finance graduate with hands-on M&A execution and FP&A automation experience. "
    "Strong grasp of produits structurés/derivatives with practical programming skills (VBA, Python) and Bloomberg exposure. "
    "Ready to support SILEX Investment Solutions Sales on pricing, backtesting, reporting, CRM workflows and client materials in a fast-paced salle de marché environment."
)

# Auraïa Capital — pick 3 bullets aligned to sales/structured products (client materials, speed, analytics)
auraia_bullets = [
    "Led production of client-facing marketing materials, maintained buyer universes, and coordinated data room management across multiple concurrent mandates under tight deadlines",
    "Built detailed financial models (DCF, trading/transaction comps) and prepared client presentations for Board meetings and investor pitches",
    "Managed relationships with clients, advisors, and counterparties throughout transaction lifecycles across Europe, the US, and Asia"
]

# RC Group — 1 bullet showcasing market analysis and memo building
rc_group_bullet = (
    "Prepared investment memos (market analysis, competitive positioning, financial projections) for 3 potential acquisitions in France/Belgium, working directly with divisional CEOs"
)

# Europ Assistance — 1 bullet emphasizing automation/reporting
europ_assistance_bullet = (
    "Built automated KPI dashboards (Excel, PowerBI) and performed monthly P&L variance analysis for the Swiss subsidiary (CHF 50M+), improving reporting accuracy for Board materials"
)

# Leadership — choose 3 aligned to commercial + data mindset
leadership_bullets = [
    "Founder & Developer of Screeny.ai — AI-driven buyer sourcing tool adopted by 3 advisory firms; reduced research time by ~90% (10h+ to 20min) through full‑stack development and B2B sales outreach",
    "Business development at AIESEC — sourced corporate leads, created pitchbooks and negotiated partnerships; 3 deals closed generating CHF 60K annual revenue (+40% placements)",
    "McKinsey x Keyrock case finalist — built a data‑driven forecasting model (order book/stat‑arb) and presented strategic insights with potential CHF 200K annual revenue"
]

# Coursework — keep to 3–4 relevant courses (NOT 5)
courses = ", ".join([
    "Derivatives",
    "Fixed Income and Credit Risk",
    "Data Science for Finance",
    "Quantitative Asset and Risk Management",
])

# Skills — one line; include exact JD keywords for ATS (Bloomberg, VBA, Python, CRM)
skills = (
    "Investment Tools: Bloomberg, Excel (Advanced), PowerPoint, CRM | Programming: VBA, Python, R"
)

folder_name, output_path, pdf_path = generate_resume(
    professional_summary=professional_summary,
    auraia_bullets=auraia_bullets,
    rc_group_bullet=rc_group_bullet,
    europ_assistance_bullet=europ_assistance_bullet,
    leadership_bullets=leadership_bullets,
    courses=courses,
    skills=skills,
    company=company,
    position=position,
)

print(f"Resume: {output_path}")
print(f"PDF: {pdf_path}")
print("=== Done ===")

