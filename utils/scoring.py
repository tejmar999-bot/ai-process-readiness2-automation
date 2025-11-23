"""Scoring utilities for the AI Process Readiness Assessment"""

from data.dimensions import DIMENSIONS


def compute_scores(answers):
    """
    Compute scores for each dimension and total score.
    
    Args:
        answers: Dictionary with question IDs as keys (e.g., 'proc_doc', 'data_quality')
                 and scores (1-5) as values
    
    Returns:
        Dictionary with dimension_scores (list), total score, percentage, and readiness_band
    """
    dimension_scores = []
    
    # Calculate score for each dimension based on its questions
    for dimension in DIMENSIONS:
        dim_total = 0
        question_count = 0
        
        for question in dimension['questions']:
            question_id = question['id']
            if question_id in answers:
                dim_total += answers[question_id]
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
            "label": "Foundational",
            "description": "First critical steps being laid.",
            "color": "#FFC107",   # Amber
        }
    elif percentage < 60:
        return {
            "label": "Emerging",
            "description": "Progress being made.",
            "color": "#FF8A65",   # Soft Coral
        }
    elif percentage < 80:
        return {
            "label": "Reliable",
            "description": "Consistent and dependable.",
            "color": "#42A5F5",   # Soft Blue
        }
    else:
        return {
            "label": "Exceptional",
            "description": "Best-in-class process performance.",
            "color": "#4CAF50",   # Vibrant Green
        }
