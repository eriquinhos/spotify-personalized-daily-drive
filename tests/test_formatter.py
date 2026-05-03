import pytest

from utils.formatter import normalize, similarity


def test_normalize_removes_accents_and_punctuation():
    assert normalize(" Café-da-Manhã!! ") == "cafe da manha"
    assert normalize("Áccênts and Spaces") == "accents and spaces"
    assert normalize("Hello, WORLD") == "hello world"


def test_similarity_calculation():
    assert similarity("Hello", "hello") == pytest.approx(1.0, rel=1e-6)
    assert similarity("Café", "Cafe manha") > 0.2
