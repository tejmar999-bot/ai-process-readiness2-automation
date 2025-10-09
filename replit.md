# AI Process Readiness Assessment

## Overview

This is a Streamlit-based web application that assesses organizational readiness for AI process implementation. The tool evaluates readiness across six key dimensions through a questionnaire format, then provides visual analytics and scoring to help organizations understand their AI adoption preparedness. Users answer questions rated on a 1-5 scale, and the application generates comprehensive reports including radar charts, dimension breakdowns, and actionable recommendations.

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

**Current Implementation**: In-memory data structures
- **Question Bank**: Python dictionaries and lists in `dimensions.py`
- **User Responses**: Streamlit session state (ephemeral)
- **Rationale**: Assessment is stateless; no persistent storage currently required
- **Future Consideration**: Database integration possible for multi-user deployments or historical tracking

**Data Models**:
- Dimensions: Structured as list of dictionaries with id, title, description, color, and nested questions
- Questions: Nested within dimensions with id and text fields
- Answers: Dictionary mapping question IDs to integer scores (1-5)

### Report Generation

**Export Functionality**: Image and data export capabilities indicated
- **Technologies**: PIL (Python Imaging Library) for image processing, BytesIO for in-memory file handling
- **Format Support**: Base64 encoding suggests PDF or image export features
- **Use Case**: Downloadable assessment reports for stakeholder sharing

## External Dependencies

### Core Framework Dependencies
- **Streamlit**: Web application framework for the entire UI layer
- **Plotly**: Interactive visualization library for charts and graphs
- **Pandas**: Data manipulation for score aggregation and analysis
- **NumPy**: Numerical computing for statistical calculations

### Utility Libraries
- **PIL (Pillow)**: Image processing for report generation and export
- **Base64**: Encoding for file downloads and embedded media

### Development Artifacts
- **Note**: Repository contains a shell script artifact for a React/TypeScript setup, but the actual application is Python/Streamlit-based. This script appears to be unused or from an alternative implementation approach that was not pursued.

### Potential Future Integrations
- Database system (PostgreSQL, MongoDB) for persistent storage of assessments
- Authentication service for multi-user support
- Email service for report distribution
- Analytics platform for aggregate readiness tracking across organizations