"""
Dimension and question definitions for AI Process Readiness Assessment
"""

# Color palette for dimensions
PALETTE = [
    '#FFB068',  # sec1 - Process Maturity
    '#C9A3FF',  # sec2 - Data Readiness  
    '#A7D6FF',  # sec3 - Technology Infrastructure
    '#FFC1D6',  # sec4 - People & Skills
    '#FFF08A',  # sec5 - Leadership & Strategy
    '#BFFFC4'   # sec6 - Change Management
]

DIMENSIONS = [
    {
        'id': 'process',
        'title': 'Process Maturity',
        'description': 'How well defined and measured your processes are.',
        'color': PALETTE[0],
        'questions': [
            {
                'id': 'proc_doc',
                'text': 'Core processes are documented and standardized across teams.'
            },
            {
                'id': 'proc_metrics',
                'text': 'Process performance metrics are tracked regularly and reliably.'
            },
            {
                'id': 'proc_variation',
                'text': 'Process variation is understood and root-causes are identified.'
            }
        ]
    },
    {
        'id': 'data',
        'title': 'Data Readiness',
        'description': 'Quality, accessibility and structure of your data.',
        'color': PALETTE[1],
        'questions': [
            {
                'id': 'data_digitized',
                'text': 'Process data is digitized and collected consistently.'
            },
            {
                'id': 'data_quality',
                'text': 'The data is cleaned, documented, and validated.'
            },
            {
                'id': 'data_access',
                'text': 'Teams can access historical data for analysis and modelling.'
            }
        ]
    },
    {
        'id': 'tech',
        'title': 'Technology Infrastructure',
        'description': 'Tools and platforms available for analytics and automation.',
        'color': PALETTE[2],
        'questions': [
            {
                'id': 'tech_stack',
                'text': 'Our tech stack supports integrations and APIs.'
            },
            {
                'id': 'analytics',
                'text': 'Analytics and reporting tools are available to teams.'
            },
            {
                'id': 'experimentation',
                'text': 'There is an environment for ML experiments or pilots.'
            }
        ]
    },
    {
        'id': 'people',
        'title': 'People & Skills',
        'description': 'Workforce capability and understanding of AI and data-driven methods.',
        'color': PALETTE[3],
        'questions': [
            {
                'id': 'ai_awareness',
                'text': 'Teams understand basic AI concepts and use-cases.'
            },
            {
                'id': 'training',
                'text': 'Training programs are in place for data and AI skills.'
            },
            {
                'id': 'roles',
                'text': 'There are named AI/data translators, champions or SMEs.'
            }
        ]
    },
    {
        'id': 'leadership',
        'title': 'Leadership & Strategy Alignment',
        'description': 'Executive commitment and strategic alignment for AI.',
        'color': PALETTE[4],
        'questions': [
            {
                'id': 'strategy',
                'text': 'AI is explicitly part of the organizational strategy.'
            },
            {
                'id': 'funding',
                'text': 'There is allocated funding for pilots and scale-up.'
            },
            {
                'id': 'outcomes',
                'text': 'AI initiatives are tied to measurable business outcomes.'
            }
        ]
    },
    {
        'id': 'change',
        'title': 'Change Management & Culture',
        'description': "Organization's openness to experimentation and cross-functional work.",
        'color': PALETTE[5],
        'questions': [
            {
                'id': 'psych_safe',
                'text': 'The culture accepts small experiments and learning from failure.'
            },
            {
                'id': 'collab',
                'text': 'Cross-functional teams actively collaborate on process work.'
            },
            {
                'id': 'scale',
                'text': 'There is a framework to scale successful pilots into operations.'
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
