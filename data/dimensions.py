"""
Dimension and question definitions for AI Process Readiness Assessment
"""

# Pastel color palette for dimensions - Distinct pastel colors
PALETTE = [
    '#A8E6CF',  # sec1 - Process Maturity (Pastel Mint Green)
    '#C7CEEA',  # sec2 - Data Readiness (Pastel Lavender)
    '#B4D4FF',  # sec3 - Technology Infrastructure (Pastel Sky Blue)
    '#FFB347',  # sec4 - People & Skills (Pastel Orange)
    '#FFE5A0',  # sec5 - Leadership & Strategy (Pastel Yellow)
    '#DDA0DD'   # sec6 - Change Management (Pastel Plum)
]

# Same colors used for titles (pastel colors work on dark backgrounds)
BRIGHT_PALETTE = [
    '#A8E6CF',  # Pastel Mint Green (Process Maturity)
    '#C7CEEA',  # Pastel Lavender (Data Readiness)
    '#B4D4FF',  # Pastel Sky Blue (Technology Infrastructure)
    '#FFB347',  # Pastel Orange (People & Skills)
    '#FFE5A0',  # Pastel Yellow (Leadership & Strategy)
    '#DDA0DD'   # Pastel Plum (Change Management)
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
                'text': 'Are your processes documented and standardized?',
                'answer_choices': {
                    1: 'No documentation',
                    2: 'Basic documentation',
                    3: 'Documented',
                    4: 'Standardized',
                    5: 'Fully standardized & optimized'
                }
            },
            {
                'id': 'proc_metrics',
                'text': 'Are performance metrics tracked regularly?',
                'answer_choices': {
                    1: 'No tracking',
                    2: 'Occasional tracking',
                    3: 'Regular tracking',
                    4: 'Automated tracking',
                    5: 'Real-time monitoring'
                }
            },
            {
                'id': 'proc_variation',
                'text': 'Is process variation understood?',
                'answer_choices': {
                    1: 'Unknown',
                    2: 'Observed',
                    3: 'Analyzed',
                    4: 'Controlled',
                    5: 'Optimized'
                }
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
                'text': 'Is process data digitized?',
                'answer_choices': {
                    1: 'Mostly manual',
                    2: 'Partially digital',
                    3: 'Mostly digital',
                    4: 'Fully digital',
                    5: 'Automated capture'
                }
            },
            {
                'id': 'data_quality',
                'text': 'Is data cleaned and integrated?',
                'answer_choices': {
                    1: 'Uncleaned/siloed',
                    2: 'Basic cleaning',
                    3: 'Cleaned in silos',
                    4: 'Integrated',
                    5: 'Automated cleaning & integration'
                }
            },
            {
                'id': 'data_access',
                'text': 'Do you have access to historical data for model training?',
                'answer_choices': {
                    1: 'No access',
                    2: 'Limited access',
                    3: 'Moderate access',
                    4: 'Good access',
                    5: 'Comprehensive historical data'
                }
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
                'text': 'Does your tech stack support APIs, analytics, and automation?',
                'answer_choices': {
                    1: 'Minimal support',
                    2: 'Basic APIs',
                    3: 'Analytics capable',
                    4: 'Automation ready',
                    5: 'Fully integrated'
                }
            },
            {
                'id': 'tech_secure',
                'text': 'Do you have secure cloud or on-prem data systems?',
                'answer_choices': {
                    1: 'No secure systems',
                    2: 'Basic security',
                    3: 'Secure on-prem',
                    4: 'Secure cloud',
                    5: 'Enterprise-grade security'
                }
            },
            {
                'id': 'tech_ml',
                'text': 'Is there access to AI experimentation environments (e.g., ML tools)?',
                'answer_choices': {
                    1: 'No access',
                    2: 'Limited access',
                    3: 'Basic ML tools',
                    4: 'Advanced ML tools',
                    5: 'Full AI platform'
                }
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
                'text': 'Do teams understand AI fundamentals?',
                'answer_choices': {
                    1: 'No understanding',
                    2: 'Minimal awareness',
                    3: 'Basic understanding',
                    4: 'Good understanding',
                    5: 'Expert knowledge'
                }
            },
            {
                'id': 'people_training',
                'text': 'Are employees trained in data-driven decision-making?',
                'answer_choices': {
                    1: 'No training',
                    2: 'Ad-hoc training',
                    3: 'Some training',
                    4: 'Regular training',
                    5: 'Comprehensive programs'
                }
            },
            {
                'id': 'people_champions',
                'text': 'Are there AI champions or data translators?',
                'answer_choices': {
                    1: 'None',
                    2: 'Few individuals',
                    3: 'Some champions',
                    4: 'Dedicated roles',
                    5: 'Center of excellence'
                }
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
                'text': 'Is AI part of your organizational strategy?',
                'answer_choices': {
                    1: 'Not mentioned',
                    2: 'Under discussion',
                    3: 'In planning',
                    4: 'Documented strategy',
                    5: 'Core strategic pillar'
                }
            },
            {
                'id': 'leadership_funding',
                'text': 'Is leadership committed to funding pilots?',
                'answer_choices': {
                    1: 'No commitment',
                    2: 'Exploring',
                    3: 'Some budget',
                    4: 'Committed funding',
                    5: 'Strategic investment'
                }
            },
            {
                'id': 'leadership_goals',
                'text': 'Are goals aligned with business impact?',
                'answer_choices': {
                    1: 'No alignment',
                    2: 'Vague goals',
                    3: 'Some alignment',
                    4: 'Well aligned',
                    5: 'Fully integrated metrics'
                }
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
                'text': 'How open is your culture to experimenting and learning from failure?',
                'answer_choices': {
                    1: 'Resistant',
                    2: 'Risk-averse',
                    3: 'Cautiously open',
                    4: 'Encouraging',
                    5: 'Innovation-driven'
                }
            },
            {
                'id': 'change_collab',
                'text': 'Are cross-functional collaborations encouraged?',
                'answer_choices': {
                    1: 'Siloed',
                    2: 'Occasional',
                    3: 'Encouraged',
                    4: 'Standard practice',
                    5: 'Embedded culture'
                }
            },
            {
                'id': 'change_scale',
                'text': 'Is there a framework for scaling successful pilots?',
                'answer_choices': {
                    1: 'No framework',
                    2: 'Ad-hoc',
                    3: 'Basic framework',
                    4: 'Structured process',
                    5: 'Mature scaling system'
                }
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
