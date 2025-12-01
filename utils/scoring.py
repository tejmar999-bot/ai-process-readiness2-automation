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
    
    # Identify strong and weak dimensions with scores
    avg_score = sum(raw_scores) / len(raw_scores)
    strong_dims = [(dimension_names[i], raw_scores[i]) for i, score in enumerate(raw_scores) if score > avg_score + 1]
    weak_dims = [(dimension_names[i], raw_scores[i]) for i, score in enumerate(raw_scores) if score < avg_score - 1]
    
    # Get critical dimension info
    data_readiness = raw_scores[2]
    leadership = raw_scores[4]
    
    # Build summary based on readiness level
    if readiness_band['label'].startswith('🟢'):
        # AI-Ready
        if strong_dims:
            top_strong = strong_dims[0][0]
            summary = f"Your organization is well-positioned for AI success, with {top_strong} ({strong_dims[0][1]:.1f}/15) showing particular strength. You've built the fundamentals needed for effective AI deployment. Now focus on execution: identify 1-2 high-impact use cases aligned with business goals, establish clear success metrics, and launch pilots with executive sponsorship to validate your approach."
        else:
            summary = f"Your organization demonstrates strong, balanced capabilities across all dimensions. You've built the fundamentals needed for effective AI deployment. Now focus on execution: identify 1-2 high-impact use cases aligned with business goals, establish clear success metrics, and launch pilots with executive sponsorship to demonstrate AI's business value."
    elif readiness_band['label'].startswith('🔵'):
        # Building Blocks
        if weak_dims:
            weakest = weak_dims[0]
            weak_list = ', '.join([d[0] for d in weak_dims])
            summary = f"You have core foundational pieces in place, but {weakest[0]} ({weakest[1]:.1f}/15) and a few other areas need targeted attention. Prioritize strengthening {weak_list} before scaling AI initiatives. Set specific improvement goals for each weak area, assign ownership, and plan to reassess in 3-6 months when you've made meaningful progress."
        else:
            summary = f"You have core foundational pieces in place with good overall balance. While each dimension could use some refinement, you're on the right track. Continue incremental improvements across your organization, then reassess in 6 months when you can pursue pilot projects with greater confidence."
    elif readiness_band['label'].startswith('🟡'):
        # Foundational Gaps
        if weak_dims:
            weakest_list = ', '.join([f"{d[0]} ({d[1]:.1f}/15)" for d in weak_dims[:2]])
            summary = f"Significant foundational work is required—{weakest_list} need urgent attention. Don't pursue AI initiatives yet; instead, invest the next 9-12 months on operational excellence. Stabilize your processes, improve data practices, and strengthen leadership alignment. Once these basics are solid, you'll be in a much better position to adopt AI effectively."
        else:
            summary = f"Significant foundational work is required across your organization before AI can deliver value. Invest the next 9-12 months on operational excellence: stabilize your processes, improve data practices, strengthen leadership alignment, and build organizational capability. Once these basics are solid, you'll be ready to explore AI more seriously."
    else:
        # Not Ready
        summary = f"Your organization needs to focus on core operations and business fundamentals first. Plan for 12-18 months of foundational work: streamline and document your key processes, invest in modern technology infrastructure, establish data governance, and build internal capability. Revisit AI readiness after making meaningful progress on these areas."
    
    # Critical dimension note - only add if there's a caution/stop, and don't repeat if already mentioned
    critical_note = ""
    if critical_status['severity'] == 'critical':
        critical_note = f"<strong>Critical Note:</strong> Both Data Readiness and Leadership & Alignment are below the minimum threshold. These two dimensions are foundational to any AI initiative—do not proceed with pilots or implementations until both are strengthened, regardless of your overall score."
    elif critical_status['severity'] == 'warning':
        # Determine which dimension is below threshold
        if data_readiness < 9:
            dim_below = f"Data Readiness ({data_readiness:.1f}/15)"
        else:
            dim_below = f"Leadership & Alignment ({leadership:.1f}/15)"
        critical_note = f"<strong>Important:</strong> {dim_below} is below the recommended threshold of 9. This critical gap must be addressed before scaling any AI initiatives, even though your overall score is in the {readiness_band['label'].split()[1].lower()} range."
    
    # Combine everything
    if critical_note:
        summary += f" {critical_note}"
    
    summary += " For detailed recommendations on improving each dimension, see below. We're here to help—please reach out if you'd like to discuss your results or need guidance."
    
    return summary
