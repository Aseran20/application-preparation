import sys
sys.path.insert(0, 'scripts')
from generate_resume import generate_resume
from generate_cover_letter import generate_cover_letter

print("=== Regenerating Resume ===")

# Resume
professional_summary = """Finance graduate with M&A execution experience across 7 concurrent mandates under tight deadlines. Demonstrated commercial aptitude through deal-making and entrepreneurial ventures, combined with strong data analysis skills (Python, Excel). Proven resilience managing high-stakes transactions with individual responsibility. Ready to bring this mindset to Glencore's trading floor."""

auraia_bullets = [
    "Managed end-to-end execution on 7 concurrent mandates (EUR 5M–50M) across healthcare, technology, and life sciences sectors, handling valuation, buyer sourcing, and deal coordination under tight deadlines in a lean 3-person team",
    "Built financial models (LBO, DCF, comps) and performed data analysis to identify strategic buyers across Europe, US, and Asia, coordinating logistical and financial execution from marketing materials to closing",
    "Sole analyst entrusted with individual responsibility for data room management, client presentations, and relationship coordination with advisors across multiple live transactions simultaneously"
]

rc_group_bullet = "Worked directly with CEO on acquisition targets in France and Belgium, preparing investment memos with market analysis and financial projections (EUR 10M–30M targets), demonstrating commercial aptitude in evaluating strategic opportunities"

europ_assistance_bullet = "Built automated financial dashboards (Excel, PowerBI) for CHF 50M+ subsidiary, performing data analysis on monthly P&L variance and developing cost allocation models with accuracy critical for Board presentations"

leadership_bullets = [
    "Founded and developed Screeny.ai, an AI-driven buyer sourcing tool for investment banks, leading full-stack development and sales outreach; tool adopted by 3 firms, reducing buyer research time by ~90% (10h+ to 20min)",
    "Led post-COVID financial recovery for AIESEC by sourcing corporate leads and negotiating partnerships; closed 3 deals generating CHF 60K annual revenue through resilience and strong communication skills",
    "Manage personal investment portfolio using options strategies (Cash Secured Puts, Covered Calls), executing disciplined trades with 45-day expiries to generate CHF 5K+ annual premiums while managing risk"
]

courses = "Data Science for Finance, Derivatives, Corporate Governance and M&A, Quantitative Asset and Risk Management"
skills = "Excel, Bloomberg Terminal, Python, SQL, PowerBI, Capital IQ"

folder_name, output_path, pdf_path = generate_resume(
    professional_summary=professional_summary,
    auraia_bullets=auraia_bullets,
    rc_group_bullet=rc_group_bullet,
    europ_assistance_bullet=europ_assistance_bullet,
    leadership_bullets=leadership_bullets,
    courses=courses,
    skills=skills,
    company="Glencore",
    position="Commercial_Graduate"
)

print(f"Resume: {output_path}")
print(f"PDF: {pdf_path}\n")

print("=== Regenerating Cover Letter ===")

# Cover Letter
company_name = "Glencore"
recipient_name = "Hiring Manager"
street_number = "Baarermatte"
postal_city_country = "6340 Baar, Switzerland"

intro_paragraph = """Glencore's strategic goal to reach 1 million tons of copper production by 2028, combined with your core value of entrepreneurialism and emphasis on individual responsibility from day one, aligns with my experience in high-stakes deal execution. I am writing to express my strong interest in the Commercial Graduate Programme, eager to apply my commercial aptitude and data analysis skills to your trading operations."""

body_paragraph_1 = """**Commercial Execution & Resilience** - At Auraïa Capital Advisory, I managed seven concurrent mandates (EUR 5M-50M) as the sole analyst, developing the resilience essential for front-line trading support. I coordinated logistical and financial execution from marketing to closing, working with clients and counterparties under tight deadlines while maintaining accuracy critical for deal negotiations."""

body_paragraph_2 = """**Entrepreneurial Abilities & Data Analysis** - As founder of Screeny.ai, an AI-driven buyer sourcing tool adopted by three M&A firms, I bring the entrepreneurial abilities valued in your programme. I built this tool to reduce research time by 90%, demonstrating my drive to leverage data analysis for operational excellence. This builder mindset, combined with Python and Excel skills, prepares me for data-driven trading operations."""

body_paragraph_3 = """**Strong Communication & Global Exposure** - I've presented to C-suite executives and managed relationships across Europe, US, and Asia throughout complex transactions. Leading post-COVID recovery at AIESEC—closing three partnerships generating CHF 60K revenue—reinforced my ability to negotiate and deliver results under pressure in cross-functional environments."""

closing_paragraph = """I am ready to contribute to Glencore's trading operations and develop my commercial career in commodities. I would welcome the chance to discuss how my experience can add value to your programme. Thank you for your time and consideration."""

output_folder = "jobs/Glencore_Commercial_Graduate_06-10-2025"

folder_name, output_path, pdf_path = generate_cover_letter(
    company_name=company_name,
    recipient_name=recipient_name,
    street_number=street_number,
    postal_city_country=postal_city_country,
    intro_paragraph=intro_paragraph,
    body_paragraph_1=body_paragraph_1,
    body_paragraph_2=body_paragraph_2,
    body_paragraph_3=body_paragraph_3,
    additional_context="",
    company_attraction="",
    closing_paragraph=closing_paragraph,
    output_folder=output_folder
)

print(f"Cover Letter: {output_path}")
print(f"PDF: {pdf_path}")

print("\n=== Done! PDFs should now have only 1 page (no blank pages) ===")
