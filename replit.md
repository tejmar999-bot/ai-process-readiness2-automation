# AI Process Readiness Assessment

## Overview
This project is a Streamlit-based web application designed to assess an organization's readiness for AI process implementation. It guides users through a questionnaire across six key dimensions, providing visual analytics, scoring, and actionable recommendations. The tool aims to help organizations understand their AI adoption preparedness, generate comprehensive reports (including PDF exports), and offer industry benchmarking. The ultimate goal is to facilitate smoother AI integration and strategic planning.

## Recent Changes (October 12, 2025)
-   **Website Address Added**: Added "tlogicconsulting.com" to right bottom corner of footer on all pages
-   **Logo Size Increased**: Enlarged logo to 2.5rem height (matching title font size) for better visibility and brand presence
-   **Copyright Footer**: Added copyright notice "© T-Logic Training & Consulting Pvt. Ltd." at the bottom of all pages (home, assessment, results)
-   **Logo Shape Update**: Changed logo to display as sharp rectangle with border-radius: 0 (no rounded corners) for cleaner appearance
-   **Progress Arrow Optimization**: Reduced arrow width from 160px/140px to 120px/100px and font from 0.7rem to 0.65rem to fit within page frame without extending beyond solid line
-   **Process Maturity Color Update**: Changed from #A8E6CF (mint green) to #FFB6C1 (light pink pastel) for better visual distinction from Data Readiness (#ADD8E6 light blue) and Technology Infrastructure (#90EE90 light green)
-   **Continue Button Reactivity**: Enhanced with input keys (user_name_input, user_email_input) for immediate enablement when valid name and email entered (no tab/enter required)
-   **Logo Display**: Simplified to native st.image() component with width=100px for better Streamlit compatibility (note: Streamlit layout system has positioning limitations that prevent moving logo higher without off-screen issues)
-   **Scroll to Top**: Verified existing implementation at lines 425-426 and 493-507 - Complete Assessment button successfully scrolls Results page to top
-   **Home Button Removal**: Removed clickable home button and hint text from header on Results page for cleaner UI
-   **Navigation Streamlining**: Removed orange "See Recommendations" button above Scoring Model; kept light blue "See Recommended Actions" button below table
-   **Recommendations Layout**: Moved "Specific Recommendations" bullet points inside dimension gray boxes for better visual grouping
-   **Help Text Update**: Changed assistance section text to "Reach out to us by clicking here" for clearer call-to-action
-   **Color Palette Updates**: Changed Data Readiness to light blue pastel (#ADD8E6) and Technology Infrastructure to light grass green pastel (#90EE90)
-   **Percentage Calculation Fix**: Changed from normalized percentage ((total-6)/(30-6))*100 to simple percentage (total/30)*100 for clearer scoring (e.g., 16/30 now shows 53% instead of 42%)
-   **Color Box Alignment**: Improved alignment of colored squares in Readiness Level table using vertical-align: baseline and position adjustments
-   **Font Size Enhancement**: Increased "Based on..." sentence under Recommended Actions to 1.1rem for better readability

## Previous Changes (October 11, 2025)
-   **Next Button Scroll Enhancement**: Fixed Next button to scroll to first visible question (#question-0) accounting for sticky header, preventing questions from being hidden
-   **Total Score Display**: Enhanced Total Score card with 2rem bold percentage font (matching score number size) for improved visibility
-   **Table Alignment Fix**: Replaced emoji readiness indicators with CSS-based colored squares for consistent cross-browser alignment in Scoring Model table
-   **Navigation Button**: Added light blue (#ADD8E6) "See Recommended Actions" button below Scoring Model table with bold black text for easy navigation
-   **Score Labels**: Added beige oval labels (Weak/Needs Work/Average/Good/Excellent) with #D4C5B9 background, 50px border-radius, and 100px min-width in Detailed Scores section
-   **Percentage Display**: Added percentage values (20%, 40%, 60%, 80%, 100%) below numerical scores in Detailed Scores section

## User Preferences
Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend
The application uses the Streamlit framework for rapid web development, prioritizing Python-native UI. Plotly is used for interactive visualizations, especially radar charts, due to its seamless integration with Streamlit. Custom CSS is embedded for styling, featuring a pastel color palette for different dimensions, card-based layouts, and a fixed header with progress indicators on assessment pages. The user flow involves initial information collection with email validation, auto-scrolling to questions, and a feedback collection form.

### Backend
The backend employs a modular Python architecture with `app.py` as the controller, `data/dimensions.py` for question definitions, and `utils/scoring.py` for business logic. The assessment model evaluates readiness across six dimensions: Process Maturity, Data Readiness, Technology Infrastructure, People & Skills, Leadership & Strategy, and Change Management. Questions use a 1-5 scale with context-specific labels. Scoring involves averaging dimension scores, calculating simple percentage out of 30 max (total/30)*100, and categorizing into readiness bands (Not Ready, Emerging, Ready, Advanced). Streamlit's session state manages ephemeral data, while PostgreSQL with SQLAlchemy handles persistent storage for organizations, users, and assessment results.

### Data Storage
PostgreSQL is the chosen database, managed via SQLAlchemy ORM. It stores organizations, users, and assessment results. Static dimension and question data are defined in Python dictionaries.

### Features
-   **Report Generation**: Exports PDF and text reports using ReportLab and PIL, including executive summaries, radar charts, detailed analyses, and company branding.
-   **Results Display**: Presents an interactive scoring model table that visually highlights the user's readiness level.
-   **Branding Customization**: Allows users to upload a custom logo, set a primary brand color for UI theming, and define the company name, all persistent via session state.
-   **Industry Benchmarking**: Compares organizational readiness against various industry benchmarks (e.g., Small Business, Enterprise, Technology Leaders) with visual indicators.
-   **Recommended Actions**: Provides holistic, insightful analysis of each dimension with acknowledgment of strengths and weaknesses, specific bullet-point recommendations, and a soft plug for complimentary 45-minute consultation regardless of score.
-   **Request Assistance**: A feature on the results page allows users to request professional support from T-Logic.
-   **Navigation**: Includes auto-scrolling, a progress indicator, and a light blue "See Recommended Actions" button below the scoring table that scrolls to the Recommended Actions section.

## External Dependencies

### Core Frameworks
-   Streamlit: Web application framework.
-   Plotly: Interactive charting library.
-   Pandas: Data manipulation.
-   NumPy: Numerical operations.

### Database
-   SQLAlchemy: ORM for database interaction.
-   psycopg2-binary: PostgreSQL adapter.

### Report Generation
-   ReportLab: PDF creation.
-   PIL (Pillow): Image processing.

### Utilities
-   Base64: Encoding for file handling.