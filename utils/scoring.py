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
            'label': '🟠 Building Blocks',
            'emoji': '🟠',
            'color': '#F59E0B',
            'description': 'Foundational elements in place, but improvements needed before scaling.',
            'next_steps': 'Strengthen weak dimensions over 3-6 months, then reassess'
        }
    elif total_score >= 42:
        return {
            'label': '🔴 Foundational Gaps',
            'emoji': '🔴',
            'color': '#EF4444',
            'description': 'Significant foundational work needed before AI can deliver value.',
            'next_steps': 'Focus on business fundamentals for 9-12 months, not AI'
        }
    else:
        return {
            'label': '⛔ Not Ready',
            'emoji': '⛔',
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
    if data_readiness < 10 and leadership < 10:
        # Both critical dimensions below threshold - STOP
        return {
            'status': 'stop',
            'icon': '🛑',
            'title': 'CRITICAL: Do Not Proceed',
            'message': f'Both critical dimensions are below threshold. Data Readiness: {data_readiness:.1f}/15 | Leadership & Alignment: {leadership:.1f}/15. Address these immediately before any AI initiatives.',
            'color': '#DC2626',
            'severity': 'critical'
        }
    elif data_readiness < 10 or leadership < 10:
        # One critical dimension below threshold - WARNING
        if data_readiness < 10:
            dim_name = 'Data Readiness'
            dim_score = data_readiness
        else:
            dim_name = 'Leadership & Alignment'
            dim_score = leadership
        
        return {
            'status': 'warning',
            'icon': '⚠️',
            'title': 'WARNING: Critical Dimension Below Threshold',
            'message': f'{dim_name} scored {dim_score:.1f}/15 (needs ≥10). This must be addressed before scaling AI initiatives.',
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
