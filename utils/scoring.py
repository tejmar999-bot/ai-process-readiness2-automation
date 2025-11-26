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
    if total_score < 11:
        return {
            'label': 'Foundational',
            'color': '#DC2626',
            'description': 'Foundation building phase - core AI readiness initiatives beginning with basic infrastructure and organizational awareness.'
        }
    elif total_score < 18:
        return {
            'label': 'Emerging',
            'color': '#EAB308',
            'description': 'Initial implementation phase - pilot projects underway with growing organizational support and foundational AI capabilities established.'
        }
    elif total_score < 25:
        return {
            'label': 'Dependable',
            'color': '#42A5F5',
            'description': 'Scaled deployment phase - proven AI processes operational across multiple areas with strong supporting infrastructure and governance.'
        }
    else:
        return {
            'label': 'Exceptional',
            'color': '#16A34A',
            'description': 'Enterprise AI platform - comprehensive AI rollout with mature governance, scaled operations, and continuous optimization capabilities.'
        }
