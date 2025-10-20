# tests/test_pdf_generator.py
import io
from utils.pdf_generator import generate_pdf_report

def make_sample_results():
    return {
        "overall_score": 3.75,
        "dimension_scores": [4.0, 3.5, 3.0, 4.5, 3.0, 3.5],
        "dimensions": [
            "Process Clarity",
            "Data Availability",
            "Technology & Tools",
            "People & Skills",
            "Governance & Risk",
            "Pilot Readiness",
        ],
        "recommendations": [
            "Start a 6-week pilot.",
            "Assign process owners.",
        ],
    }

def test_generate_pdf_bytes_not_empty():
    results = make_sample_results()
    pdf_bytes = generate_pdf_report(results)
    assert isinstance(pdf_bytes, (bytes, bytearray))
    assert len(pdf_bytes) > 100  # not empty

def test_generate_pdf_header():
    results = make_sample_results()
    pdf_bytes = generate_pdf_report(results)
    # PDF files start with '%PDF'
    assert pdf_bytes[:4] == b"%PDF"
