# utils/scoring.py
from typing import List, Tuple


def compute_scores(answers: List[float]) -> Tuple[List[float], float]:
    """
    Compute per-dimension averages and overall average.

    Expects `answers` to be a list of numeric values, ideally length 18 (6 dims * 3 questions).
    Behavior:
      - Partition answers into chunks of size 3 (questions per dimension).
      - Compute the average for each full chunk.
      - If fewer than 6 chunks present, pad remaining dimensions with 0.0 so the returned
        dimension list always has length 6.
      - overall is the average of the *present* dimension averages (i.e., across num_full_chunks)
        or 0.0 if no answers.

    Returns:
        (dimension_scores_list_of_length_6, overall_average_across_present_dims)
    """
    if not answers:
        return ([0.0] * 6, 0.0)

    # Ensure it's a list and convert numeric-like values to float where possible
    vals = []
    for v in answers:
        try:
            vals.append(float(v))
        except Exception:
            # Non-convertible values treated as neutral 3.0
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

    # Overall is the average of the present dims only
    overall = round(sum(dim_scores[:num_full_chunks]) / max(1, num_full_chunks), 2)

    # Ensure returned dimension list length is exactly 6
    return (dim_scores[:6], overall)


def get_readiness_band(score: float) -> str:
    """
    Map an overall numeric score (0-5 scale) to a readiness band string.
      - "High"    -> score >= 4.0
      - "Moderate"-> 3.0 <= score < 4.0
      - "Low"     -> score < 3.0
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
