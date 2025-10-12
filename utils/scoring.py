"""
Scoring utilities for AI Process Readiness Assessment
"""
from typing import Dict, List, Any
from data.dimensions import DIMENSIONS

def compute_scores(answers: Dict[str, int]) -> Dict[str, Any]:
    """
    Calculate dimension scores and overall readiness metrics
    
    Args:
        answers: Dictionary mapping question IDs to scores (1-5)
        
    Returns:
        Dictionary containing dimension scores, total, percentage, and readiness band
    """
    dimension_scores = []
    
    for dimension in DIMENSIONS:
        # Get scores for this dimension's questions
        question_scores = []
        for question in dimension['questions']:
            score = answers.get(question['id'], 3)  # Default to neutral if not answered
            question_scores.append(score)
        
        # Calculate average score for this dimension
        if question_scores:
            avg_score = sum(question_scores) / len(question_scores)
            rounded_score = round(avg_score)
        else:
            rounded_score = 3  # Default neutral
        
        dimension_scores.append({
            'id': dimension['id'],
            'title': dimension['title'],
            'score': rounded_score
        })
    
    # Calculate total score
    total_score = sum(score['score'] for score in dimension_scores)
    
    # Calculate percentage (simple percentage out of 30 max)
    percentage = round((total_score / 30) * 100)
    
    # Determine readiness band
    readiness_band = get_readiness_band(total_score)
    
    return {
        'dimension_scores': dimension_scores,
        'total': total_score,
        'percentage': percentage,
        'readiness_band': readiness_band
    }

def get_readiness_band(total_score: int) -> Dict[str, str]:
    """
    Determine readiness band based on total score
    
    Args:
        total_score: Sum of all dimension scores
        
    Returns:
        Dictionary with label and color for the readiness band
    """
    if total_score >= 25:
        return {'label': 'Advanced', 'color': '#16A34A'}  # Green
    elif total_score >= 18:
        return {'label': 'Ready', 'color': '#F59E0B'}     # Yellow
    elif total_score >= 11:
        return {'label': 'Emerging', 'color': '#FB923C'}   # Orange
    else:
        return {'label': 'Not Ready', 'color': '#E11D48'}  # Red

def calculate_dimension_average(answers: Dict[str, int], dimension_id: str) -> float:
    """
    Calculate average score for a specific dimension
    
    Args:
        answers: Dictionary mapping question IDs to scores
        dimension_id: ID of the dimension to calculate average for
        
    Returns:
        Average score for the dimension
    """
    dimension = next((d for d in DIMENSIONS if d['id'] == dimension_id), None)
    if not dimension:
        return 0.0
    
    scores = []
    for question in dimension['questions']:
        score = answers.get(question['id'], 3)
        scores.append(score)
    
    return sum(scores) / len(scores) if scores else 0.0

def get_recommendations(dimension_scores: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """
    Generate recommendations based on dimension scores
    
    Args:
        dimension_scores: List of dimension score dictionaries
        
    Returns:
        Dictionary mapping dimension IDs to recommendation lists
    """
    recommendations = {}
    
    for score_data in dimension_scores:
        dimension_id = score_data['id']
        score = score_data['score']
        
        # Find the dimension definition
        dimension = next((d for d in DIMENSIONS if d['id'] == dimension_id), None)
        if not dimension:
            continue
        
        recs = []
        
        if score <= 2:  # Low scores need fundamental improvements
            if dimension_id == 'process':
                recs = [
                    "Document core processes with clear step-by-step procedures",
                    "Establish basic performance metrics and tracking systems",
                    "Identify process owners and standardize workflows"
                ]
            elif dimension_id == 'data':
                recs = [
                    "Begin digitizing manual processes and data collection",
                    "Implement basic data quality checks and validation",
                    "Establish centralized data storage and access protocols"
                ]
            elif dimension_id == 'tech':
                recs = [
                    "Evaluate and upgrade core technology infrastructure",
                    "Implement basic analytics and reporting tools",
                    "Create sandboxed environment for experimentation"
                ]
            elif dimension_id == 'people':
                recs = [
                    "Conduct AI awareness training for key stakeholders",
                    "Identify and train data champions within teams",
                    "Establish basic data literacy programs"
                ]
            elif dimension_id == 'leadership':
                recs = [
                    "Develop clear AI strategy aligned with business goals",
                    "Secure dedicated funding for AI initiatives",
                    "Define measurable outcomes for AI projects"
                ]
            elif dimension_id == 'change':
                recs = [
                    "Foster culture of experimentation and learning",
                    "Establish cross-functional collaboration frameworks",
                    "Create mechanisms for scaling successful pilots"
                ]
        
        elif score <= 3:  # Moderate scores need focused improvements
            if dimension_id == 'process':
                recs = [
                    "Enhance process documentation with variation analysis",
                    "Implement automated process monitoring and alerts",
                    "Conduct regular process improvement reviews"
                ]
            elif dimension_id == 'data':
                recs = [
                    "Improve data quality through automated validation",
                    "Implement master data management practices",
                    "Enable self-service analytics capabilities"
                ]
            # Add more moderate recommendations as needed...
        
        recommendations[dimension_id] = recs
    
    return recommendations
