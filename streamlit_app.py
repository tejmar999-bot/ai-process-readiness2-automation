# streamlit_app.py
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import io
import datetime
import os

# Optional PDF support
try:
    from fpdf import FPDF
    PDF_SUPPORTED = True
except Exception:
    PDF_SUPPORTED = False

# ---------- App constants & style ----------
APP_TITLE = "AI-Enabled Process Readiness"
COPYRIGHT = "© T-Logic Consulting LLP"
DISCLAIMER = (
    "This is a high-level representation based on subjective inputs and should not be interpreted "
    "as an actual readiness assessment without a thorough professional evaluation."
)

# Palette (light, trending colors)
PALETTE = {
    "dim1": "#FFD8B5",  # light orange
    "dim2": "#E8D2FF",  # violet
    "dim3": "#D7F2FF",  # light blue
    "dim4": "#FFD6E8",  # pinkish
    "dim5": "#FFF5C2",  # light yellow
    "dim6": "#E8FFDA",  # light green
}

DARK_BG = "#1f1f1f"
BURNT_ORANGE = "#d35a00"  # app name color
WHITE = "#FFFFFF"
DARK_GREY_TEXT = "#666"

# Questions: 6 dimensions x 3 questions each (18 total)
DIMENSION_TITLES = [
    "Process Clarity",
    "Data Availability",
    "Technology & Tools",
    "People & Skills",
    "Governance & Risk",
    "Pilot Readiness",
]

QUESTIONS = [
    # Dimension 1
    "Processes are well documented and standardized across teams.",
    "Key process metrics are consistently measured and reported.",
    "There is a clear process owner for the target processes.",
    # Dimension 2
    "Required process data exists in digital form for at least 3 months.",
    "Data quality is sufficient (accurate, complete, consistent).",
    "Data can be exported easily (APIs/CSV) for analysis.",
    # Dimension 3
    "There are tools/platforms that support automation or analytics.",
    "IT can provision environments or tools quickly for pilots.",
    "Integrations exist to extract process-relevant data.",
    # Dimension 4
    "Team members have basic analytics or automation skills.",
    "There is available time for staff to run a pilot.",
    "Leaders support training and skill development plans.",
    # Dimension 5
    "There are documented governance policies for data and AI usage.",
    "Risk assessment is performed for new automation initiatives.",
    "Legal/Compliance has been engaged for pilot scoping.",
    # Dimension 6
    "There is a clear high-value use case identified for a pilot.",
    "Success criteria and KPIs are defined for the pilot.",
    "Budget and resources are allocated to run the pilot.",
]

# scoring scale 1-5 (sliders)
MIN_SCORE = 1
MAX_SCORE = 5

# ---------- Helper functions ----------

def _inject_css():
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {DARK_BG};
            color: {WHITE};
        }}
        .title-row {{
            display:flex;
            justify-content:space-between;
            align-items:center;
            gap:20px;
        }}
        .app-title {{
            color: {BURNT_ORANGE};
            font-size:32px;
            font-weight:700;
        }}
        .section-box {{
            border-radius:8px;
            padding:18px;
            margin-bottom:12px;
        }}
        .question-text {{
            color: #000000;
            font-weight:600;
        }}
        .slider-label {{
            color: {DARK_GREY_TEXT};
        }}
        .progress-arrows {{
            display:flex;
            gap:6px;
            margin-bottom:18px;
            align-items:center;
        }}
        .arrow {{
            padding:8px 12px;
            border-radius:6px;
            color:#222;
            font-weight:700;
            min-width:40px;
            text-align:center;
        }}
        .step-info {{
            color: {WHITE};
            font-weight:600;
            margin-bottom:6px;
        }}
        .footer-note {{
            color: #bdbdbd;
            font-size:12px;
            margin-top:18px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

def init_state():
    if "page" not in st.session_state:
        st.session_state.page = 0  # 0 is home, 1-6 are dimension pages, 7 results
    if "answers" not in st.session_state:
        # list of 18 values default mid value
        st.session_state.answers = [3.0] * len(QUESTIONS)
    if "dimension_scores" not in st.session_state:
        st.session_state.dimension_scores = [0.0] * 6

def page_to_dimension(page_idx: int):
    # page 1 -> dimension index 0
    return page_idx - 1

def calculate_scores():
    # compute per-dimension average of its 3 questions
    dim_scores = []
    for d in range(6):
        start = d * 3
        vals = st.session_state.answers[start:start+3]
        avg = sum(vals) / len(vals)
        dim_scores.append(avg)
    st.session_state.dimension_scores = dim_scores
    overall = sum(dim_scores) / len(dim_scores)
    return dim_scores, overall

def render_progress_arrows(active_page:int):
    colors = list(PALETTE.values())
    arrow_html = "<div class='progress-arrows'>"
    for i in range(6):
        idx = i + 1
        color = colors[i]
        if idx == active_page:
            # filled with color and white text
            arrow_html += f"<div class='arrow' style='background:{color}; color:#000'>{idx}</div>"
        else:
            arrow_html += f"<div class='arrow' style='background:#ddd; opacity:0.25; color:#fff'>{idx}</div>"
    arrow_html += "</div>"
    st.markdown(arrow_html, unsafe_allow_html=True)

def render_home():
    st.markdown("<div class='title-row'>", unsafe_allow_html=True)
    st.markdown(f"<div class='app-title'>{APP_TITLE}</div>", unsafe_allow_html=True)
    logo_path = "static/T_Logic_Logo.png"
    if os.path.isfile(logo_path):
        st.image(logo_path, width=140)
    else:
        # placeholder small orange rect
        st.markdown(f"<div style='color:{BURNT_ORANGE}; font-weight:700'>T-LOGIC</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>")
    st.markdown("<div style='color: white; font-size:18px'>Quick self-assessment for process improvement leaders (6 dimensions, ~3 minutes)</div>", unsafe_allow_html=True)
    st.markdown("<br>")

    st.markdown("<div style='margin-top:18px'>", unsafe_allow_html=True)
    st.markdown("<button style='background:"+BURNT_ORANGE+"; color:#000; padding:10px 18px; border-radius:6px; font-weight:700;' onclick=\"window.location.href='#start'\">Start Assessment</button>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<br>")

    st.markdown(f"<div style='color:white'>{COPYRIGHT}</div>", unsafe_allow_html=True)
    st.markdown("<hr style='border-top:1px solid #333' />", unsafe_allow_html=True)

def render_dimension_page(page_idx:int):
    # page_idx in 1..6
    dim_index = page_to_dimension(page_idx)
    color_keys = list(PALETTE.keys())
    color = list(PALETTE.values())[dim_index]

    # header with step label
    st.markdown(f"<div class='step-info'>Step {page_idx} of 6 — {DIMENSION_TITLES[dim_index]}</div>", unsafe_allow_html=True)
    render_progress_arrows(page_idx)

    # three questions for this dimension
    start_q = dim_index * 3
    for i in range(3):
        q_idx = start_q + i
        q_num = q_idx + 1
        # question box with colored background (only question box has color)
        st.markdown(
            f"<div class='section-box' style='background:{color};'>"
            f"<div class='question-text'>{q_num}. {QUESTIONS[q_idx]}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
        # slider with darker grey label
        label = f"Rating (1 - {MIN_SCORE}, 5 - {MAX_SCORE})"
        val = st.slider(label, min_value=MIN_SCORE, max_value=MAX_SCORE, value=int(st.session_state.answers[q_idx]), key=f"q{q_idx}")
        st.session_state.answers[q_idx] = float(val)
        st.markdown("<br>", unsafe_allow_html=True)

    # Navigation buttons: Previous / Next or Results on final page
    cols = st.columns([1,1,4])
    with cols[0]:
        if st.button("Previous"):
            st.session_state.page = max(0, st.session_state.page - 1)
            st.experimental_rerun()
    with cols[1]:
        if page_idx < 6:
            if st.button("Next"):
                st.session_state.page = page_idx + 1
                st.experimental_rerun()
        else:
            # page 6 -> show Go to Results
            if st.button("Go to Results"):
                st.session_state.page = 7  # results
                st.experimental_rerun()

def render_results():
    st.markdown("<div class='step-info'>Results</div>", unsafe_allow_html=True)
    render_progress_arrows(0)  # show neutral progress

    # calculate scores
    dim_scores, overall = calculate_scores()
    # convert to 0-5 scale (they are already 1-5 averages) keep as is
    df = pd.DataFrame({
        "Dimension": DIMENSION_TITLES,
        "Score": dim_scores
    })

    # display numeric summary
    st.markdown(f"### Overall readiness: **{overall:.2f} / 5.0**")
    st.markdown("Per-dimension scores:")
    st.table(df.set_index("Dimension"))

    # Radar chart using plotly
    categories = DIMENSION_TITLES
    values = dim_scores
    # plotly radar requires closing the loop
    fig = go.Figure(
        data=[
            go.Scatterpolar(r=values + [values[0]], theta=categories + [categories[0]], fill='toself', name='Readiness')
        ],
        layout=go.Layout(
            polar=dict(radialaxis=dict(visible=True, range=[0,5])),
            showlegend=False,
            paper_bgcolor=DARK_BG,
            plot_bgcolor=DARK_BG,
            font=dict(color=WHITE)
        )
    )
    st.plotly_chart(fig, use_container_width=True)

    # Interpretation / recommendations
    st.markdown("### Recommendations")
    # simple recommendations based on thresholds
    for i, s in enumerate(dim_scores):
        if s >= 4.0:
            note = "Strong — ready to scale practices in this area."
        elif s >= 3.0:
            note = "Moderate — possible quick wins with focused work."
        else:
            note = "Low — prioritize for pilot preparation."
        st.markdown(f"**{DIMENSION_TITLES[i]}**: {s:.2f} / 5 — {note}")

    st.markdown("<br>")
    # Actionable next steps
    st.markdown("### Actionable Next Steps")
    steps = []
    if overall < 3.0:
        steps.append("- Start with a small, high-impact pilot and secure executive sponsorship.")
        steps.append("- Improve basic data availability and assign a process owner.")
    else:
        steps.append("- Run a 6-week pilot with clear KPIs and a cross-functional team.")
        steps.append("- Document results and plan scale-up for areas scoring above 3.5.")
    for s in steps:
        st.markdown(s)

    # Downloads: TXT and PDF
    def build_transcript_text():
        ts = datetime.datetime.utcnow().isoformat() + "Z"
        lines = [f"AI-Enabled Process Readiness — Results ({ts})", ""]
        lines.append(f"Overall readiness: {overall:.2f} / 5.0")
        for i, sc in enumerate(dim_scores):
            lines.append(f"{DIMENSION_TITLES[i]}: {sc:.2f} / 5")
        lines.append("")
        lines.append("Recommendations:")
        lines.extend(steps)
        return "\n".join(lines)

    transcript_text = build_transcript_text()
    st.download_button("Download results (TXT)", transcript_text, file_name="ai_readiness_results.txt", mime="text/plain")

    if PDF_SUPPORTED:
        # Unicode font optional support path
        font_path = None
        possible = [os.path.join(os.getcwd(), "fonts", "DejaVuSans.ttf"), os.path.join(os.getcwd(), "DejaVuSans.ttf")]
        for p in possible:
            if os.path.isfile(p):
                font_path = p
                break

        def make_pdf_bytes_unicode(text: str) -> bytes:
            pdf = FPDF()
            try:
                pdf.add_page()
                if font_path:
                    pdf.add_font("DejaVu", "", font_path, uni=True)
                    pdf.set_font("DejaVu", size=12)
                else:
                    pdf.set_font("Arial", size=12)
                pdf.set_auto_page_break(auto=True, margin=15)
                for line in text.split("\n"):
                    pdf.multi_cell(0, 7, line)
                bio = io.BytesIO()
                pdf.output(bio)
                return bio.getvalue()
            except Exception as e:
                # fall back to ascii-only
                import unicodedata
                normalized = unicodedata.normalize("NFKD", text)
                ascii_only = normalized.encode("ascii", "ignore").decode("ascii")
                pdf2 = FPDF()
                pdf2.add_page()
                pdf2.set_font("Arial", size=12)
                for line in ascii_only.split("\n"):
                    pdf2.multi_cell(0, 7, line)
                bio2 = io.BytesIO()
                pdf2.output(bio2)
                return bio2.getvalue()

        pdf_bytes = make_pdf_bytes_unicode(transcript_text)
        st.download_button("Download results (PDF)", pdf_bytes, file_name="ai_readiness_results.pdf", mime="application/pdf")
    else:
        st.info("PDF export not available. To enable it, add 'fpdf' to requirements.txt in your repo.")

    st.markdown(f"<div class='footer-note'>{DISCLAIMER}</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='color:#999'>{COPYRIGHT}</div>", unsafe_allow_html=True)

    # Back to top / restart
    if st.button("Start New Assessment"):
        st.session_state.answers = [3.0] * len(QUESTIONS)
        st.session_state.dimension_scores = [0.0] * 6
        st.session_state.page = 0
        # cross-version safe rerun
        rerun_fn = getattr(st, "experimental_rerun", None)
        if callable(rerun_fn):
            rerun_fn()
        else:
            st.success("Session cleared — please refresh the page to start a new assessment.")
            st.stop()

# ---------- App layout ----------
def main():
    _inject_css()
    init_state()

    # layout: two columns - left for progress/story and right for content
    # We'll keep single-column content for simplicity and consistency
    if st.session_state.page == 0:
        render_home()
        # anchor: clicking Start button earlier isn't actionable in Streamlit, so provide explicit button
        if st.button("Start Assessment"):
            st.session_state.page = 1
            rerun = getattr(st, "experimental_rerun", None)
            if callable(rerun):
                rerun()
            else:
                st.experimental_show = getattr(st, "experimental_show", None)
    elif 1 <= st.session_state.page <= 6:
        render_dimension_page(st.session_state.page)
    elif st.session_state.page == 7:
        render_results()
    else:
        # safety fallback
        st.session_state.page = 0
        st.experimental_rerun()

if __name__ == "__main__":
    main()
