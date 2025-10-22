"""Scoring utilities for the AI Process Readiness Assessment"""


def compute_scores(answers):
    """
    Compute scores for each dimension and total score.
    
    Args:
        answers: Dictionary with keys like '0-0', '0-1', etc.
                 where first number is dimension, second is question
    
    Returns:
        Dictionary with dimension_scores (list), total score, percentage, and readiness_band
    """
    dimension_scores = []
    
    # There are 6 dimensions, each with 5 questions
    for dim in range(6):
        dim_total = 0
        question_count = 0
        
        for q in range(5):
            key = f"{dim}-{q}"
            if key in answers:
                dim_total += answers[key]
                question_count += 1
        
        # Calculate average for this dimension (out of 5)
        if question_count > 0:
            dim_score = dim_total / question_count
        else:
            dim_score = 0
        
        dimension_scores.append(round(dim_score, 1))
    
    # Total score is sum of all dimension scores
    total_score = sum(dimension_scores)
    total_score_rounded = round(total_score, 1)
    percentage = round((total_score / 30) * 100)  # 30 is max (6 dimensions * 5)
    
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
    Determine readiness band based on total score.
    
    Args:
        total_score: Total score out of 30
    
    Returns:
        Dictionary with label, color, and description
    """
    percentage = (total_score / 30) * 100
    
    if percentage < 40:
        return {
            'label': 'Not Ready',
            'color': '#EF4444',  # Red
            'description': 'Significant gaps exist in AI readiness. Focus on foundational improvements.'
        }
    elif percentage < 60:
        return {
            'label': 'Emerging',
            'color': '#F59E0B',  # Orange
            'description': 'Basic foundations in place, but substantial work needed for AI implementation.'
        }
    elif percentage < 80:
        return {
            'label': 'Ready',
            'color': '#3B82F6',  # Blue
            'description': 'Strong foundation for AI adoption. Address remaining gaps for optimal results.'
        }
    else:
        return {
            'label': 'Advanced',
            'color': '#10B981',  # Green
            'description': 'Excellent readiness for AI implementation. Well-positioned for success.'
        }
