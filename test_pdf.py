# test_pdf.py
from utils.pdf_generator import generate_pdf_report

def main():
    sample = {
        "overall_score": 3.4,
        "readiness_band": {"label": "Reliable", "description": "Consistent and dependable."},
        "dimension_scores": {
            "Process Maturity": 3.2,
            "Technology Infrastructure": 3.4,
            "Data Readiness": 3.1,
            "People & Culture": 3.6,
            "Leadership & Alignment": 3.8,
            "Governance & Risk": 3.2,
        },
        "dimension_notes": {
            # optional per-dimension one-line notes
            "Process Maturity": "Processes are documented in key areas but some steps are manual.",
        },
        "recommendations": [
            "Improve data quality to enable reliable analytics.",
            "Establish clear process owners for critical flows."
        ],
        "industry_average": None,
        "notes": "Short executive summary: This test report was generated for layout verification."
    }

    pdf = generate_pdf_report(
        results=sample,
        company_name="Sample Company Ltd.",
        tagline="AI-Enabled Process Readiness",
        logo_path="static/TLogic_Logo4.png",   # adjust path if your logo is elsewhere
        industry_baseline=[3.2, 3.4, 3.1, 3.6, 3.8, 3.2]  # your provided baseline
    )
    if pdf:
        with open("test_output.pdf", "wb") as f:
            f.write(pdf)
        print("Wrote test_output.pdf")
    else:
        print("PDF generation failed")

if __name__ == "__main__":
    main()
