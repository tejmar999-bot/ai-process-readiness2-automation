# app.py
import streamlit as st
from utils.pdf_generator import generate_pdf_report
import os

st.set_page_config(page_title="AI Process Readiness - T-Logic", layout="wide")

# Top header with logo (left) and title
col1, col2 = st.columns([1, 3])
with col1:
    logo_path = "attached_assets/TLogic_Logo6.png"
    if os.path.isfile(logo_path):
        st.image(logo_path, width=220)
with col2:
    st.markdown("<h1 style='margin-bottom:0px'>AI-Enabled Process Readiness</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #888'>Free 3-minute operational readiness assessment — private & fast</p>", unsafe_allow_html=True)

st.write("---")

# Simple mode toggle for mock/test
test_mode = st.checkbox("Use mock data (quick test)", value=True)

if test_mode:
    # Quick mock values for fast testing
    results = {
        "total": 21,
        "percentage": 70,
        "readiness_band": {"label": "Established", "description": "Good foundations; ready to scale."},
        "dimension_scores": [
            {"title": "Strategy", "description": "Strategy is defined", "score": 4.0},
            {"title": "People", "description": "People and skills available", "score": 3.5},
            {"title": "Technology", "description": "Core tech in place", "score": 4.0},
            {"title": "Process", "description": "Repeatable processes", "score": 3.5},
            {"title": "Data", "description": "Data quality improving", "score": 3.0},
            {"title": "Governance", "description": "Basic governance", "score": 3.0},
        ],
        "notes": "This is a mock report for testing the PDF layout and generation.",
        "recommendations": [
            "Prioritize data quality improvements in key pipelines.",
            "Define a measurable AI roadmap with pilot milestones."
        ],
        "subtitle": "Clarity across 6 readiness dimensions. Instant. Private. No sign-up."
    }

    st.info("Mock data loaded. Uncheck 'Use mock data' and fill the live form to generate real reports.")
    if st.button("Generate sample PDF"):
        pdf_bytes = generate_pdf_report(results, company_name="T-Logic Consulting", logo_path="attached_assets/TLogic_Logo6.png")
        st.success("PDF generated — ready to download.")
        st.download_button("Download Sample PDF", data=pdf_bytes, file_name="TLogic_AI_Readiness_Sample.pdf", mime="application/pdf")
else:
    st.header("Enter assessment answers")
    company_name = st.text_input("Company name (optional)")
    st.write("Enter dimension scores and descriptions:")

    dimension_scores = []
    for i in range(1, 7):
        st.subheader(f"Dimension {i}")
        title = st.text_input(f"Dimension {i} title", value=f"Dimension {i}", key=f"title_{i}")
        desc = st.text_area(f"Dimension {i} description", value="", key=f"desc_{i}")
        score = st.slider(f"Dimension {i} score (0-5)", 0.0, 5.0, 3.0, 0.5, key=f"score_{i}")
        dimension_scores.append({"title": title, "description": desc, "score": score})

    total = sum([d["score"] for d in dimension_scores])
    percentage = int((total / (5.0 * len(dimension_scores))) * 100)

    band_label = st.selectbox("Readiness band", ["Foundational", "Emerging", "Established", "Leading"])

    notes = st.text_area("Additional notes (optional)")

    if st.button("Generate PDF"):
        results = {
            "total": total,
            "percentage": percentage,
            "readiness_band": {"label": band_label},
            "dimension_scores": dimension_scores,
            "notes": notes,
            "recommendations": []
        }
        pdf_bytes = generate_pdf_report(results, company_name=company_name or "T-Logic Consulting", logo_path="attached_assets/TLogic_Logo6.png")
        st.success("PDF generated — ready to download.")
        st.download_button("Download PDF", data=pdf_bytes, file_name="AI_Readiness_Report.pdf", mime="application/pdf")
