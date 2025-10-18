"""
utils/scoring.py

Provides simple scoring helpers used by streamlit_app.py:
- compute_scores(answers): returns (dimension_scores_list, overall_score)
- get_readiness_band(score): returns a human-friendly band string
"""

from typing import List, Tuple


def compute_scores(answers: List[float]) -> Tuple[List[float], float]:
    """
    Compute per-dimension average scores and overall average.

    We assume answers contains 18 numeric values (6 dimensions × 3 questions each).
    If a different length is provided, this function will attempt to partition into
    equal-sized chunks; if that fails, it will compute per-3-question averages
    for as many full dimensions as possible and ignore trailing values.

    Returns:
        (dimension_scores, overall_score)
    """
    if not answers:
        return ([0.0] * 6, 0.0)

    # Prefer 6 dims × 3 = 18 standard layout; otherwise compute in groups of 3
    chunk_size = 3
    num_full_chunks = len(answers) // chunk_size
    if num_full_chunks == 0:
        # nothing meaningful, return zeros
        return ([0.0] * 6, 0.0)

    dim_scores = []
    for i in range(num_full_chunks):
        start = i * chunk_size
        chunk = answers[start:start + chunk_size]
        avg = sum(chunk) / len(chunk)
        dim_scores.append(round(avg, 2))

    # If fewer than 6 dims present, pad with zeros to length 6 (compatibility)
    if len(dim_scores) < 6:
        dim_scores.extend([0.0] * (6 - len(dim_scores)))

    overall = round(sum(dim_scores[:num_full_chunks]) / max(1, num_full_chunks), 2)
    return (dim_scores[:6], overall)


def get_readiness_band(score: float) -> str:
    """
    Map an overall numeric score (0-5 assumed) to a readiness band.

    Bands:
      - 'Low'       -> score < 3.0
      - 'Moderate'  -> 3.0 <= score < 4.0
      - 'High'      -> score >= 4.0

    Returns a short label string.
    """
    try:
        s = float(score)
    except Exception:
        return "Unknown"

    if s >= 4.0:
        return "High"
    if s >= 3.0:
        return "Moderate"
    return "Low"
