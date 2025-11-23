# app.py — wizard flow (landing -> 6 dimension pages -> summary -> PDF)
import os
from typing import Dict, List

import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

from utils.pdf_generator import generate_pdf_report  # must exist in utils/

# -------------------------
# Config / constants
# -------------------------
DIMENSIONS = {
    "Process Maturity": [
        "Are core processes documented and repeatable?",
        "Is there a regular review / improvement cycle for priority processes?",
        "Are process metrics tracked and used for decisions?",
    ],
    "Technology Infrastructure": [
        "Is the technology stack modern and well-supported?",
        "Are systems integrated to allow data flow where needed?",
        "Is security and access control consistently applied?",
    ],
    "Data Readiness": [
        "Is necessary data available and discoverable?",
        "Is data quality measured and improving?",
        "Are pipelines/ETL for core data reliable?",
    ],
    "People & Culture": [
        "Do staff have baseline data/AI skills for their roles?",
        "Is the organization open to data-driven change?",
        "Are training and upskilling programs in place?",
    ],
    "Leadership & Alignment": [
        "Does leadership sponsor AI/process improvement initiatives?",
        "Are objectives for AI tied to measurable business outcomes?",
        "Is there dedicated budget or allocated resources?",
    ],
    "Governance & Risk": [
        "Are policies in place to govern AI and data use?",
        "Is change management applied when processes change?",
        "Are compliance/privacy risks identified and monitored?",
    ],
}

PASTEL_COLORS = {
    "Process Maturity": "#F4B4B4",
    "Technology Infrastructure": "#FCD0A4",
    "Data Readiness": "#FFF4B9",
    "People & Culture": "#B9F0C9",
    "Leadership & Alignment": "#B3E5FC",
    "Governance & Risk": "#D7BDE2",
}

READINESS_ORDERED = [
    ("Foundational", "First critical steps being laid."),
    ("Emerging", "Progress being made."),
    ("Reliable", "Consistent and dependable."),
    ("Exceptional", "Best-in-class process performance."),
]


# -------------------------
# Helpers
# -------------------------
def safe_avg(values: List[float]) -> float:
    return float(sum(values)) / len(values) if values else 0.0


def compute_dim_scores(responses: Dict[str, List[float]]) -> Dict[str, float]:
    return {d: round(safe_avg(vals), 2) for d, vals in responses.items()}


def overall_score_from_dims(dim_scores: Dict[str, float]) -> float:
    return round(safe_avg(list(dim_scores.values())), 2) if dim_scores else 0.0


def readiness_from_score(score: float) -> Dict[str, str]:
    if score < 2.5:
        return {"label": "Foundational", "desc": READINESS_ORDERED[0][1]}
    if score < 3.5:
        return {"label": "Emerging", "desc": READINESS_ORDERED[1][1]}
    if score < 4.2:
        return {"label": "Reliable", "desc": READINESS_ORDERED[2][1]}
    return {"label": "Exceptional", "desc": READINESS_ORDERED[3][1]}


def radar_image(dim_scores: Dict[str, float], size=4.2):
    # returns matplotlib figure (png) object in memory (we'll display in Streamlit)
    labels = list(dim_scores.keys())
    values = [float(dim_scores[k]) for k in labels]
    values += values[:1]
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]

    fig = plt.figure(figsize=(size, size))
    ax = fig.add_subplot(111, polar=True)
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylim(0, 5)
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_yticklabels(["1", "2", "3", "4", "5"], fontsize=8)

    ax.plot(angles, values, linewidth=2, color="#333333")
    ax.fill(angles, values, color="#6EC6FF", alpha=0.25)

    fig.tight_layout()
    return fig


# -------------------------
# Streamlit UI (wizard)
# -------------------------
st.set_page_config(page_title="AI Readiness — T-Logic", layout="wide")
st.title("AI-Enabled Process Readiness")

if "step" not in st.session_state:
    st.session_state.step = 0  # 0=landing, 1..n = dimension pages, last=summary
if "responses" not in st.session_state:
    # prepopulate with neutral 3.0 answers
    st.session_state.responses = {
        d: [3.0] * len(qs)
        for d, qs in DIMENSIONS.items()
    }
if "company" not in st.session_state:
    st.session_state.company = ""
if "tagline" not in st.session_state:
    st.session_state.tagline = "AI-Enabled Readiness Assessment"
if "logo_path" not in st.session_state:
    st.session_state.logo_path = None
if "exec_summary" not in st.session_state:
    st.session_state.exec_summary = ""
if "latest_pdf" not in st.session_state:
    st.session_state.latest_pdf = None


def go_next():
    st.session_state.step += 1


def go_back():
    if st.session_state.step > 0:
        st.session_state.step -= 1


# Landing page
if st.session_state.step == 0:
    colL, colR = st.columns([2, 1])
    with colL:
        st.header("Welcome")
        st.write(
            "Complete a quick 3-question-per-dimension assessment. "
            "At the end you'll see a summary, recommendations, and can generate a branded PDF report."
        )
        st.session_state.company = st.text_input(
            "Company name", value=st.session_state.company)
        st.session_state.tagline = st.text_input(
            "Tagline (optional)", value=st.session_state.tagline)
        st.write(
            "Note: email is required only to download the PDF (not for the assessment)."
        )
        st.checkbox("Use mock data (fast test)",
                    key="use_mock",
                    help="Populate with example scores for a quick preview.")

        uploaded = st.file_uploader("Upload a logo (optional). PNG / JPG",
                                    type=["png", "jpg", "jpeg"])
        if uploaded:
            os.makedirs("attached_assets", exist_ok=True)
            path = os.path.join("attached_assets", "user_logo.png")
            with open(path, "wb") as f:
                f.write(uploaded.getbuffer())
            st.session_state.logo_path = path
            st.success(
                "Logo uploaded and saved to attached_assets/user_logo.png")
        else:
            # fallback check static or attached_assets
            if os.path.exists("attached_assets/TLogic_Logo6.png"):
                st.session_state.logo_path = "attached_assets/TLogic_Logo6.png"
            elif os.path.exists("static/TLogic_Logo4.png"):
                st.session_state.logo_path = "static/TLogic_Logo4.png"

    with colR:
        st.subheader("Pastel dimension colors")
        for k, v in PASTEL_COLORS.items():
            st.markdown(f"<span style='color:{v}'>■</span> {k}",
                        unsafe_allow_html=True)

    if st.button("Start assessment"):
        # if mock requested, set some example data
        if st.session_state.get("use_mock", False):
            st.session_state.responses = {
                "Process Maturity": [3.0, 3.0, 3.0],
                "Technology Infrastructure": [3.5, 3.0, 3.0],
                "Data Readiness": [3.0, 3.0, 2.5],
                "People & Culture": [3.5, 3.0, 3.0],
                "Leadership & Alignment": [3.0, 3.0, 2.5],
                "Governance & Risk": [2.5, 3.0, 3.0],
            }
        st.session_state.step = 1
        st.experimental_rerun()

# Dimension pages
elif 1 <= st.session_state.step <= len(DIMENSIONS):
    idx = st.session_state.step - 1
    dimension = list(DIMENSIONS.keys())[idx]
    st.header(f"{dimension} — ({idx+1} of {len(DIMENSIONS)})")
    st.write("Please rate each question (1 = low / 5 = high).")

    cols = st.columns(3)
    questions = DIMENSIONS[dimension]
    for i, q in enumerate(questions):
        key = f"{dimension}_{i}"
        default = st.session_state.responses.get(dimension,
                                                 [3.0] * len(questions))[i]
        # Ensure step increments don't collide with other keys; keys are unique per question
        val = cols[i].slider(q,
                             min_value=1.0,
                             max_value=5.0,
                             value=float(default),
                             step=0.5,
                             key=key)
        # Save back to session state
        if dimension not in st.session_state.responses:
            st.session_state.responses[dimension] = [3.0] * len(questions)
        st.session_state.responses[dimension][i] = float(val)

    nav_col1, nav_col2, nav_col3 = st.columns([1, 1, 2])
    with nav_col1:
        if st.button("Back"):
            go_back()
            st.experimental_rerun()
    with nav_col2:
        if st.button("Next"):
            go_next()
            st.experimental_rerun()
    with nav_col3:
        st.write("")  # spacer
        st.info(
            "You can navigate with Back / Next. Your answers are stored in this session."
        )

# Summary page
else:
    st.header("Summary & Recommendations")
    dim_scores = compute_dim_scores(st.session_state.responses)
    overall = overall_score_from_dims(dim_scores)
    band = readiness_from_score(overall)

    st.subheader(f"Overall score: {overall:.2f} / 5 — {band['label']}")
    st.write(band["desc"])

    # Radar chart
    st.markdown("### Radar chart")
    fig = radar_image(dim_scores)
    st.pyplot(fig)

    st.markdown("### Dimension scores")
    for d, v in dim_scores.items():
        pct = max(0.0, min(v / 5.0, 1.0))
        st.write(f"**{d}** — {v:.1f} / 5")
        st.progress(pct)

    st.markdown("### Executive summary (editable)")
    st.session_state.exec_summary = st.text_area(
        "Write a short executive summary (optional)",
        value=st.session_state.exec_summary,
        height=120)

    # Generate recommendations (simple dynamic rules)
    st.markdown("### Recommendations (sample)")
    recs = []
    if overall < 2.5:
        recs = [
            "Prioritize foundational process documentation and quick wins.",
            "Establish a small cross-functional pilot to prove value.",
            "Create a short-term roadmap and assign ownership."
        ]
    elif overall < 3.5:
        recs = [
            "Scale successful pilots and improve data quality pipelines.",
            "Invest in training for priority teams.",
            "Define measurable business outcomes for next initiatives."
        ]
    elif overall < 4.2:
        recs = [
            "Standardize best practices across business units.",
            "Strengthen governance and monitoring frameworks.",
            "Prepare to scale models and embed into operations."
        ]
    else:
        recs = [
            "Share best practices externally; consider productizing capabilities.",
            "Invest in continuous improvement and advanced use cases.",
            "Consider thought leadership and advanced compliance frameworks."
        ]

    for r in recs:
        st.write("• " + r)

    # PDF generation
    st.markdown("---")
    st.subheader("Generate branded PDF report")
    company_name = st.session_state.company.strip() or "[Your Company]"
    tagline = st.session_state.tagline.strip(
    ) or "AI-Enabled Readiness Assessment"

    if st.button("Generate PDF"):
        payload = {
            "overall_score": overall,
            "readiness_band": {
                "label": band["label"],
                "description": band["desc"]
            },
            "dimension_scores": dim_scores,
            "notes": st.session_state.exec_summary,
            "subtitle": f"AI-Enabled Process Readiness for {company_name}",
        }
        pdf_bytes = generate_pdf_report(
            results=payload,
            company_name=company_name,
            tagline=tagline,
            logo_path=st.session_state.logo_path,
        )
        if isinstance(pdf_bytes, (bytes, bytearray)):
            st.session_state.latest_pdf = pdf_bytes
            st.success("PDF generated. Use the download button to save it.")
        else:
            st.error(
                "PDF generation returned no content; check server logs and utils/pdf_generator.py"
            )

    if st.session_state.latest_pdf:
        st.download_button(
            label="Download PDF",
            data=st.session_state.latest_pdf,
            file_name=f"{company_name.replace(' ', '_')}_readiness_report.pdf",
            mime="application/pdf",
        )

    st.markdown("---")
    if st.button("Restart assessment"):
        st.session_state.step = 0
        st.experimental_rerun()
