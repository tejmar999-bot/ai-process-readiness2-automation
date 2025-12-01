"""
2-page HTML report generator for AI Process Readiness Assessment.
Light theme, print-optimized with professional layout.
"""
from datetime import datetime
from utils.scoring import generate_executive_summary

def generate_html_report(scores_data, company_name="", company_logo_b64=None, primary_color="#F97316", assessment_date=None):
    """
    Generate a professional 2-page HTML report optimized for printing.
    
    Args:
        scores_data: Dictionary with assessment scores
        company_name: Company name
        company_logo_b64: Base64 encoded company logo
        primary_color: Primary brand color
        assessment_date: Date of assessment
    
    Returns:
        HTML string for the report
    """
    
    if not assessment_date:
        assessment_date = datetime.now().strftime("%B %d, %Y")
    
    # Extract data
    total_score = scores_data.get('total', 0)
    percentage = scores_data.get('percentage', 0)
    readiness_band = scores_data.get('readiness_band', {})
    critical_status = scores_data.get('critical_status', {})
    raw_scores = scores_data.get('raw_dimension_scores', [])
    avg_score = round(total_score / 6, 1)
    
    # Dimension info
    dimension_names = ['Process Maturity', 'Technology Infrastructure', 'Data Readiness', 'People & Culture', 'Leadership & Alignment', 'Governance & Risk']
    dimension_icons = ['⚙️', '💻', '📊', '👥', '🎯', '⚖️']
    critical_dims = [2, 4]  # Data Readiness (2) and Leadership (4)
    
    # Get color for score
    def get_score_color(score):
        if score < 7:
            return "#DC2626"  # Red
        elif score < 9:
            return "#F97316"  # Orange
        elif score < 12:
            return "#10B981"  # Green
        else:
            return "#059669"  # Dark Green
    
    # Executive summary
    exec_summary = generate_executive_summary(scores_data)
    
    # Build recommendations by dimension
    recommendations = {
        0: ["Document and standardize critical business processes", "Implement process monitoring and KPI tracking", "Establish continuous improvement culture with data-driven decisions"],
        1: ["Develop API-first infrastructure for AI integration", "Invest in secure cloud systems with scalability", "Establish AI experimentation platforms"],
        2: ["Implement data quality frameworks and governance", "Build historical data repositories", "Create unified data access layers"],
        3: ["Launch AI literacy programs across organization", "Provide hands-on training in data-driven decision making", "Identify and empower AI champions"],
        4: ["Integrate AI into strategic planning with clear objectives", "Secure executive sponsorship and dedicated funding", "Align AI goals with measurable business outcomes"],
        5: ["Establish formal AI governance structures", "Develop AI risk assessment frameworks", "Implement continuous monitoring of AI systems"]
    }
    
    # Priority actions - focus on weak dimensions
    priority_actions = []
    for i, score in enumerate(raw_scores):
        if score < 9:
            priority_actions.append({
                'dimension': dimension_names[i],
                'score': score,
                'action': recommendations[i][0],
                'timeline': '90 days' if score < 6 else '60 days'
            })
    
    priority_actions = sorted(priority_actions, key=lambda x: x['score'])[:4]
    
    # Build HTML
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Readiness Assessment Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: Arial, Helvetica, sans-serif;
            background-color: #F9FAFB;
            color: #1F2937;
            line-height: 1.6;
        }}
        
        .report {{
            max-width: 8.5in;
            height: 11in;
            margin: 0.5in auto;
            background-color: white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            padding: 0.5in;
            page-break-after: always;
        }}
        
        .page-break {{
            page-break-after: always;
            clear: both;
        }}
        
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 1.5rem;
            border-bottom: 2px solid {primary_color};
            padding-bottom: 1rem;
        }}
        
        .header-left h1 {{
            font-size: 24px;
            font-weight: bold;
            color: {primary_color};
            margin-bottom: 0.3rem;
        }}
        
        .header-left p {{
            font-size: 11px;
            color: #6B7280;
        }}
        
        .header-right {{
            text-align: right;
            font-size: 10px;
            color: #6B7280;
        }}
        
        .metrics-box {{
            display: flex;
            gap: 1rem;
            margin-bottom: 1.5rem;
            justify-content: space-between;
        }}
        
        .metric-item {{
            flex: 1;
            border: 1px solid #E5E7EB;
            padding: 1rem;
            border-radius: 6px;
            text-align: center;
            background-color: #F9FAFB;
        }}
        
        .metric-item h3 {{
            font-size: 11px;
            color: #6B7280;
            margin-bottom: 0.3rem;
            font-weight: normal;
        }}
        
        .metric-item .value {{
            font-size: 20px;
            font-weight: bold;
            color: {primary_color};
        }}
        
        .critical-alert {{
            background-color: {('#FEF3C7' if critical_status.get('severity') == 'warning' else '#FEE2E2')};
            border-left: 4px solid {('#F59E0B' if critical_status.get('severity') == 'warning' else '#DC2626')};
            padding: 0.75rem;
            margin-bottom: 1rem;
            border-radius: 4px;
            font-size: 11px;
            line-height: 1.5;
        }}
        
        .critical-alert strong {{
            display: block;
            margin-bottom: 0.3rem;
            font-size: 12px;
        }}
        
        .scoring-table {{
            width: 100%;
            font-size: 10px;
            border-collapse: collapse;
            margin-bottom: 1rem;
        }}
        
        .scoring-table th {{
            background-color: #E5E7EB;
            padding: 0.5rem;
            text-align: left;
            font-weight: bold;
        }}
        
        .scoring-table td {{
            padding: 0.5rem;
            border-bottom: 1px solid #E5E7EB;
        }}
        
        .scoring-table tr.current {{
            background-color: #FEF3C7;
            font-weight: bold;
        }}
        
        .dimension-bars {{
            margin-bottom: 1.5rem;
        }}
        
        .bar-item {{
            display: flex;
            align-items: center;
            margin-bottom: 0.7rem;
            gap: 0.5rem;
        }}
        
        .bar-label {{
            font-size: 11px;
            width: 35%;
            font-weight: 600;
        }}
        
        .bar-container {{
            flex: 1;
            height: 20px;
            background-color: #E5E7EB;
            border-radius: 4px;
            overflow: hidden;
            position: relative;
        }}
        
        .bar-fill {{
            height: 100%;
            background-color: #10B981;
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding-right: 0.3rem;
            color: white;
            font-size: 9px;
            font-weight: bold;
        }}
        
        .bar-star {{
            margin-left: 0.3rem;
            font-size: 14px;
        }}
        
        .exec-summary {{
            font-size: 12px;
            font-style: italic;
            line-height: 1.6;
            color: #374151;
            margin-bottom: 1rem;
        }}
        
        h2 {{
            font-size: 18px;
            font-weight: bold;
            color: {primary_color};
            margin-bottom: 1rem;
            border-bottom: 1px solid #E5E7EB;
            padding-bottom: 0.5rem;
        }}
        
        h3 {{
            font-size: 14px;
            font-weight: bold;
            color: #1F2937;
            margin: 0.8rem 0 0.4rem 0;
        }}
        
        .dimension-card {{
            margin-bottom: 0.8rem;
            border-left: 3px solid {primary_color};
            padding: 0.6rem;
            background-color: #F9FAFB;
            font-size: 11px;
        }}
        
        .dimension-card h4 {{
            font-size: 12px;
            font-weight: bold;
            margin-bottom: 0.2rem;
        }}
        
        .dimension-score {{
            font-size: 10px;
            color: #6B7280;
            margin-bottom: 0.3rem;
        }}
        
        .dimension-card ul {{
            margin-left: 1.2rem;
            font-size: 10px;
            line-height: 1.4;
        }}
        
        .dimension-card li {{
            margin-bottom: 0.2rem;
        }}
        
        .priority-box {{
            background-color: #F0F9FF;
            border: 1px solid #BAE6FD;
            border-radius: 4px;
            padding: 0.6rem;
            margin-bottom: 0.8rem;
            font-size: 10px;
        }}
        
        .priority-box strong {{
            color: {primary_color};
        }}
        
        .timeline {{
            display: flex;
            gap: 1rem;
            margin: 1rem 0;
            font-size: 11px;
        }}
        
        .timeline-item {{
            flex: 1;
            border-left: 3px solid {primary_color};
            padding-left: 0.6rem;
        }}
        
        .timeline-item strong {{
            color: {primary_color};
            display: block;
            margin-bottom: 0.2rem;
        }}
        
        .cta {{
            background-color: #F0F9FF;
            border-top: 2px solid {primary_color};
            padding: 1rem;
            margin-top: 1rem;
            border-radius: 4px;
            text-align: center;
            font-size: 11px;
        }}
        
        .cta h3 {{
            color: {primary_color};
            margin-bottom: 0.3rem;
        }}
        
        .footer {{
            font-size: 10px;
            color: #9CA3AF;
            text-align: center;
            margin-top: 1rem;
            padding-top: 0.5rem;
            border-top: 1px solid #E5E7EB;
        }}
        
        @media print {{
            body {{
                background-color: white;
            }}
            .report {{
                box-shadow: none;
                margin: 0;
                padding: 0.5in;
                max-width: 100%;
                page-break-after: always;
            }}
        }}
    </style>
</head>
<body>

<!-- PAGE 1: EXECUTIVE SUMMARY -->
<div class="report">
    <div class="header">
        <div class="header-left">
            <h1>AI Readiness Assessment</h1>
            <p>Results Report</p>
        </div>
        <div class="header-right">
            <strong>T-Logic Consulting</strong><br>
            Date: {assessment_date}<br>
            {f'Company: {company_name}' if company_name else ''}
        </div>
    </div>
    
    <!-- Key Metrics -->
    <div class="metrics-box">
        <div class="metric-item">
            <h3>Total Score</h3>
            <div class="value">{int(total_score)}<span style="font-size: 14px; color: #6B7280;">/90</span></div>
            <p style="font-size: 10px; color: #6B7280;">{percentage}%</p>
        </div>
        <div class="metric-item">
            <h3>Readiness Level</h3>
            <div class="value" style="font-size: 16px;">{readiness_band.get('label', 'N/A')}</div>
        </div>
        <div class="metric-item">
            <h3>Average Score</h3>
            <div class="value">{avg_score}<span style="font-size: 14px; color: #6B7280;">/15</span></div>
        </div>
    </div>
    
    <!-- Critical Alert -->
    {f'''<div class="critical-alert">
        <strong>{critical_status.get("icon", "")} {critical_status.get("title", "")}</strong>
        {critical_status.get("message", "")}
    </div>''' if critical_status.get('severity') != 'info' else ''}
    
    <!-- Scoring Model Table -->
    <table class="scoring-table">
        <thead>
            <tr>
                <th>Score Range</th>
                <th>Readiness Level</th>
                <th>Meaning</th>
            </tr>
        </thead>
        <tbody>
            <tr {"class='current'" if 0 <= total_score <= 41 else ""}>
                <td>0-41</td>
                <td>🔴 Not Ready</td>
                <td>High risk; focus on business fundamentals first.</td>
            </tr>
            <tr {"class='current'" if 42 <= total_score <= 55 else ""}>
                <td>42-55</td>
                <td>🟡 Foundational Gaps</td>
                <td>Significant work needed; start with basics.</td>
            </tr>
            <tr {"class='current'" if 56 <= total_score <= 69 else ""}>
                <td>56-69</td>
                <td>🔵 Building Blocks</td>
                <td>Address weak dimensions before scaling.</td>
            </tr>
            <tr {"class='current'" if total_score >= 70 else ""}>
                <td>70-90</td>
                <td>🟢 AI-Ready</td>
                <td>Strong foundation; focus on strategic pilots.</td>
            </tr>
        </tbody>
    </table>
    
    <!-- Dimension Scores -->
    <h3 style="font-size: 14px; margin-bottom: 0.6rem;">Dimension Scores</h3>
    <div class="dimension-bars">
        {f""".join([f'''
        <div class="bar-item">
            <div class="bar-label">{dimension_icons[i]} {dimension_names[i]}{' ⭐' if i in critical_dims else ''}</div>
            <div class="bar-container">
                <div class="bar-fill" style="width: {(raw_scores[i]/15)*100:.0f}%; background-color: {get_score_color(raw_scores[i])};">
                    {raw_scores[i]:.1f}/15
                </div>
            </div>
        </div>
        ''' for i in range(len(dimension_names))])}
    </div>
    
    <!-- Executive Summary -->
    <h3 style="font-size: 13px; margin-top: 1rem; margin-bottom: 0.5rem;">Executive Summary</h3>
    <div class="exec-summary">
        {exec_summary[:300]}...
    </div>
    
    <div class="footer">
        Page 1 of 2 | AI Process Readiness Assessment | T-Logic Consulting
    </div>
</div>

<!-- PAGE 2: RECOMMENDATIONS & ACTION PLAN -->
<div class="report page-break">
    <h2>Recommendations & Action Plan</h2>
    
    <!-- Dimension-by-Dimension -->
    {f""".join([f'''
    <div class="dimension-card" style="border-left-color: {PALETTE[i]};">
        <h4>{dimension_icons[i]} {dimension_names[i]} {' ⭐' if i in critical_dims else ''}</h4>
        <div class="dimension-score">Score: {raw_scores[i]:.1f}/15 ({int((raw_scores[i]/15)*100)}%)</div>
        <ul>
    ''' + "".join([f"<li>{rec}</li>" for rec in recommendations[i][:2]]) + f"""
        </ul>
    </div>
    ''' for i in range(len(dimension_names))])}
    
    <!-- Priority Actions -->
    <h3 style="margin-top: 1.2rem;">Priority Actions</h3>
    {f""".join([f'''
    <div class="priority-box">
        <strong>Priority {i+1}: {action['dimension']}</strong><br>
        {action['action']}<br>
        <strong style="color: #6B7280;">Timeline: {action['timeline']}</strong>
    </div>
    ''' for i, action in enumerate(priority_actions)])}
    
    <!-- Timeline Roadmap -->
    <h3 style="margin-top: 1rem;">Implementation Timeline</h3>
    <div class="timeline">
        <div class="timeline-item">
            <strong>30 Days</strong>
            Assess current state & quick wins
        </div>
        <div class="timeline-item">
            <strong>90 Days</strong>
            Address critical gaps
        </div>
        <div class="timeline-item">
            <strong>6 Months</strong>
            Reassess & plan pilots
        </div>
    </div>
    
    <!-- Call-to-Action -->
    <div class="cta">
        <h3>Let's Discuss Your AI Journey</h3>
        <p>We're here to help you develop a strategic roadmap for AI implementation. Schedule a consultation to dive deeper into your results.</p>
        <p style="margin-top: 0.5rem;"><strong>tej@tlogic.consulting | www.tlogic.consulting</strong></p>
    </div>
    
    <div class="footer">
        Page 2 of 2 | AI Process Readiness Assessment | T-Logic Consulting
    </div>
</div>

</body>
</html>
"""
    
    # Add PALETTE constant reference
    PALETTE = ['#D17070', '#FDD9B8', '#FFFB4B', '#B9F0C9', '#9DD0F8', '#D7BDE2']
    
    return html
