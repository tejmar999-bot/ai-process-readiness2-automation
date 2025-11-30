"""Scoring utilities for the AI Process Readiness Assessment"""

from data.dimensions import DIMENSIONS


def compute_scores(answers):
    """
    Compute weighted scores for each dimension and total score.
    
    Args:
        answers: Dictionary with question IDs as keys and scores (1-5) as values
    
    Returns:
        Dictionary with dimension_scores (list), total score, percentage, and readiness_band
    """
    dimension_scores = []
    total_weighted_score = 0
    
    # Calculate weighted score for each dimension based on its questions
    for dimension in DIMENSIONS:
        dim_total = 0
        question_count = 0
        
        for question in dimension['questions']:
            question_id = question['id']
            if question_id in answers:
                dim_total += answers[question_id]
                question_count += 1
        
        # Calculate raw score for this dimension (sum of 3 questions)
        if question_count > 0:
            dim_raw_score = dim_total  # Sum of the 3 questions (3-15 range)
        else:
            dim_raw_score = 0
        
        # Apply weight to get weighted score
        weight = dimension.get('weight', 1.0)
        dim_weighted_score = dim_raw_score * weight
        
        # Store weighted score as the dimension score
        dimension_scores.append(round(dim_weighted_score, 1))
        total_weighted_score += dim_weighted_score
    
    # Total score is sum of all weighted dimension scores (max 270)
    total_score_rounded = round(total_weighted_score, 1)
    percentage = round((total_score_rounded / 270) * 100)  # Max is 270
    
    # Get readiness band
    readiness_band = get_readiness_band(total_score_rounded)
    
    return {
        'dimension_scores': dimension_scores,
        'total': total_score_rounded,
        'percentage': percentage,
        'readiness_band': readiness_band
    }


def get_readiness_band(total_score):
    """
    Determine readiness band based on total weighted score.
    
    Args:
        total_score: Total weighted score out of 270
    
    Returns:
        Dictionary with label, color, and description
    """
    if total_score < 90:
        return {
            'label': 'Not Ready',
            'color': '#DC2626',
            'description': 'High risk; focus on business fundamentals first. Significant foundational work required before AI deployment.'
        }
    elif total_score < 135:
        return {
            'label': 'Foundational Gaps',
            'color': '#EAB308',
            'description': 'Significant work needed; start with process and data basics. Address foundational gaps before scaling.'
        }
    elif total_score < 180:
        return {
            'label': 'Building Blocks In Place',
            'color': '#42A5F5',
            'description': 'Address 1-2 weak dimensions before scaling. You have a foundation to build upon with focused improvements.'
        }
    else:
        return {
            'label': 'AI-Ready',
            'color': '#16A34A',
            'description': 'Strong foundation; focus on strategic pilots. Your organization is well-positioned for AI implementation.'
        }
