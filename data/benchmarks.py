"""
Industry Benchmarks for AI Process Readiness Assessment
"""

# Industry benchmark scores (average scores across different maturity levels)
INDUSTRY_BENCHMARKS = {
    'Small Business (< 50 employees)': {
        'process': 2.5,
        'data': 2.3,
        'tech': 2.4,
        'people': 2.2,
        'leadership': 2.6,
        'change': 2.7,
        'total': 14.7,
        'description': 'Small businesses typically have informal processes and limited AI infrastructure'
    },
    'Mid-Market (50-500 employees)': {
        'process': 3.2,
        'data': 3.0,
        'tech': 3.1,
        'people': 2.8,
        'leadership': 3.3,
        'change': 3.1,
        'total': 18.5,
        'description': 'Mid-market companies often have established processes and are beginning AI adoption'
    },
    'Enterprise (500+ employees)': {
        'process': 3.8,
        'data': 3.7,
        'tech': 3.9,
        'people': 3.5,
        'leadership': 4.0,
        'change': 3.6,
        'total': 22.5,
        'description': 'Large enterprises typically have mature processes and active AI initiatives'
    },
    'Technology Leaders': {
        'process': 4.3,
        'data': 4.5,
        'tech': 4.6,
        'people': 4.2,
        'leadership': 4.5,
        'change': 4.4,
        'total': 26.5,
        'description': 'Technology-first companies with advanced AI capabilities and mature practices'
    },
    'Industry Average': {
        'process': 3.1,
        'data': 3.0,
        'tech': 3.2,
        'people': 2.9,
        'leadership': 3.2,
        'change': 3.0,
        'total': 18.4,
        'description': 'Overall average across all industries and company sizes'
    }
}

def get_benchmark_comparison(your_scores, benchmark_name='Industry Average'):
    """
    Compare user scores against a specific benchmark
    
    Args:
        your_scores: Dictionary with dimension_scores from compute_scores
        benchmark_name: Name of the benchmark to compare against
        
    Returns:
        Dictionary with comparison data
    """
    if benchmark_name not in INDUSTRY_BENCHMARKS:
        benchmark_name = 'Industry Average'
    
    benchmark = INDUSTRY_BENCHMARKS[benchmark_name]
    dimension_scores = your_scores['dimension_scores']
    
    comparison = {
        'benchmark_name': benchmark_name,
        'benchmark_description': benchmark['description'],
        'your_total': your_scores['total'],
        'benchmark_total': benchmark['total'],
        'total_difference': your_scores['total'] - benchmark['total'],
        'dimensions': []
    }
    
    for score_data in dimension_scores:
        dim_id = score_data['id']
        your_score = score_data['score']
        benchmark_score = benchmark.get(dim_id, 3.0)
        
        comparison['dimensions'].append({
            'id': dim_id,
            'title': score_data['title'],
            'your_score': your_score,
            'benchmark_score': benchmark_score,
            'difference': your_score - benchmark_score,
            'percentage_of_benchmark': round((your_score / benchmark_score * 100) if benchmark_score > 0 else 0, 1)
        })
    
    return comparison

def get_all_benchmarks():
    """Get list of all available benchmarks"""
    return list(INDUSTRY_BENCHMARKS.keys())

def get_benchmark_data(benchmark_name):
    """Get benchmark data for a specific benchmark"""
    return INDUSTRY_BENCHMARKS.get(benchmark_name, INDUSTRY_BENCHMARKS['Industry Average'])
