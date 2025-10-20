# utils/scoring.py
from typing import List, Tuple


def compute_scores(answers: List[float]) -> Tuple[List[float], float]:
    """
    Compute per-dimension averages and overall average.

    Expects `answers` to be a list of numeric values, ideally length 18 (6 dims * 3 questions).
    Returns (dimension_scores_list_of_length_6, overall_average_across_present_dims)
    """
    if not answers:
        return ([0.0] * 6, 0.0)

    # Convert to floats, non-convertible -> neutral 3.0
    vals = []
    for v in answers:
        try:
            vals.append(float(v))
        except Exception:
            vals.append(3.0)

    CHUNK = 3
    num_full_chunks = len(vals) // CHUNK
    if num_full_chunks == 0:
        return ([0.0] * 6, 0.0)

    dim_scores: List[float] = []
    for i in range(num_full_chunks):
        start = i * CHUNK
        chunk = vals[start:start + CHUNK]
        avg = round(sum(chunk) / len(chunk), 2)
        dim_scores.append(avg)

    # Pad to 6 dims
    if len(dim_scores) < 6:
        dim_scores.extend([0.0] * (6 - len(dim_scores)))

    # overall is average of present dims only
    overall = round(sum(dim_scores[:num_full_chunks]) / max(1, num_full_chunks), 2)

    return (dim_scores[:6], overall)


def get_readiness_band(score: float) -> str:
    """
    Map overall score to 'High'/'Moderate'/'Low'
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
