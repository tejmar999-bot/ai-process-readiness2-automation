"""
Dimension and question definitions for AI Process Readiness Assessment
"""

# Pastel color palette for dimensions - Distinct pastel colors
PALETTE = [
    '#D4A5A5',  # sec1 - Process Maturity
    '#FCD0A4',  # sec2 - Technology Infrastructure
    '#FFFB4B',  # sec3 - Data Readiness
    '#B9F0C9',  # sec4 - People & Culture
    '#B3E5FC',  # sec5 - Leadership & Alignment
    '#D7BDE2'   # sec6 - Governance & Risk
]

# Same colors used for titles
BRIGHT_PALETTE = [
    '#D4A5A5',  # Process Maturity
    '#FCD0A4',  # Technology Infrastructure
    '#FFFB4B',  # Data Readiness
    '#B9F0C9',  # People & Culture
    '#B3E5FC',  # Leadership & Alignment
    '#D7BDE2'   # Governance & Risk
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
                'id': 'proc_defined',
                'text': 'How well-defined and repeatable are your core processes?',
                'answer_choices': {
                    1: 'Ad hoc processes',
                    2: 'Partially defined',
                    3: 'Well-defined',
                    4: 'Highly standardized',
                    5: 'Fully optimized & repeatable'
                }
            },
            {
                'id': 'proc_compliance',
                'text': 'How consistently do teams follow documented procedures?',
                'answer_choices': {
                    1: 'Rarely follow',
                    2: 'Sometimes follow',
                    3: 'Generally follow',
                    4: 'Consistently follow',
                    5: 'Always follow'
                }
            },
            {
                'id': 'proc_efficiency',
                'text': 'How efficiently are tasks completed with minimal delays?',
                'answer_choices': {
                    1: 'Significant delays',
                    2: 'Occasional delays',
                    3: 'Mostly timely',
                    4: 'Very timely',
                    5: 'Highly efficient'
                }
            }
        ]
    },
    {
        'id': 'tech',
        'title': 'Technology Infrastructure',
        'what_it_measures': 'Availability of tools, platforms, and IT support for AI deployment.',
        'description': 'Tools and platforms available for analytics and automation.',
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
                'id': 'tech_modern',
                'text': 'How modern and scalable is your tech stack?',
                'answer_choices': {
                    1: 'Legacy systems',
                    2: 'Outdated',
                    3: 'Somewhat modern',
                    4: 'Modern',
                    5: 'Cutting-edge & scalable'
                }
            },
            {
                'id': 'tech_reliability',
                'text': 'How well-maintained and reliable are your core systems?',
                'answer_choices': {
                    1: 'Frequently unstable',
                    2: 'Periodically unstable',
                    3: 'Generally reliable',
                    4: 'Very reliable',
                    5: 'Highly reliable & stable'
                }
            },
            {
                'id': 'tech_automation',
                'text': 'How effectively do your tools support automation?',
                'answer_choices': {
                    1: 'Manual processes only',
                    2: 'Limited automation',
                    3: 'Some automation',
                    4: 'Strong automation',
                    5: 'Fully automated'
                }
            }
        ]
    },
    {
        'id': 'data',
        'title': 'Data Readiness',
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
                'id': 'data_accessible',
                'text': 'How accessible is relevant data to teams who need it?',
                'answer_choices': {
                    1: 'Not accessible',
                    2: 'Difficult to access',
                    3: 'Moderately accessible',
                    4: 'Easily accessible',
                    5: 'Readily accessible'
                }
            },
            {
                'id': 'data_quality',
                'text': 'How complete and accurate is your operational data?',
                'answer_choices': {
                    1: 'Incomplete & inaccurate',
                    2: 'Often incomplete',
                    3: 'Mostly complete',
                    4: 'Complete & accurate',
                    5: 'Comprehensive & verified'
                }
            },
            {
                'id': 'data_standardized',
                'text': 'How standardized are data formats across systems?',
                'answer_choices': {
                    1: 'No standardization',
                    2: 'Minimal standardization',
                    3: 'Partial standardization',
                    4: 'Well standardized',
                    5: 'Fully standardized'
                }
            }
        ]
    },
    {
        'id': 'people',
        'title': 'People & Culture',
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
                'id': 'people_adoption',
                'text': 'How comfortable are staff with adopting new tools?',
                'answer_choices': {
                    1: 'Very uncomfortable',
                    2: 'Somewhat uncomfortable',
                    3: 'Neutral',
                    4: 'Comfortable',
                    5: 'Very comfortable'
                }
            },
            {
                'id': 'people_experiment',
                'text': 'How willing are teams to experiment with new technology?',
                'answer_choices': {
                    1: 'Resistant',
                    2: 'Reluctant',
                    3: 'Somewhat willing',
                    4: 'Willing',
                    5: 'Highly willing & proactive'
                }
            },
            {
                'id': 'people_collaboration',
                'text': 'How effectively do teams collaborate across functions?',
                'answer_choices': {
                    1: 'Siloed',
                    2: 'Limited collaboration',
                    3: 'Regular collaboration',
                    4: 'Strong collaboration',
                    5: 'Excellent cross-functional collaboration'
                }
            }
        ]
    },
    {
        'id': 'leadership',
        'title': 'Leadership & Alignment',
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
                'id': 'leadership_commitment',
                'text': 'How committed are leaders to operational improvement?',
                'answer_choices': {
                    1: 'No commitment',
                    2: 'Minimal commitment',
                    3: 'Some commitment',
                    4: 'Committed',
                    5: 'Highly committed & invested'
                }
            },
            {
                'id': 'leadership_communication',
                'text': 'How consistently leadership communicates priorities?',
                'answer_choices': {
                    1: 'Inconsistent & unclear',
                    2: 'Sometimes clear',
                    3: 'Mostly consistent',
                    4: 'Consistent',
                    5: 'Very clear & consistent'
                }
            },
            {
                'id': 'leadership_resources',
                'text': 'How well are resources allocated toward transformation?',
                'answer_choices': {
                    1: 'No resources',
                    2: 'Minimal resources',
                    3: 'Adequate resources',
                    4: 'Well allocated',
                    5: 'Strategically invested'
                }
            }
        ]
    },
    {
        'id': 'governance',
        'title': 'Governance & Risk',
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
                'id': 'governance_roles',
                'text': 'How clearly defined are roles and responsibilities?',
                'answer_choices': {
                    1: 'Unclear',
                    2: 'Somewhat defined',
                    3: 'Defined',
                    4: 'Well-defined',
                    5: 'Crystal clear & documented'
                }
            },
            {
                'id': 'governance_risk',
                'text': 'How effectively are risks identified and mitigated?',
                'answer_choices': {
                    1: 'No risk management',
                    2: 'Ad-hoc approach',
                    3: 'Some processes',
                    4: 'Structured processes',
                    5: 'Comprehensive risk management'
                }
            },
            {
                'id': 'governance_compliance',
                'text': 'How well do compliance and processes stay aligned?',
                'answer_choices': {
                    1: 'Frequently misaligned',
                    2: 'Often misaligned',
                    3: 'Partially aligned',
                    4: 'Generally aligned',
                    5: 'Fully aligned & monitored'
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
