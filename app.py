import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from PIL import Image
from utils.scoring import compute_scores, get_readiness_band
from data.dimensions import DIMENSIONS, get_all_questions

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

def initialize_session_state():
    """Initialize session state variables"""
    if 'answers' not in st.session_state:
        st.session_state.answers = {}
    if 'current_dimension' not in st.session_state:
        st.session_state.current_dimension = 0
    if 'assessment_complete' not in st.session_state:
        st.session_state.assessment_complete = False
    if 'company_logo' not in st.session_state:
        st.session_state.company_logo = None
    if 'company_name' not in st.session_state:
        st.session_state.company_name = "T-Logic"
    if 'primary_color' not in st.session_state:
        st.session_state.primary_color = "#BF6A16"

def render_header():
    """Render the main header with logo and branding"""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f'<div class="main-header" style="color: {st.session_state.primary_color};">AI-Enabled Process Readiness</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-header">Quick self-assessment for process improvement leaders (6 dimensions, ~3 minutes)</div>', unsafe_allow_html=True)
    
    with col2:
        if st.session_state.company_logo is not None:
            st.image(st.session_state.company_logo, width=200)
        else:
            st.markdown(f"**{st.session_state.company_name}**", unsafe_allow_html=True)

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
    """Render progress bar"""
    progress = (st.session_state.current_dimension + 1) / len(DIMENSIONS)
    st.progress(progress)
    st.write(f"Dimension {st.session_state.current_dimension + 1} of {len(DIMENSIONS)}")

def render_dimension_questions(dimension_idx):
    """Render questions for a specific dimension"""
    dimension = DIMENSIONS[dimension_idx]
    
    st.markdown(f"""
    <div class="dimension-card">
        <h3 style="color: {dimension['color']}; margin-bottom: 1rem;">{dimension['title']}</h3>
        <p style="color: #9CA3AF; margin-bottom: 1.5rem;">{dimension['description']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    for i, question in enumerate(dimension['questions']):
        st.markdown(f'<div class="question-text">{i+1}. {question["text"]}</div>', unsafe_allow_html=True)
        
        # Create rating scale
        rating = st.radio(
            "Rating",
            options=[1, 2, 3, 4, 5],
            format_func=lambda x: {
                1: "1 - Strongly Disagree",
                2: "2 - Disagree", 
                3: "3 - Neutral",
                4: "4 - Agree",
                5: "5 - Strongly Agree"
            }[x],
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
                st.rerun()
    
    with col2:
        if st.button("Reset Assessment", type="secondary"):
            st.session_state.answers = {}
            st.session_state.current_dimension = 0
            st.session_state.assessment_complete = False
            st.rerun()
    
    with col3:
        if st.session_state.current_dimension < len(DIMENSIONS) - 1:
            if st.button("Next →", type="primary"):
                st.session_state.current_dimension += 1
                st.rerun()
        else:
            if st.button("Complete Assessment", type="primary"):
                st.session_state.assessment_complete = True
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
    
    # Action buttons
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Retake Assessment", type="primary"):
            st.session_state.answers = {}
            st.session_state.current_dimension = 0
            st.session_state.assessment_complete = False
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
            label="Download Results",
            data=results_text,
            file_name="ai_readiness_assessment_results.txt",
            mime="text/plain"
        )

def main():
    """Main application function"""
    initialize_session_state()
    
    # Render branding sidebar first
    render_branding_sidebar()
    
    render_header()
    
    if not st.session_state.assessment_complete:
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
