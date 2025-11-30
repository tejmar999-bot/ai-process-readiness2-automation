"""
Scoring utilities for the AI Process Readiness Assessment
Implements Scenario 2: Asymmetric Threshold Weighting
"""

from data.dimensions import DIMENSIONS


def compute_scores(answers):
    """
    Compute scores using Scenario 2: Asymmetric Threshold Weighting.
    
    Critical dimensions (Data Readiness & Leadership) use asymmetric penalties:
    - Score ≥10: No penalty (use raw score)
    - Score 7-9: Moderate penalty (divide by 1.5)
    - Score <7: Severe penalty (divide by 2.5)
    
    Standard dimensions: No adjustment
    
    Args:
        answers: Dictionary with question IDs as keys and scores (1-5) as values
    
    Returns:
        Dictionary with raw and weighted scores, total, percentage, readiness_band,
        critical dimension statuses, and detailed breakdown
    """
    raw_dimension_scores = []
    weighted_dimension_scores = []
    critical_statuses = {}
    
    # Step 1 & 2: Calculate raw scores and apply asymmetric weighting
    for dimension in DIMENSIONS:
        # Calculate raw score (sum of 3 questions = 3-15 range)
        dim_total = 0
        question_count = 0
        
        for question in dimension['questions']:
            question_id = question['id']
            if question_id in answers:
                dim_total += answers[question_id]
                question_count += 1
        
        # Get raw score
        if question_count > 0:
            dim_raw_score = dim_total
        else:
            dim_raw_score = 0
        
        raw_dimension_scores.append(round(dim_raw_score, 1))
        
        # Apply asymmetric weighting for critical dimensions
        dim_id = dimension['id']
        is_critical = dimension.get('critical', False)
        
        if is_critical:
            # Critical dimension weighting
            if dim_raw_score >= 10:
                dim_weighted_score = dim_raw_score  # No penalty
            elif dim_raw_score >= 7:
                dim_weighted_score = dim_raw_score / 1.5  # Moderate penalty
            else:
                dim_weighted_score = dim_raw_score / 2.5  # Severe penalty
            
            # Set critical dimension status
            if dim_raw_score >= 10:
                critical_statuses[dim_id] = {'status': 'Strong', 'emoji': '✓', 'color': '#16A34A'}
            elif dim_raw_score >= 7:
                critical_statuses[dim_id] = {'status': 'Yellow Flag', 'emoji': '⚠', 'color': '#EAB308'}
            else:
                critical_statuses[dim_id] = {'status': 'Red Flag', 'emoji': '❌', 'color': '#DC2626'}
        else:
            # Standard dimension: no adjustment
            dim_weighted_score = dim_raw_score
        
        weighted_dimension_scores.append(round(dim_weighted_score, 1))
    
    # Step 3: Calculate total weighted score
    total_weighted_score = sum(weighted_dimension_scores)
    total_weighted_score_rounded = round(total_weighted_score, 1)
    
    # Step 4: Calculate percentage (out of 90 maximum)
    percentage = round((total_weighted_score_rounded / 90) * 100)
    
    # Step 5: Determine readiness level with gating logic
    data_raw = raw_dimension_scores[2]  # Data Readiness (index 2)
    leadership_raw = raw_dimension_scores[4]  # Leadership & Alignment (index 4)
    
    readiness_band = get_readiness_band_with_gating(
        total_weighted_score_rounded,
        percentage,
        data_raw,
        leadership_raw
    )
    
    return {
        'raw_dimension_scores': raw_dimension_scores,
        'dimension_scores': weighted_dimension_scores,
        'total': total_weighted_score_rounded,
        'percentage': percentage,
        'readiness_band': readiness_band,
        'critical_statuses': critical_statuses,
        'data_readiness_raw': data_raw,
        'leadership_raw': leadership_raw
    }


def get_readiness_band_with_gating(total_score, percentage, data_raw, leadership_raw):
    """
    Determine readiness band with critical dimension gating.
    
    Critical dimensions gate overall readiness:
    - Both critical ≥10: Standard bands apply
    - One critical 7-9: Can reach "AI-Ready with Caution"
    - One critical <7: Capped at "Building Blocks"
    - Both critical <7: Capped at "Foundational Gaps"
    
    Args:
        total_score: Total weighted score (0-90)
        percentage: Percentage (0-100)
        data_raw: Raw Data Readiness score (3-15)
        leadership_raw: Raw Leadership score (3-15)
    
    Returns:
        Dictionary with label, color, and description
    """
    
    # Check critical dimension status
    both_critical_strong = (data_raw >= 10) and (leadership_raw >= 10)
    one_critical_yellow = ((data_raw >= 7 and data_raw < 10) or 
                           (leadership_raw >= 7 and leadership_raw < 10))
    one_critical_red = (data_raw < 7) or (leadership_raw < 7)
    both_critical_red = (data_raw < 7) and (leadership_raw < 7)
    
    # Main gating logic
    if both_critical_strong:
        # Both critical dimensions strong: use standard bands
        if total_score >= 70:
            return {
                'label': 'AI-Ready',
                'color': '#16A34A',
                'description': 'Strong foundation; focus on strategic pilots. Your organization is well-positioned for AI implementation.'
            }
        elif total_score >= 56:
            return {
                'label': 'Building Blocks In Place',
                'color': '#42A5F5',
                'description': 'Address 1-2 weak dimensions before scaling. You have a foundation to build upon with focused improvements.'
            }
        elif total_score >= 42:
            return {
                'label': 'Foundational Gaps',
                'color': '#EAB308',
                'description': 'Significant work needed; start with process and data basics. Address foundational gaps before scaling.'
            }
        else:
            return {
                'label': 'Not Ready',
                'color': '#DC2626',
                'description': 'High risk; focus on business fundamentals first. Significant foundational work required before AI deployment.'
            }
    
    elif one_critical_yellow:
        # One critical dimension is yellow (7-9): can reach "AI-Ready with Caution"
        if percentage >= 70:
            return {
                'label': 'AI-Ready with Caution',
                'color': '#F59E0B',
                'description': 'Addressable gaps in critical dimensions. Proceed with focused improvement plan before scaling; monitor closely.'
            }
        elif percentage >= 56:
            return {
                'label': 'Building Blocks In Place',
                'color': '#42A5F5',
                'description': 'Address 1-2 weak dimensions before scaling. You have a foundation to build upon with focused improvements.'
            }
        else:
            return {
                'label': 'Foundational Gaps',
                'color': '#EAB308',
                'description': 'Significant work needed; start with process and data basics. Address foundational gaps before scaling.'
            }
    
    elif both_critical_red:
        # Both critical dimensions red (<7): capped at Foundational Gaps
        return {
            'label': 'Foundational Gaps (CAPPED)',
            'color': '#EAB308',
            'description': 'Critical gaps in both Data and Leadership. Foundational work required—cannot proceed with AI until both critical dimensions improve.'
        }
    
    else:
        # One critical dimension red (<7): capped at Building Blocks
        if percentage >= 70:
            return {
                'label': 'Building Blocks (CAPPED)',
                'color': '#42A5F5',
                'description': 'Critical gap limiting readiness. Address the weak critical dimension before scaling AI initiatives.'
            }
        elif percentage >= 56:
            return {
                'label': 'Building Blocks',
                'color': '#42A5F5',
                'description': 'Address 1-2 weak dimensions before scaling. You have a foundation to build upon with focused improvements.'
            }
        else:
            return {
                'label': 'Foundational Gaps',
                'color': '#EAB308',
                'description': 'Significant work needed; start with process and data basics. Address foundational gaps before scaling.'
            }


def get_critical_dimension_analysis(data_raw, leadership_raw):
    """
    Get detailed analysis of critical dimension performance.
    
    Args:
        data_raw: Raw Data Readiness score
        leadership_raw: Raw Leadership score
    
    Returns:
        Dictionary with status, recommendations, and risk level for each critical dimension
    """
    analysis = {}
    
    # Data Readiness analysis
    if data_raw >= 10:
        data_status = 'Strong'
        data_risk = 'Low'
        data_rec = 'Maintain current data practices and continue monitoring quality and pipeline reliability.'
    elif data_raw >= 7:
        data_status = 'Yellow Flag'
        data_risk = 'Medium'
        data_rec = 'Prioritize improving data availability, quality, or pipeline reliability before scaling AI initiatives.'
    else:
        data_status = 'Red Flag'
        data_risk = 'High'
        data_rec = 'Critical: Data readiness must be addressed first. AI cannot succeed without reliable, quality data. Consider data infrastructure investments before proceeding.'
    
    analysis['data'] = {
        'dimension': 'Data Readiness',
        'raw_score': data_raw,
        'status': data_status,
        'risk_level': data_risk,
        'recommendation': data_rec
    }
    
    # Leadership & Alignment analysis
    if leadership_raw >= 10:
        leadership_status = 'Strong'
        leadership_risk = 'Low'
        leadership_rec = 'Maintain executive sponsorship and continue strong strategic alignment on AI goals.'
    elif leadership_raw >= 7:
        leadership_status = 'Yellow Flag'
        leadership_risk = 'Medium'
        leadership_rec = 'Increase executive engagement, clarify AI goals, or secure committed budget before scaling.'
    else:
        leadership_status = 'Red Flag'
        leadership_risk = 'High'
        leadership_rec = 'Critical: Without strong leadership alignment, AI initiatives will fail. Secure executive sponsorship, clear goals, and dedicated budget as priority.'
    
    analysis['leadership'] = {
        'dimension': 'Leadership & Alignment',
        'raw_score': leadership_raw,
        'status': leadership_status,
        'risk_level': leadership_risk,
        'recommendation': leadership_rec
    }
    
    return analysis
