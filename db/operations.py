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

def get_or_create_user(name: str, email: str, organization_id: int) -> User:
    """Get existing user or create new one"""
    session = get_db_session()
    try:
        user = session.query(User).filter_by(email=email, organization_id=organization_id).first()
        if not user:
            user = User(
                name=name,
                email=email,
                organization_id=organization_id
            )
            session.add(user)
            session.commit()
            session.refresh(user)
        return user
    finally:
        session.close()

def save_assessment(
    company_name: str,
    scores_data: Dict,
    answers: Dict,
    primary_color: str = '#BF6A16',
    user_name: str = None,
    user_email: str = None
) -> Assessment:
    """Save assessment results to database"""
    session = get_db_session()
    try:
        # Get or create organization
        org = session.query(Organization).filter_by(name=company_name).first()
        if not org:
            org = Organization(name=company_name)
            session.add(org)
            session.commit()
            session.refresh(org)
        
        # Get or create user if provided (in same session)
        user_id = None
        if user_name and user_email:
            user = session.query(User).filter_by(email=user_email, organization_id=org.id).first()
            if not user:
                user = User(
                    name=user_name,
                    email=user_email,
                    organization_id=org.id
                )
                session.add(user)
                session.commit()
                session.refresh(user)
            user_id = user.id
        
        # Create assessment
        assessment = Assessment(
            organization_id=org.id,
            user_id=user_id,
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
    except Exception as e:
        session.rollback()
        raise e
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

def get_team_statistics(company_name: str) -> Dict:
    """Get team/organization statistics for a specific company"""
    session = get_db_session()
    try:
        # Get organization
        org = session.query(Organization).filter_by(name=company_name).first()
        if not org:
            return {
                'total_assessments': 0,
                'average_score': 0,
                'latest_score': 0,
                'score_trend': 'N/A'
            }
        
        # Query assessments for this organization
        query = session.query(Assessment).filter_by(organization_id=org.id)
        
        total_assessments = query.count()
        
        if total_assessments == 0:
            return {
                'total_assessments': 0,
                'average_score': 0,
                'latest_score': 0,
                'score_trend': 'N/A'
            }
        
        # Get average score for this organization only
        avg_score = session.query(func.avg(Assessment.total_score))\
            .filter_by(organization_id=org.id)\
            .scalar()
        
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

def get_team_members(company_name: str) -> List[Dict]:
    """Get all team members who have completed assessments"""
    session = get_db_session()
    try:
        org = session.query(Organization).filter_by(name=company_name).first()
        if not org:
            return []
        
        # Get all assessments with user info
        assessments = session.query(Assessment).filter_by(organization_id=org.id).all()
        
        # Track users and their assessments
        user_map = {}
        
        for assessment in assessments:
            # Check if assessment has user_id attribute and it's not None
            if hasattr(assessment, 'user_id') and assessment.user_id:
                user = session.query(User).filter_by(id=assessment.user_id).first()
                if user:
                    if user.id not in user_map:
                        user_map[user.id] = {
                            'id': user.id,
                            'name': user.name,
                            'email': user.email,
                            'assessments': [],
                            'latest_score': 0,
                            'latest_percentage': 0,
                            'latest_date': None
                        }
                    
                    user_map[user.id]['assessments'].append({
                        'score': assessment.total_score,
                        'percentage': assessment.percentage,
                        'date': assessment.completed_at
                    })
        
        # Get latest assessment for each user
        team_members = []
        for user_id, user_data in user_map.items():
            latest = max(user_data['assessments'], key=lambda x: x['date'])
            user_data['latest_score'] = latest['score']
            user_data['latest_percentage'] = latest['percentage']
            user_data['latest_date'] = latest['date'].strftime('%Y-%m-%d %H:%M')
            user_data['total_assessments'] = len(user_data['assessments'])
            del user_data['assessments']  # Remove detailed assessments
            team_members.append(user_data)
        
        return sorted(team_members, key=lambda x: x['latest_date'], reverse=True)
    finally:
        session.close()

def get_team_dimension_averages(company_name: str) -> Dict:
    """Get average dimension scores across all team assessments"""
    session = get_db_session()
    try:
        org = session.query(Organization).filter_by(name=company_name).first()
        if not org:
            return {}
        
        assessments = session.query(Assessment).filter_by(organization_id=org.id).all()
        
        if not assessments:
            return {}
        
        # Aggregate dimension scores
        dimension_totals = {}
        dimension_counts = {}
        
        for assessment in assessments:
            for dim_score in assessment.dimension_scores:
                dim_id = dim_score['id']
                dim_title = dim_score['title']
                
                if dim_id not in dimension_totals:
                    dimension_totals[dim_id] = {
                        'title': dim_title,
                        'total': 0,
                        'count': 0
                    }
                
                dimension_totals[dim_id]['total'] += dim_score['score']
                dimension_totals[dim_id]['count'] += 1
        
        # Calculate averages
        dimension_averages = []
        for dim_id, data in dimension_totals.items():
            dimension_averages.append({
                'id': dim_id,
                'title': data['title'],
                'average': round(data['total'] / data['count'], 2),
                'assessments': data['count']
            })
        
        return dimension_averages
    finally:
        session.close()

def get_team_readiness_distribution(company_name: str) -> Dict:
    """Get distribution of readiness levels across team"""
    session = get_db_session()
    try:
        org = session.query(Organization).filter_by(name=company_name).first()
        if not org:
            return {}
        
        assessments = session.query(Assessment).filter_by(organization_id=org.id).all()
        
        distribution = {}
        for assessment in assessments:
            band = assessment.readiness_band
            if band not in distribution:
                distribution[band] = 0
            distribution[band] += 1
        
        return distribution
    finally:
        session.close()
