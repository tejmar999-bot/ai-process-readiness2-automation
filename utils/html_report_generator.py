"""
HTML/Text report generator for T-Logic AI-Enabled Process Readiness results.
Generates a professional, printable HTML report with company branding.
"""
from datetime import datetime


def generate_html_report(
    results: dict,
    company_name: str = "Your Company",
    company_logo_b64: str = None,
    primary_color: str = "#BF6A16"
) -> str:
    """
    Generate a professional HTML report that can be printed or saved as PDF.
    
    Args:
        results: Dictionary with assessment results from compute_scores
        company_name: Company name for branding
        company_logo_b64: Optional base64-encoded company logo
        primary_color: Primary brand color
        
    Returns:
        HTML string that can be downloaded
    """
    
    # Extract data with safe type conversion
    try:
        overall_score = float(results.get('total', 0) or 0)
    except:
        overall_score = 0.0
    
    try:
        percentage = int(results.get('percentage', 0) or 0)
    except:
        percentage = 0
    
    readiness_band = results.get('readiness_band', {})
    readiness_label = readiness_band.get('label', 'Foundational')
    readiness_color = readiness_band.get('color', '#999999')
    
    # Dimension scores as list - convert all to floats
    raw_scores = results.get('dimension_scores', [])
    dimension_scores_list = []
    for score in raw_scores:
        try:
            if isinstance(score, dict):
                dimension_scores_list.append(float(score.get('score', 0) or 0))
            else:
                dimension_scores_list.append(float(score) if score else 0.0)
        except (TypeError, ValueError):
            dimension_scores_list.append(0.0)
    
    dimension_names = [
        "Process Maturity",
        "Technology Infrastructure",
        "Data Readiness",
        "People & Culture",
        "Leadership & Alignment",
        "Governance & Risk"
    ]
    
    # Color mapping for dimensions
    dimension_colors = {
        "Process Maturity": "#DFA5A0",
        "Technology Infrastructure": "#FDD9B8",
        "Data Readiness": "#FFFB4B",
        "People & Culture": "#B9F0C9",
        "Leadership & Alignment": "#B3E5FC",
        "Governance & Risk": "#D7BDE2",
    }
    
    current_date = datetime.now().strftime("%B %d, %Y")
    
    logo_html = ""
    if company_logo_b64:
        logo_html = '<img src="data:image/png;base64,' + company_logo_b64 + '" alt="Logo" style="height: 60px; width: auto;">'
    
    # Build dimension items HTML
    dimension_items_html = ""
    for name, score in zip(dimension_names, dimension_scores_list):
        color = dimension_colors.get(name, '#999')
        score = float(score) if score else 0.0
        percentage_val = int((score / 5.0) * 100)
        dimension_items_html += '''
            <div class="dimension-item" style="border-color: {0};">
                <div class="dimension-name">{1}</div>
                <div class="dimension-score">
                    <span class="score-text">{2:.1f} / 5.0</span>
                    <div class="score-bar">
                        <div class="score-fill" style="width: {3}%; background-color: {4};"></div>
                    </div>
                    <span class="score-text" style="text-align: right; min-width: 40px;">{3}%</span>
                </div>
            </div>
            '''.format(color, name, score, percentage_val, color)
    
    # Build dimension table rows HTML
    dimension_table_rows = ""
    for name, score in zip(dimension_names, dimension_scores_list):
        color = dimension_colors.get(name, '#999')
        score = float(score) if score else 0.0
        status = "✅ Strong" if score >= 4 else "✓ Good" if score >= 3 else "⚠ Needs Work"
        dimension_table_rows += '''
                    <tr>
                        <td>{0}</td>
                        <td style="font-weight: bold; color: {1};">{2:.1f} / 5.0</td>
                        <td>{3}</td>
                    </tr>
                    '''.format(name, color, score, status)
    
    html = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Process Readiness Assessment Report</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #333;
            line-height: 1.6;
            background: white;
        }
        
        @page {
            size: A4;
            margin: 1cm;
        }
        
        @media print {
            body { margin: 0; padding: 0; }
            .page { page-break-after: always; margin: 0; padding: 2cm 1.5cm; }
            .page:last-child { page-break-after: avoid; }
        }
        
        .page {
            width: 8.5in;
            height: 11in;
            margin: 0 auto;
            padding: 0.75in;
            background: white;
            position: relative;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            page-break-after: always;
        }
        
        .page-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 20px;
            border-bottom: 3px solid {primary_color};
            margin-bottom: 30px;
        }
        
        .header-left {
            flex: 1;
        }
        
        .header-right {
            flex: 0 0 80px;
            text-align: right;
        }
        
        .page-footer {
            position: absolute;
            bottom: 0.5in;
            left: 0.75in;
            right: 0.75in;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-top: 1px solid #ddd;
            padding-top: 10px;
            font-size: 0.85em;
            color: #666;
        }
        
        .page-number {
            text-align: right;
        }
        
        .company-info {
            font-size: 0.9em;
            text-align: center;
            color: #666;
        }
        
        h1 {
            color: {primary_color};
            font-size: 28px;
            margin-bottom: 10px;
        }
        
        h2 {
            color: {primary_color};
            font-size: 20px;
            margin-top: 20px;
            margin-bottom: 15px;
            border-bottom: 2px solid {primary_color};
            padding-bottom: 10px;
        }
        
        h3 {
            color: {primary_color};
            font-size: 16px;
            margin-top: 15px;
            margin-bottom: 10px;
        }
        
        .score-box {
            background: linear-gradient(135deg, {primary_color}15, {primary_color}05);
            border-left: 4px solid {primary_color};
            padding: 15px;
            margin: 15px 0;
            border-radius: 4px;
        }
        
        .score-grid {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 15px;
            margin: 20px 0;
        }
        
        .score-card {
            background: #f8f8f8;
            border: 1px solid #ddd;
            padding: 15px;
            border-radius: 4px;
            text-align: center;
        }
        
        .score-card-label {
            font-size: 0.9em;
            color: #666;
            margin-bottom: 5px;
        }
        
        .score-card-value {
            font-size: 24px;
            font-weight: bold;
            color: {primary_color};
        }
        
        .score-card-sublabel {
            font-size: 0.85em;
            color: {readiness_color};
            margin-top: 5px;
        }
        
        .dimension-item {
            margin: 12px 0;
            padding: 10px;
            background: #f9f9f9;
            border-left: 4px solid;
            border-radius: 2px;
        }
        
        .dimension-name {
            font-weight: 600;
            color: #333;
            margin-bottom: 5px;
        }
        
        .dimension-score {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .score-text {
            font-size: 0.95em;
        }
        
        .score-bar {
            flex: 1;
            height: 20px;
            background: #e0e0e0;
            border-radius: 10px;
            margin: 0 10px;
            overflow: hidden;
        }
        
        .score-fill {
            height: 100%;
            border-radius: 10px;
            transition: width 0.3s ease;
        }
        
        .readiness-badge {
            display: inline-block;
            padding: 8px 16px;
            background-color: {readiness_color};
            color: white;
            border-radius: 4px;
            font-weight: bold;
            font-size: 0.95em;
        }
        
        .readiness-description {
            color: #666;
            font-size: 0.95em;
            margin-top: 8px;
            font-style: italic;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            font-size: 0.9em;
        }
        
        th {
            background-color: {primary_color}20;
            border-bottom: 2px solid {primary_color};
            padding: 10px;
            text-align: left;
            color: {primary_color};
            font-weight: 600;
        }
        
        td {
            border-bottom: 1px solid #e0e0e0;
            padding: 10px;
        }
        
        tr:hover {
            background-color: #f5f5f5;
        }
        
        .content {
            height: auto;
            padding-bottom: 40px;
        }
        
        .page-1 .content {
            height: auto;
        }
        
        ul {
            margin-left: 20px;
        }
        
        li {
            margin-bottom: 8px;
        }
    </style>
</head>
<body>
    <div class="page page-1">
        <div class="page-header">
            <div class="header-left">
                <h1>AI-Enabled Process Readiness Assessment</h1>
                <p style="color: #666; margin-top: 5px; font-size: 0.95em;">Report for {company_name}</p>
                <p style="color: #999; font-size: 0.85em; margin-top: 3px;">{current_date}</p>
            </div>
            <div class="header-right">
                {logo_html}
            </div>
        </div>
        
        <div class="content">
            <h2>Executive Summary</h2>
            
            <div class="score-grid">
                <div class="score-card">
                    <div class="score-card-label">Overall Score</div>
                    <div class="score-card-value">{overall_score:.1f}</div>
                    <div class="score-card-sublabel">out of 30</div>
                </div>
                <div class="score-card">
                    <div class="score-card-label">Readiness %</div>
                    <div class="score-card-value">{percentage}%</div>
                    <div class="score-card-sublabel">completion</div>
                </div>
                <div class="score-card">
                    <div class="score-card-label">Readiness Level</div>
                    <div class="score-card-value" style="font-size: 18px; color: {readiness_color};">{readiness_label}</div>
                    <div class="score-card-sublabel">{readiness_desc}</div>
                </div>
            </div>
            
            <div class="score-box">
                <h3>Assessment Interpretation</h3>
                <p>Your organization scored <strong>{overall_score:.1f} out of 30</strong>, placing you in the <strong>{readiness_label}</strong> readiness band. 
                <strong>{readiness_desc}</strong> This assessment evaluates your organization's preparedness for adopting and rolling out AI at scale across 
                six critical dimensions including process maturity, technology infrastructure, data readiness, people and culture, leadership alignment, and governance. 
                The insights provided highlight your current capabilities and identify priority areas for advancement.</p>
            </div>
        </div>
        
        <div class="page-footer">
            <div>www.tlogic.consulting</div>
            <div class="company-info">© T-Logic Consulting Pvt. Ltd.</div>
            <div class="page-number">Page 1</div>
        </div>
    </div>
    
    <div class="page page-2">
        <div class="page-header">
            <div class="header-left">
                <h1 style="font-size: 22px;">Dimension Breakdown</h1>
            </div>
            <div class="header-right">
                {logo_html}
            </div>
        </div>
        
        <div class="content">
            <p style="margin-bottom: 15px; color: #666;">Your scores across the six dimensions of AI readiness:</p>
            
            {dimension_items_html}
            
            <h2 style="margin-top: 30px;">Summary by Dimension</h2>
            
            <table>
                <thead>
                    <tr>
                        <th>Dimension</th>
                        <th>Score</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {dimension_table_rows}
                </tbody>
            </table>
        </div>
        
        <div class="page-footer">
            <div>www.tlogic.consulting</div>
            <div class="company-info">© T-Logic Consulting Pvt. Ltd.</div>
            <div class="page-number">Page 2</div>
        </div>
    </div>
    
    <div class="page page-3">
        <div class="page-header">
            <div class="header-left">
                <h1 style="font-size: 22px;">Next Steps</h1>
            </div>
            <div class="header-right">
                {logo_html}
            </div>
        </div>
        
        <div class="content">
            <h2>Recommended Actions</h2>
            
            <div class="score-box">
                <h3>Your Readiness Profile: {readiness_label}</h3>
                <p>{readiness_desc}</p>
                <p style="margin-top: 10px;">Based on your assessment results, here are key areas to focus on:</p>
            </div>
            
            <h3>Immediate Priority Areas</h3>
            <ul style="margin-bottom: 20px;">
                <li>Evaluate your organization's readiness across all dimensions</li>
                <li>Prioritize improvements in your lowest-scoring dimensions</li>
                <li>Develop an action plan with clear milestones and timelines</li>
                <li>Identify quick wins that can build momentum for change</li>
                <li>Engage stakeholders and ensure alignment on AI transformation goals</li>
            </ul>
            
            <div class="score-box">
                <h3>Get Expert Support</h3>
                <p>T-Logic specializes in helping organizations like yours accelerate their AI readiness journey. Our team can provide:</p>
                <ul style="margin-top: 10px;">
                    <li>Detailed assessment consultation</li>
                    <li>Customized implementation roadmaps</li>
                    <li>Change management support</li>
                    <li>Process optimization and AI integration</li>
                </ul>
                <p style="margin-top: 15px; font-weight: bold;">Contact us at: tej@tlogic.consulting</p>
            </div>
        </div>
        
        <div class="page-footer">
            <div>www.tlogic.consulting</div>
            <div class="company-info">© T-Logic Consulting Pvt. Ltd.</div>
            <div class="page-number">Page 3</div>
        </div>
    </div>
</body>
</html>'''

    # Safe string replacement to avoid format string issues
    readiness_desc = readiness_band.get('description', '')
    html = html.replace('{primary_color}', primary_color)
    html = html.replace('{readiness_color}', readiness_color)
    html = html.replace('{company_name}', company_name)
    html = html.replace('{current_date}', current_date)
    html = html.replace('{overall_score:.1f}', str(round(overall_score, 1)))
    html = html.replace('{percentage}', str(percentage))
    html = html.replace('{readiness_label}', readiness_label)
    html = html.replace('{readiness_desc}', readiness_desc)
    html = html.replace('{logo_html}', logo_html)
    html = html.replace('{dimension_items_html}', dimension_items_html)
    html = html.replace('{dimension_table_rows}', dimension_table_rows)
    
    return html
