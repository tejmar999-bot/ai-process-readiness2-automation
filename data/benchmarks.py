"""
Industry Benchmarks for AI Process Readiness Assessment
"""
from db.models import DEFAULT_BASELINE

# Industry benchmark scores (average scores across different maturity levels)
INDUSTRY_BENCHMARKS = {
    'Small Business (< 50 employees)': {
        'process': 7.4,
        'tech': 7.0,
        'data': 6.8,
        'people': 7.7,
        'leadership': 6.4,
        'change': 6.1,
        'total': 41.4,
        'description': 'Small businesses typically have informal processes and limited AI infrastructure'
    },
    'Mid-Market (50-500 employees)': {
        'process': 8.9,
        'tech': 8.4,
        'data': 8.3,
        'people': 9.3,
        'leadership': 8.1,
        'change': 7.8,
        'total': 50.8,
        'description': 'Mid-market companies often have established processes and are beginning AI adoption'
    },
    'Enterprise (500+ employees)': {
        'process': 10.1,
        'tech': 10.3,
        'data': 9.9,
        'people': 11.0,
        'leadership': 9.5,
        'change': 9.1,
        'total': 59.9,
        'description': 'Large enterprises typically have mature processes and active AI initiatives'
    },
    'Technology Leaders': {
        'process': 11.5,
        'tech': 11.8,
        'data': 11.2,
        'people': 12.3,
        'leadership': 10.9,
        'change': 10.5,
        'total': 68.2,
        'description': 'Technology-first companies with advanced AI capabilities and mature practices'
    },
    'Industry Average': {
        'process': 11.1,
        'tech': 10.5,
        'data': 10.2,
        'people': 11.5,
        'leadership': 9.6,
        'change': 9.2,
        'total': 62.1,
        'description': 'Overall average across all industries and company sizes'
    }
}

def get_benchmark_comparison(your_scores, benchmark_name='Industry Average'):
    """
    Compare user scores against a specific benchmark using ID-based matching
    
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
    
    # Use ID-based matching to ensure correct benchmark alignment
    for score_data in dimension_scores:
        dim_id = score_data['id']
        your_score = score_data['score']
        
        # Get benchmark score by ID, default to 9.1 if not found
        benchmark_score = benchmark.get(dim_id, 9.1)
        
        # Ensure benchmark_score is valid for division
        if benchmark_score == 0:
            percentage = 0
        else:
            percentage = round((your_score / benchmark_score * 100), 1)
        
        comparison['dimensions'].append({
            'id': dim_id,
            'title': score_data['title'],
            'your_score': your_score,
            'benchmark_score': round(benchmark_score, 1),  # Round for display consistency
            'difference': round(your_score - benchmark_score, 1),
            'percentage_of_benchmark': percentage
        })
    
    return comparison

def get_all_benchmarks():
    """Get list of all available benchmarks including moving average"""
    benchmarks = ['Moving Average Benchmark'] + list(INDUSTRY_BENCHMARKS.keys())
    return benchmarks

def get_benchmark_data(benchmark_name):
    """Get benchmark data for a specific benchmark"""
    if benchmark_name == 'Moving Average Benchmark':
        return get_moving_average_benchmark()
    return INDUSTRY_BENCHMARKS.get(benchmark_name, INDUSTRY_BENCHMARKS['Industry Average'])

def get_moving_average_benchmark():
    """
    Get the current moving average benchmark from the database.
    This is updated as users complete assessments (excluding outliers).
    
    Returns:
        Dictionary with dimension scores and metadata similar to INDUSTRY_BENCHMARKS format
    """
    try:
        from db.operations import get_current_benchmark
        
        benchmark_scores = get_current_benchmark()
        
        # Map dimension IDs to benchmark scores
        dimension_ids = ['process', 'tech', 'data', 'people', 'leadership', 'change']
        
        benchmark_dict = {}
        total = 0
        for i, dim_id in enumerate(dimension_ids):
            score = benchmark_scores[i] if i < len(benchmark_scores) else 9.1
            benchmark_dict[dim_id] = round(score, 1)
            total += score
        
        return {
            'process': benchmark_dict.get('process', 11.1),
            'tech': benchmark_dict.get('tech', 10.5),
            'data': benchmark_dict.get('data', 10.2),
            'people': benchmark_dict.get('people', 11.5),
            'leadership': benchmark_dict.get('leadership', 9.6),
            'change': benchmark_dict.get('change', 9.2),
            'total': round(total, 1),
            'description': 'Moving average benchmark from all valid assessments'
        }
    except Exception as e:
        print(f"Error fetching moving average benchmark: {e}")
        # Return default baseline on error
        return {
            'process': 11.1,
            'tech': 10.5,
            'data': 10.2,
            'people': 11.5,
            'leadership': 9.6,
            'change': 9.2,
            'total': 62.1,
            'description': 'Default baseline (moving average unavailable)'
        }
