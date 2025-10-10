import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
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
    if 'user_info_collected' not in st.session_state:
        st.session_state.user_info_collected = False

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
            st.session_state.user_info_collected = False
            st.session_state.user_name = ""
            st.session_state.user_email = ""
            st.rerun()
    
    with col3:
        if st.session_state.current_dimension < len(DIMENSIONS) - 1:
            if st.button("Next →", type="primary"):
                st.session_state.current_dimension += 1
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
    
    # Historical Tracking Section
    st.markdown("---")
    st.markdown(f"### 📈 Historical Progress Tracking", unsafe_allow_html=True)
    
    try:
        # Get assessment history
        history = get_assessment_history(st.session_state.company_name)
        
        if len(history) > 1:
            # Show assessment history table
            st.markdown("#### Assessment History")
            
            history_data = []
            for h in history:
                history_data.append({
                    'Date': h['date'],
                    'Total Score': f"{h['total_score']}/30",
                    'Percentage': f"{h['percentage']}%",
                    'Readiness Level': h['readiness_band']
                })
            
            df_history = pd.DataFrame(history_data)
            st.dataframe(df_history, use_container_width=True, hide_index=True)
            
            # Get dimension trends
            trends = get_dimension_trends(st.session_state.company_name)
            
            if trends:
                st.markdown("#### Dimension Progress Over Time")
                
                # Create line chart for dimension trends
                fig_trends = go.Figure()
                
                for dim_id, trend_data in trends.items():
                    fig_trends.add_trace(go.Scatter(
                        x=trend_data['dates'],
                        y=trend_data['scores'],
                        mode='lines+markers',
                        name=trend_data['title'],
                        line=dict(width=2),
                        marker=dict(size=8)
                    ))
                
                fig_trends.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    yaxis=dict(
                        title='Score',
                        range=[0, 5],
                        gridcolor='rgba(255,255,255,0.2)'
                    ),
                    xaxis=dict(
                        title='Assessment Date',
                        gridcolor='rgba(255,255,255,0.2)'
                    ),
                    legend=dict(
                        orientation="v",
                        yanchor="top",
                        y=1,
                        xanchor="left",
                        x=1.02
                    ),
                    height=400,
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig_trends, use_container_width=True)
                
                # Show improvement summary
                st.markdown("#### Progress Summary")
                col1, col2, col3 = st.columns(3)
                
                latest = history[0]
                oldest = history[-1]
                total_improvement = latest['total_score'] - oldest['total_score']
                
                with col1:
                    st.metric(
                        label="Total Assessments",
                        value=len(history)
                    )
                
                with col2:
                    st.metric(
                        label="Score Change",
                        value=f"{latest['total_score']}/30",
                        delta=f"{total_improvement:+d} points" if total_improvement != 0 else "No change"
                    )
                
                with col3:
                    percentage_change = latest['percentage'] - oldest['percentage']
                    st.metric(
                        label="Percentage Change",
                        value=f"{latest['percentage']}%",
                        delta=f"{percentage_change:+d}%" if percentage_change != 0 else "No change"
                    )
        
        elif len(history) == 1:
            st.info("📊 Complete more assessments to see your progress over time!")
        
        else:
            st.info("💡 Your assessment history will appear here after completing assessments.")
    
    except Exception as e:
        st.warning(f"Historical tracking unavailable: {str(e)}")
    
    # Team Analytics Section
    st.markdown("---")
    st.markdown(f"### 👥 Team Analytics", unsafe_allow_html=True)
    
    try:
        team_members = get_team_members(st.session_state.company_name)
        
        if team_members and len(team_members) > 0:
            # Show team members table
            st.markdown("#### Team Members")
            
            team_data = []
            for member in team_members:
                team_data.append({
                    'Name': member['name'],
                    'Email': member['email'],
                    'Latest Score': f"{member['latest_score']}/30",
                    'Percentage': f"{member['latest_percentage']}%",
                    'Assessments': member['total_assessments'],
                    'Last Assessment': member['latest_date']
                })
            
            df_team = pd.DataFrame(team_data)
            st.dataframe(df_team, use_container_width=True, hide_index=True)
            
            # Team dimension averages
            dimension_averages = get_team_dimension_averages(st.session_state.company_name)
            
            if dimension_averages:
                st.markdown("#### Team Dimension Averages")
                
                # Create radar chart for team averages
                categories = [dim['title'] for dim in dimension_averages]
                values = [dim['average'] for dim in dimension_averages]
                
                fig_team = go.Figure()
                
                # Add team average
                fig_team.add_trace(go.Scatterpolar(
                    r=values,
                    theta=categories,
                    fill='toself',
                    name='Team Average',
                    line=dict(color=st.session_state.primary_color, width=2),
                    fillcolor=f"rgba({int(st.session_state.primary_color[1:3], 16)}, {int(st.session_state.primary_color[3:5], 16)}, {int(st.session_state.primary_color[5:7], 16)}, 0.3)"
                ))
                
                # Add industry average benchmark for comparison
                benchmark_data = get_benchmark_data('Industry Average')
                benchmark_values = [benchmark_data[dim['id']] for dim in dimension_averages]
                
                fig_team.add_trace(go.Scatterpolar(
                    r=benchmark_values,
                    theta=categories,
                    fill='toself',
                    name='Industry Average',
                    line=dict(color='#60A5FA', width=2),
                    fillcolor='rgba(96, 165, 250, 0.2)'
                ))
                
                fig_team.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 5],
                            gridcolor='rgba(255,255,255,0.2)'
                        ),
                        angularaxis=dict(
                            gridcolor='rgba(255,255,255,0.2)'
                        )
                    ),
                    showlegend=True,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    height=500
                )
                
                st.plotly_chart(fig_team, use_container_width=True)
                
                # Readiness distribution
                st.markdown("#### Team Readiness Distribution")
                
                distribution = get_team_readiness_distribution(st.session_state.company_name)
                
                if distribution:
                    fig_dist = go.Figure(data=[go.Pie(
                        labels=list(distribution.keys()),
                        values=list(distribution.values()),
                        hole=.3,
                        marker=dict(
                            colors=['#EF4444', '#F59E0B', '#10B981', '#3B82F6', '#8B5CF6']
                        )
                    )])
                    
                    fig_dist.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='white'),
                        height=400
                    )
                    
                    st.plotly_chart(fig_dist, use_container_width=True)
                
                # Team statistics summary
                st.markdown("#### Team Summary")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        label="Team Members",
                        value=len(team_members)
                    )
                
                with col2:
                    team_avg_score = sum([m['latest_score'] for m in team_members]) / len(team_members)
                    st.metric(
                        label="Average Team Score",
                        value=f"{team_avg_score:.1f}/30"
                    )
                
                with col3:
                    total_assessments = sum([m['total_assessments'] for m in team_members])
                    st.metric(
                        label="Total Team Assessments",
                        value=total_assessments
                    )
        
        else:
            st.info("💡 Team analytics will appear here when team members complete assessments with their information.")
    
    except Exception as e:
        st.warning(f"Team analytics unavailable: {str(e)}")
    
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
    
    if not st.session_state.assessment_complete:
        # Show user info collection form if not yet collected
        if not st.session_state.user_info_collected:
            st.markdown("### 👤 Your Information (Optional)")
            st.markdown("Add your details to enable team analytics and track individual progress.")
            
            col1, col2 = st.columns(2)
            with col1:
                user_name = st.text_input("Your Name", value=st.session_state.user_name, placeholder="e.g., John Smith")
            with col2:
                user_email = st.text_input("Your Email", value=st.session_state.user_email, placeholder="e.g., john@company.com")
            
            col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
            with col_btn1:
                if st.button("Continue", type="primary"):
                    st.session_state.user_name = user_name
                    st.session_state.user_email = user_email
                    st.session_state.user_info_collected = True
                    st.rerun()
            
            with col_btn2:
                if st.button("Skip"):
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
