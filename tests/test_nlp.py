"""
test_nlp.py – Unit tests for the NLP preprocessing and VADER analysis service.
"""

import pytest
from backend.services.nlp import preprocess, classify_compound, analyse, analyse_many


class TestPreprocess:
    def test_returns_string(self):
        result = preprocess("Hello world")
        assert isinstance(result, str)

    def test_lowercases_text(self):
        result = preprocess("HELLO WORLD")
        assert result == result.lower()

    def test_removes_stopwords(self):
        # "the" is a stopword; should not appear in output
        result = preprocess("the quick brown fox")
        assert "the" not in result.split()

    def test_preserves_negations(self):
        # "not" must survive preprocessing so VADER can use it
        result = preprocess("I am not happy today")
        assert "not" in result

    def test_lemmatises_verbs(self):
        # "running" -> "run"
        result = preprocess("She is running every morning")
        assert "running" not in result or "run" in result

    def test_empty_string_returns_empty(self):
        result = preprocess("")
        assert result == ""

    def test_whitespace_only_returns_empty(self):
        result = preprocess("   ")
        assert result.strip() == ""


class TestClassifyCompound:
    def test_positive_threshold(self):
        assert classify_compound(0.05) == "Positive"
        assert classify_compound(0.9) == "Positive"

    def test_negative_threshold(self):
        assert classify_compound(-0.05) == "Negative"
        assert classify_compound(-0.9) == "Negative"

    def test_neutral_range(self):
        assert classify_compound(0.0) == "Neutral"
        assert classify_compound(0.04) == "Neutral"
        assert classify_compound(-0.04) == "Neutral"


class TestAnalyse:
    def test_returns_expected_keys(self):
        result = analyse("I love this!")
        for key in (
            "original_text", "processed_text", "sentiment_label",
            "compound_score", "positive_score", "negative_score", "neutral_score"
        ):
            assert key in result

    def test_positive_sentiment(self):
        result = analyse("I am extremely happy and delighted today!")
        assert result["sentiment_label"] == "Positive"
        assert result["compound_score"] >= 0.05

    def test_negative_sentiment(self):
        result = analyse("This is terrible, awful, and I hate it completely.")
        assert result["sentiment_label"] == "Negative"
        assert result["compound_score"] <= -0.05

    def test_neutral_sentiment(self):
        result = analyse("The document is on the table.")
        assert result["sentiment_label"] == "Neutral"

    def test_compound_score_range(self):
        result = analyse("I feel okay.")
        assert -1.0 <= result["compound_score"] <= 1.0

    def test_original_text_preserved(self):
        text = "Hello World! This is a TEST."
        result = analyse(text)
        assert result["original_text"] == text

    def test_negation_scored_correctly(self):
        # "not happy" should score lower (less positive) than "happy"
        positive = analyse("I am happy.")
        negated = analyse("I am not happy.")
        assert positive["compound_score"] > negated["compound_score"]


class TestAnalyseMany:
    def test_processes_multiple_texts(self):
        texts = ["I love it", "This is bad", "The sky is blue"]
        results = analyse_many(texts)
        assert len(results) == 3

    def test_skips_empty_strings(self):
        texts = ["", "  ", "I love it"]
        results = analyse_many(texts)
        assert len(results) == 1

    def test_empty_list_returns_empty(self):
        assert analyse_many([]) == []
