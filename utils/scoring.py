"""
Scoring utilities for the AI Process Readiness Assessment
Simplified approach: Direct sum of raw scores with critical dimension warnings
"""

from data.dimensions import DIMENSIONS


def compute_scores(answers):
    """
    Compute scores using simplified approach.
    
    - Raw score per dimension = sum of 3 questions (3-15 range)
    - Total score = sum of all 6 raw scores (max 90)
    - Readiness level based on total score only
    - Critical dimension warnings (Data & Leadership) are separate UI elements
    
    Args:
        answers: Dictionary with question IDs as keys and scores (1-5) as values
    
    Returns:
        Dictionary with raw_dimension_scores, total, percentage, readiness_band, and critical_status
    """
    raw_dimension_scores = []
    
    # Calculate raw scores for each dimension
    for dimension in DIMENSIONS:
        dim_total = 0
        question_count = 0
        
        for question in dimension['questions']:
            question_id = question['id']
            if question_id in answers:
                dim_total += answers[question_id]
                question_count += 1
        
        # Raw score (3-15 range)
        if question_count > 0:
            dim_raw_score = dim_total
        else:
            dim_raw_score = 0
        
        raw_dimension_scores.append(round(dim_raw_score, 1))
    
    # Calculate total score (simple sum, max 90)
    total_score = sum(raw_dimension_scores)
    total_score_rounded = round(total_score, 1)
    
    # Calculate percentage
    percentage = round((total_score_rounded / 90) * 100)
    
    # Get critical dimension scores
    data_readiness = raw_dimension_scores[2]  # Index 2
    leadership = raw_dimension_scores[4]  # Index 4
    
    # Determine readiness level based on total score only
    readiness_band = get_readiness_band(total_score_rounded)
    
    # Determine critical dimension status
    critical_status = get_critical_dimension_status(data_readiness, leadership)
    
    return {
        'raw_dimension_scores': raw_dimension_scores,
        'dimension_scores': raw_dimension_scores,  # Same as raw (no weighting)
        'total': total_score_rounded,
        'percentage': percentage,
        'readiness_band': readiness_band,
        'critical_status': critical_status,
        'data_readiness': data_readiness,
        'leadership': leadership
    }


def get_readiness_band(total_score):
    """
    Determine readiness level based on total score only.
    
    Args:
        total_score: Total score out of 90
    
    Returns:
        Dictionary with label, emoji, color, description, and next_steps
    """
    if total_score >= 70:
        return {
            'label': '🟢 AI-Ready',
            'emoji': '🟢',
            'color': '#10B981',
            'description': 'Strong foundation for AI implementation. Begin strategic pilots with confidence.',
            'next_steps': 'Select 1-2 high-value use cases, establish success metrics, launch pilots'
        }
    elif total_score >= 56:
        return {
            'label': '🔵 Building Blocks',
            'emoji': '🔵',
            'color': '#3B82F6',
            'description': 'Foundational elements in place, but improvements needed before scaling.',
            'next_steps': 'Strengthen weak dimensions over 3-6 months, then reassess'
        }
    elif total_score >= 42:
        return {
            'label': '🟡 Foundational Gaps',
            'emoji': '🟡',
            'color': '#FBBF24',
            'description': 'Significant foundational work needed before AI can deliver value.',
            'next_steps': 'Focus on business fundamentals for 9-12 months, not AI'
        }
    else:
        return {
            'label': '🔴 Not Ready',
            'emoji': '🔴',
            'color': '#DC2626',
            'description': 'Focus on core operations before considering AI.',
            'next_steps': 'Improve processes, data, infrastructure (12-18 months)'
        }


def get_critical_dimension_status(data_readiness, leadership):
    """
    Determine critical dimension status for UI display.
    
    Args:
        data_readiness: Raw score for Data Readiness (3-15)
        leadership: Raw score for Leadership & Alignment (3-15)
    
    Returns:
        Dictionary with status, icon, message, and color
    """
    if data_readiness < 9 and leadership < 9:
        # Both critical dimensions below threshold - STOP
        return {
            'status': 'stop',
            'icon': '🛑',
            'title': 'CRITICAL: Do Not Proceed',
            'message': f'Both critical dimensions are below threshold. Data Readiness: {data_readiness:.1f}/15 | Leadership & Alignment: {leadership:.1f}/15. Address these immediately before any AI initiatives.',
            'color': '#DC2626',
            'severity': 'critical'
        }
    elif data_readiness < 9 or leadership < 9:
        # One critical dimension below threshold - WARNING
        if data_readiness < 9:
            dim_name = 'Data Readiness'
            dim_score = data_readiness
        else:
            dim_name = 'Leadership & Alignment'
            dim_score = leadership
        
        return {
            'status': 'warning',
            'icon': '⚠️',
            'title': 'WARNING: Critical Dimension Below Threshold',
            'message': f'{dim_name} scored {dim_score:.1f}/15 (needs ≥9). This must be addressed before scaling AI initiatives.',
            'color': '#F59E0B',
            'severity': 'warning'
        }
    else:
        # Both critical dimensions meet threshold - READY
        return {
            'status': 'ready',
            'icon': '✓',
            'title': 'Critical Dimensions: READY',
            'message': f'Data Readiness: {data_readiness:.1f}/15 ✓ | Leadership & Alignment: {leadership:.1f}/15 ✓',
            'color': '#10B981',
            'severity': 'info'
        }


def generate_executive_summary(scores_data):
    """
    Generate executive summary text based on assessment scores.
    
    Args:
        scores_data: Dictionary with scores, readiness band, and critical status
    
    Returns:
        String with executive summary
    """
    raw_scores = scores_data['raw_dimension_scores']
    total_score = scores_data['total']
    readiness_band = scores_data['readiness_band']
    critical_status = scores_data['critical_status']
    
    # Dimension names
    dimension_names = ['Process Maturity', 'Technology Infrastructure', 'Data Readiness', 'People & Culture', 'Leadership & Alignment', 'Governance & Risk']
    
    # Identify strong and weak dimensions
    avg_score = sum(raw_scores) / len(raw_scores)
    strong_dims = [dimension_names[i] for i, score in enumerate(raw_scores) if score > avg_score + 1]
    weak_dims = [dimension_names[i] for i, score in enumerate(raw_scores) if score < avg_score - 1]
    
    # Build summary based on readiness level
    if readiness_band['label'].startswith('🟢'):
        # AI-Ready
        strengths = f"Across the board, your organization shows strong capabilities. Your {', '.join(strong_dims) if strong_dims else 'key dimensions'} are particularly well-developed."
        next_steps = "Begin strategic pilots with confidence. Select 1-2 high-value use cases, establish clear success metrics, and launch pilots to demonstrate AI's business impact."
    elif readiness_band['label'].startswith('🔵'):
        # Building Blocks
        if weak_dims:
            weak_list = ', '.join(weak_dims)
            strengths = f"You have foundational elements in place. Focus on strengthening {weak_list} over the next 3-6 months to accelerate your AI readiness."
        else:
            strengths = "You have foundational elements in place with good balance across dimensions."
        next_steps = "Build on your foundation by addressing identified gaps. Plan targeted improvements for the next 3-6 months, then reassess before scaling."
    elif readiness_band['label'].startswith('🟡'):
        # Foundational Gaps
        if weak_dims:
            weak_list = ', '.join(weak_dims[:2])  # Show top 2
            strengths = f"Significant foundational work is needed. Weak areas include {weak_list}. Focus on business fundamentals rather than AI implementation at this time."
        else:
            strengths = "Significant foundational work is needed across multiple dimensions. Focus on business fundamentals rather than AI implementation at this time."
        next_steps = "Invest 9-12 months improving your core operations, data quality, and organizational alignment. Build a strong foundation before pursuing AI initiatives."
    else:
        # Not Ready
        strengths = "Your organization needs foundational improvements across multiple areas before AI can deliver meaningful value."
        next_steps = "Focus on core operations, process optimization, and data infrastructure first. Plan for 12-18 months of foundational work before reconsidering AI initiatives."
    
    # Critical dimension note
    critical_note = ""
    if critical_status['severity'] == 'critical':
        critical_note = f"<strong>Important: {critical_status['icon']} Both critical dimensions are below threshold.</strong> {critical_status['message'].split('Address')[1].strip() if 'Address' in critical_status['message'] else ''} Proceed with caution—do not scale AI initiatives until these are addressed, regardless of overall score."
    elif critical_status['severity'] == 'warning':
        critical_note = f"<strong>Caution: {critical_status['icon']} One critical dimension needs attention.</strong> {critical_status['message'].split('This')[1].strip() if 'This' in critical_status['message'] else ''} Address this before scaling, despite your overall score."
    
    # Combine everything
    summary = f"{strengths} {next_steps}"
    if critical_note:
        summary += f" {critical_note}"
    
    summary += " For more detailed recommendations on each dimension, please see below. As always, feel free to reach out to us for any assistance!"
    
    return summary
