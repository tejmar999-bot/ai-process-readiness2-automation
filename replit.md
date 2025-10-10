# AI Process Readiness Assessment

## Overview

This is a Streamlit-based web application that assesses organizational readiness for AI process implementation. The tool evaluates readiness across six key dimensions through a questionnaire format, then provides visual analytics and scoring to help organizations understand their AI adoption preparedness. Users answer questions rated on a 1-5 scale, and the application generates comprehensive reports including radar charts, dimension breakdowns, actionable recommendations, PDF exports, industry benchmarking, historical progress tracking, and multi-user team analytics.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture

**Technology Stack**: Streamlit framework for rapid web application development
- **Rationale**: Streamlit enables Python-native UI development without requiring separate frontend frameworks, ideal for data-focused applications
- **Alternatives Considered**: React/Next.js would provide more customization but requires JavaScript expertise and separate backend
- **Pros**: Rapid prototyping, Python-native, built-in state management
- **Cons**: Limited UI customization, less suitable for complex interactions

**Visualization Layer**: Plotly for interactive charts
- **Rationale**: Plotly integrates seamlessly with Streamlit and provides interactive, publication-quality visualizations
- **Key Use**: Radar charts for multi-dimensional readiness assessment
- **Pros**: Rich interactivity, professional appearance, Python-native
- **Cons**: Larger bundle size compared to simpler charting libraries

**Styling Approach**: Custom CSS embedded in Streamlit
- **Rationale**: Direct CSS injection allows brand-specific styling while maintaining Streamlit's simplicity
- **Color Palette**: Six-color scheme mapped to assessment dimensions (#FFB068, #C9A3FF, #A7D6FF, #FFC1D6, #FFF08A, #BFFFC4)
- **Design Pattern**: Card-based layouts with left-border dimension indicators

### Backend Architecture

**Application Structure**: Modular Python architecture
- **Core Logic**: `app.py` serves as the main application controller
- **Data Layer**: `data/dimensions.py` contains dimension and question definitions
- **Business Logic**: `utils/scoring.py` handles score calculations and readiness band determination

**Assessment Model**: Six-dimension evaluation framework
1. Process Maturity - Process documentation and standardization
2. Data Readiness - Data quality and accessibility  
3. Technology Infrastructure - Systems and tools capability
4. People & Skills - Team competencies and capabilities
5. Leadership & Strategy - Organizational direction and commitment
6. Change Management - Change adoption and support mechanisms

**Scoring Algorithm**:
- **Input**: 1-5 Likert scale responses per question
- **Calculation**: Dimension scores averaged from constituent questions
- **Total Score Range**: 6-30 (6 dimensions × 1-5 scale)
- **Percentage Conversion**: Normalized to 0-100% scale using formula: ((total - 6) / (30 - 6)) × 100
- **Readiness Bands**: Total scores mapped to qualitative readiness levels via `get_readiness_band()` function

**State Management**: Streamlit session state
- **Rationale**: Built-in session state eliminates need for external state management
- **Use Case**: Persisting user answers across re-renders and navigation

### Data Storage Solutions

**Current Implementation**: PostgreSQL database with SQLAlchemy ORM
- **Question Bank**: Python dictionaries and lists in `dimensions.py` (static data)
- **User Responses**: Streamlit session state (ephemeral during assessment)
- **Persistent Storage**: PostgreSQL database for assessments, users, and organizations
- **Database Models**:
  - **Organizations**: Company/organization records with relationships to assessments and users
  - **Users**: Team member records with name, email, and organization linkage
  - **Assessments**: Assessment results with dimension scores, answers, branding info, and optional user linkage

**Data Models**:
- **Dimensions**: Structured as list of dictionaries with id, title, description, color, and nested questions
- **Questions**: Nested within dimensions with id and text fields  
- **Answers**: Dictionary mapping question IDs to integer scores (1-5)
- **Assessment Records**: JSON storage of dimension_scores and answers with metadata (total_score, percentage, readiness_band, primary_color)
- **User Profiles**: Name, email, organization_id for multi-user team tracking

### Report Generation

**Export Functionality**: PDF and text report generation with comprehensive analytics
- **Technologies**: ReportLab for PDF generation, PIL for image processing, BytesIO for in-memory file handling
- **PDF Report Components**:
  - Executive summary with overall readiness score and band
  - Radar chart visualization of dimension scores
  - Detailed dimension-by-dimension analysis with recommendations
  - Company branding (logo and primary color customization)
- **Text Export**: Plain text format with scores and readiness summary
- **Use Case**: Downloadable assessment reports for stakeholder sharing and documentation

### Branding Customization

**Company Branding**: Personalized assessment experience
- **Logo Upload**: Custom company logo displayed on results and PDF reports (supports PNG, JPG, JPEG)
- **Primary Color**: Customizable brand color for UI theming and charts
- **Company Name**: Editable organization name displayed throughout the application
- **Session Persistence**: Branding preferences maintained across re-renders via Streamlit session state
- **Default Branding**: T-Logic logo and orange (#BF6A16) color scheme

### Industry Benchmarking

**Benchmark Comparison**: Compare organizational readiness against industry standards
- **Benchmark Categories**: 
  - Small Business (< 50 employees)
  - Mid-Market (50-500 employees)
  - Enterprise (500+ employees)
  - Technology Leaders
  - Industry Average
- **Comparison Metrics**: Dimension-by-dimension comparison showing gaps and strengths
- **Visual Indicators**: Color-coded status (Below/At/Above benchmark)
- **ID-Based Matching**: Reliable dimension matching using dimension IDs ('process', 'data', 'tech', 'people', 'leadership', 'change')

### Historical Tracking

**Progress Monitoring**: Track readiness improvement over time
- **Assessment History**: Table showing all past assessments with dates, scores, and readiness levels
- **Dimension Trends**: Line chart visualizing score changes across all six dimensions over time
- **Progress Summary**: Metrics showing total assessments, score change, and percentage improvement
- **Organization Scoping**: History filtered by company/organization for accurate tracking
- **Database Persistence**: All assessments stored in PostgreSQL for long-term historical analysis

### Multi-User Team Analytics

**Team Collaboration**: Support for multiple users from the same organization
- **User Profiles**: Optional name and email collection at assessment start
- **Team Members Table**: Display all team members with their latest scores and assessment counts
- **Team Dimension Averages**: Radar chart comparing team average scores to industry benchmarks
- **Readiness Distribution**: Pie chart showing distribution of readiness levels across team
- **Team Summary**: Aggregate metrics including team size, average score, and total assessments
- **Organization Linking**: All users and assessments linked to organization for proper team aggregation
- **Database Schema**: Users table with organization_id foreign key, assessments with optional user_id

## External Dependencies

### Core Framework Dependencies
- **Streamlit**: Web application framework for the entire UI layer
- **Plotly**: Interactive visualization library for charts and graphs
- **Pandas**: Data manipulation for score aggregation and analysis
- **NumPy**: Numerical computing for statistical calculations

### Database Dependencies
- **SQLAlchemy**: ORM for database interactions and model definitions
- **psycopg2-binary**: PostgreSQL database adapter

### Report Generation Libraries
- **ReportLab**: PDF document generation with customization
- **PIL (Pillow)**: Image processing for logos and charts

### Utility Libraries
- **Base64**: Encoding for file downloads and embedded media

### Potential Future Enhancements
- Email service for automated report distribution
- Advanced authentication with role-based access control
- Multi-organization support with separate data isolation
- API endpoints for integration with external systems