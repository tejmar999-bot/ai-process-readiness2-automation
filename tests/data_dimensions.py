# tests/test_data_dimensions.py
from data.dimensions import DIMENSIONS, BRIGHT_PALETTE, get_all_questions

def test_dimensions_count():
    assert isinstance(DIMENSIONS, list)
    assert len(DIMENSIONS) == 6

def test_palette_length():
    assert isinstance(BRIGHT_PALETTE, list)
    assert len(BRIGHT_PALETTE) >= 6

def test_questions_count():
    q = get_all_questions()
    assert isinstance(q, list)
    assert len(q) == 18
