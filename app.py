import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import base64
from io import BytesIO
from PIL import Image
from utils.scoring import compute_scores, get_readiness_band
from data.dimensions import DIMENSIONS, BRIGHT_PALETTE, get_all_questions
from utils.pdf_generator import generate_pdf_report
from data.benchmarks import get_benchmark_comparison, get_all_benchmarks, get_benchmark_data
from db.operations import (
    ensure_tables_exist, 
    save_assessment, 
    get_assessment_history,
    get_dimension_trends,
    get_team_statistics,
    get_team_members,
    get_team_dimension_averages,
    get_team_readiness_distribution
)
from utils.gmail_sender import send_assistance_request_email, send_feedback_email, send_user_registration_email

# Page configuration
st.set_page_config(
    page_title="AI Process Readiness Assessment",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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
</style>
""", unsafe_allow_html=True)

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
            default_logo = Image.open('static/T_Logic_Logo.png')
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

def render_header():
    """Render the main header with logo and branding"""
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.markdown(f'<div class="main-header" style="color: {st.session_state.primary_color};">AI-Enabled Process Readiness</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-header">Quick self-assessment for process improvement leaders (6 dimensions, ~3 minutes)</div>', unsafe_allow_html=True)
    
    with col2:
        if st.session_state.company_logo is not None:
            # Display logo matching title size (40px = 2.5rem)
            # Logo is pre-resized to 40px height via PIL, CSS provides fallback constraints
            st.markdown(
                f"""
                <div style="text-align: right;">
                    <img src="data:image/png;base64,{image_to_base64(st.session_state.company_logo, max_height=40)}" 
                         style="height: 40px; width: auto; border-radius: 0; display: block; margin-left: auto;" />
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(f"<div style='text-align: center; margin-top: 0.5rem;'><strong>{st.session_state.company_name}</strong></div>", unsafe_allow_html=True)

def render_footer():
    """Render copyright footer at the bottom of the page"""
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 1rem 2rem; color: #9CA3AF; font-size: 0.9rem; border-top: 1px solid #374151; margin-top: 2rem;">
            <div style="text-align: center; flex: 1;">
                © T-Logic Training & Consulting Pvt. Ltd.
            </div>
            <div style="text-align: right;">
                www.tlogicconsulting.com
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_branding_sidebar():
    """Render branding customization in sidebar"""
    with st.sidebar:
        st.markdown("### 🎨 Branding")
        
        # Company name input
        company_name = st.text_input(
            "Company Name",
            value=st.session_state.company_name,
            key="company_name_input"
        )
        if company_name != st.session_state.company_name:
            st.session_state.company_name = company_name
            st.rerun()
        
        # Logo upload
        uploaded_file = st.file_uploader(
            "Upload Company Logo",
            type=['png', 'jpg', 'jpeg'],
            help="Upload your company logo (PNG, JPG)"
        )
        
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
            help="Choose your brand's primary color"
        )
        if primary_color != st.session_state.primary_color:
            st.session_state.primary_color = primary_color
            st.rerun()
        
        st.markdown("---")

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
    arrows_html = f'<div id="progress-anchor" data-render="{timestamp}" style="display: flex; align-items: center; margin-bottom: 1rem; gap: 0; max-width: 100%;">'
    
    for i, dim in enumerate(DIMENSIONS):
        # Determine if this arrow should be lit up
        is_active = i <= current_dim
        arrow_color = dim['color'] if is_active else '#374151'
        text_color = '#000000' if is_active else '#6B7280'
        margin_left = '-15px' if i > 0 else '0'
        z_index = len(DIMENSIONS) - i
        
        # Fixed width arrows with text wrapping - single line to avoid rendering issues
        arrow_html = f'<div style="position: relative; background-color: {arrow_color}; height: 60px; width: 120px; min-width: 100px; display: flex; align-items: center; justify-content: center; clip-path: polygon(0 0, calc(100% - 15px) 0, 100% 50%, calc(100% - 15px) 100%, 0 100%, 15px 50%); margin-left: {margin_left}; z-index: {z_index};"><span style="color: {text_color}; font-size: 0.65rem; font-weight: 600; text-align: center; padding: 0 18px; line-height: 1.1; word-wrap: break-word; overflow-wrap: break-word;">{dim["title"]}</span></div>'
        arrows_html += arrow_html
    
    arrows_html += '</div>'
    
    # Use Streamlit container with custom CSS for sticky positioning
    st.markdown(
        f"""
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
            padding: 1.5rem 1rem 1rem 1rem !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3) !important;
        }}
        /* Add spacer after sticky header */
        .header-spacer {{
            height: 300px !important;
            width: 100% !important;
        }}
        </style>
        <div class="sticky-header-container">
            <div style="height: 4px; background-color: {dimension_color}; margin-bottom: 1rem;"></div>
            {arrows_html}
            <p style="text-align: center; color: #9CA3AF; margin: 0.75rem 0; font-size: 0.9rem;">Dimension {current_dim + 1} of {len(DIMENSIONS)}</p>
            <h2 style="color: {bright_color}; margin: 0.5rem 0; text-align: center; font-size: 2rem; font-weight: 700;">{dimension["title"]}</h2>
            <p style="color: #D1D5DB; font-style: italic; margin: 0.75rem 0 0 0; text-align: center; font-size: 1.05rem; line-height: 1.5;">{dimension["what_it_measures"]}</p>
        </div>
        <div class="header-spacer"></div>
        """,
        unsafe_allow_html=True
    )

def render_dimension_questions(dimension_idx):
    """Render questions for a specific dimension"""
    dimension = DIMENSIONS[dimension_idx]
    
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
        st.markdown(f'<div id="question-{i}" class="question-text">{i+1}. {question["text"]}</div>', unsafe_allow_html=True)
        
        # Get current answer or default
        current_answer = st.session_state.answers.get(question['id'], 3)
        
        # Use question-specific answer choices if available, otherwise use dimension scoring labels
        answer_choices = question.get('answer_choices', dimension.get('scoring_labels', {
            1: "1", 2: "2", 3: "3", 4: "4", 5: "5"
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
            args=(question['id'], i)
        )
        
        st.session_state.answers[question['id']] = rating
        st.markdown("---")
    
    # Execute auto-scroll script only if scroll is triggered for a specific question
    if st.session_state.scroll_to_question is not None:
        target_question_idx = st.session_state.scroll_to_question
        components.html(
            f"""
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
            height=0
        )
        # Clear the flag after scrolling
        st.session_state.scroll_to_question = None
    
    # Auto-scroll to first question if flag is set (for Next button and dimension changes)
    if st.session_state.should_scroll_to_top:
        components.html(
            """
            <script>
                function scrollToFirstQuestion(retries) {
                    var firstQuestion = window.parent.document.querySelector('#question-0');
                    
                    if (firstQuestion) {
                        // Use scrollIntoView with CSS scroll-padding handling sticky header
                        firstQuestion.scrollIntoView({
                            behavior: 'smooth',
                            block: 'start'
                        });
                    } else if (retries > 0) {
                        setTimeout(function() { scrollToFirstQuestion(retries - 1); }, 100);
                    }
                }
                setTimeout(function() { scrollToFirstQuestion(15); }, 200);
            </script>
            """,
            height=0
        )
        st.session_state.should_scroll_to_top = False

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
                        user_email=st.session_state.user_email or ""
                    )
                    st.session_state.current_assessment_id = assessment.id
                except Exception as e:
                    st.error(f"Error saving assessment: {str(e)}")
                
                st.session_state.assessment_complete = True
                st.session_state.should_scroll_to_top = True  # Scroll to top to show results
                st.rerun()

def create_radar_chart(dimension_scores):
    """Create radar chart for dimension scores"""
    categories = [score['title'] for score in dimension_scores]
    values = [score['score'] for score in dimension_scores]
    colors = [DIMENSIONS[i]['color'] for i in range(len(dimension_scores))]
    
    # Close the radar chart by adding the first value at the end
    categories_closed = categories + [categories[0]]
    values_closed = values + [values[0]]
    
    # Convert hex color to rgba for fill
    primary_color = st.session_state.primary_color
    hex_color = primary_color.lstrip('#')
    rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    fillcolor = f'rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, 0.2)'
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values_closed,
        theta=categories_closed,
        fill='toself',
        fillcolor=fillcolor,
        line=dict(color=primary_color, width=2),
        marker=dict(color=primary_color, size=8),
        name='Your Scores'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 5],
                tickfont=dict(color='white'),
                gridcolor='rgba(255,255,255,0.2)'
            ),
            angularaxis=dict(
                tickfont=dict(color='white', size=12),
                gridcolor='rgba(255,255,255,0.2)'
            ),
            bgcolor='rgba(0,0,0,0)'
        ),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=500
    )
    
    return fig

def render_results_dashboard():
    """Render the results dashboard"""
    # Execute scroll to top FIRST, before rendering any content
    if st.session_state.should_scroll_to_top:
        components.html(
            """
            <script>
                function scrollToTopResults(retries) {
                    try {
                        // Use document.documentElement to bypass scroll-padding
                        if (window.parent.document.documentElement) {
                            window.parent.document.documentElement.scrollTop = 0;
                        } else if (window.parent.document.body) {
                            window.parent.document.body.scrollTop = 0;
                        }
                        // Also try window.parent.scrollTo as fallback
                        window.parent.scrollTo(0, 0);
                    } catch (e) {
                        if (retries > 0) {
                            setTimeout(function() { scrollToTopResults(retries - 1); }, 100);
                        }
                    }
                }
                setTimeout(function() { scrollToTopResults(10); }, 500);
            </script>
            """,
            height=0
        )
        st.session_state.should_scroll_to_top = False
    
    # Calculate scores
    scores_data = compute_scores(st.session_state.answers)
    dimension_scores = scores_data['dimension_scores']
    total_score = scores_data['total']
    percentage = scores_data['percentage']
    readiness_band = scores_data['readiness_band']
    
    primary_color = st.session_state.primary_color
    st.markdown(f'<div class="main-header" style="color: {primary_color};">Assessment Results</div>', unsafe_allow_html=True)
    
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
        """, unsafe_allow_html=True)
    
    with col2:
        band_color = readiness_band['color']
        st.markdown(f"""
        <div class="score-card">
            <h3 style="color: {primary_color};">Readiness Level</h3>
            <div class="readiness-band" style="color: {band_color};">{readiness_band['label']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        avg_score = round(total_score / 6, 1)
        st.markdown(f"""
        <div class="score-card">
            <h3 style="color: {primary_color};">Average Score</h3>
            <div style="font-size: 2rem; font-weight: bold;">{avg_score}/5</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Scoring Model Table
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown(f'<h3 style="color: {primary_color}; text-align: center; margin-bottom: 1rem;">📊 Scoring Model</h3>', unsafe_allow_html=True)
    
    # Define scoring model data
    scoring_model = [
        {"range": "0-10", "level": "🟥 Not Ready", "meaning": "Foundational work needed before AI introduction", "min": 0, "max": 10},
        {"range": "11-17", "level": "🟧 Emerging", "meaning": "Some digital and process maturity; pilot-level readiness", "min": 11, "max": 17},
        {"range": "18-24", "level": "🟨 Ready", "meaning": "Data, processes, and leadership alignment in place for scaled AI use", "min": 18, "max": 24},
        {"range": "25-30", "level": "🟩 Advanced", "meaning": "AI-ready culture and infrastructure for sustainable transformation", "min": 25, "max": 30}
    ]
    
    # Create table with clean, properly aligned cells
    # Map emoji colors to their hex equivalents for CSS squares
    color_map = {
        "🟥 Not Ready": ("#DC2626", "Not Ready"),
        "🟧 Emerging": ("#F97316", "Emerging"),
        "🟨 Ready": ("#EAB308", "Ready"),
        "🟩 Advanced": ("#16A34A", "Advanced")
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
        """, unsafe_allow_html=True)
    
    # Radar chart
    st.markdown("### Dimension Breakdown")
    fig = create_radar_chart(dimension_scores)
    st.plotly_chart(fig, use_container_width=True)
    
    # Dimension scores breakdown
    st.markdown("### Detailed Scores by Dimension")
    
    for i, score_data in enumerate(dimension_scores):
        dimension = DIMENSIONS[i]
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"""
            <div style="padding: 1rem; background-color: #374151; border-radius: 0.5rem; margin: 0.5rem 0;">
                <h4 style="color: {dimension['color']}; margin-bottom: 0.5rem;">{score_data['title']}</h4>
                <p style="color: #9CA3AF; font-size: 0.9rem;">{dimension['description']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Map scores to labels
            score_labels = {
                1: "Weak",
                2: "Needs Work",
                3: "Average",
                4: "Good",
                5: "Excellent"
            }
            score = score_data['score']
            label = score_labels.get(score, "Average")
            percentage = (score / 5) * 100
            
            # Adjust font size based on label length to fit in oval
            font_size = "0.7rem" if len(label) > 8 else "0.8rem"
            
            st.markdown(f"""
            <div style="text-align: center; padding: 1rem;">
                <div style="font-size: 1.5rem; font-weight: bold; color: {dimension['color']};">
                    {score_data['score']}/5
                </div>
                <div style="color: #9CA3AF; font-size: 0.9rem; margin-top: 0.25rem;">
                    ({percentage:.0f}%)
                </div>
                <div style="margin-top: 0.5rem;">
                    <span style="display: inline-block; background-color: #D4C5B9; color: #000000; padding: 0.4rem 1rem; border-radius: 50px; min-width: 100px; font-size: {font_size}; font-weight: 600;">{label}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Benchmark Comparison Section
    st.markdown("---")
    st.markdown(f"### 📊 Industry Benchmark Comparison", unsafe_allow_html=True)
    
    # Benchmark selector
    col1, col2 = st.columns([2, 3])
    
    with col1:
        all_benchmarks = get_all_benchmarks()
        default_idx = all_benchmarks.index('Industry Average') if 'Industry Average' in all_benchmarks else 0
        benchmark_name = st.selectbox(
            "Compare against:",
            options=all_benchmarks,
            index=default_idx
        )
    
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
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="score-card">
            <h4 style="color: {primary_color};">Benchmark Score</h4>
            <div style="font-size: 1.5rem; font-weight: bold;">{comparison['benchmark_total']}/30</div>
        </div>
        """, unsafe_allow_html=True)
    
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
        """, unsafe_allow_html=True)
    
    # Dimension-by-dimension comparison
    st.markdown("#### Dimension Comparison")
    
    # Create comparison chart
    dimension_names = [d['title'] for d in comparison['dimensions']]
    your_scores_list = [d['your_score'] for d in comparison['dimensions']]
    benchmark_scores_list = [d['benchmark_score'] for d in comparison['dimensions']]
    
    fig_comparison = go.Figure()
    
    # Add your scores
    fig_comparison.add_trace(go.Bar(
        name='Your Scores',
        x=dimension_names,
        y=your_scores_list,
        marker_color=primary_color
    ))
    
    # Add benchmark scores
    fig_comparison.add_trace(go.Bar(
        name=f'{benchmark_name}',
        x=dimension_names,
        y=benchmark_scores_list,
        marker_color='#6B7280'
    ))
    
    fig_comparison.update_layout(
        barmode='group',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        yaxis=dict(
            title='Score',
            range=[0, 5],
            gridcolor='rgba(255,255,255,0.2)'
        ),
        xaxis=dict(
            gridcolor='rgba(255,255,255,0.2)'
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=400
    )
    
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
    st.markdown(f'<h3 id="recommended-actions" style="color: {primary_color}; text-align: center; margin-top: 2rem;">🎯 Recommended Actions</h3>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #9CA3AF; margin-bottom: 1.5rem; font-size: 1.1rem;">Based on your assessment, here are holistic insights and specific recommendations to accelerate your AI readiness journey.</p>', unsafe_allow_html=True)
    
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
        
        recommendations = recommendations_map.get(dimension['id'], ["Focus on building foundational capabilities in this area."])
        
        # Display dimension analysis card with recommendations inside
        recommendations_html = "".join([f'<p style="color: #D1D5DB; line-height: 1.5; margin-left: 1rem; margin-top: 0.5rem; margin-bottom: 0.5rem;">• {rec}</p>' for rec in recommendations])
        
        st.markdown(f"""
        <div style="background-color: #374151; border-left: 4px solid {dimension['color']}; padding: 1.5rem; margin: 1rem 0; border-radius: 0.5rem;">
            <h4 style="color: {dimension['color']}; margin-bottom: 1rem;">📌 {dimension['title']}</h4>
            <p style="color: #E5E7EB; line-height: 1.6; margin-bottom: 1rem;">{insight}</p>
            <p style="color: #D1D5DB; margin-bottom: 0.5rem;"><strong>Specific Recommendations:</strong></p>
            {recommendations_html}
        </div>
        """, unsafe_allow_html=True)
        
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
    """, unsafe_allow_html=True)
    
    # Request Assistance Section
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f'<h4 style="color: {primary_color}; text-align: center;">Need Help Implementing These Recommendations?</h4>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #9CA3AF; margin-bottom: 1rem;">Reach out to us by clicking here.</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📧 Request Assistance from T-Logic", type="primary", use_container_width=True):
            # Send assistance request email
            success, message = send_assistance_request_email(
                user_name=st.session_state.user_name or "Anonymous",
                user_email=st.session_state.user_email or "No email provided",
                user_company=st.session_state.user_company or "Not specified",
                assessment_results=scores_data
            )
            
            if success:
                st.success("""
                ✅ **Request sent successfully!**
                
                We've received your assistance request and will contact you at:
                📧 """ + st.session_state.user_email + """
                
                Our team will reach out within 24 hours to discuss how we can help with your AI process implementation.
                """)
            else:
                st.error(f"""
                ❌ **Unable to send request automatically.**
                
                Please email us directly at: info@tlogicconsulting.com
                
                Include your assessment results and contact information.
                
                Error: {message}
                """)
    
    # Action buttons
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Retake Assessment", type="primary"):
            st.session_state.answers = {}
            st.session_state.current_dimension = 0
            st.session_state.assessment_complete = False
            st.session_state.user_info_collected = False
            st.session_state.user_name = ""
            st.session_state.user_email = ""
            st.rerun()
    
    with col2:
        # Export results as text
        results_text = f"""AI Process Readiness Assessment Results

Overall Score: {total_score}/30 ({percentage}%)
Readiness Level: {readiness_band['label']}

Dimension Breakdown:
"""
        for score_data in dimension_scores:
            results_text += f"• {score_data['title']}: {score_data['score']}/5\n"
        
        st.download_button(
            label="📄 Download TXT",
            data=results_text,
            file_name="ai_readiness_assessment.txt",
            mime="text/plain"
        )
    
    with col3:
        # Generate PDF report
        try:
            pdf_buffer = generate_pdf_report(
                scores_data,
                company_name=st.session_state.company_name,
                primary_color=st.session_state.primary_color,
                logo_image=st.session_state.company_logo
            )
            
            st.download_button(
                label="📊 Download PDF Report",
                data=pdf_buffer,
                file_name=f"{st.session_state.company_name}_AI_Readiness_Report.pdf",
                mime="application/pdf",
                type="primary"
            )
        except Exception as e:
            st.error(f"Error generating PDF: {str(e)}")
    
    # Feedback Section
    st.markdown("---")
    st.markdown(f'<h3 style="color: {primary_color}; text-align: center; margin-top: 2rem;">💬 Help Us Improve</h3>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #9CA3AF; margin-bottom: 1.5rem;">We value your feedback! Please share your thoughts to help us improve this assessment tool.</p>', unsafe_allow_html=True)
    
    if not st.session_state.feedback_submitted:
        feedback_text = st.text_area(
            "Your Feedback",
            placeholder="What did you like? What could be improved? Any suggestions?",
            height=120,
            key="feedback_input"
        )
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("📧 Submit Feedback", type="primary", use_container_width=True):
                if feedback_text and feedback_text.strip():
                    # Send feedback email
                    success, message = send_feedback_email(
                        user_name=st.session_state.user_name or "Anonymous",
                        user_email=st.session_state.user_email or "No email provided",
                        feedback_text=feedback_text,
                        assessment_score=f"{total_score}/30 ({percentage}%)"
                    )
                    
                    if success:
                        st.session_state.feedback_text = feedback_text
                        st.session_state.feedback_submitted = True
                        st.rerun()
                    else:
                        st.error(f"Unable to send feedback automatically. Error: {message}")
                        st.info("Please email your feedback to: info@tlogicconsulting.com")
                else:
                    st.warning("Please enter your feedback before submitting.")
    else:
        st.success("✅ Thank you for your feedback! We appreciate your input.")
        if st.button("Submit More Feedback"):
            st.session_state.feedback_submitted = False
            st.rerun()

def main():
    """Main application function"""
    initialize_session_state()
    
    # Render branding sidebar first
    render_branding_sidebar()
    
    # Only render header on assessment pages, not on results page
    if not st.session_state.assessment_complete:
        render_header()
    
    if not st.session_state.assessment_complete:
        # Show user info collection form if not yet collected
        if not st.session_state.user_info_collected:
            st.markdown("### 👤 Your Information")
            st.markdown("Please enter your details to begin the assessment.")
            
            # Required fields
            col1, col2 = st.columns(2)
            with col1:
                user_name = st.text_input("Name *", value=st.session_state.user_name, placeholder="e.g., John Smith", key="user_name_input")
            with col2:
                user_email = st.text_input("Email *", value=st.session_state.user_email, placeholder="e.g., john@company.com", key="user_email_input")
            
            # Optional fields
            col3, col4 = st.columns(2)
            with col3:
                user_title = st.text_input("Title", value=st.session_state.user_title, placeholder="e.g., Director of Operations")
            with col4:
                user_company = st.text_input("Company Name", value=st.session_state.user_company, placeholder="e.g., Acme Corp")
            
            col5, col6 = st.columns(2)
            with col5:
                user_phone = st.text_input("Phone Number", value=st.session_state.user_phone, placeholder="e.g., (555) 123-4567")
            with col6:
                user_location = st.text_input("Location", value=st.session_state.user_location, placeholder="e.g., New York, NY")
            
            # Email validation regex
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            is_valid_email = bool(re.match(email_pattern, user_email)) if user_email else False
            
            # Validation messages
            if user_email and not is_valid_email:
                st.error("⚠️ Please enter a valid email address")
            
            # Continue button - only enabled when required fields filled and email valid
            can_continue = bool(user_name and user_name.strip()) and is_valid_email
            
            if st.button("Continue", type="primary", disabled=not can_continue):
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
                    user_location=user_location if user_location else None
                )
                
                st.session_state.user_info_collected = True
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
            completed_questions = len([q for q in get_all_questions() if q['id'] in st.session_state.answers])
            total_questions = len(get_all_questions())
            st.write(f"Questions completed: {completed_questions}/{total_questions}")
            
            if st.session_state.answers:
                st.markdown("### Your Current Answers")
                for dim_idx, dimension in enumerate(DIMENSIONS):
                    dim_answers = []
                    for q in dimension['questions']:
                        if q['id'] in st.session_state.answers:
                            dim_answers.append(st.session_state.answers[q['id']])
                    
                    if dim_answers:
                        avg_score = sum(dim_answers) / len(dim_answers)
                        st.write(f"**{dimension['title']}**: {avg_score:.1f}/5")
    
    else:
        # Results mode
        render_results_dashboard()
    
    # Render copyright footer at the bottom
    render_footer()

if __name__ == "__main__":
    main()
