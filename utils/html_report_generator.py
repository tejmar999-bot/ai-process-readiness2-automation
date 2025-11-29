"""
HTML/Text report generator for T-Logic AI-Enabled Process Readiness results.
Generates a professional, printable HTML report with company branding.
"""
from datetime import datetime

# Recommendations map for each dimension
RECOMMENDATIONS_MAP = {
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
    'governance': [
        "Establish formal governance structures for AI decision-making and oversight",
        "Develop comprehensive AI risk assessment and mitigation frameworks",
        "Create and enforce compliance guardrails throughout AI processes",
        "Define clear roles and responsibilities for AI initiatives",
        "Implement continuous monitoring and auditing of AI systems"
    ]
}


def generate_html_report(
    results: dict,
    company_name: str = "Your Company",
    company_logo_b64=None,
    primary_color: str = "#BF6A16",
    benchmark_comparison=None
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
    
    # Use "Your Company" as default if company_name is empty
    if not company_name or company_name.strip() == "":
        company_name = "Your Company"
    
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
    
    # Build benchmark table HTML
    benchmark_table_html = ""
    benchmark_title = ""
    if benchmark_comparison:
        your_total = benchmark_comparison.get('your_total', overall_score)
        benchmark_total = benchmark_comparison.get('benchmark_total', 18.4)
        benchmark_title = f"Your Scores vs. Benchmark Scores ({your_total:.1f} vs. Benchmark of {benchmark_total:.1f} overall)"
        
        benchmark_table_html = '<table style="background-color: #f0f0f0; font-size: 0.8em; margin: 0;"><thead><tr><th style="background-color: #e0e0e0; color: black; padding: 6px;">Dimension</th><th style="background-color: #e0e0e0; color: black; padding: 6px;">Your Score</th><th style="background-color: #e0e0e0; color: black; padding: 6px;">Benchmark</th><th style="background-color: #e0e0e0; color: black; padding: 6px;">Difference</th><th style="background-color: #e0e0e0; color: black; padding: 6px;">Status</th></tr></thead><tbody>'
        
        for dim in benchmark_comparison.get('dimensions', []):
            your_score = dim.get('your_score', 0)
            bench_score = dim.get('benchmark_score', 0)
            diff = dim.get('difference', 0)
            
            # Status icons and colors based on difference
            if diff < 0:
                status = "⚠️"
                color = '#DC2626'
            elif diff == 0 or (diff > -0.2 and diff < 0.2):
                status = "✓"
                color = 'black'
            else:
                status = "✅"
                color = '#16A34A'
            
            benchmark_table_html += f'<tr style="background-color: #f9f9f9; color: black;"><td style="color: black; padding: 5px;">{dim.get("title", "")}</td><td style="color: black; font-weight: bold; padding: 5px;">{your_score:.1f}/5</td><td style="color: black; padding: 5px;">{bench_score:.1f}/5</td><td style="color: {color}; font-weight: bold; padding: 5px;">{diff:+.1f}</td><td style="color: {color}; text-align: center; font-weight: bold; padding: 5px;">{status}</td></tr>'
        
        benchmark_table_html += '</tbody></table>'
    
    # Build dimension table rows HTML (no longer used but kept for compatibility)
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
            padding: 15px 20px;
            border-bottom: 3px solid {primary_color};
            margin-bottom: 30px;
            background-color: #4B5563;
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
            color: #FF8C00;
            font-size: 28px;
            margin-bottom: 10px;
        }
        
        h2 {
            color: {primary_color};
            font-size: 18px;
            margin-top: 15px;
            margin-bottom: 10px;
            border-bottom: 2px solid {primary_color};
            padding-bottom: 8px;
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
            margin: 2px 0;
            padding: 2px 10px;
            background: #f9f9f9;
            border-left: 16px solid;
            border-radius: 2px;
            transform: scale(0.765);
            transform-origin: left;
        }
        
        .report-subtitle {
            font-size: 14px;
            font-weight: normal;
            color: #E5E7EB;
            margin-top: 5px;
            margin-bottom: 0;
        }
        
        .dimension-name {
            font-weight: 600;
            color: #333;
            margin-bottom: 3px;
            font-size: 1.05em;
        }
        
        .dimension-score {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .score-text {
            font-size: 0.95em;
            font-weight: 500;
        }
        
        .score-bar {
            flex: 1;
            height: 12px;
            background: #e0e0e0;
            border-radius: 6px;
            margin: 0 4px;
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
                <p class="report-subtitle">Report for {company_name}</p>
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
                <p style="margin-top: 12px; font-size: 0.85em; color: #666; font-style: italic;"><strong>Note:</strong> These results are based on subjective assessments and do not necessarily serve as a substitute for AI implementation preparedness using a more thorough investigation of the organization's capabilities and performance.</p>
            </div>
        </div>
        
        <div class="page-footer">
            <div>www.tlogic.consulting</div>
            <div class="company-info">© T-Logic Consulting Pvt. Ltd.</div>
            <div class="page-number">Pg. 1/3</div>
        </div>
    </div>
    
    <div class="page page-2">
        <div class="page-header">
            <div class="header-left">
                <h1 style="font-size: 22px;">Dimension Breakdown</h1>
                <p class="report-subtitle">Report for {company_name}</p>
            </div>
            <div class="header-right">
                {logo_html}
            </div>
        </div>
        
        <div class="content">
            <h2>Your Scores Across All Dimensions</h2>
            <p style="margin-bottom: 12px; color: #666;">Your scores across the six dimensions of AI readiness:</p>
            
            {dimension_items_html}
            
            <h2 style="margin-top: 12px; margin-bottom: 8px;">{benchmark_title}</h2>
            {benchmark_table_html}
        </div>
        
        <div class="page-footer">
            <div>www.tlogic.consulting</div>
            <div class="company-info">© T-Logic Consulting Pvt. Ltd.</div>
            <div class="page-number">Pg. 2/3</div>
        </div>
    </div>
    
    <div class="page page-3">
        <div class="page-header">
            <div class="header-left">
                <h1 style="font-size: 22px;">Next Steps</h1>
                <p class="report-subtitle">Report for {company_name}</p>
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
            <div class="page-number">Pg. 3/3</div>
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
    html = html.replace('{benchmark_title}', benchmark_title)
    html = html.replace('{benchmark_table_html}', benchmark_table_html)
    
    return html
