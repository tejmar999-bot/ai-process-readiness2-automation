"""
Database models for AI Process Readiness Assessment
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

Base = declarative_base()

class Organization(Base):
    """Organization/Company table"""
    __tablename__ = 'organizations'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    assessments = relationship("Assessment", back_populates="organization")

class Assessment(Base):
    """Assessment results table"""
    __tablename__ = 'assessments'
    
    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    company_name = Column(String(255), nullable=False)
    total_score = Column(Integer, nullable=False)
    percentage = Column(Integer, nullable=False)
    readiness_band = Column(String(50), nullable=False)
    
    # Dimension scores (stored as JSON)
    dimension_scores = Column(JSON, nullable=False)
    
    # Individual question answers (stored as JSON)
    answers = Column(JSON, nullable=False)
    
    # Branding info
    primary_color = Column(String(7), default='#BF6A16')
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    organization = relationship("Organization", back_populates="assessments")

class User(Base):
    """User table for multi-user support"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=True)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(String(50), default='user')  # user, admin, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Database connection and session management
def get_db_engine():
    """Get database engine"""
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL environment variable not set")
    return create_engine(database_url)

def get_db_session():
    """Get database session"""
    engine = get_db_engine()
    Session = sessionmaker(bind=engine)
    return Session()

def init_db():
    """Initialize database - create all tables"""
    engine = get_db_engine()
    Base.metadata.create_all(engine)
    return engine
