import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import base64
from io import BytesIO
from PIL import Image
from utils.scoring import compute_scores, get_readiness_band
from data.dimensions import DIMENSIONS, get_all_questions
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
    color: #9CA3AF;
    font-size: 1rem;
    margin-bottom: 2rem;
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

def image_to_base64(image):
    """Convert PIL Image to base64 string"""
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

def render_header():
    """Render the main header with logo and branding"""
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.markdown(f'<div class="main-header" style="color: {st.session_state.primary_color};">AI-Enabled Process Readiness</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-header">Quick self-assessment for process improvement leaders (6 dimensions, ~3 minutes)</div>', unsafe_allow_html=True)
    
    with col2:
        if st.session_state.company_logo is not None:
            # Display logo with rectangular styling (no border-radius)
            st.markdown(
                f"""
                <div style="text-align: right; margin-top: 0.5rem;">
                    <img src="data:image/png;base64,{image_to_base64(st.session_state.company_logo)}" 
                         style="height: 2.5rem; width: auto; border-radius: 0px;" />
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(f"<div style='text-align: right; margin-top: 0.5rem;'><strong>{st.session_state.company_name}</strong></div>", unsafe_allow_html=True)

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
    """Render progress bar with arrow indicators"""
    current_dim = st.session_state.current_dimension
    dimension_color = DIMENSIONS[current_dim]['color']
    
    # Create arrow progress indicator with scroll anchor
    arrows_html = '<div id="progress-anchor" style="display: flex; align-items: center; margin-bottom: 1rem; gap: 0;">'
    
    for i, dimension in enumerate(DIMENSIONS):
        # Determine if this arrow should be lit up
        is_active = i <= current_dim
        arrow_color = dimension['color'] if is_active else '#374151'
        text_color = '#FFFFFF' if is_active else '#6B7280'
        margin_left = '-15px' if i > 0 else '0'
        z_index = len(DIMENSIONS) - i
        
        # Arrow shape using CSS - single line to avoid rendering issues
        arrow_html = f'<div style="position: relative; background-color: {arrow_color}; height: 50px; flex: 1; display: flex; align-items: center; justify-content: center; clip-path: polygon(0 0, calc(100% - 15px) 0, 100% 50%, calc(100% - 15px) 100%, 0 100%, 15px 50%); margin-left: {margin_left}; z-index: {z_index};"><span style="color: {text_color}; font-size: 0.75rem; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; padding: 0 20px;">{dimension["title"]}</span></div>'
        arrows_html += arrow_html
    
    arrows_html += '</div>'
    
    # Colored line above dimension counter
    st.markdown(f'<div style="height: 3px; background-color: {dimension_color}; margin-bottom: 0.5rem;"></div>', unsafe_allow_html=True)
    st.markdown(arrows_html, unsafe_allow_html=True)
    st.markdown(f'<p style="text-align: center; color: #9CA3AF; margin-bottom: 1.5rem;">Dimension {current_dim + 1} of {len(DIMENSIONS)}</p>', unsafe_allow_html=True)

def render_dimension_questions(dimension_idx):
    """Render questions for a specific dimension"""
    dimension = DIMENSIONS[dimension_idx]
    
    # Dimension heading
    st.markdown(f'<h3 style="color: {dimension["color"]}; margin-bottom: 0.5rem;">{dimension["title"]}</h3>', unsafe_allow_html=True)
    
    # "What it Measures" text directly below
    st.markdown(f'<p style="color: #9CA3AF; font-style: italic; margin-bottom: 1.5rem;">{dimension["what_it_measures"]}</p>', unsafe_allow_html=True)
    
    # Get scoring labels for this dimension
    scoring_labels = dimension.get('scoring_labels', {
        1: "1", 2: "2", 3: "3", 4: "4", 5: "5"
    })
    
    for i, question in enumerate(dimension['questions']):
        st.markdown(f'<div class="question-text">{i+1}. {question["text"]}</div>', unsafe_allow_html=True)
        
        # Create rating scale with dimension-specific labels
        rating = st.radio(
            "Rating",
            options=[1, 2, 3, 4, 5],
            format_func=lambda x: f"{x} - {scoring_labels[x]}",
            key=f"q_{question['id']}",
            index=2,  # Default to neutral
            horizontal=True
        )
        
        st.session_state.answers[question['id']] = rating
        st.markdown("---")

def render_navigation_buttons():
    """Render navigation buttons"""
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.session_state.current_dimension > 0:
            if st.button("← Previous", type="secondary"):
                st.session_state.current_dimension -= 1
                st.session_state.should_scroll_to_top = True
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
                        user_name=st.session_state.user_name if st.session_state.user_name else None,
                        user_email=st.session_state.user_email if st.session_state.user_email else None
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
            <div style="color: #9CA3AF;">({percentage}%)</div>
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
    
    # Create table HTML - single line format to avoid rendering issues
    table_html = '<table style="width: 100%; border-collapse: collapse; margin-bottom: 2rem;"><thead><tr style="background-color: #374151;"><th style="padding: 1rem; text-align: center; border: 1px solid #4B5563;">Score Range</th><th style="padding: 1rem; text-align: center; border: 1px solid #4B5563;">Readiness Level</th><th style="padding: 1rem; text-align: left; border: 1px solid #4B5563;">Meaning</th></tr></thead><tbody>'
    
    for row in scoring_model:
        # Check if this is the user's readiness level
        is_current = row['min'] <= total_score <= row['max']
        border_style = f'border: 3px solid {primary_color};' if is_current else 'border: 1px solid #4B5563;'
        bg_color = 'background-color: #1F2937;' if is_current else 'background-color: #111827;'
        font_weight = 'bold' if is_current else 'normal'
        
        table_html += f'<tr style="{bg_color}"><td style="padding: 1rem; text-align: center; {border_style} font-weight: {font_weight};">{row["range"]}</td><td style="padding: 1rem; text-align: center; {border_style} font-weight: {font_weight};">{row["level"]}</td><td style="padding: 1rem; text-align: left; {border_style} font-weight: {font_weight};">{row["meaning"]}</td></tr>'
    
    table_html += '</tbody></table>'
    
    st.markdown(table_html, unsafe_allow_html=True)
    
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
            st.markdown(f"""
            <div style="text-align: center; padding: 1rem;">
                <div style="font-size: 1.5rem; font-weight: bold; color: {dimension['color']};">
                    {score_data['score']}/5
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

def main():
    """Main application function"""
    initialize_session_state()
    
    # Render branding sidebar first
    render_branding_sidebar()
    
    render_header()
    
    # Auto-scroll to show progress indicators if flag is set
    if st.session_state.should_scroll_to_top:
        components.html(
            """
            <script>
                function attemptScroll(retries) {
                    var progressAnchor = window.parent.document.getElementById('progress-anchor');
                    var mainSection = window.parent.document.querySelector('section.main');
                    
                    if (progressAnchor && mainSection) {
                        // Scroll to ensure element is visible
                        var elementPosition = progressAnchor.offsetTop;
                        var offsetPosition = elementPosition - 50;
                        mainSection.scrollTop = Math.max(0, offsetPosition);
                    } else if (retries > 0) {
                        setTimeout(function() { attemptScroll(retries - 1); }, 100);
                    } else if (mainSection) {
                        mainSection.scrollTo(0, 0);
                    }
                }
                setTimeout(function() { attemptScroll(5); }, 100);
            </script>
            """,
            height=0
        )
        st.session_state.should_scroll_to_top = False
    
    if not st.session_state.assessment_complete:
        # Show user info collection form if not yet collected
        if not st.session_state.user_info_collected:
            st.markdown("### 👤 Your Information")
            st.markdown("Please enter your details to begin the assessment.")
            
            # Required fields
            col1, col2 = st.columns(2)
            with col1:
                user_name = st.text_input("Name *", value=st.session_state.user_name, placeholder="e.g., John Smith")
            with col2:
                user_email = st.text_input("Email *", value=st.session_state.user_email, placeholder="e.g., john@company.com")
            
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
                st.session_state.user_name = user_name
                st.session_state.user_email = user_email
                st.session_state.user_title = user_title
                st.session_state.user_company = user_company
                st.session_state.user_phone = user_phone
                st.session_state.user_location = user_location
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

if __name__ == "__main__":
    main()
