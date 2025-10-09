"""
PDF Report Generation for AI Process Readiness Assessment
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from io import BytesIO
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from data.dimensions import DIMENSIONS
from utils.scoring import get_recommendations

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple for ReportLab"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16)/255.0 for i in (0, 2, 4))

def create_radar_chart_image(dimension_scores, primary_color='#BF6A16'):
    """Create a radar chart image for PDF"""
    categories = [score['title'] for score in dimension_scores]
    values = [score['score'] for score in dimension_scores]
    
    # Number of variables
    num_vars = len(categories)
    
    # Compute angle for each axis
    angles = [n / float(num_vars) * 2 * 3.14159 for n in range(num_vars)]
    values += values[:1]
    angles += angles[:1]
    
    # Create figure
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(projection='polar'))
    
    # Plot data
    rgb = hex_to_rgb(primary_color)
    ax.plot(angles, values, 'o-', linewidth=2, color=rgb, label='Your Scores')
    ax.fill(angles, values, alpha=0.25, color=rgb)
    
    # Fix axis to go in the right order
    ax.set_theta_offset(3.14159 / 2)
    ax.set_theta_direction(-1)
    
    # Draw axis lines for each angle and label
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, size=8)
    
    # Set y-axis limits
    ax.set_ylim(0, 5)
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_yticklabels(['1', '2', '3', '4', '5'], size=8)
    
    # Add grid
    ax.grid(True)
    
    # Save to BytesIO
    img_buffer = BytesIO()
    plt.tight_layout()
    plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
    plt.close()
    img_buffer.seek(0)
    
    return img_buffer

def generate_pdf_report(scores_data, company_name="T-Logic", primary_color="#BF6A16", logo_image=None):
    """
    Generate a comprehensive PDF report for the assessment
    
    Args:
        scores_data: Dictionary with dimension_scores, total, percentage, readiness_band
        company_name: Name of the company
        primary_color: Primary brand color in hex
        logo_image: PIL Image object for company logo (optional)
        
    Returns:
        BytesIO buffer containing the PDF
    """
    buffer = BytesIO()
    
    # Create the PDF document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18,
    )
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    rgb_primary = hex_to_rgb(primary_color)
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.Color(*rgb_primary),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.Color(*rgb_primary),
        spaceAfter=12,
        spaceBefore=12
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.Color(*rgb_primary),
        spaceAfter=8,
        spaceBefore=8
    )
    
    body_style = styles['BodyText']
    body_style.alignment = TA_JUSTIFY
    
    # Add logo if available
    if logo_image:
        try:
            img_buffer = BytesIO()
            logo_image.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            logo = Image(img_buffer, width=2*inch, height=0.8*inch)
            logo.hAlign = 'CENTER'
            elements.append(logo)
            elements.append(Spacer(1, 12))
        except:
            pass
    
    # Title
    elements.append(Paragraph(f"AI Process Readiness Assessment", title_style))
    elements.append(Paragraph(f"{company_name}", styles['Heading3']))
    elements.append(Spacer(1, 12))
    
    # Executive Summary
    elements.append(Paragraph("Executive Summary", heading_style))
    
    dimension_scores = scores_data['dimension_scores']
    total_score = scores_data['total']
    percentage = scores_data['percentage']
    readiness_band = scores_data['readiness_band']
    
    summary_text = f"""
    This report presents the results of your AI Process Readiness Assessment across six critical dimensions.
    Your organization achieved an overall score of <b>{total_score}/30 ({percentage}%)</b>, placing you in the 
    <b style="color: {readiness_band['color']}">{readiness_band['label']}</b> readiness category.
    """
    elements.append(Paragraph(summary_text, body_style))
    elements.append(Spacer(1, 20))
    
    # Overall Scores Table
    elements.append(Paragraph("Overall Assessment Scores", heading_style))
    
    score_data = [
        ['Metric', 'Score'],
        ['Total Score', f"{total_score}/30"],
        ['Percentage', f"{percentage}%"],
        ['Readiness Level', readiness_band['label']],
        ['Average Score', f"{round(total_score/6, 1)}/5"]
    ]
    
    score_table = Table(score_data, colWidths=[3*inch, 2*inch])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.Color(*rgb_primary)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    
    elements.append(score_table)
    elements.append(Spacer(1, 20))
    
    # Radar Chart
    elements.append(Paragraph("Visual Assessment Overview", heading_style))
    radar_img_buffer = create_radar_chart_image(dimension_scores, primary_color)
    radar_img = Image(radar_img_buffer, width=5*inch, height=5*inch)
    radar_img.hAlign = 'CENTER'
    elements.append(radar_img)
    elements.append(Spacer(1, 20))
    
    # Dimension Breakdown
    elements.append(PageBreak())
    elements.append(Paragraph("Dimension Breakdown", heading_style))
    elements.append(Spacer(1, 12))
    
    # Get recommendations
    recommendations = get_recommendations(dimension_scores)
    
    for i, score_data in enumerate(dimension_scores):
        dimension = DIMENSIONS[i]
        
        # Dimension title and score
        dim_title = f"{score_data['title']} - Score: {score_data['score']}/5"
        elements.append(Paragraph(dim_title, subheading_style))
        
        # Description
        elements.append(Paragraph(dimension['description'], body_style))
        elements.append(Spacer(1, 8))
        
        # Questions and answers (if we had individual question scores, we'd show them here)
        questions_text = "<b>Assessment Areas:</b><br/>"
        for q in dimension['questions']:
            questions_text += f"• {q['text']}<br/>"
        elements.append(Paragraph(questions_text, body_style))
        elements.append(Spacer(1, 8))
        
        # Recommendations
        if dimension['id'] in recommendations and recommendations[dimension['id']]:
            elements.append(Paragraph("<b>Recommendations:</b>", body_style))
            for rec in recommendations[dimension['id']]:
                elements.append(Paragraph(f"• {rec}", body_style))
        
        elements.append(Spacer(1, 16))
    
    # Next Steps
    elements.append(PageBreak())
    elements.append(Paragraph("Next Steps", heading_style))
    
    if readiness_band['label'] == 'Not Ready':
        next_steps = """
        Your organization is in the early stages of AI readiness. Focus on:
        <br/>• Building foundational process documentation and standardization
        <br/>• Establishing basic data collection and digitization practices
        <br/>• Developing AI awareness among key stakeholders
        <br/>• Securing executive sponsorship and initial funding for AI exploration
        """
    elif readiness_band['label'] == 'Emerging':
        next_steps = """
        Your organization has made initial progress. Prioritize:
        <br/>• Enhancing data quality and accessibility
        <br/>• Implementing pilot AI projects in controlled environments
        <br/>• Building cross-functional collaboration frameworks
        <br/>• Establishing metrics to measure AI initiative success
        """
    elif readiness_band['label'] == 'Ready':
        next_steps = """
        Your organization is well-positioned for AI adoption. Focus on:
        <br/>• Scaling successful pilots to production
        <br/>• Developing advanced analytics and automation capabilities
        <br/>• Strengthening change management practices
        <br/>• Building internal AI expertise and training programs
        """
    else:  # Advanced
        next_steps = """
        Your organization demonstrates advanced AI readiness. Continue to:
        <br/>• Drive innovation through AI-first approaches
        <br/>• Share best practices and lessons learned across the organization
        <br/>• Explore cutting-edge AI technologies and methodologies
        <br/>• Mentor other teams and functions in AI adoption
        """
    
    elements.append(Paragraph(next_steps, body_style))
    elements.append(Spacer(1, 20))
    
    # Conclusion
    elements.append(Paragraph("Conclusion", heading_style))
    conclusion_text = f"""
    This assessment provides a snapshot of your organization's current AI process readiness across six key dimensions.
    Use these insights to prioritize investments, build capabilities, and drive your AI transformation journey.
    Regular reassessment is recommended to track progress and adjust strategies as your organization evolves.
    """
    elements.append(Paragraph(conclusion_text, body_style))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    
    return buffer
