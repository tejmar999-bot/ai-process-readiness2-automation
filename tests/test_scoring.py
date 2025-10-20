# tests/test_scoring.py
from utils.scoring import compute_scores, get_readiness_band

def test_compute_scores_standard():
    answers = [3.0] * 18
    dims, overall = compute_scores(answers)
    assert len(dims) == 6
    assert all(abs(d - 3.0) < 1e-6 for d in dims)
    assert abs(overall - 3.0) < 1e-6

def test_compute_scores_partial():
    answers = [5.0] * 9  # 3 full dimensions only
    dims, overall = compute_scores(answers)
    assert dims[0] == 5.0
    assert dims[1] == 5.0
    assert dims[2] == 5.0
    assert overall == 5.0

def test_get_readiness_band():
    assert get_readiness_band(4.5) == "High"
    assert get_readiness_band(3.5) == "Moderate"
    assert get_readiness_band(2.9) == "Low"
