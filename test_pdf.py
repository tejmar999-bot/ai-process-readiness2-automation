from utils.pdf_generator import generate_pdf_report
sample = {
    "overall_score": 3.6,
    "readiness_band": {"label": "Emerging"},
    "dimension_scores": {
        "Process Maturity": 3.0,
        "Technology Infrastructure": 2.7,
        "Data Readiness": 3.8,
        "People & Culture": 3.2,
        "Leadership & Alignment": 4.0,
        "Governance & Risk": 3.5
    },
    "executive_summary": "Short test executive summary for local testing."
}
pdf_bytes = generate_pdf_report(sample, company_name="T-Logic Demo", tagline="AI-Enabled Readiness Assessment", logo_path="static/TLogic_Logo4.png")
with open("test_output.pdf", "wb") as f:
    f.write(pdf_bytes)
print("Wrote test_output.pdf")
