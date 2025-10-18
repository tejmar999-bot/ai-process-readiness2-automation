# utils/scoring.py
from typing import List, Tuple

def compute_scores(answers: List[float]) -> Tuple[List[float], float]:
    """
    Compute per-dimension averages and overall average.
    Expects answers to be a list of numeric values (ideally 18 entries: 6 dims x 3).
    Returns (dimension_scores_list_of_length_6, overall_average).
    """
    if not answers:
        return ([0.0] * 6, 0.0)

    chunk_size = 3
    num_full_chunks = len(answers) // chunk_size
    dim_scores = []
    for i in range(num_full_chunks):
        start = i * chunk_size
        chunk = answers[start:start + chunk_size]
        avg = round(sum(chunk) / len(chunk), 2)
        dim_scores.append(avg)

    # Pad to 6 dimensions if needed
    if len(dim_scores) < 6:
        dim_scores.extend([0.0] * (6 - len(dim_scores)))

    overall = round(sum(dim_scores[:num_full_chunks]) / max(1, num_full_chunks), 2)
    return (dim_scores[:6], overall)


def get_readiness_band(score: float) -> str:
    """
    Map overall score (0-5) to band label.
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
