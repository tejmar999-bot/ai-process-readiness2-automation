# app.py
import streamlit as st
import os
from utils.pdf_generator import generate_pdf_report

st.set_page_config(page_title="T-Logic • AI Readiness", layout="wide")

col1, col2 = st.columns([1, 3])
with col1:
    logo_file = "attached_assets/TLogic_Logo6.png"
    if os.path.isfile(logo_file):
        st.image(logo_file, width=180)
with col2:
    st.markdown(
        "<h1 style='margin-bottom:0px'>AI-Enabled Readiness Assessment</h1>",
        unsafe_allow_html=True)
    st.markdown(
        "<p style='color:#9AA0A3;margin-top:2px'>Fast operational readiness scan across 6 dimensions</p>",
        unsafe_allow_html=True)

st.write("---")

# Quick test mode
test_mode = st.checkbox("Use mock data (fast test)", value=True)

if test_mode:
    st.info("Mock data loaded for quick PDF preview.")
    if st.button("Generate sample branded PDF"):
        results = {
            "total":
            21,
            "percentage":
            70,
            "readiness_band": {
                "label": "Established",
                "description": "Good foundation."
            },
            "dimension_scores": [
                {
                    "title": "Strategy",
                    "description": "Clear strategy",
                    "score": 4
                },
                {
                    "title": "People",
                    "description": "Skilled team",
                    "score": 3.5
                },
                {
                    "title": "Technology",
                    "description": "Platforms in place",
                    "score": 4
                },
                {
                    "title": "Process",
                    "description": "Repeatable processes",
                    "score": 3.5
                },
                {
                    "title": "Data",
                    "description": "Improving data quality",
                    "score": 3.0
                },
                {
                    "title": "Governance",
                    "description": "Basic governance",
                    "score": 3.0
                },
            ],
            "notes":
            "This is a mock report for layout testing.",
            "recommendations": [
                "Prioritize data pipeline reliability.",
                "Set measurable OKRs for first pilots."
            ],
            "subtitle":
            "Clarity across 6 readiness dimensions. Instant. Private."
        }
        pdf = generate_pdf_report(results,
                                  company_name="T-Logic Consulting",
                                  tagline="AI-Enabled Readiness Assessment",
                                  logo_path=logo_file)
        st.success("Sample PDF generated.")
        st.download_button("Download Branded PDF",
                           data=pdf,
                           file_name="TLogic_AI_Readiness_Sample.pdf",
                           mime="application/pdf")
else:
    st.write(
        "Live assessment form (not enabled in this demo). Use mock mode for quick testing."
    )
