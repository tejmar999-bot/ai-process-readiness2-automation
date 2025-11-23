# app.py
"""
Production-ready Streamlit app that preserves your original flow:
- Landing page (company + logo + user info note)
- One screen per dimension (3 questions each) with Back / Next navigation
- Results page that uses your compute_scores(...) from utils.scoring (unchanged)
- Generate PDF button wired to utils.pdf_generator.generate_pdf_report(...)
"""

import os
from io import BytesIO
from typing import Dict, Any

import streamlit as st
from PIL import Image

# Use your existing scoring, dimensions and pdf generator
from utils.scoring import compute_scores  # uses your existing logic; unchanged. :contentReference[oaicite:3]{index=3}
from data.dimensions import DIMENSIONS  # dimension/question definitions (titles, ids, colors). :contentReference[oaicite:4]{index=4}
from utils.pdf_generator import generate_pdf_report  # new production-ready PDF generator. :contentReference[oaicite:5]{index=5}

# Optional: DB save function if present (safe import)
try:
    from db.operations import save_assessment, ensure_tables_exist
    DB_AVAILABLE = True
except Exception:
    DB_AVAILABLE = False

# -----------------------
# App configuration
# -----------------------
st.set_page_config(page_title="AI Process Readiness — T-Logic",
                   layout="wide",
                   initial_sidebar_state="collapsed")

# Initialize session state
if "current_dimension" not in st.session_state:
    st.session_state.current_dimension = 0  # 0..5
if "answers" not in st.session_state:
    st.session_state.answers = {}  # question_id -> integer 1..5
if "company_name" not in st.session_state:
    st.session_state.company_name = ""
if "tagline" not in st.session_state:
    st.session_state.tagline = "AI-Enabled Process Readiness"
if "logo_path" not in st.session_state:
    st.session_state.logo_path = None
if "latest_pdf" not in st.session_state:
    st.session_state.latest_pdf = None
if "assessment_saved_id" not in st.session_state:
    st.session_state.assessment_saved_id = None

# Helper: save uploaded logo to attached_assets
def save_uploaded_logo(uploaded) -> str:
    folder = "attached_assets"
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, "user_logo.png")
    with open(path, "wb") as f:
        f.write(uploaded.getbuffer())
    return path

# -----------------------
# Layout: Header
# -----------------------
def render_header():
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f"<h1 style='color:#BF6A16;margin:0;'>AI-Enabled Process Readiness</h1>", unsafe_allow_html=True)
        st.markdown("<div style='color:#9CA3AF;margin-top:6px;'>Quick 3-question-per-dimension self-assessment — printable PDF report available.</div>", unsafe_allow_html=True)
    with col2:
        logo = None
        if st.session_state.logo_path and os.path.exists(st.session_state.logo_path):
            try:
                logo = Image.open(st.session_state.logo_path)
            except Exception:
                logo = None
        else:
            # fallback static
            if os.path.exists("static/TLogic_Logo4.png"):
                try:
                    logo = Image.open("static/TLogic_Logo4.png")
                except Exception:
                    logo = None
        if logo:
            st.image(logo, width=120)

render_header()
st.markdown("---")

# -----------------------
# Landing / Info Page
# -----------------------
if st.session_state.current_dimension == -1:
    # reserved (not used) — but kept for parity
    st.session_state.current_dimension = 0

if st.session_state.current_dimension == 0:
    st.header("Start assessment")
    st.session_state.company_name = st.text_input("Company name", value=st.session_state.company_name)
    st.session_state.tagline = st.text_input("Tagline (optional)", value=st.session_state.tagline)
    uploaded_logo = st.file_uploader("Upload a logo (optional). It will appear on the PDF header/footer.", type=["png", "jpg", "jpeg"])
    if uploaded_logo:
        st.session_state.logo_path = save_uploaded_logo(uploaded_logo)
        st.success("Logo uploaded.")
    st.markdown("Email is required only if you want to download the PDF report. You can complete the assessment without providing an email.")
    st.markdown("---")
    st.write("Click **Start** to go to the first dimension.")
    cols = st.columns([1, 1, 1])
    if cols[2].button("Start"):
        st.session_state.current_dimension = 1
        st.experimental_rerun()

# -----------------------
# Dimension pages (1..N)
# -----------------------
num_dimensions = len(DIMENSIONS)
if 1 <= st.session_state.current_dimension <= num_dimensions:
    idx = st.session_state.current_dimension - 1
    dim = DIMENSIONS[idx]
    # compact header for the dimension
    st.markdown(f"### {dim['title']}  —  {dim.get('what_it_measures', '')}")
    st.write(dim.get("description", ""))

    # Render questions (3 per dimension)
    questions = dim["questions"]
    cols = st.columns(3)
    for i, q in enumerate(questions):
        qid = q["id"]
        key = f"q_{qid}"
        # default to previously chosen or 3
        default = st.session_state.answers.get(qid, 3)
        with cols[i]:
            st.write(f"**{i+1}. {q['text']}**")
            val = st.radio("", options=[1,2,3,4,5], index=int(default)-1, horizontal=True, key=key)
            st.session_state.answers[qid] = int(val)

    # Navigation
    nav_col1, nav_col2, nav_col3 = st.columns([1,1,1])
    with nav_col1:
        if st.session_state.current_dimension > 1:
            if st.button("← Previous"):
                st.session_state.current_dimension -= 1
                st.experimental_rerun()
    with nav_col2:
        if st.button("Reset"):
            st.session_state.answers = {}
            st.session_state.current_dimension = 0
            st.session_state.latest_pdf = None
            st.experimental_rerun()
    with nav_col3:
        if st.session_state.current_dimension < num_dimensions:
            if st.button("Next →"):
                st.session_state.current_dimension += 1
                st.experimental_rerun()
        else:
            if st.button("Complete Assessment"):
                st.session_state.current_dimension = num_dimensions + 1
                st.experimental_rerun()

# -----------------------
# Results page
# -----------------------
if st.session_state.current_dimension == num_dimensions + 1:
    st.header("Results")
    # Use your existing compute_scores to ensure identical calculation. :contentReference[oaicite:6]{index=6}
    scores_data = compute_scores(st.session_state.answers)
    # scores_data expected: { 'dimension_scores': [...], 'total': x.x, 'percentage': y, 'readiness_band': {...} }
    dimension_scores_list = scores_data.get("dimension_scores", [])
    total = scores_data.get("total", 0.0)
    percentage = scores_data.get("percentage", 0)
    readiness = scores_data.get("readiness_band", {})

    # Display summary cards
    avg_score = round((total / max(1, num_dimensions)), 1)
    colA, colB, colC = st.columns(3)
    with colA:
        st.metric("Total score (out of 30)", f"{total}")
    with colB:
        st.metric("Average (per dimension)", f"{avg_score} / 5")
    with colC:
        band_label = readiness.get("label", "N/A")
        st.markdown(f"**Readiness level:** <span style='color:{readiness.get('color','#000')}; font-weight:700'>{band_label}</span>", unsafe_allow_html=True)
        st.caption(readiness.get("description",""))

    st.markdown("---")

    # Detailed per-dimension breakdown matching your DIMENSIONS structure (order preserved)
    st.subheader("Dimension scores")
    for i, score in enumerate(dimension_scores_list):
        d = DIMENSIONS[i]
        title = d["title"]
        color = d.get("color", "#BBBBBB")
        desc = d.get("description", "")
        # display with progress bar and 1-decimal score
        col_left, col_right = st.columns([4,1])
        with col_left:
            st.markdown(f"**{title}** — {desc}")
            pct = max(0.0, min(1.0, float(score) / 5.0))
            st.progress(pct)
        with col_right:
            st.markdown(f"**{score:.1f}/5**" if isinstance(score, (int, float)) else f"**{score}/5**")

    st.markdown("---")

    # Executive summary editable
    st.subheader("Executive Summary (optional)")
    exec_summary = st.text_area("Edit the executive summary for the PDF", height=120, key="exec_summary")

    # Recommendations: simple auto-generated (you can customize later)
    st.subheader("Suggested next steps")
    recs = []
    if avg_score < 2.5:
        recs = [
            "Focus on foundational process documentation and quick wins.",
            "Set ownership for core processes and capture baseline metrics.",
            "Run 1-2 focused pilot projects."
        ]
    elif avg_score < 3.5:
        recs = [
            "Improve data pipelines and increase data quality monitoring.",
            "Upskill one cross-functional team to build repeatable success.",
            "Prioritize automation for manual repetitive tasks."
        ]
    elif avg_score < 4.2:
        recs = [
            "Standardize model deployment and strengthen governance.",
            "Scale successful pilots into production with monitoring.",
            "Invest in lifecycle tooling and observability."
        ]
    else:
        recs = [
            "Publish internal best-practices and expand AI capabilities.",
            "Invest in advanced AI operations and continuous improvement.",
            "Consider a Centre of Excellence for AI."
        ]

    for r in recs:
        st.write("• " + r)

    # -----------------------
    # PDF generation (wired to your new generator). :contentReference[oaicite:7]{index=7}
    # Build payload expected by utils.pdf_generator.generate_pdf_report
    # -----------------------
    st.markdown("---")
    st.subheader("Generate PDF Report")
    company_name = st.session_state.company_name.strip() or "[Your Company]"
    tagline = st.session_state.tagline.strip() or "AI-Enabled Process Readiness"

    # Build dimension_scores dict (map DIMENSIONS order -> score)
    dimension_scores_dict = {}
    for i, d in enumerate(DIMENSIONS):
        name = d["title"]
        val = dimension_scores_list[i] if i < len(dimension_scores_list) else 0.0
        dimension_scores_dict[name] = float(val)

    payload = {
        "overall_score": avg_score,  # 0..5
        "readiness_band": readiness,
        "dimension_scores": dimension_scores_dict,
        "dimension_notes": {},  # leave empty for now
        "recommendations": recs,
        "industry_average": None,
        "subtitle": f"AI-Enabled Process Readiness for {company_name}",
        "notes": exec_summary or ""
    }

    if st.button("Generate PDF"):
        pdf_bytes = generate_pdf_report(results=payload, company_name=company_name, tagline=tagline, logo_path=st.session_state.logo_path)
        if pdf_bytes:
            st.session_state.latest_pdf = pdf_bytes
            st.success("PDF generated — use the Download button below.")
            # optionally save to DB
            if DB_AVAILABLE:
                try:
                    rec = save_assessment(company_name=company_name, scores_data=scores_data, answers=st.session_state.answers)
                    st.session_state.assessment_saved_id = getattr(rec, "id", None)
                except Exception as e:
                    st.warning(f"Saving assessment to DB failed: {e}")
        else:
            st.error("PDF generation failed. Check logs.")

    if st.session_state.latest_pdf:
        st.download_button("Download latest PDF", data=st.session_state.latest_pdf, file_name=f"{company_name.replace(' ','_')}_readiness_report.pdf", mime="application/pdf")

    st.markdown("---")
    if st.button("Restart assessment"):
        st.session_state.answers = {}
        st.session_state.current_dimension = 0
        st.session_state.latest_pdf = None
        st.experimental_rerun()

# -----------------------
# Side navigation: allow jumping between dimensions
# -----------------------
with st.sidebar:
    st.markdown("### Navigation")
    for i, d in enumerate(DIMENSIONS):
        if st.button(f"{i+1}. {d['title']}"):
            st.session_state.current_dimension = i + 1
            st.experimental_rerun()

# Render footer
st.markdown("<br><br>")
st.markdown(f"<div style='text-align:center;color:#9CA3AF;'>T-Logic Consulting Pvt. Ltd. • www.tlogic.consulting</div>", unsafe_allow_html=True)

