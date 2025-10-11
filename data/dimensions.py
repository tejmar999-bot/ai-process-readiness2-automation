"""
Dimension and question definitions for AI Process Readiness Assessment
"""

# Color palette for dimensions - Green/Blue/Brown scheme
PALETTE = [
    '#2D6A4F',  # sec1 - Process Maturity (Forest Green)
    '#1B9AAA',  # sec2 - Data Readiness (Teal Blue)
    '#2C5F8D',  # sec3 - Technology Infrastructure (Deep Blue)
    '#8B6F47',  # sec4 - People & Skills (Warm Brown)
    '#7A5C3D',  # sec5 - Leadership & Strategy (Earth Brown)
    '#52B788'   # sec6 - Change Management (Sea Green)
]

# Bright versions for titles on dark backgrounds
BRIGHT_PALETTE = [
    '#4ADE80',  # Bright Light Green (Process Maturity)
    '#22D3EE',  # Bright Cyan (Data Readiness)
    '#60A5FA',  # Bright Sky Blue (Technology Infrastructure)
    '#F59E0B',  # Bright Amber (People & Skills)
    '#D97706',  # Bright Orange (Leadership & Strategy)
    '#34D399'   # Bright Emerald (Change Management)
]

DIMENSIONS = [
    {
        'id': 'process',
        'title': 'Process Maturity',
        'what_it_measures': 'How well-defined, measured, and optimized processes are before applying AI.',
        'description': 'How well defined and measured your processes are.',
        'color': PALETTE[0],
        'scoring_labels': {
            1: 'Ad hoc',
            2: 'Defined',
            3: 'Measured',
            4: 'Controlled',
            5: 'Optimized'
        },
        'questions': [
            {
                'id': 'proc_doc',
                'text': 'Are your processes documented and standardized?'
            },
            {
                'id': 'proc_metrics',
                'text': 'Are performance metrics tracked regularly?'
            },
            {
                'id': 'proc_variation',
                'text': 'Is process variation understood?'
            }
        ]
    },
    {
        'id': 'data',
        'title': 'Data Readiness',
        'what_it_measures': 'Quality, accessibility, and structure of process data available for AI analysis.',
        'description': 'Quality, accessibility and structure of your data.',
        'color': PALETTE[1],
        'scoring_labels': {
            1: 'Mostly manual',
            2: 'Some digital data',
            3: 'Structured data in silos',
            4: 'Integrated systems',
            5: 'Unified, high-quality data'
        },
        'questions': [
            {
                'id': 'data_digitized',
                'text': 'Is process data digitized?'
            },
            {
                'id': 'data_quality',
                'text': 'Is data cleaned and integrated?'
            },
            {
                'id': 'data_access',
                'text': 'Do you have access to historical data for model training?'
            }
        ]
    },
    {
        'id': 'tech',
        'title': 'Technology Infrastructure',
        'what_it_measures': 'Availability of tools, platforms, and IT support for AI deployment.',
        'description': 'Tools and platforms available for analytics and automation.',
        'color': PALETTE[2],
        'scoring_labels': {
            1: 'Minimal',
            2: 'Basic tools',
            3: 'Analytics in place',
            4: 'Automation + ML tools',
            5: 'AI-integrated platforms'
        },
        'questions': [
            {
                'id': 'tech_stack',
                'text': 'Does your tech stack support APIs, analytics, and automation?'
            },
            {
                'id': 'tech_secure',
                'text': 'Do you have secure cloud or on-prem data systems?'
            },
            {
                'id': 'tech_ml',
                'text': 'Is there access to AI experimentation environments (e.g., ML tools)?'
            }
        ]
    },
    {
        'id': 'people',
        'title': 'People & Skills',
        'what_it_measures': 'Workforce awareness, capability, and openness toward AI and digital transformation.',
        'description': 'Workforce capability and understanding of AI and data-driven methods.',
        'color': PALETTE[3],
        'scoring_labels': {
            1: 'Unaware',
            2: 'Skeptical',
            3: 'Learning',
            4: 'Engaged',
            5: 'Proactive AI advocates'
        },
        'questions': [
            {
                'id': 'people_understand',
                'text': 'Do teams understand AI fundamentals?'
            },
            {
                'id': 'people_training',
                'text': 'Are employees trained in data-driven decision-making?'
            },
            {
                'id': 'people_champions',
                'text': 'Are there AI champions or data translators?'
            }
        ]
    },
    {
        'id': 'leadership',
        'title': 'Leadership & Strategy Alignment',
        'what_it_measures': 'Executive commitment and strategic clarity for AI adoption.',
        'description': 'Executive commitment and strategic alignment for AI.',
        'color': PALETTE[4],
        'scoring_labels': {
            1: 'No alignment',
            2: 'Conceptual interest',
            3: 'Pilot discussions',
            4: 'Clear roadmap',
            5: 'Fully integrated vision'
        },
        'questions': [
            {
                'id': 'leadership_strategy',
                'text': 'Is AI part of your organizational strategy?'
            },
            {
                'id': 'leadership_funding',
                'text': 'Is leadership committed to funding pilots?'
            },
            {
                'id': 'leadership_goals',
                'text': 'Are goals aligned with business impact?'
            }
        ]
    },
    {
        'id': 'change',
        'title': 'Change Management & Culture',
        'what_it_measures': "Organizational culture's adaptability to change and innovation.",
        'description': "Organization's openness to experimentation and cross-functional work.",
        'color': PALETTE[5],
        'scoring_labels': {
            1: 'Resistant',
            2: 'Limited openness',
            3: 'Accepting',
            4: 'Adaptive',
            5: 'Agile & innovation-oriented'
        },
        'questions': [
            {
                'id': 'change_experiment',
                'text': 'How open is your culture to experimenting and learning from failure?'
            },
            {
                'id': 'change_collab',
                'text': 'Are cross-functional collaborations encouraged?'
            },
            {
                'id': 'change_scale',
                'text': 'Is there a framework for scaling successful pilots?'
            }
        ]
    }
]

def get_all_questions():
    """
    Get all questions from all dimensions as a flat list
    
    Returns:
        List of all question dictionaries
    """
    questions = []
    for dimension in DIMENSIONS:
        questions.extend(dimension['questions'])
    return questions

def get_dimension_by_id(dimension_id: str):
    """
    Get dimension definition by ID
    
    Args:
        dimension_id: The dimension ID to look up
        
    Returns:
        Dimension dictionary or None if not found
    """
    return next((d for d in DIMENSIONS if d['id'] == dimension_id), None)

def get_questions_by_dimension(dimension_id: str):
    """
    Get all questions for a specific dimension
    
    Args:
        dimension_id: The dimension ID
        
    Returns:
        List of question dictionaries for that dimension
    """
    dimension = get_dimension_by_id(dimension_id)
    return dimension['questions'] if dimension else []
