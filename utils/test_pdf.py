from utils.pdf_generator import generate_pdf_report

mock_results = {
    "overall_score": 22.5,
    "dimension_scores": {
        "Process Maturity": 3.5,
        "Technology Infrastructure": 3.8,
        "Data Readiness": 2.9,
        "People & Culture": 3.7,
        "Leadership & Alignment": 4.2,
        "Governance & Risk": 3.1,
    },
    "summary": "This is a sample executive summary...",
    "recommendations": {
        "Process Maturity": ["Improve documentation", "Increase automation"],
        "People & Culture": ["Upskill workforce", "Adopt change mgmt routines"],
    }
}

pdf_bytes = generate_pdf_report(mock_results, logo_path="/static/TLogic_Logo4.png")

with open("test_output.pdf", "wb") as f:
    f.write(pdf_bytes)

print("Generated test_output.pdf")