# AI Process Readiness Assessment

## Overview
This project is a Streamlit-based web application designed to assess an organization's readiness for AI process implementation. It guides users through a questionnaire across six key dimensions, providing visual analytics, scoring, and actionable recommendations. The tool aims to help organizations understand their AI adoption preparedness, generate comprehensive reports (including PDF exports), and offer industry benchmarking. The ultimate goal is to facilitate smoother AI integration and strategic planning.

## User Preferences
Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend
The application uses the Streamlit framework for rapid web development, prioritizing Python-native UI. Plotly is used for interactive visualizations, especially radar charts, due to its seamless integration with Streamlit. Custom CSS is embedded for styling, featuring a pastel color palette for different dimensions, card-based layouts, and a fixed header with progress indicators on assessment pages. The user flow involves initial information collection with email validation, auto-scrolling to questions, and a feedback collection form.

### Backend
The backend employs a modular Python architecture with `app.py` as the controller, `data/dimensions.py` for question definitions, and `utils/scoring.py` for business logic. The assessment model evaluates readiness across six dimensions: Process Maturity, Data Readiness, Technology Infrastructure, People & Skills, Leadership & Strategy, and Change Management. Questions use a 1-5 scale with context-specific labels. Scoring involves averaging dimension scores, normalizing to a 0-100% scale, and categorizing into readiness bands (Not Ready, Emerging, Ready, Advanced). Streamlit's session state manages ephemeral data, while PostgreSQL with SQLAlchemy handles persistent storage for organizations, users, and assessment results.

### Data Storage
PostgreSQL is the chosen database, managed via SQLAlchemy ORM. It stores organizations, users, and assessment results. Static dimension and question data are defined in Python dictionaries.

### Features
-   **Report Generation**: Exports PDF and text reports using ReportLab and PIL, including executive summaries, radar charts, detailed analyses, and company branding.
-   **Results Display**: Presents an interactive scoring model table that visually highlights the user's readiness level.
-   **Branding Customization**: Allows users to upload a custom logo, set a primary brand color for UI theming, and define the company name, all persistent via session state.
-   **Industry Benchmarking**: Compares organizational readiness against various industry benchmarks (e.g., Small Business, Enterprise, Technology Leaders) with visual indicators.
-   **Recommended Actions**: Provides personalized, actionable recommendations for low-scoring areas, grouped by dimension with clear calls to action.
-   **Request Assistance**: A feature on the results page allows users to request professional support from T-Logic.
-   **Navigation**: Includes auto-scrolling, a progress indicator, and a home button on the results page to reset the assessment.

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