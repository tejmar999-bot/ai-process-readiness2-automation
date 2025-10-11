# AI Process Readiness Assessment

## Overview

This is a Streamlit-based web application that assesses organizational readiness for AI process implementation. The tool evaluates readiness across six key dimensions through a question-format questionnaire, then provides visual analytics and scoring to help organizations understand their AI adoption preparedness. Users answer questions rated on a dimension-specific 1-5 scale with custom labels (e.g., Process Maturity: Ad hoc → Defined → Measured → Controlled → Optimized). The application generates comprehensive reports including radar charts, dimension breakdowns, scoring model visualization, actionable recommendations, PDF exports, and industry benchmarking.

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
- **Color Palette**: Distinct pastel colors for all dimensions
  - Process Maturity: #A8E6CF (Pastel Mint Green)
  - Data Readiness: #C7CEEA (Pastel Lavender)
  - Technology Infrastructure: #B4D4FF (Pastel Sky Blue)
  - People & Skills: #FFCBA4 (Pastel Peach)
  - Leadership & Strategy: #FFE5A0 (Pastel Yellow)
  - Change Management: #FFAEC9 (Pastel Rose)
  - All colors are distinct and easily distinguishable
- **Design Pattern**: Card-based layouts with left-border dimension indicators
- **Logo Display**: Company logo rendered in top-right corner at 2.5rem height with rectangular shape (no border-radius)
- **User Flow**: User information collection on first page with 2 required fields (Name, Email) and 4 optional fields (Title, Company Name, Phone Number, Location). Email validation required before assessment begins. Continue button activates as soon as both required fields are filled.
- **Navigation**: 
  - Auto-scroll when Next/Previous button pressed and when assessment completed
  - Scroll offset: 200px to ensure progress arrows and dimension title are fully visible
  - Scroll executes after progress bar is rendered to avoid timing issues
  - Progress indicator: 6 connected arrow segments that light up in dimension colors as user progresses
  - Arrow text color: White for active segments, gray for inactive (optimal contrast with earthy colors)
  - Colored line above dimension counter matches current dimension color
- **Fixed Header on Dimension Pages**: 
  - Header is FIXED to viewport top (position: fixed, top: 0) and stays visible while scrolling
  - Contains: colored line (4px), progress arrows (fixed width 160px), "Dimension X of 6" counter, dimension title, and "What it Measures" description
  - Background color #1F2937 with box-shadow for depth
  - Z-index 9999 ensures header stays above all content
  - Streamlit header hidden on dimension pages for clean appearance
  - Content margin-top: 300px prevents overlap with fixed header
  - Dimension title: 2rem font, bold (700 weight), pastel colors for visibility
  - "What it Measures" text: 1.05rem font, #D1D5DB color for readability
  - Progress arrows: Fixed width (160px/140px min) with text wrapping, white text on pastel backgrounds
- **Auto-Scroll to Next Question**:
  - When user answers a question, page smoothly scrolls to next question automatically
  - Uses on_change callback to detect when answer is selected (prevents unwanted scroll on page load)
  - Scroll accounts for sticky header height to ensure next question is visible below header
  - No auto-scroll on last question (no next question to scroll to)
  - Session state flag (`scroll_to_question`) controls when scroll executes and clears after completion
- **Feedback Collection**: User feedback form on results page with text area and submit button (saves to session state, email integration pending)

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

**Question Format**:
- **Design**: Question-format prompts (e.g., "Are your processes documented and standardized?")
- **Answer Choices**: Question-specific 1-5 scale labels that match each question's context
  - Each of the 18 questions has unique answer choices tailored to that specific question
  - Examples:
    - "Are your processes documented and standardized?" → No documentation → Basic documentation → Documented → Standardized → Fully standardized & optimized
    - "Is process data digitized?" → Mostly manual → Partially digital → Mostly digital → Fully digital → Automated capture
    - "Is data cleaned and integrated?" → Uncleaned/siloed → Basic cleaning → Cleaned in silos → Integrated → Automated cleaning & integration
- **Dimension Scoring Labels** (used for dimension-level summaries):
  - Process Maturity: Ad hoc → Defined → Measured → Controlled → Optimized
  - Data Readiness: Mostly manual → Some digital data → Structured data in silos → Integrated systems → Unified, high-quality data
  - Technology Infrastructure: Minimal → Basic tools → Analytics in place → Automation + ML tools → AI-integrated platforms
  - People & Skills: Unaware → Skeptical → Learning → Engaged → Proactive AI advocates
  - Leadership & Strategy: No alignment → Conceptual interest → Pilot discussions → Clear roadmap → Fully integrated vision
  - Change Management: Resistant → Limited openness → Accepting → Adaptive → Agile & innovation-oriented
- **Implementation**: Questions store answer choices in 'answer_choices' dict, with fallback to dimension 'scoring_labels' for backwards compatibility
- **"What it Measures"**: Each dimension includes expandable context accessible via ❓ icon explaining the dimension's purpose

**Scoring Algorithm**:
- **Input**: 1-5 scale responses per question with dimension-specific labels
- **Calculation**: Dimension scores averaged from constituent questions
- **Total Score Range**: 6-30 (6 dimensions × 1-5 scale)
- **Percentage Conversion**: Normalized to 0-100% scale using formula: ((total - 6) / (30 - 6)) × 100
- **Readiness Bands**: 
  - 0-10: Not Ready (foundational work needed)
  - 11-17: Emerging (pilot-level readiness)
  - 18-24: Ready (scaled AI use)
  - 25-30: Advanced (AI-ready culture and infrastructure)

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

### Results Display

**Scoring Model Table**: Interactive readiness level visualization
- **Table Structure**: 3-column table (Score Range, Readiness Level, Meaning)
- **Readiness Bands**:
  - 0-10: 🟥 Not Ready - Foundational work needed
  - 11-17: 🟧 Emerging - Pilot-level readiness
  - 18-24: 🟨 Ready - Scaled AI use readiness
  - 25-30: 🟩 Advanced - AI-ready culture and infrastructure
- **Visual Highlighting**: User's readiness level highlighted with 3px border in primary brand color and bold text
- **Dynamic Display**: Table shown immediately below score cards on results page

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