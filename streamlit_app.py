import streamlit as st
import io
import datetime

# Optional: PDF generation via fpdf
try:
    from fpdf import FPDF
    PDF_SUPPORTED = True
except Exception:
    PDF_SUPPORTED = False

# Configure the page
st.set_page_config(page_title="AI-Enabled Process Readiness", page_icon="🤖", layout="wide")

st.title("AI-Enabled Process Readiness – Interactive Assessment")

st.markdown(
    """
    Use this tool to evaluate your organization's readiness for incorporating AI into business processes.
    Answer the questions below to get personalized recommendations — no API key required.
    """
)

# === Tone selector ===
tone_choice = st.selectbox(
    "Preferred tone for recommendations",
    options=["Consultant (business)", "Executive Coach (strategic)", "Friendly Advisor (approachable)"],
    index=0,
)

# Helper: canned offline recommendation generator
def generate_canned_reply(user_text: str, tone: str) -> str:
    lower = (user_text or "").lower()
    recs = []
    if any(k in lower for k in ["data", "dataset", "histor", "record"]):
        recs.append("Ensure process data is cleaned and at least 3 months of historical data is available for initial pilots.")
    else:
        recs.append("Start by digitizing the most critical process steps and collecting basic metrics.")
    if any(k in lower for k in ["train", "skill", "people", "team"]):
        recs.append("Run a short training for process owners and analytics champions to create a shared understanding.")
    else:
        recs.append("Assign a process owner and identify one analytics SME to support the pilot.")
    if any(k in lower for k in ["api", "tool", "system", "erp", "integrat"]):
        recs.append("Validate that your tech stack can extract required data via APIs or exports for the pilot.")
    else:
        recs.append("Prototype the pilot using spreadsheets or lightweight tools before investing in integrations.")

    if tone.startswith("Executive"):
        header = "Executive summary:\n"
        body = "\n".join([f"- {r}" for r in recs[:3]])
        footer = "\nSuggested KPI: time-to-resolution and pilot ROI estimate."
        return header + body + footer
    elif tone.startswith("Friendly"):
        header = "Quick friendly suggestions:\n"
        body = "\n".join([f"• {r}" for r in recs[:3]])
        footer = "\nTry one small experiment this month and gather your first metrics."
        return header + body + footer
    else:
        header = "Actionable recommendations:\n"
        body = "\n".join([f"1) {r}" for r in recs[:3]])
        footer = "\nNext step: design a 6-week pilot with clear success criteria."
        return header + body + footer

# Input fields for user results
with st.form("assessment_form"):
    user_summary = st.text_area("Paste your assessment summary or describe your results:")
    submitted = st.form_submit_button("Analyze")

# Chat UI setup
if 'messages' not in st.session_state:
    st.session_state.messages = []

if submitted and user_summary:
    st.session_state.messages.append({"role": "user", "content": user_summary})
    canned = generate_canned_reply(user_summary, tone_choice)
    st.session_state.messages.append({"role": "assistant", "content": canned})

# Display conversation
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message("user").markdown(msg["content"])
    else:
        st.chat_message("assistant").markdown(msg["content"])

# --- Export transcript ---
if st.session_state.messages:
    def build_transcript(messages):
        lines = []
        ts = datetime.datetime.utcnow().isoformat() + 'Z'
        lines.append(f"AI-Enabled Process Readiness — Assessment Results ({ts})")
        lines.append("")
        for m in messages:
            role = 'You' if m.get('role') == 'user' else 'Assistant'
            lines.append(f"[{role}]\n{m.get('content')}\n")
        return "\n".join(lines)

    transcript_text = build_transcript(st.session_state.messages)

    st.download_button(
        label="Download transcript (TXT)",
        data=transcript_text,
        file_name="ai_readiness_transcript.txt",
        mime="text/plain",
    )

import unicodedata

def _sanitize_for_pdf(text: str) -> str:
    """
    Normalize and strip non-ASCII characters for FPDF (latin-1) compatibility.
    We attempt to preserve readability by removing accents and unsupported symbols.
    """
    if not isinstance(text, str):
        return ''
    # Normalize accents, etc.
    normalized = unicodedata.normalize('NFKD', text)
    # Encode to ASCII bytes (drop unsupported chars), then decode back to str
    ascii_only = normalized.encode('ascii', 'ignore').decode('ascii')
    return ascii_only

def make_pdf_bytes(text: str) -> bytes:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # sanitize entire text to avoid unicode encode issues in FPDF
    clean_text = _sanitize_for_pdf(text)

    # write using multi_cell which will wrap long lines
    for line in clean_text.split('\n'):
        pdf.multi_cell(0, 7, line)

    bio = io.BytesIO()
    pdf.output(bio)
    return bio.getvalue()

# Optional reset button
if st.button("Start New Assessment"):
    st.session_state.messages = []
    st.experimental_rerun()

st.markdown(
    """---
    **Note:** This tool provides general guidance based on your inputs and does not replace a professional evaluation.\n
    © T-Logic Consulting LLP
    """
)
