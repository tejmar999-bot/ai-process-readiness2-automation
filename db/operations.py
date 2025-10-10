"""
Database operations for AI Process Readiness Assessment
"""
from db.models import Organization, Assessment, User, get_db_session, init_db
from datetime import datetime
from sqlalchemy import desc, func
from typing import List, Dict, Optional

def ensure_tables_exist():
    """Ensure database tables are created"""
    try:
        init_db()
        return True
    except Exception as e:
        print(f"Error initializing database: {e}")
        return False

def get_or_create_organization(company_name: str) -> Organization:
    """Get existing organization or create new one"""
    session = get_db_session()
    try:
        org = session.query(Organization).filter_by(name=company_name).first()
        if not org:
            org = Organization(name=company_name)
            session.add(org)
            session.commit()
            session.refresh(org)
        return org
    finally:
        session.close()

def save_assessment(
    company_name: str,
    scores_data: Dict,
    answers: Dict,
    primary_color: str = '#BF6A16'
) -> Assessment:
    """Save assessment results to database"""
    session = get_db_session()
    try:
        # Get or create organization
        org = get_or_create_organization(company_name)
        
        # Create assessment
        assessment = Assessment(
            organization_id=org.id,
            company_name=company_name,
            total_score=scores_data['total'],
            percentage=scores_data['percentage'],
            readiness_band=scores_data['readiness_band']['label'],
            dimension_scores=scores_data['dimension_scores'],
            answers=answers,
            primary_color=primary_color
        )
        
        session.add(assessment)
        session.commit()
        session.refresh(assessment)
        return assessment
    finally:
        session.close()

def get_organization_assessments(company_name: str, limit: int = 10) -> List[Assessment]:
    """Get all assessments for an organization"""
    session = get_db_session()
    try:
        org = session.query(Organization).filter_by(name=company_name).first()
        if not org:
            return []
        
        assessments = session.query(Assessment)\
            .filter_by(organization_id=org.id)\
            .order_by(desc(Assessment.completed_at))\
            .limit(limit)\
            .all()
        
        return assessments
    finally:
        session.close()

def get_latest_assessment(company_name: str) -> Optional[Assessment]:
    """Get the most recent assessment for an organization"""
    session = get_db_session()
    try:
        org = session.query(Organization).filter_by(name=company_name).first()
        if not org:
            return None
        
        assessment = session.query(Assessment)\
            .filter_by(organization_id=org.id)\
            .order_by(desc(Assessment.completed_at))\
            .first()
        
        return assessment
    finally:
        session.close()

def get_assessment_history(company_name: str) -> List[Dict]:
    """Get assessment history with simplified data structure"""
    assessments = get_organization_assessments(company_name, limit=20)
    
    history = []
    for assessment in assessments:
        history.append({
            'id': assessment.id,
            'date': assessment.completed_at.strftime('%Y-%m-%d %H:%M'),
            'total_score': assessment.total_score,
            'percentage': assessment.percentage,
            'readiness_band': assessment.readiness_band,
            'dimension_scores': assessment.dimension_scores
        })
    
    return history

def get_dimension_trends(company_name: str) -> Dict:
    """Get dimension score trends over time"""
    assessments = get_organization_assessments(company_name, limit=10)
    
    if not assessments:
        return {}
    
    # Organize data by dimension
    trends = {}
    dates = []
    
    for assessment in reversed(assessments):  # Oldest first
        date = assessment.completed_at.strftime('%Y-%m-%d')
        dates.append(date)
        
        for dim_score in assessment.dimension_scores:
            dim_id = dim_score['id']
            dim_title = dim_score['title']
            
            if dim_id not in trends:
                trends[dim_id] = {
                    'title': dim_title,
                    'scores': [],
                    'dates': []
                }
            
            trends[dim_id]['scores'].append(dim_score['score'])
            trends[dim_id]['dates'].append(date)
    
    return trends

def get_team_statistics(organization_id: Optional[int] = None) -> Dict:
    """Get team/organization statistics"""
    session = get_db_session()
    try:
        query = session.query(Assessment)
        
        if organization_id:
            query = query.filter_by(organization_id=organization_id)
        
        total_assessments = query.count()
        
        if total_assessments == 0:
            return {
                'total_assessments': 0,
                'average_score': 0,
                'latest_score': 0,
                'score_trend': 'N/A'
            }
        
        # Get average score
        avg_score = session.query(func.avg(Assessment.total_score)).scalar()
        
        # Get latest and previous for trend
        latest = query.order_by(desc(Assessment.completed_at)).first()
        previous = query.order_by(desc(Assessment.completed_at)).offset(1).first()
        
        trend = 'stable'
        if previous:
            if latest.total_score > previous.total_score:
                trend = 'improving'
            elif latest.total_score < previous.total_score:
                trend = 'declining'
        
        return {
            'total_assessments': total_assessments,
            'average_score': round(avg_score, 1) if avg_score else 0,
            'latest_score': latest.total_score if latest else 0,
            'score_trend': trend
        }
    finally:
        session.close()

def delete_assessment(assessment_id: int) -> bool:
    """Delete an assessment by ID"""
    session = get_db_session()
    try:
        assessment = session.query(Assessment).filter_by(id=assessment_id).first()
        if assessment:
            session.delete(assessment)
            session.commit()
            return True
        return False
    finally:
        session.close()
