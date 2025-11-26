import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go
import pandas as pd
import base64
import os
from io import BytesIO
from PIL import Image
from utils.scoring import compute_scores
from data.dimensions import DIMENSIONS, BRIGHT_PALETTE, get_all_questions
from utils.pdf_generator import generate_pdf_report
from utils.html_report_generator import generate_html_report
from data.benchmarks import get_benchmark_comparison, get_all_benchmarks, get_benchmark_data
from db.operations import (ensure_tables_exist, save_assessment)
from utils.gmail_sender import send_assistance_request_email, send_feedback_email, send_user_registration_email, send_verification_code_email, send_pdf_download_notification, generate_verification_code
from utils.ai_chat import get_chat_response, get_assessment_insights

def scroll_to_top():
    """Inject JS snippet that scrolls the window to the top."""
    components.html(
        """
        <script>
        window.scrollTo({ top: 0, behavior: 'smooth' });
        </script>
        """,
        height=0,
    )
# --- Compact, page-specific header for Dimension pages ---


def render_dimension_header(title: str, description: str, idx: int, total: int = 6):
    """
    Render a compact header for dimension pages:
      - title placed left, with description immediately to the right (same font sizes)
      - dimension label placed in upper-right corner, at larger font size
      - header height reduced by ~30% compared to original (compact spacing)
    Call this at the top of each Dimension page render.
    """
    # CSS - safe scoped class names so it doesn't affect other parts of the app.
    css = """
    <style>
    /* Container: compact header */
    .tlogic-dim-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 8px 12px;            /* compact vertical padding */
        gap: 16px;
        height: 56px;                 /* compact height: adjust if needed (30% smaller than ~80) */
        box-sizing: border-box;
        background: transparent;
        margin-bottom: 6px;           /* give slight space below header */
    }

    /* Left block: title + description inline */
    .tlogic-dim-left {
        display: flex;
        align-items: baseline;
        gap: 12px;
        flex: 1 1 auto;
        min-width: 0;                 /* allow text truncation instead of layout break */
    }

    .tlogic-dim-title {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        font-size: 1.35rem;           /* same visual weight as current - tweak if needed */
        font-weight: 700;
        color: #ffffff;               /* main heading color (keeps existing white) */
        margin: 0;
        line-height: 1;
    }

    .tlogic-dim-desc {
        color: #D1D5DB;               /* slightly lighter for description */
        font-size: 1.0rem;            /* same size/style as before (user requested) */
        margin: 0;
        line-height: 1;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    /* Right block: dimension label */
    .tlogic-dim-label {
        flex: 0 0 auto;
        text-align: right;
        font-size: 2.0rem;            /* double the prior size (increase visually) */
        font-weight: 700;
        color: #ffffff;
        margin-left: 12px;
        line-height: 1;
    }

    /* Responsive: if small width, allow description to truncate */
    @media (max-width: 880px) {
        .tlogic-dim-desc {
            display: none;           /* hide long descriptions on tiny screens - keeps layout compact */
        }
        .tlogic-dim-title {
            font-size: 1.2rem;
        }
        .tlogic-dim-label {
            font-size: 1.4rem;
        }
    }
    </style>
    """

    # HTML markup for the header
    html = f"""
    {css}
    <div class="tlogic-dim-header" role="banner" aria-label="Dimension header">
      <div class="tlogic-dim-left">
        <div class="tlogic-dim-title">{title} -</div>
        <div class="tlogic-dim-desc">{description}</div>
      </div>
      <div class="tlogic-dim-label">Dimension {idx} of {total}</div>
    </div>
    """

    # Render as safe HTML so the header layout appears precisely as intended.
    st.markdown(html, unsafe_allow_html=True)


# Page configuration
st.set_page_config(page_title="AI Process Readiness Assessment",
                   page_icon="🤖",
                   layout="wide",
                   initial_sidebar_state="collapsed")

# Custom CSS for styling
st.markdown("""
<style>
.main-header {
    color: #BF6A16;
    font-size: 2.5rem;
    font-weight: bold;
    margin-bottom: 0.5rem;
}
.sub-header {
    color: #D1D5DB;
    font-size: 1.15rem;
    font-weight: 500;
    margin-bottom: 2rem;
    letter-spacing: 0.01em;
}
.dimension-card {
    background-color: #374151;
    padding: 1.5rem;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
    border-left: 4px solid #BF6A16;
}
.question-text {
    font-size: 1.1rem;
    margin-bottom: 1rem;
    color: #F3F4F6;
    scroll-margin-top: 250px;
}
.score-card {
    background-color: #374151;
    padding: 1.5rem;
    border-radius: 0.5rem;
    text-align: center;
    margin: 0.5rem;
}
.readiness-band {
    font-size: 1.5rem;
    font-weight: bold;
    margin: 0.5rem 0;
}
.dimension-score {
    font-size: 1.1rem;
    margin: 0.25rem 0;
}
/* Black text on orange/primary buttons */
button[kind="primary"] {
    color: #000000 !important;
}
button[kind="primary"] p {
    color: #000000 !important;
}
/* White text for Continue button on home page only */
button.continue-home-btn {
    color: #FFFFFF !important;
}
button.continue-home-btn p {
    color: #FFFFFF !important;
}
/* Softer orange buttons for Results page */
.softer-orange-btn {
    display: inline-block;
    background-color: #F59E0B;
    color: #000000;
    padding: 0.5rem 1.5rem;
    border: none;
    border-radius: 0.375rem;
    font-weight: 500;
    font-size: 1rem;
    cursor: pointer;
    transition: background-color 0.2s;
    width: 100%;
    text-align: center;
    box-sizing: border-box;
}
.softer-orange-btn:hover {
    background-color: #F97316;
}
.softer-orange-btn:active {
    background-color: #EA580C;
}
</style>
""",
            unsafe_allow_html=True)


def image_to_base64(image, max_height=None):
    """Convert PIL Image to base64 string, optionally resizing to max height"""
    if max_height:
        # Calculate new dimensions maintaining aspect ratio
        aspect_ratio = image.width / image.height
        new_height = max_height
        new_width = int(new_height * aspect_ratio)
        image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str


def initialize_session_state():
    """Initialize session state variables"""
    # Initialize database
    if 'db_initialized' not in st.session_state:
        st.session_state.db_initialized = ensure_tables_exist()

    if 'answers' not in st.session_state:
        st.session_state.answers = {}
    if 'current_dimension' not in st.session_state:
        st.session_state.current_dimension = 0
    if 'assessment_complete' not in st.session_state:
        st.session_state.assessment_complete = False
    if 'current_assessment_id' not in st.session_state:
        st.session_state.current_assessment_id = None
    if 'company_logo' not in st.session_state:
        # Load default T-Logic logo
        try:
            default_logo = Image.open('static/TLogic_Logo4.png')
            st.session_state.company_logo = default_logo
        except:
            st.session_state.company_logo = None
    if 'company_name' not in st.session_state:
        st.session_state.company_name = "T-Logic"
    if 'primary_color' not in st.session_state:
        st.session_state.primary_color = "#BF6A16"
    if 'user_name' not in st.session_state:
        st.session_state.user_name = ""
    if 'user_email' not in st.session_state:
        st.session_state.user_email = ""
    if 'user_title' not in st.session_state:
        st.session_state.user_title = ""
    if 'user_company' not in st.session_state:
        st.session_state.user_company = ""
    if 'user_phone' not in st.session_state:
        st.session_state.user_phone = ""
    if 'user_location' not in st.session_state:
        st.session_state.user_location = ""
    if 'user_info_collected' not in st.session_state:
        st.session_state.user_info_collected = False
    if 'should_scroll_to_top' not in st.session_state:
        st.session_state.should_scroll_to_top = False
    if 'feedback_submitted' not in st.session_state:
        st.session_state.feedback_submitted = False
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
    if 'ai_insights_generated' not in st.session_state:
        st.session_state.ai_insights_generated = False
    if 'ai_insights_text' not in st.session_state:
        st.session_state.ai_insights_text = ""
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "assessment"
    if 'standalone_chat_messages' not in st.session_state:
        st.session_state.standalone_chat_messages = []


def render_header():
    """Render the main header with logo and branding"""
    col1, col2 = st.columns([4, 1])

    with col1:
        st.markdown(
            f'<div class="main-header" style="color: {st.session_state.primary_color};">AI-Enabled Process Readiness</div>',
            unsafe_allow_html=True)
        st.markdown(
            '<div class="sub-header">Quick self-assessment for process improvement leaders (6 dimensions, ~ 10 minutes)</div>',
            unsafe_allow_html=True)

    with col2:
        if st.session_state.company_logo is not None:
            # Logo sized at 105px (same as Results page)
            st.markdown(f"""
                <div style="text-align: right; height: 105px; overflow: visible; margin-left: auto; display: flex; align-items: center; justify-content: flex-end;">
                    <img src="data:image/png;base64,{image_to_base64(st.session_state.company_logo, max_height=105)}" 
                         style="height: 105px; width: auto; display: block; border: none; background: transparent;" />
                </div>
                """,
                        unsafe_allow_html=True)
        else:
            st.markdown(
                f"<div style='text-align: center; margin-top: 0.5rem;'><strong>{st.session_state.company_name}</strong></div>",
                unsafe_allow_html=True)


def render_footer():
    """Render copyright footer at the bottom of the page"""
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 1rem 2rem; color: #9CA3AF; font-size: 0.9rem; border-top: 1px solid #374151; margin-top: 2rem;">
            <div style="text-align: center; flex: 1;">
                © T-Logic Training & Consulting Pvt. Ltd.
            </div>
            <div style="text-align: right;">
                www.tlogicconsulting.com
            </div>
        </div>
        """,
                unsafe_allow_html=True)


def render_branding_sidebar():
    """Render branding customization in sidebar"""
    with st.sidebar:
        st.markdown("### 🎨 Branding")

        # Company name input
        company_name = st.text_input("Company Name",
                                     value=st.session_state.company_name,
                                     key="company_name_input")
        if company_name != st.session_state.company_name:
            st.session_state.company_name = company_name
            st.rerun()

        # Logo upload
        uploaded_file = st.file_uploader(
            "Upload Company Logo",
            type=['png', 'jpg', 'jpeg'],
            help="Upload your company logo (PNG, JPG)")

        if uploaded_file is not None:
            try:
                image = Image.open(uploaded_file)
                st.session_state.company_logo = image
                st.success("Logo uploaded successfully!")
            except Exception as e:
                st.error(f"Error uploading logo: {str(e)}")

        # Option to remove logo
        if st.session_state.company_logo is not None:
            if st.button("Remove Logo"):
                st.session_state.company_logo = None
                st.rerun()

        # Primary color picker
        primary_color = st.color_picker(
            "Primary Brand Color",
            value=st.session_state.primary_color,
            help="Choose your brand's primary color")
        if primary_color != st.session_state.primary_color:
            st.session_state.primary_color = primary_color
            st.rerun()

        st.markdown("---")
        
with st.container():
    st.markdown(
        """
        <style>
        div[data-testid="stVerticalBlock"] {
            max-height: 80vh;
            overflow-y: auto;
            padding-right: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def render_progress_bar():
    """Render progress bar with arrow indicators - Sticky header"""
    current_dim = st.session_state.current_dimension
    dimension_color = DIMENSIONS[current_dim]['color']
    bright_color = BRIGHT_PALETTE[current_dim]
    dimension = DIMENSIONS[current_dim]

    # Add timestamp to force re-rendering
    import time
    timestamp = int(time.time() * 1000)

    # Build arrows HTML with fixed width and text wrapping
    arrows_html = f'<div id="progress-anchor" data-render="{timestamp}" style="display: flex; align-items: center; margin-bottom: 0.5rem; gap: 0; max-width: 100%;">'

    for i, dim in enumerate(DIMENSIONS):
        # Determine if this arrow should be lit up
        is_active = i <= current_dim
        arrow_color = dim['color'] if is_active else '#374151'
        text_color = '#000000' if is_active else '#6B7280'
        margin_left = '-15px' if i > 0 else '0'
        z_index = len(DIMENSIONS) - i

        # Fixed width arrows with text wrapping - single line to avoid rendering issues
        arrow_html = f'<div style="position: relative; background-color: {arrow_color}; height: 60px; width: 120px; min-width: 100px; display: flex; align-items: center; justify-content: center; clip-path: polygon(0 0, calc(100% - 15px) 0, 100% 50%, calc(100% - 15px) 100%, 0 100%, 15px 50%); margin-left: {margin_left}; z-index: {z_index};"><span style="color: {text_color}; font-size: 0.85rem; font-weight: 600; text-align: center; padding: 0 8px; line-height: 1.2; word-wrap: break-word; overflow-wrap: break-word; max-width: 104px;">{dim["title"]}</span></div>'
        arrows_html += arrow_html

    arrows_html += '</div>'

    # Use Streamlit container with custom CSS for sticky positioning
    st.markdown(f"""
        <style>
        /* Hide Streamlit header on dimension pages for clean sticky header */
        [data-testid="stHeader"] {{
            display: none !important;
        }}
        /* Use fixed positioning to truly freeze header at viewport top */
        .sticky-header-container {{
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            right: 0 !important;
            width: 100% !important;
            z-index: 9999 !important;
            background-color: #1F2937 !important;
            padding: 1rem 1rem 0.75rem 1rem !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3) !important;
        }}
        /* Add spacer after sticky header - reduced height */
        .header-spacer {{
            height: 200px !important;
            width: 100% !important;
        }}
        /* Container for title/description and dimension label */
        .header-content-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 0.5rem;
            gap: 1rem;
        }}
        .title-description {{
            flex: 1;
            text-align: left;
        }}
        .dimension-label {{
            flex: 0 0 auto;
            text-align: right;
        }}
        </style>
        <div class="sticky-header-container">
            <div style="height: 4px; background-color: {dimension_color}; margin-bottom: 0.5rem;"></div>
            {arrows_html}
            <div class="header-content-row">
                <div class="title-description">
                    <span style="color: {bright_color}; font-size: 2rem; font-weight: 700;">{dimension["title"]}</span>
                    <span style="color: #D1D5DB; font-size: 1.05rem; font-style: italic;"> - {dimension["what_it_measures"]}</span>
                </div>
                <div class="dimension-label">
                    <span style="color: #9CA3AF; font-size: 1.1rem; font-weight: 600;">Dimension {current_dim + 1} of {len(DIMENSIONS)}</span>
                </div>
            </div>
        </div>
        <div class="header-spacer"></div>
        """,
                unsafe_allow_html=True)


def render_dimension_questions(dimension_idx):
    """Render questions for a specific dimension"""
    scroll_to_top()
    
    dimension = DIMENSIONS[dimension_idx]

    # --- Dimension page helper: ALWAYS scroll to top when entering dimension page ---
    components.html("""
<script>
(function() {
  var parentDoc = window.parent.document;
  var parentWin = window.parent;
  
  // FAIL-PROOF scroll-to-top: Ensures user ALWAYS lands at question 1
  function scrollToTop() {
    try {
      // 1. Reset parent window scroll
      try { parentWin.scrollTo(0, 0); } catch (e) {}
      
      // 2. Reset document scrolling element
      var doc = parentDoc.scrollingElement || parentDoc.documentElement;
      if (doc) {
        try { doc.scrollTo({ top: 0, behavior: 'auto' }); } catch (e) { doc.scrollTop = 0; }
      }
      
      // 3. Reset main section scroll
      var main = parentDoc.querySelector('section.main') || parentDoc.querySelector('main');
      if (main) {
        try { main.scrollTo({ top: 0, behavior: 'auto' }); } catch (e) { main.scrollTop = 0; }
      }
      
      // 4. Find ALL elements with scrollTop > 0 and reset them
      var allElems = parentDoc.getElementsByTagName('*');
      for (var i = 0; i < allElems.length; i++) {
        var elem = allElems[i];
        if (elem.scrollTop && elem.scrollTop > 0) {
          try { elem.scrollTo({ top: 0, behavior: 'auto' }); } catch (e) { elem.scrollTop = 0; }
        }
      }
    } catch (e) {
      try { parentWin.scrollTo(0,0); } catch (e2) {}
    }
  }

  // Execute immediately
  scrollToTop();

  // Run multiple times with delays to catch async renders
  setTimeout(scrollToTop, 50);
  setTimeout(scrollToTop, 100);
  setTimeout(scrollToTop, 200);
  setTimeout(scrollToTop, 300);
  setTimeout(scrollToTop, 500);
  setTimeout(scrollToTop, 800);

  // Run after load event
  window.addEventListener('load', function(){ setTimeout(scrollToTop, 40); }, false);
  
  // Monitor DOM changes and scroll to top when content loads
  var moDebounceTimer = null;
  var mo = new MutationObserver(function(muts) {
    if (moDebounceTimer) clearTimeout(moDebounceTimer);
    moDebounceTimer = setTimeout(scrollToTop, 60);
  });
  mo.observe(document.body, { childList: true, subtree: true });
})();
</script>
""", height=8)

    # Inject CSS to compress spacing between questions
    components.html("""
    <style>
    /* Ultra-aggressive compression for question containers */
    div[data-testid="column"] > div:has(.question-text) {
        margin: -0.75rem 0 -0.85rem 0 !important;
        padding: 0 !important;
    }
    .question-text {
        margin: 0 0 0 0 !important;
        padding: 0 !important;
        line-height: 1.2 !important;
    }
    /* Compress radio button spacing */
    div[data-testid="column"] > div:has([role="radiogroup"]) {
        margin: -0.7rem 0 -0.6rem 0 !important;
        padding: 0 !important;
    }
    /* Compress dividers */
    hr {
        margin: 0.08rem 0 !important;
        padding: 0 !important;
        height: 1px !important;
    }
    /* Remove extra padding from Streamlit containers */
    div[data-testid="column"] > div {
        gap: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    </style>
    """, height=0)

    # Initialize scroll trigger if not exists
    if 'scroll_to_question' not in st.session_state:
        st.session_state.scroll_to_question = None

    def on_answer_change(question_id, question_idx):
        """Callback when a question is answered"""
        # Only trigger scroll if not the last question
        if question_idx < len(dimension['questions']) - 1:
            st.session_state.scroll_to_question = question_idx + 1

    for i, question in enumerate(dimension['questions']):
        question_id = f"q_{question['id']}"

        # Create unique anchor for each question
        st.markdown(
            f'<div id="question-{i}" style="color: {dimension["color"]}; margin-bottom: -0.3rem;">{i+1}. {question["text"]}</div>',
            unsafe_allow_html=True)

        # Get current answer or default
        current_answer = st.session_state.answers.get(question['id'], 3)

        # Use question-specific answer choices if available, otherwise use dimension scoring labels
        answer_choices = question.get(
            'answer_choices',
            dimension.get('scoring_labels', {
                1: "1",
                2: "2",
                3: "3",
                4: "4",
                5: "5"
            }))

        # Create rating scale with question-specific labels with on_change callback
        rating = st.radio(
            "Rating",
            options=[1, 2, 3, 4, 5],
            format_func=lambda x: f"{x} - {answer_choices[x]}",
            key=question_id,
            index=current_answer - 1,  # Convert to 0-indexed
            horizontal=True,
            on_change=on_answer_change,
            args=(question['id'], i),
            label_visibility="collapsed")

        st.session_state.answers[question['id']] = rating
        st.markdown('<div style="margin: -0.4rem 0 -0.3rem 0;"><hr style="margin: 0.15rem 0;"></hr></div>', unsafe_allow_html=True)

    # Execute auto-scroll script only if scroll is triggered for a specific question
    if st.session_state.scroll_to_question is not None:
        target_question_idx = st.session_state.scroll_to_question
        components.html(f"""
            <script>
                (function() {{
                    var mainSection = window.parent.document.querySelector('section.main');
                    var nextQuestion = window.parent.document.getElementById('question-{target_question_idx}');
                    
                    if (nextQuestion && mainSection) {{
                        setTimeout(function() {{
                            var elementPosition = nextQuestion.offsetTop;
                            var stickyHeader = window.parent.document.querySelector('.sticky-header-container');
                            var stickyHeight = stickyHeader ? stickyHeader.offsetHeight : 200;
                            var offsetPosition = elementPosition - stickyHeight - 20;
                            mainSection.scrollTo({{
                                top: offsetPosition,
                                behavior: 'smooth'
                            }});
                        }}, 200);
                    }}
                }})();
            </script>
            """,
                        height=0)
        # Clear the flag after scrolling
        st.session_state.scroll_to_question = None

    # 🔁 Reliable scroll reset for every dimension page
    components.html("""
        <script>
        (function() {
            const main = window.document.querySelector('section.main') || window.document.scrollingElement;
            if (main) {
                main.scrollTo({ top: 0, behavior: 'auto' });
            } else {
                window.scrollTo(0, 0);
            }
        })();
        </script>
        """, height=0)


def render_navigation_buttons():
    """Render navigation buttons"""
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.session_state.current_dimension > 0:
            if st.button("← Previous", type="secondary"):
                st.session_state.current_dimension -= 1
                st.session_state.should_scroll_to_top = True
                st.session_state.scroll_to_question = None  # Clear question scroll when changing dimensions
                st.rerun()

    with col2:
        if st.button("Reset Assessment", type="secondary"):
            st.session_state.answers = {}
            st.session_state.current_dimension = 0
            st.session_state.assessment_complete = False
            st.session_state.user_info_collected = False
            st.session_state.user_name = ""
            st.session_state.user_email = ""
            st.session_state.user_title = ""
            st.session_state.user_company = ""
            st.session_state.user_phone = ""
            st.session_state.user_location = ""
            st.rerun()

    with col3:
        if st.session_state.current_dimension < len(DIMENSIONS) - 1:
            if st.button("Next →", type="primary"):
                st.session_state.current_dimension += 1
                st.session_state.should_scroll_to_top = True
                st.session_state.scroll_to_question = None  # Clear question scroll when changing dimensions
                st.rerun()
        else:
            if st.button("Complete Assessment", type="primary"):
                # Calculate scores
                scores_data = compute_scores(st.session_state.answers)

                # Save to database
                try:
                    assessment = save_assessment(
                        company_name=st.session_state.company_name,
                        scores_data=scores_data,
                        answers=st.session_state.answers,
                        primary_color=st.session_state.primary_color,
                        user_name=st.session_state.user_name or "",
                        user_email=st.session_state.user_email or "")
                    st.session_state.current_assessment_id = assessment.id
                except Exception as e:
                    st.error(f"Error saving assessment: {str(e)}")

                st.session_state.assessment_complete = True
                st.session_state.should_scroll_to_top = True  # Scroll to top to show results
                st.rerun()


def create_dimension_breakdown_chart(dimension_scores):
    """Create horizontal bar chart for dimension scores with percentages"""
    # Reverse the order so Process Maturity is at top and Governance & Risk is at bottom
    dimension_scores_reversed = list(reversed(dimension_scores))
    
    categories = [score['title'] for score in dimension_scores_reversed]
    values = [score['score'] for score in dimension_scores_reversed]
    percentages = [(score['score'] / 5) * 100 for score in dimension_scores_reversed]
    colors = [score['color'] for score in dimension_scores_reversed]

    # Create text labels with score and percentage in bold, positioned inside bars when possible
    text_labels = [f"<b>{val:.1f}/5 ({pct:.0f}%)</b>" for val, pct in zip(values, percentages)]
    text_positions = []
    
    # Position text inside bar if there's enough space, otherwise outside
    for val in values:
        if val > 2.5:
            text_positions.append('inside')
        else:
            text_positions.append('outside')

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            y=categories,
            x=values,
            orientation='h',
            marker=dict(color=colors),
            text=text_labels,
            textposition=text_positions,
            textfont=dict(size=12, color=['#000000' if pos == 'inside' else '#E5E7EB' for pos in text_positions]),
            hovertemplate='<b>%{y}</b><br>Score: %{x:.1f}/5<extra></extra>',
            showlegend=False
        )
    )

    fig.update_layout(
        xaxis=dict(
            range=[0, 5],
            tickfont=dict(color='#9CA3AF', size=11),
            gridcolor='rgba(255,255,255,0.1)',
            showgrid=True,
            title='Score'
        ),
        yaxis=dict(
            tickfont=dict(color='#E5E7EB', size=14),
            categoryorder='array',
            categoryarray=categories
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#E5E7EB'),
        height=450,
        margin=dict(l=200, r=150, t=40, b=40)
    )

    return fig


def render_results_dashboard():
    """Render the results dashboard"""
    # Calculate scores
    scores_data = compute_scores(st.session_state.answers)
    dimension_scores_raw = scores_data['dimension_scores']
    total_score = scores_data['total']
    percentage = scores_data['percentage']
    readiness_band = scores_data['readiness_band']

    # Format dimension scores for display (combine with dimension info)
    dimension_scores = []
    for i, score in enumerate(dimension_scores_raw):
        dimension_scores.append({
            'id': DIMENSIONS[i]['id'],
            'title': DIMENSIONS[i]['title'],
            'score': score,
            'color': DIMENSIONS[i]['color'],
            'description': DIMENSIONS[i]['description']
        })

    # Update scores_data with formatted dimension scores for benchmark comparison
    scores_data['dimension_scores'] = dimension_scores

    primary_color = st.session_state.primary_color

    # Header with logo (same layout as home page)
    col1, col2 = st.columns([4, 1])

    with col1:
        st.markdown(
            f'<div id="assessment-results-header" class="main-header" style="color: {primary_color};">Assessment Results</div>',
            unsafe_allow_html=True)

    with col2:
        if st.session_state.company_logo is not None:
            # Logo sized at 105px (50% larger than previous 70px)
            st.markdown(f"""
                <div style="text-align: right; height: 105px; overflow: visible; margin-left: auto; display: flex; align-items: center; justify-content: flex-end;">
                    <img src="data:image/png;base64,{image_to_base64(st.session_state.company_logo, max_height=105)}" 
                         style="height: 105px; width: auto; display: block; border: none; background: transparent;" />
                </div>
                """,
                        unsafe_allow_html=True)

    # Custom CSS for Results page scrollbars
    st.markdown("""
        <style>
        /* Hide all scrollbars except the main page scrollbar */
        .stDataFrame, 
        .stDataFrame > div,
        .element-container,
        .row-widget,
        [data-testid="stVerticalBlock"],
        [data-testid="stHorizontalBlock"],
        div[data-testid="column"],
        .stMarkdown,
        .stPlotlyChart {
            overflow: visible !important;
            scrollbar-width: none !important;
            -ms-overflow-style: none !important;
        }
        
        .stDataFrame::-webkit-scrollbar,
        .stDataFrame > div::-webkit-scrollbar,
        .element-container::-webkit-scrollbar,
        .row-widget::-webkit-scrollbar,
        [data-testid="stVerticalBlock"]::-webkit-scrollbar,
        [data-testid="stHorizontalBlock"]::-webkit-scrollbar,
        div[data-testid="column"]::-webkit-scrollbar,
        .stMarkdown::-webkit-scrollbar,
        .stPlotlyChart::-webkit-scrollbar {
            display: none !important;
        }
        
        /* Make the main page scrollbar more visible */
        section.main::-webkit-scrollbar {
            width: 14px !important;
        }
        
        section.main::-webkit-scrollbar-track {
            background: rgba(255, 255, 255, 0.1) !important;
            border-radius: 7px !important;
        }
        
        section.main::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.4) !important;
            border-radius: 7px !important;
            border: 2px solid rgba(0, 0, 0, 0.2) !important;
        }
        
        section.main::-webkit-scrollbar-thumb:hover {
            background: rgba(255, 255, 255, 0.6) !important;
        }
        
        /* For Firefox */
        section.main {
            scrollbar-width: auto !important;
            scrollbar-color: rgba(255, 255, 255, 0.4) rgba(255, 255, 255, 0.1) !important;
        }
        </style>
        """, unsafe_allow_html=True)
    
    # FAIL-PROOF scroll to top when Results page loads
    components.html("""
<script>
(function() {
  var parentDoc = window.parent.document;
  var parentWin = window.parent;
  
  function scrollToTop() {
    try {
      // 1. Reset parent window scroll
      try { parentWin.scrollTo(0, 0); } catch (e) {}
      
      // 2. Reset document scrolling element
      var doc = parentDoc.scrollingElement || parentDoc.documentElement;
      if (doc) {
        try { doc.scrollTo({ top: 0, behavior: 'auto' }); } catch (e) { doc.scrollTop = 0; }
      }
      
      // 3. Reset main section scroll
      var main = parentDoc.querySelector('section.main') || parentDoc.querySelector('main');
      if (main) {
        try { main.scrollTo({ top: 0, behavior: 'auto' }); } catch (e) { main.scrollTop = 0; }
      }
      
      // 4. Find ALL elements with scrollTop > 0 and reset them
      var allElems = parentDoc.getElementsByTagName('*');
      for (var i = 0; i < allElems.length; i++) {
        var elem = allElems[i];
        if (elem.scrollTop && elem.scrollTop > 0) {
          try { elem.scrollTo({ top: 0, behavior: 'auto' }); } catch (e) { elem.scrollTop = 0; }
        }
      }
    } catch (e) {
      try { parentWin.scrollTo(0,0); } catch (e2) {}
    }
  }

  // Execute immediately and repeatedly with MORE attempts for results page
  scrollToTop();

  // Run many times with delays - very aggressive for results page
  setTimeout(scrollToTop, 50);
  setTimeout(scrollToTop, 100);
  setTimeout(scrollToTop, 150);
  setTimeout(scrollToTop, 200);
  setTimeout(scrollToTop, 300);
  setTimeout(scrollToTop, 400);
  setTimeout(scrollToTop, 500);
  setTimeout(scrollToTop, 600);
  setTimeout(scrollToTop, 800);
  setTimeout(scrollToTop, 1000);
  setTimeout(scrollToTop, 1200);
  setTimeout(scrollToTop, 1500);
  setTimeout(scrollToTop, 2000);

  // Run after load event multiple times
  window.addEventListener('load', function(){ 
    setTimeout(scrollToTop, 40);
    setTimeout(scrollToTop, 100);
    setTimeout(scrollToTop, 300);
    setTimeout(scrollToTop, 500);
  }, false);
  
  // Monitor DOM changes and scroll to top when content loads
  var moDebounceTimer = null;
  var scrollCount = 0;
  var mo = new MutationObserver(function(muts) {
    if (moDebounceTimer) clearTimeout(moDebounceTimer);
    moDebounceTimer = setTimeout(function() {
      scrollToTop();
      scrollCount++;
      // Keep scrolling aggressively for first 30 mutations
      if (scrollCount < 30) {
        setTimeout(scrollToTop, 100);
      }
    }, 60);
  });
  mo.observe(document.body, { childList: true, subtree: true });
})();
</script>
        """, height=0)


    # Overall score cards
    col1, col2, col3 = st.columns(3)

    primary_color = st.session_state.primary_color

    with col1:
        st.markdown(f"""
        <div class="score-card">
            <h3 style="color: {primary_color};">Total Score</h3>
            <div style="font-size: 2rem; font-weight: bold;">{total_score}/30</div>
            <div style="font-size: 2rem; font-weight: bold; color: #9CA3AF;">({percentage}%)</div>
        </div>
        """,
                    unsafe_allow_html=True)

    with col2:
        band_color = readiness_band['color']
        st.markdown(f"""
        <div class="score-card">
            <h3 style="color: {primary_color};">Readiness Level</h3>
            <div class="readiness-band" style="color: {band_color};">{readiness_band['label']}</div>
        </div>
        """,
                    unsafe_allow_html=True)

    with col3:
        avg_score = round(total_score / 6, 1)
        st.markdown(f"""
        <div class="score-card">
            <h3 style="color: {primary_color};">Average Score</h3>
            <div style="font-size: 2rem; font-weight: bold;">{avg_score}/5</div>
        </div>
        """,
                    unsafe_allow_html=True)

    # Scoring Model Table
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        f'<h3 style="color: {primary_color}; text-align: center; margin-bottom: 1rem;">📊 Scoring Model</h3>',
        unsafe_allow_html=True)

    # Define scoring model data
    scoring_model = [{
        "range": "0-10",
        "level": "🟥 Foundational",
        "meaning": "First critical steps being laid",
        "min": 0,
        "max": 10
    }, {
        "range": "11-17",
        "level": "🟨 Emerging",
        "meaning": "Meaningful progress being made",
        "min": 11,
        "max": 17
    }, {
        "range": "18-24",
        "level": "🟦 Dependable",
        "meaning":
        "Mostly consistent and reliable processes",
        "min": 18,
        "max": 24
    }, {
        "range": "25-30",
        "level": "🟩 Exceptional",
        "meaning":
        "Best-in-class process performance",
        "min": 25,
        "max": 30
    }]

    # Create table with clean, properly aligned cells
    # Map emoji colors to their hex equivalents for CSS squares
    color_map = {
        "🟥 Foundational": ("#DC2626", "Foundational"),
        "🟨 Emerging": ("#EAB308", "Emerging"),
        "🟦 Dependable": ("#42A5F5", "Dependable"),
        "🟩 Exceptional": ("#16A34A", "Exceptional")
    }

    # Build table rows
    table_rows = ""
    for row in scoring_model:
        is_current = row['min'] <= total_score <= row['max']
        bg_color = '#1F2937' if is_current else '#111827'
        box_shadow = f'box-shadow: inset 0 0 0 2px {primary_color};' if is_current else ''
        font_weight = 'bold' if is_current else 'normal'

        color_hex, level_text = color_map[row["level"]]

        table_rows += f'<tr style="background-color: {bg_color};"><td style="padding: 1rem; text-align: center; border: 1px solid #4B5563; {box_shadow} font-weight: {font_weight}; vertical-align: middle;">{row["range"]}</td><td style="padding: 1rem; text-align: center; border: 1px solid #4B5563; {box_shadow} font-weight: {font_weight}; vertical-align: middle;"><span style="display: inline-block; width: 10px; height: 10px; margin-right: 6px; vertical-align: baseline; position: relative; top: 1px; background-color: {color_hex};"></span>{level_text}</td><td style="padding: 1rem; text-align: left; border: 1px solid #4B5563; {box_shadow} font-weight: {font_weight}; vertical-align: middle;">{row["meaning"]}</td></tr>'

    # Complete table HTML
    table_html = f'<table style="width: 100%; border-collapse: collapse; margin-bottom: 2rem;"><thead><tr style="background-color: #374151;"><th style="padding: 1rem; text-align: center; border: 1px solid #4B5563; vertical-align: middle;">Score Range</th><th style="padding: 1rem; text-align: center; border: 1px solid #4B5563; vertical-align: middle;">Readiness Level</th><th style="padding: 1rem; text-align: left; border: 1px solid #4B5563; vertical-align: middle;">Meaning</th></tr></thead><tbody>{table_rows}</tbody></table>'

    st.markdown(table_html, unsafe_allow_html=True)

    # Add "See Recommended Actions" button at bottom center of Scoring Model
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; margin-top: 1rem; margin-bottom: 2rem;">
            <a href="#recommended-actions" style="text-decoration: none;">
                <button style="background-color: #ADD8E6; color: #000000; padding: 0.75rem 2rem; border: none; border-radius: 0.5rem; font-size: 1rem; font-weight: bold; cursor: pointer; transition: opacity 0.2s;">
                    See Recommended Actions
                </button>
            </a>
        </div>
        """,
                    unsafe_allow_html=True)

    # Dimension Breakdown Chart
    st.markdown("### Dimension Breakdown")
    fig = create_dimension_breakdown_chart(dimension_scores)
    st.plotly_chart(fig, use_container_width=True)

    # Benchmark Comparison Section
    st.markdown("---")
    st.markdown("### 📊 Industry Benchmark Comparison", unsafe_allow_html=True)

    # Benchmark selector
    col1, col2 = st.columns([2, 3])

    with col1:
        all_benchmarks = get_all_benchmarks()
        default_idx = all_benchmarks.index(
            'Moving Average Benchmark') if 'Moving Average Benchmark' in all_benchmarks else 0
        benchmark_name = st.selectbox("Compare against:",
                                      options=all_benchmarks,
                                      index=default_idx)

    with col2:
        benchmark_info = get_benchmark_data(benchmark_name)
        st.info(benchmark_info['description'])

    # Get comparison data
    comparison = get_benchmark_comparison(scores_data, benchmark_name)

    # Comparison summary
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="score-card">
            <h4 style="color: {primary_color};">Your Score</h4>
            <div style="font-size: 1.5rem; font-weight: bold;">{comparison['your_total']}/30</div>
        </div>
        """,
                    unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="score-card">
            <h4 style="color: {primary_color};">Benchmark Score</h4>
            <div style="font-size: 1.5rem; font-weight: bold;">{comparison['benchmark_total']}/30</div>
        </div>
        """,
                    unsafe_allow_html=True)

    with col3:
        diff = comparison['total_difference']
        diff_color = '#16A34A' if diff >= 0 else '#E11D48'
        diff_symbol = '↑' if diff >= 0 else '↓'
        diff_text = 'Above' if diff >= 0 else 'Below'

        st.markdown(f"""
        <div class="score-card">
            <h4 style="color: {primary_color};">Difference</h4>
            <div style="font-size: 1.5rem; font-weight: bold; color: {diff_color};">
                {diff_symbol} {abs(diff):.1f} ({diff_text})
            </div>
        </div>
        """,
                    unsafe_allow_html=True)

    # Dimension-by-dimension comparison
    st.markdown("#### Dimension Comparison")

    # Create comparison chart
    dimension_names = [d['title'] for d in comparison['dimensions']]
    your_scores_list = [d['your_score'] for d in comparison['dimensions']]
    benchmark_scores_list = [
        d['benchmark_score'] for d in comparison['dimensions']
    ]

    fig_comparison = go.Figure()

    # Add your scores with text labels
    fig_comparison.add_trace(
        go.Bar(name='Your Scores',
               x=dimension_names,
               y=your_scores_list,
               marker_color=primary_color,
               text=[f'{score:.1f}' for score in your_scores_list],
               textposition='outside'))

    # Add benchmark scores with text labels
    fig_comparison.add_trace(
        go.Bar(name='Average of All Submissions',
               x=dimension_names,
               y=benchmark_scores_list,
               marker_color='#6B7280',
               text=[f'{score:.1f}' for score in benchmark_scores_list],
               textposition='outside'))

    fig_comparison.update_layout(barmode='group',
                                 plot_bgcolor='rgba(0,0,0,0)',
                                 paper_bgcolor='rgba(0,0,0,0)',
                                 font=dict(color='white'),
                                 yaxis=dict(title='Score',
                                            range=[0, 5.5],
                                            gridcolor='rgba(255,255,255,0.2)'),
                                 xaxis=dict(gridcolor='rgba(255,255,255,0.2)'),
                                 legend=dict(orientation="h",
                                             yanchor="bottom",
                                             y=1.02,
                                             xanchor="right",
                                             x=1),
                                 height=400)

    st.plotly_chart(fig_comparison, use_container_width=True)

    # Detailed comparison table
    st.markdown("#### Detailed Comparison")

    comparison_data = []
    for dim in comparison['dimensions']:
        diff = dim['difference']
        status = '✅' if diff >= 0 else '⚠️'
        comparison_data.append({
            'Dimension': dim['title'],
            'Your Score': f"{dim['your_score']}/5",
            'Benchmark': f"{dim['benchmark_score']:.1f}/5",
            'Difference': f"{diff:+.1f}",
            'Status': status
        })

    df_comparison = pd.DataFrame(comparison_data)
    st.dataframe(df_comparison, use_container_width=True, hide_index=True)

    # Recommended Actions Section
    st.markdown("---")
    st.markdown(
        f'<h3 id="recommended-actions" style="color: {primary_color}; text-align: center; margin-top: 2rem;">🎯 Recommended Actions*</h3>',
        unsafe_allow_html=True)
    st.markdown(
        '<p style="text-align: center; color: #9CA3AF; margin-bottom: 1.5rem; font-size: 1.1rem;">*Based on your assessment, here are holistic insights and specific recommendations to accelerate your AI readiness journey. This assessment provides a high-level representation based on subjective inputs and should not be interpreted as definitive readiness without a thorough professional evaluation.</p>',
        unsafe_allow_html=True)

    # Analyze each dimension holistically
    dimension_analyses = []

    for dim_idx, dimension in enumerate(DIMENSIONS):
        # Calculate dimension average score
        dim_scores = []
        for question in dimension['questions']:
            score = st.session_state.answers.get(question['id'], 3)
            dim_scores.append(score)

        avg_score = sum(dim_scores) / len(dim_scores) if dim_scores else 0

        # Count strengths (4-5) and weaknesses (1-3)
        strengths = [s for s in dim_scores if s >= 4]
        weaknesses = [s for s in dim_scores if s <= 3]

        dimension_analyses.append({
            'dimension': dimension,
            'avg_score': avg_score,
            'strengths_count': len(strengths),
            'weaknesses_count': len(weaknesses),
            'total_questions': len(dim_scores)
        })

    # Generate holistic recommendations for each dimension
    for analysis in dimension_analyses:
        dimension = analysis['dimension']
        avg_score = analysis['avg_score']
        strengths_count = analysis['strengths_count']
        weaknesses_count = analysis['weaknesses_count']
        total = analysis['total_questions']

        # Determine insight based on score distribution
        if avg_score >= 4.0:
            insight = f"🌟 **Strong Foundation:** Your {dimension['title'].lower()} shows excellent maturity with {strengths_count}/{total} areas rated highly. This dimension is a key strength that can serve as a foundation for AI implementation."
        elif avg_score >= 3.0:
            insight = f"✅ **Solid Progress:** Your {dimension['title'].lower()} demonstrates good progress with {strengths_count} strong area(s) and {weaknesses_count} area(s) needing attention. Building on your strengths while addressing gaps will accelerate readiness."
        else:
            insight = f"📈 **Growth Opportunity:** Your {dimension['title'].lower()} presents a significant opportunity for improvement. With focused attention on {weaknesses_count} key area(s), you can build the foundation needed for successful AI adoption."

        # Dimension-specific recommendations
        recommendations_map = {
            'process': [
                "Document and standardize critical business processes with clear workflows and performance metrics",
                "Implement regular process monitoring and variation analysis to identify optimization opportunities",
                "Establish a continuous improvement culture with data-driven decision making",
                "Create process maps that highlight where AI could deliver the most impact"
            ],
            'data': [
                "Digitize manual data collection processes and eliminate paper-based workflows",
                "Implement data quality frameworks including cleaning, validation, and integration protocols",
                "Build historical data repositories with proper governance and accessibility controls",
                "Ensure data is structured and labeled appropriately for AI model training",
                "Address any data silos by creating unified data access layers"
            ],
            'tech': [
                "Develop API-first infrastructure to enable seamless AI integration",
                "Invest in secure cloud or hybrid systems with scalability in mind",
                "Establish AI experimentation platforms or sandboxes for safe testing",
                "Ensure robust cybersecurity measures are in place before AI deployment",
                "Evaluate and select AI/ML platforms aligned with your use cases"
            ],
            'people': [
                "Launch AI literacy and awareness programs across all organizational levels",
                "Provide hands-on training in data-driven decision making and AI tools",
                "Identify and empower AI champions who can drive adoption within teams",
                "Create cross-functional teams to bridge technical and business expertise",
                "Develop clear career paths that reward AI skill development"
            ],
            'leadership': [
                "Integrate AI into strategic planning with clear business objectives and ROI expectations",
                "Secure executive sponsorship and dedicated funding for AI pilots and initiatives",
                "Align AI goals with measurable business outcomes and KPIs",
                "Establish governance frameworks for ethical AI use and risk management",
                "Communicate a compelling AI vision that connects to organizational mission"
            ],
            'change': [
                "Foster a culture of experimentation where failure is treated as a learning opportunity",
                "Encourage cross-functional collaboration to break down departmental barriers",
                "Develop frameworks for scaling successful AI pilots across the organization",
                "Create feedback loops to continuously refine AI initiatives based on results",
                "Build change management capacity to support AI-driven transformations"
            ]
        }

        recommendations = recommendations_map.get(
            dimension['id'],
            ["Focus on building foundational capabilities in this area."])

        # Display dimension analysis card with recommendations inside
        recommendations_html = "".join([
            f'<p style="color: #D1D5DB; line-height: 1.5; margin-left: 1rem; margin-top: 0.5rem; margin-bottom: 0.5rem;">• {rec}</p>'
            for rec in recommendations
        ])

        st.markdown(f"""
        <div style="background-color: #374151; border-left: 4px solid {dimension['color']}; padding: 1.5rem; margin: 1rem 0; border-radius: 0.5rem;">
            <h4 style="color: {dimension['color']}; margin-bottom: 1rem;">📌 {dimension['title']}</h4>
            <p style="color: #E5E7EB; line-height: 1.6; margin-bottom: 1rem;">{insight}</p>
            <p style="color: #D1D5DB; margin-bottom: 0.5rem;"><strong>Specific Recommendations:</strong></p>
            {recommendations_html}
        </div>
        """,
                    unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

    # Add consultation plug (regardless of score)
    st.markdown(f"""
    <div style="background-color: #1F2937; border: 2px solid {primary_color}; padding: 1.5rem; margin: 2rem 0; border-radius: 0.75rem; text-align: center;">
        <h4 style="color: {primary_color}; margin-bottom: 1rem;">🤝 Let's Discuss Your AI Journey</h4>
        <p style="color: #E5E7EB; line-height: 1.6; margin-bottom: 1rem;">
            Whether you're looking to understand these results better, develop a detailed action plan, or need guidance on implementation, 
            we're here to help. Our team specializes in helping organizations like yours navigate the AI readiness journey.
        </p>
        <p style="color: #D1D5DB; font-size: 1.1rem; margin-bottom: 0.5rem;">
            <strong>Schedule a complimentary 45-minute consultation</strong> to discuss your results and explore how we can support your AI transformation.
        </p>
        <p style="color: #9CA3AF; font-size: 0.9rem;">
            No obligations—just expert insights tailored to your organization's unique needs.
        </p>
    </div>
    """,
                unsafe_allow_html=True)

    # Request Assistance Section
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f'<h4 style="color: {primary_color}; text-align: center;">Need Help Implementing These Recommendations?</h4>',
        unsafe_allow_html=True)
    st.markdown(
        '<p style="text-align: center; color: #9CA3AF; margin-bottom: 1rem;">Reach out to us by clicking here.</p>',
        unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📧 Request Assistance from T-Logic",
                     type="primary",
                     use_container_width=True):
            st.session_state.show_assistance_dialog = True
    
    # Assistance Request Dialog
    if st.session_state.get("show_assistance_dialog", False):
        st.markdown("---")
        st.markdown(
            f'<h4 style="color: {primary_color}; text-align: center;">📧 Request Assistance</h4>',
            unsafe_allow_html=True)
        
        # Initialize form fields in session state if not present
        if 'assistance_name' not in st.session_state:
            st.session_state.assistance_name = st.session_state.user_name or ""
        if 'assistance_email' not in st.session_state:
            st.session_state.assistance_email = st.session_state.user_email or ""
        if 'assistance_query' not in st.session_state:
            st.session_state.assistance_query = ""
        
        # Form fields
        st.session_state.assistance_name = st.text_input(
            "Your Name",
            value=st.session_state.assistance_name,
            key="assistance_name_input"
        )
        
        st.session_state.assistance_email = st.text_input(
            "Your Email Address",
            value=st.session_state.assistance_email,
            key="assistance_email_input"
        )
        
        st.session_state.assistance_query = st.text_area(
            "Your Query or Question",
            value=st.session_state.assistance_query,
            placeholder="Tell us what you'd like help with...",
            height=120,
            key="assistance_query_input"
        )
        
        # Action buttons
        col_submit, col_cancel = st.columns(2)
        
        with col_submit:
            if st.button("Submit", type="primary", use_container_width=True):
                # Validate fields
                if not st.session_state.assistance_name.strip():
                    st.error("Please enter your name.")
                elif not st.session_state.assistance_email.strip():
                    st.error("Please enter your email address.")
                elif not st.session_state.assistance_query.strip():
                    st.error("Please enter your query or question.")
                else:
                    # Send assistance request email
                    success, message = send_assistance_request_email(
                        user_name=st.session_state.assistance_name,
                        user_email=st.session_state.assistance_email,
                        query=st.session_state.assistance_query,
                        assessment_results=scores_data)

                    if success:
                        st.success("""
                        ✅ **Request sent successfully!**
                        
                        We've received your assistance request and will contact you at:
                        📧 """ + st.session_state.assistance_email + """
                        
                        Our team will reach out within 24 hours to discuss how we can help with your AI process implementation.
                        """)
                        # Clear dialog
                        st.session_state.show_assistance_dialog = False
                        st.session_state.assistance_name = ""
                        st.session_state.assistance_email = ""
                        st.session_state.assistance_query = ""
                        st.rerun()
                    else:
                        st.error(f"""
                        ❌ **Unable to send request automatically.**
                        
                        Please email us directly at: tej@tlogic.consulting
                        
                        Error: {message}
                        """)
        
        with col_cancel:
            if st.button("Cancel", use_container_width=True):
                st.session_state.show_assistance_dialog = False
                st.rerun()

    # Action buttons
    st.markdown("---")
    
    # Inject JavaScript to style buttons with lighter orange
    st.markdown("""
    <script>
    setTimeout(function() {
        // Get all buttons on the page
        const buttons = document.querySelectorAll('button');
        buttons.forEach(button => {
            // Check if this is a button on the results page that should be light orange
            const text = button.textContent || button.innerText;
            if (text.includes('Retake Assessment') || 
                text.includes('Download') || 
                text.includes('Send Verification') ||
                text.includes('Verify & Download') ||
                text.includes('Resend Code') ||
                text.includes('Submit Feedback') ||
                text.includes('Request Assistance')) {
                // Apply lighter orange styling
                button.style.backgroundColor = '#FCD34D';
                button.style.color = '#000000';
            }
        });
    }, 100);
    </script>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if st.button("Retake Assessment", type="primary", use_container_width=True):
            st.session_state.answers = {}
            st.session_state.current_dimension = 0
            st.session_state.assessment_complete = False
            st.session_state.user_info_collected = False
            st.session_state.user_name = ""
            st.session_state.user_email = ""
            st.rerun()

    with col2:
        st.empty()
    
    with col3:
        if st.button("📄 Download Text Report", type="primary", use_container_width=True):
            st.session_state.show_email_verification = True
            st.session_state.download_type = "text"
    
    # Email Verification Dialog for Report Download
    if st.session_state.get("show_email_verification", False):
        st.markdown("---")
        st.markdown(
            f'<h4 style="color: {primary_color}; text-align: center;">📧 Verify Your Email</h4>',
            unsafe_allow_html=True)
        st.markdown(
            '<p style="text-align: center; color: #9CA3AF; margin-bottom: 1rem;">We need to verify your email before downloading your report.</p>',
            unsafe_allow_html=True)
        
        # Initialize verification fields if not present
        if 'verification_email' not in st.session_state:
            st.session_state.verification_email = st.session_state.user_email or ""
        if 'verification_code_sent' not in st.session_state:
            st.session_state.verification_code_sent = False
        if 'verification_code_expected' not in st.session_state:
            st.session_state.verification_code_expected = ""
        if 'verification_step' not in st.session_state:
            st.session_state.verification_step = "email"  # email or code
        if 'download_type' not in st.session_state:
            st.session_state.download_type = "text"
        
        # Step 1: Enter email
        if st.session_state.verification_step == "email":
            # Allow user to modify the email
            verification_email_input = st.text_input(
                "Enter Your Email Address",
                value=st.session_state.verification_email,
                key="verification_email_input"
            )
            # Update session state with the current input value
            if verification_email_input:
                st.session_state.verification_email = verification_email_input
            
            col_send, col_cancel = st.columns(2)
            with col_send:
                if st.button("Send Verification Code", type="primary", use_container_width=True):
                    if not st.session_state.verification_email.strip():
                        st.error("Please enter your email address.")
                    else:
                        # Generate and send verification code
                        verification_code = generate_verification_code()
                        success, message = send_verification_code_email(
                            st.session_state.verification_email,
                            verification_code
                        )
                        
                        if success:
                            st.session_state.verification_code_expected = verification_code
                            st.session_state.verification_step = "code"
                            st.success(f"✅ Verification code sent to {st.session_state.verification_email}")
                            st.rerun()
                        else:
                            st.error(f"Failed to send verification code: {message}")
            
            with col_cancel:
                if st.button("Cancel", use_container_width=True):
                    st.session_state.show_email_verification = False
                    st.rerun()
        
        # Step 2: Enter verification code
        elif st.session_state.verification_step == "code":
            st.info(f"📧 Verification code sent to: {st.session_state.verification_email}")
            
            verification_code_entered = st.text_input(
                "Enter the 6-digit verification code",
                placeholder="000000",
                key="verification_code_input",
                max_chars=6
            )
            
            col_verify, col_resend, col_cancel = st.columns(3)
            
            with col_verify:
                if st.button("Verify & Download", type="primary", use_container_width=True):
                    if not verification_code_entered:
                        st.error("Please enter the verification code.")
                    elif verification_code_entered != st.session_state.verification_code_expected:
                        st.error("Invalid verification code. Please try again.")
                    else:
                        # Code is correct - generate HTML report
                        try:
                            import base64
                            
                            # Generate HTML report
                            logo_b64 = None
                            if st.session_state.company_logo is not None:
                                from io import BytesIO
                                buffered = BytesIO()
                                st.session_state.company_logo.save(buffered, format="PNG")
                                logo_b64 = base64.b64encode(buffered.getvalue()).decode()
                            
                            html_content = generate_html_report(
                                scores_data,
                                company_name=st.session_state.company_name,
                                company_logo_b64=logo_b64,
                                primary_color=st.session_state.primary_color
                            )
                            
                            # Create download link for HTML
                            filename = f"{st.session_state.company_name}_AI_Readiness_Report.html"
                            html_b64 = base64.b64encode(html_content.encode()).decode()
                            
                            download_script = f"""
                            <script>
                            (function() {{
                                const link = document.createElement('a');
                                link.href = 'data:text/html;base64,{html_b64}';
                                link.download = '{filename}';
                                document.body.appendChild(link);
                                link.click();
                                document.body.removeChild(link);
                            }})();
                            </script>
                            """
                            st.success("✅ Email verified! Downloading your report...")
                            st.components.v1.html(download_script, height=0)
                            
                            # Send notification to T-Logic
                            send_pdf_download_notification(
                                st.session_state.verification_email,
                                assessment_results=scores_data
                            )
                            
                            # Reset state after download
                            st.session_state.show_email_verification = False
                            st.session_state.verification_step = "email"
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error generating report: {str(e)}")
            
            with col_resend:
                if st.button("Resend Code", use_container_width=True):
                    verification_code = generate_verification_code()
                    success, message = send_verification_code_email(
                        st.session_state.verification_email,
                        verification_code
                    )
                    if success:
                        st.session_state.verification_code_expected = verification_code
                        st.info("✅ New verification code sent!")
                    else:
                        st.error(f"Failed to resend code: {message}")
            
            with col_cancel:
                if st.button("Cancel", use_container_width=True):
                    st.session_state.show_email_verification = False
                    st.session_state.verification_step = "email"
                    st.rerun()

    # Feedback Section
    st.markdown("---")
    st.markdown(
        f'<h3 style="color: {primary_color}; text-align: center; margin-top: 2rem;">💬 Help Us Improve</h3>',
        unsafe_allow_html=True)
    st.markdown(
        '<p style="text-align: center; color: #9CA3AF; margin-bottom: 1.5rem;">We value your feedback! Please share your thoughts to help us improve this assessment tool.</p>',
        unsafe_allow_html=True)

    if not st.session_state.feedback_submitted:
        feedback_text = st.text_area(
            "Your Feedback",
            placeholder=
            "What did you like? What could be improved? Any suggestions?",
            height=120,
            key="feedback_input")

        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("📧 Submit Feedback",
                         type="primary",
                         use_container_width=True):
                if feedback_text and feedback_text.strip():
                    # Send feedback email
                    success, message = send_feedback_email(
                        user_name=st.session_state.user_name or "Anonymous",
                        user_email=st.session_state.user_email
                        or "No email provided",
                        feedback_text=feedback_text,
                        assessment_score=f"{total_score}/30 ({percentage}%)")

                    if success:
                        st.session_state.feedback_text = feedback_text
                        st.session_state.feedback_submitted = True
                        # Show thank you popup
                        st.success("✅ Thank you for your feedback!")
                        st.balloons()
                        # Auto-close feedback section after short delay
                        import time
                        time.sleep(1.5)
                        st.rerun()
                    else:
                        st.error(
                            f"Unable to send feedback automatically. Error: {message}"
                        )
                        st.info(
                            "Please email your feedback to: info@tlogic.consulting"
                        )
                else:
                    st.warning("Please enter your feedback before submitting.")
    else:
        st.success("✅ Thank you for your feedback! We appreciate your input.")
        if st.button("Submit More Feedback"):
            st.session_state.feedback_submitted = False
            st.rerun()


def render_chatgpt_assistant():
    """Render standalone ChatGPT AI assistant page"""
    primary_color = st.session_state.primary_color

    # Header with logo
    col1, col2 = st.columns([4, 1])

    with col1:
        st.markdown(
            f'<div class="main-header" style="color: {primary_color};">🤖 ChatGPT AI Assistant</div>',
            unsafe_allow_html=True)
        st.markdown(
            '<div class="sub-header">Chat with AI about anything - process improvement, AI strategy, or general questions</div>',
            unsafe_allow_html=True)

    with col2:
        if st.session_state.company_logo is not None:
            st.markdown(f"""
                <div style="text-align: right; width: 139px; height: 40px; overflow: hidden; margin-left: auto;">
                    <img src="data:image/png;base64,{image_to_base64(st.session_state.company_logo, max_height=40)}" 
                         style="width: 100%; height: auto; display: block;" />
                </div>
                """,
                        unsafe_allow_html=True)

    # Check if OpenAI API key is available
    if not os.environ.get("OPENAI_API_KEY"):
        st.error(
            "💡 **OpenAI API key is not configured.** Please add your OPENAI_API_KEY to the environment secrets to use this feature."
        )
        return

    st.markdown("---")

    # Display chat messages
    chat_container = st.container()
    with chat_container:
        if st.session_state.standalone_chat_messages:
            for msg in st.session_state.standalone_chat_messages:
                role = msg['role']
                content = msg['content']

                if role == 'user':
                    st.markdown(f"""
                    <div style="background-color: #1F2937; padding: 1rem; margin: 0.5rem 0; border-radius: 0.5rem; border-left: 3px solid {primary_color};">
                        <strong style="color: {primary_color};">You:</strong><br>
                        <span style="color: #E5E7EB;">{content}</span>
                    </div>
                    """,
                                unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="background-color: #374151; padding: 1rem; margin: 0.5rem 0; border-radius: 0.5rem;">
                        <strong style="color: #10B981;">ChatGPT:</strong><br>
                        <span style="color: #E5E7EB;">{content}</span>
                    </div>
                    """,
                                unsafe_allow_html=True)
        else:
            st.info(
                "👋 Welcome! I'm your AI assistant. Ask me anything about process improvement, AI strategy, or any general questions you have."
            )

    # Chat input at the bottom
    st.markdown("---")

    # Use session state to manage input value for clearing after send
    if 'chat_input_value' not in st.session_state:
        st.session_state.chat_input_value = ""

    col1, col2 = st.columns([5, 1])
    with col1:
        user_message = st.text_input("Type your message",
                                     placeholder="Ask me anything...",
                                     value=st.session_state.chat_input_value,
                                     key="standalone_chat_input",
                                     label_visibility="collapsed")
    with col2:
        send_button = st.button("Send",
                                type="primary",
                                use_container_width=True,
                                key="standalone_send")

    if send_button and user_message and user_message.strip():
        # Add user message to chat
        st.session_state.standalone_chat_messages.append({
            'role':
            'user',
            'content':
            user_message
        })

        # Get AI response
        with st.spinner("ChatGPT is thinking..."):
            try:
                messages = [{
                    'role': msg['role'],
                    'content': msg['content']
                } for msg in st.session_state.standalone_chat_messages]

                ai_response = get_chat_response(messages,
                                                assessment_context=None)

                st.session_state.standalone_chat_messages.append({
                    'role':
                    'assistant',
                    'content':
                    ai_response
                })
            except Exception as e:
                st.session_state.standalone_chat_messages.append({
                    'role':
                    'assistant',
                    'content':
                    f"I apologize, but I encountered an error: {str(e)}"
                })

        # Clear input field after sending
        st.session_state.chat_input_value = ""
        st.rerun()

    # Clear chat button
    if st.session_state.standalone_chat_messages:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🗑️ Clear Chat History",
                         type="secondary",
                         use_container_width=True):
                st.session_state.standalone_chat_messages = []
                st.rerun()

    # Back to assessment button
    st.markdown("---")
    if st.button("← Back to Assessment", type="secondary"):
        st.session_state.current_page = "assessment"
        st.rerun()


def main():
    """Main application function"""
    initialize_session_state()

    # Render branding sidebar first
    render_branding_sidebar()

    # Add navigation in sidebar
    with st.sidebar:
        st.markdown("### 🧭 Navigation")
        if st.button("📊 Assessment",
                     use_container_width=True,
                     type="primary" if st.session_state.current_page
                     == "assessment" else "secondary"):
            st.session_state.current_page = "assessment"
            st.rerun()
        if st.button("🤖 ChatGPT Assistant",
                     use_container_width=True,
                     type="primary" if st.session_state.current_page
                     == "chatgpt" else "secondary"):
            st.session_state.current_page = "chatgpt"
            st.rerun()
        st.markdown("---")

    # Route to appropriate page
    if st.session_state.current_page == "chatgpt":
        render_chatgpt_assistant()
        render_footer()
        return

    # Only render header on home page (before user info collected), not on dimension pages or results page
    if not st.session_state.assessment_complete and not st.session_state.user_info_collected:
        render_header()

    if not st.session_state.assessment_complete:
        # Show user info collection form if not yet collected
        if not st.session_state.user_info_collected:
            # Make home page static with no scrolling and compact layout
            st.markdown("""
                <style>
                /* Hide Streamlit's default sticky header on home page */
                [data-testid="stHeader"] {
                    display: none !important;
                }
                
                /* Remove all scrollbars on home page */
                section.main,
                section.main > div,
                .block-container,
                [data-testid="stVerticalBlock"],
                .element-container {
                    overflow: visible !important;
                    scrollbar-width: none !important;
                    -ms-overflow-style: none !important;
                }
                
                section.main::-webkit-scrollbar,
                section.main > div::-webkit-scrollbar,
                .block-container::-webkit-scrollbar {
                    display: none !important;
                }
                
                /* Compact the entire page to fit in viewport */
                .block-container {
                    padding-top: 1rem !important;
                    padding-bottom: 1rem !important;
                    max-width: 100% !important;
                }
                
                /* Compact spacing on home page */
                .main-header {
                    font-size: 1.8rem !important;
                    margin-bottom: 0.2rem !important;
                    line-height: 1.1 !important;
                    margin-top: 0 !important;
                }
                
                .sub-header {
                    font-size: 1.05rem !important;
                    margin-bottom: 0.3rem !important;
                    line-height: 1.2 !important;
                }
                
                /* Reduce spacing between form elements */
                .stTextInput {
                    margin-bottom: 0.3rem !important;
                }
                
                .stTextInput > label {
                    font-size: 0.9rem !important;
                    margin-bottom: 0.2rem !important;
                }
                
                .stTextInput > div > div > input {
                    padding: 0.4rem 0.6rem !important;
                    font-size: 0.9rem !important;
                }
                
                div[data-testid="column"] {
                    padding-top: 0 !important;
                    padding-bottom: 0 !important;
                }
                
                /* Compact headings */
                .element-container h3 {
                    margin-top: 0.3rem !important;
                    margin-bottom: 0.2rem !important;
                    font-size: 1.1rem !important;
                }
                
                /* Reduce button spacing */
                .stButton {
                    margin-top: 0.5rem !important;
                    margin-bottom: 0.5rem !important;
                }
                
                .stButton > button {
                    padding: 0.4rem 1rem !important;
                    font-size: 0.95rem !important;
                }
                
                /* Compact rows */
                div.row-widget {
                    margin-bottom: 0.3rem !important;
                }
                </style>
                """, unsafe_allow_html=True)

            st.markdown('<h3 style="margin-top: 0.5rem; margin-bottom: 0.2rem; font-size: 1.2rem;">👤 Your Information</h3>', unsafe_allow_html=True)
            st.markdown(
                '<p style="margin-top: 0; margin-bottom: 0.5rem;"><strong style="color: #FFFFFF;">Please enter your details to begin the assessment</strong> <span style="color: #FFFFFF;">(Optional)</span></p>',
                unsafe_allow_html=True)

            # All fields are optional
            col1, col2 = st.columns(2)
            with col1:
                user_name = st.text_input("Name",
                                          value=st.session_state.user_name,
                                          placeholder="e.g., John Smith",
                                          key="user_name_input")
            with col2:
                st.markdown('<label style="font-size: 0.9rem; margin-bottom: 0.2rem;">Email <span style="color: red;">*</span></label>', unsafe_allow_html=True)
                user_email = st.text_input(
                    "",
                    value=st.session_state.user_email,
                    placeholder="e.g., john@company.com",
                    key="user_email_input",
                    label_visibility="collapsed")
                st.markdown('<p style="margin-top: -0.8rem; margin-bottom: 0.3rem; font-size: 0.8rem; color: #FF0000;">*Required only if downloading PDF output report</p>', unsafe_allow_html=True)

            # Optional fields
            col3, col4 = st.columns(2)
            with col3:
                user_title = st.text_input(
                    "Title",
                    value=st.session_state.user_title,
                    placeholder="e.g., Director of Operations")
            with col4:
                user_company = st.text_input(
                    "Company Name",
                    value=st.session_state.user_company,
                    placeholder="e.g., Acme Corp")

            col5, col6 = st.columns(2)
            with col5:
                user_phone = st.text_input("Phone Number",
                                           value=st.session_state.user_phone,
                                           placeholder="e.g., (555) 123-4567")
            with col6:
                user_location = st.text_input(
                    "Location",
                    value=st.session_state.user_location,
                    placeholder="e.g., New York, NY")

            # Apply white text styling to Continue button
            components.html("""
                <script>
                    (function() {
                        // Find all primary buttons
                        var buttons = window.parent.document.querySelectorAll('button[kind="primary"]');
                        
                        // Find the Continue button by its text content
                        buttons.forEach(function(btn) {
                            if (btn.textContent.includes('Continue')) {
                                btn.classList.add('continue-home-btn');
                            }
                        });
                    })();
                </script>
                """,
                            height=0)

            if st.button("Continue",
                         type="primary",
                         key="continue_button_home"):
                # Save user info to session state
                st.session_state.user_name = user_name
                st.session_state.user_email = user_email
                st.session_state.user_title = user_title
                st.session_state.user_company = user_company
                st.session_state.user_phone = user_phone
                st.session_state.user_location = user_location

                # Send registration email to T-Logic
                send_user_registration_email(
                    user_name=user_name,
                    user_email=user_email,
                    user_title=user_title if user_title else None,
                    user_company=user_company if user_company else None,
                    user_phone=user_phone if user_phone else None,
                    user_location=user_location if user_location else None)

                st.session_state.user_info_collected = True
                st.session_state.should_scroll_to_top = True  # Scroll to first question
                st.rerun()

        else:
            # Assessment mode
            render_progress_bar()

            # Render current dimension questions
            render_dimension_questions(st.session_state.current_dimension)

            # Navigation
            render_navigation_buttons()

        # Show current answers summary in sidebar
        with st.sidebar:
            st.markdown("### 📊 Current Progress")
            completed_questions = len([
                q for q in get_all_questions()
                if q['id'] in st.session_state.answers
            ])
            total_questions = len(get_all_questions())
            st.write(
                f"Questions completed: {completed_questions}/{total_questions}"
            )

            if st.session_state.answers:
                st.markdown("### Your Current Answers")
                for dim_idx, dimension in enumerate(DIMENSIONS):
                    dim_answers = []
                    for q in dimension['questions']:
                        if q['id'] in st.session_state.answers:
                            dim_answers.append(
                                st.session_state.answers[q['id']])

                    if dim_answers:
                        avg_score = sum(dim_answers) / len(dim_answers)
                        st.write(
                            f"**{dimension['title']}**: {avg_score:.1f}/5")

    else:
        # Results mode
        render_results_dashboard()

    # Render copyright footer at the bottom
    render_footer()


if __name__ == "__main__":
    main()
