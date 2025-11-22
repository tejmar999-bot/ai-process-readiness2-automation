# run_test_pdf.py
# Quick test runner for the ReportLab PDF generator

import json
from utils.pdf_generator import generate_pdf_report

results = {
    "total": 18,
    "percentage": 60,
    "readiness_band": {"label": "Emerging", "description": "Some capabilities exist."},
    "dimension_scores": [
        {"title": "Strategy", "description": "Strategy exists", "score": 3},
        {"title": "People", "description": "People OK", "score": 3},
        {"title": "Technology", "description": "Some tools", "score": 4},
        {"title": "Process", "description": "Ad-hoc processes", "score": 2},
        {"title": "Data", "description": "Data improving", "score": 3},
        {"title": "Governance", "description": "Basic governance", "score": 3},
    ],
    "notes": "Local test notes",
    "recommendations": ["Test rec 1", "Test rec 2"],
    "subtitle": "Local test subtitle"
}

# Path to logo stored inside attached_assets
logo_path = "attached_assets/TLogic_Logo6.png"

print("Generating PDF…")

pdf_bytes = generate_pdf_report(
    results,
    company_name="T-Logic Consulting",
    logo_path=logo_path
)

with open("test_report.pdf", "wb") as f:
    f.write(pdf_bytes)

print("Done! Wrote test_report.pdf")