"""
Dimension and question definitions for AI Process Readiness Assessment
"""

# Pastel color palette for dimensions - Distinct pastel colors
PALETTE = [
    '#D17070',  # sec1 - Process Maturity (brick red pastel)
    '#FDD9B8',  # sec2 - Technology Infrastructure
    '#FFFB4B',  # sec3 - Data Readiness
    '#B9F0C9',  # sec4 - People & Culture
    '#9DD0F8',  # sec5 - Leadership & Alignment
    '#D7BDE2'   # sec6 - Governance & Risk
]

# Same colors used for titles
BRIGHT_PALETTE = [
    '#D17070',  # Process Maturity (brick red pastel)
    '#FDD9B8',  # Technology Infrastructure
    '#FFFB4B',  # Data Readiness
    '#B9F0C9',  # People & Culture
    '#9DD0F8',  # Leadership & Alignment
    '#D7BDE2'   # Governance & Risk
]

DIMENSIONS = [
    {
        'id': 'process',
        'title': 'Process Maturity',
        'weight': 1.0,
        'what_it_measures': 'How well-defined, measured, and optimized processes are before applying AI.',
        'description': 'How well defined and measured your processes are.',
        'color': PALETTE[0],
        'scoring_labels': {
            1: 'Undocumented',
            2: 'Informal',
            3: 'Documented',
            4: 'Followed',
            5: 'Updated'
        },
        'questions': [
            {
                'id': 'proc_doc',
                'text': 'How well are your core business processes documented?',
                'answer_choices': {
                    1: 'Mostly undocumented; exists in people\'s heads',
                    2: 'Some informal documentation (emails, notes)',
                    3: 'Key processes documented but not consistently followed',
                    4: 'Processes documented and regularly followed',
                    5: 'Processes documented, followed, and regularly updated'
                }
            },
            {
                'id': 'proc_sop',
                'text': 'Do you have standard operating procedures (SOPs) for priority workflows?',
                'answer_choices': {
                    1: 'No written procedures exist',
                    2: 'Procedures exist for 1-2 critical processes only',
                    3: 'Procedures exist for some key processes (~25-50%)',
                    4: 'Procedures exist for most key processes (~50-75%)',
                    5: 'Comprehensive procedures for all critical processes (75%+)'
                }
            },
            {
                'id': 'proc_metrics',
                'text': 'How do you track process performance?',
                'answer_choices': {
                    1: 'No metrics tracked',
                    2: 'Ad-hoc tracking when problems arise',
                    3: 'Basic metrics tracked manually (spreadsheets)',
                    4: 'Regular metrics tracked with some automation',
                    5: 'Real-time dashboards with KPIs for key processes'
                }
            }
        ]
    },
    {
        'id': 'tech',
        'title': 'Technology Infrastructure',
        'weight': 1.2,
        'what_it_measures': 'Availability of tools, platforms, and IT support for AI deployment.',
        'description': 'Tools and platforms available for analytics and automation.',
        'color': PALETTE[1],
        'scoring_labels': {
            1: 'Legacy',
            2: 'Mixed',
            3: 'Current',
            4: 'Modern',
            5: 'Cutting-edge'
        },
        'questions': [
            {
                'id': 'tech_systems',
                'text': 'How would you describe your technology systems?',
                'answer_choices': {
                    1: 'Legacy systems, many unsupported or outdated',
                    2: 'Mix of old and new; some systems nearing end-of-life',
                    3: 'Mostly current systems with vendor support',
                    4: 'Modern, cloud-based systems with regular updates',
                    5: 'Cutting-edge, API-first platforms with strong vendor roadmaps'
                }
            },
            {
                'id': 'tech_integration',
                'text': 'How well do your systems share data with each other?',
                'answer_choices': {
                    1: 'Siloed systems; manual data transfer (email, USB, re-keying)',
                    2: 'Limited integration; mostly manual processes',
                    3: 'Some automated integration for critical workflows',
                    4: 'Most systems integrated with reliable data flow',
                    5: 'Fully integrated ecosystem with real-time data sync'
                }
            },
            {
                'id': 'tech_security',
                'text': 'How consistently is security and access control applied?',
                'answer_choices': {
                    1: 'Minimal security; shared passwords common',
                    2: 'Basic security but inconsistently applied',
                    3: 'Security policies exist; moderately enforced',
                    4: 'Strong security with role-based access mostly enforced',
                    5: 'Enterprise-grade security, audited, consistently enforced'
                }
            }
        ]
    },
    {
        'id': 'data',
        'title': 'Data Readiness',
        'weight': 1.5,
        'critical': True,
        'what_it_measures': 'Availability, accessibility, and accuracy of operational data for decision-making and AI.',
        'description': 'Availability, accessibility and accuracy of operational data.',
        'color': PALETTE[2],
        'scoring_labels': {
            1: 'Missing',
            2: 'Fragmented',
            3: 'Available',
            4: 'Accessible',
            5: 'Self-service'
        },
        'questions': [
            {
                'id': 'data_available',
                'text': 'How available is the data you need for decision-making?',
                'answer_choices': {
                    1: 'Critical data often missing or inaccessible',
                    2: 'Data exists but hard to access or fragmented',
                    3: 'Most data available but requires significant effort to compile',
                    4: 'Data readily accessible for most decisions',
                    5: 'Comprehensive data available on-demand via self-service tools'
                }
            },
            {
                'id': 'data_quality',
                'text': 'How would you rate your data quality?',
                'answer_choices': {
                    1: 'Significant errors, duplicates, or gaps in data',
                    2: 'Quality issues frequently impact decisions',
                    3: 'Acceptable quality but some known issues',
                    4: 'Good quality with occasional cleanup needed',
                    5: 'High quality, actively monitored and continuously improved'
                }
            },
            {
                'id': 'data_pipelines',
                'text': 'How reliable are your data pipelines and access?',
                'answer_choices': {
                    1: 'No automated pipelines; manual data collection',
                    2: 'Unreliable pipelines; frequent breaks or delays',
                    3: 'Pipelines work but require regular manual intervention',
                    4: 'Reliable automated pipelines with minimal issues',
                    5: 'Enterprise-grade pipelines with monitoring and alerting'
                }
            }
        ]
    },
    {
        'id': 'people',
        'title': 'People & Culture',
        'weight': 1.3,
        'what_it_measures': 'Workforce awareness, capability, and openness toward AI and digital transformation.',
        'description': 'Workforce capability and understanding of AI and data-driven methods.',
        'color': PALETTE[3],
        'scoring_labels': {
            1: 'Limited',
            2: 'Basic',
            3: 'Comfortable',
            4: 'Skilled',
            5: 'Champions'
        },
        'questions': [
            {
                'id': 'people_capability',
                'text': 'What is your team\'s baseline capability with data and technology?',
                'answer_choices': {
                    1: 'Limited digital/data skills; resistance to tech changes',
                    2: 'Basic digital literacy; minimal data analysis skills',
                    3: 'Comfortable with standard tools (Excel, email, CRM)',
                    4: 'Some team members skilled in data analysis/automation',
                    5: 'Strong data literacy across teams; champions in place'
                }
            },
            {
                'id': 'people_openness',
                'text': 'How open is your organization to data-driven change?',
                'answer_choices': {
                    1: 'Strong resistance; "we\'ve always done it this way" culture',
                    2: 'Skeptical; change happens slowly with pushback',
                    3: 'Neutral; willing to try but need convincing',
                    4: 'Generally open; early adopters encourage others',
                    5: 'Innovation-focused culture; actively seeks improvements'
                }
            },
            {
                'id': 'people_learning',
                'text': 'What learning and upskilling efforts are in place?',
                'answer_choices': {
                    1: 'No formal training or development programs',
                    2: 'Occasional ad-hoc training when issues arise',
                    3: 'Annual training budget but not strategically planned',
                    4: 'Regular training programs with some tracking',
                    5: 'Comprehensive learning paths with tracked skill development'
                }
            }
        ]
    },
    {
        'id': 'leadership',
        'title': 'Leadership & Alignment',
        'weight': 1.5,
        'critical': True,
        'what_it_measures': 'Executive commitment and strategic clarity for AI adoption.',
        'description': 'Executive commitment and strategic alignment for AI.',
        'color': PALETTE[4],
        'scoring_labels': {
            1: 'Unaware',
            2: 'Aware',
            3: 'Supportive',
            4: 'Sponsor',
            5: 'Champion'
        },
        'questions': [
            {
                'id': 'leadership_involvement',
                'text': 'How involved is senior leadership in AI/digital initiatives?',
                'answer_choices': {
                    1: 'Unaware or dismissive of AI opportunities',
                    2: 'Aware but not actively engaged',
                    3: 'Supportive when asked; delegates to others',
                    4: 'Actively sponsors specific initiatives',
                    5: 'Champions AI strategy; personally involved in key decisions'
                }
            },
            {
                'id': 'leadership_goals',
                'text': 'How well are AI/automation goals connected to business outcomes?',
                'answer_choices': {
                    1: 'No clear goals for AI or automation',
                    2: 'Vague aspirations ("we should use AI somehow")',
                    3: 'General goals but not linked to specific business metrics',
                    4: 'Clear goals tied to measurable business outcomes',
                    5: 'Strategic roadmap with AI tied to revenue, cost, or customer goals'
                }
            },
            {
                'id': 'leadership_budget',
                'text': 'Is there committed budget and resources for AI initiatives?',
                'answer_choices': {
                    1: 'No budget allocated',
                    2: 'Budget discussions only; no commitment',
                    3: 'Small experimental budget (<5% of IT/ops budget)',
                    4: 'Dedicated budget with assigned resources (5-15%)',
                    5: 'Strategic investment with cross-functional resources (15%+)'
                }
            }
        ]
    },
    {
        'id': 'governance',
        'title': 'Governance & Risk',
        'weight': 1.0,
        'what_it_measures': 'Clear roles, risk management, guardrails, and compliance frameworks for AI and process management.',
        'description': 'Roles, risk management, guardrails, and compliance frameworks.',
        'color': PALETTE[5],
        'scoring_labels': {
            1: 'No policies',
            2: 'Informal',
            3: 'Basic',
            4: 'Clear',
            5: 'Comprehensive'
        },
        'questions': [
            {
                'id': 'governance_policies',
                'text': 'What policies exist for responsible AI use?',
                'answer_choices': {
                    1: 'No policies or guidelines',
                    2: 'Aware of the need but nothing documented',
                    3: 'Basic guidelines in development',
                    4: 'Clear policies documented and communicated',
                    5: 'Comprehensive framework with regular reviews and training'
                }
            },
            {
                'id': 'governance_change',
                'text': 'How is change managed when implementing new processes or tools?',
                'answer_choices': {
                    1: 'No formal change management; changes announced and imposed',
                    2: 'Minimal communication; changes often surprise employees',
                    3: 'Basic communication plan for major changes',
                    4: 'Structured change management for most initiatives',
                    5: 'Mature change management with stakeholder engagement and feedback loops'
                }
            },
            {
                'id': 'governance_compliance',
                'text': 'How are compliance and regulatory risks addressed?',
                'answer_choices': {
                    1: 'Not considered or reactive only when issues arise',
                    2: 'Aware of requirements but inconsistently addressed',
                    3: 'Compliance checked for major initiatives',
                    4: 'Regular compliance reviews with documented processes',
                    5: 'Proactive risk monitoring with legal/compliance integration'
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
