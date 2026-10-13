"""
nlp.py – Text preprocessing pipeline and VADER sentiment analysis.

Pipeline overview
-----------------
Two representations are produced for each input text:

1. processed_text  – used for display, shows what was cleaned.
   Steps: lowercase → strip excess whitespace → tokenise with spaCy →
          remove stop-words (but preserve negations) → lemmatise.

2. vader_input     – passed directly to VADER for scoring.
   VADER is trained on social media text and expects near-original casing,
   punctuation, and negation words.  We only apply minimal normalisation
   (whitespace collapse) so its heuristics work correctly.

Negation preservation
----------------------
Words such as "not", "never", "no", "n't" are explicitly excluded from
stop-word removal so that VADER's negation handling is not broken.

VADER thresholds (standard)
----------------------------
compound >= 0.05  → Positive
compound <= -0.05 → Negative
otherwise         → Neutral
"""

import re
import unicodedata

import nltk
import spacy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# ── One-time resource downloads ───────────────────────────────────────────────

def _download_nltk_resources() -> None:
    for resource in ("stopwords", "punkt", "punkt_tab"):
        try:
            nltk.data.find(f"tokenizers/{resource}")
        except LookupError:
            nltk.download(resource, quiet=True)

    try:
        nltk.data.find("corpora/stopwords")
    except LookupError:
        nltk.download("stopwords", quiet=True)


_download_nltk_resources()

from nltk.corpus import stopwords  # noqa: E402 – must follow download

_ENGLISH_STOPWORDS: set[str] = set(stopwords.words("english"))

# Negation words that MUST be kept so VADER scores correctly.
_NEGATIONS: set[str] = {
    "no", "not", "nor", "never", "neither", "nothing", "nowhere",
    "nobody", "none", "hardly", "scarcely", "barely",
    "n't",  # covers contractions split by tokeniser
}
_FILTERED_STOPWORDS: set[str] = _ENGLISH_STOPWORDS - _NEGATIONS


def _load_spacy() -> spacy.language.Language:
    """Load the small English spaCy model, downloading it if absent."""
    try:
        return spacy.load("en_core_web_sm", disable=["parser", "ner"])
    except OSError:
        from spacy.cli import download as spacy_download
        spacy_download("en_core_web_sm")
        return spacy.load("en_core_web_sm", disable=["parser", "ner"])


_nlp = _load_spacy()
_vader = SentimentIntensityAnalyzer()


# ── Preprocessing ─────────────────────────────────────────────────────────────

def _normalise_whitespace(text: str) -> str:
    """Collapse runs of whitespace to a single space and strip ends."""
    return re.sub(r"\s+", " ", text).strip()


def _unicode_normalise(text: str) -> str:
    """NFC-normalise unicode to handle combining characters consistently."""
    return unicodedata.normalize("NFC", text)


def preprocess(text: str) -> str:
    """
    Return a cleaned, lemmatised representation of *text* for display.

    Steps
    -----
    1. Unicode NFC normalisation
    2. Whitespace collapse
    3. Lowercase
    4. spaCy tokenisation and lemmatisation
    5. Stop-word removal (negations preserved)

    The processed text is NOT used for VADER scoring.
    """
    text = _unicode_normalise(text)
    text = _normalise_whitespace(text)
    text = text.lower()

    doc = _nlp(text)
    tokens = [
        token.lemma_
        for token in doc
        if not token.is_space
        and token.lemma_.lower() not in _FILTERED_STOPWORDS
        and not token.is_punct
    ]
    return " ".join(tokens)


# ── Sentiment analysis ────────────────────────────────────────────────────────

def _vader_input(text: str) -> str:
    """
    Return a minimally normalised version of *text* suitable for VADER.
    Only collapses whitespace – preserves original casing, punctuation,
    negations, and capitalisation that VADER's rules depend on.
    """
    return _normalise_whitespace(_unicode_normalise(text))


def classify_compound(compound: float) -> str:
    """
    Map a VADER compound score to a sentiment label using standard thresholds:
      >= 0.05  → Positive
      <= -0.05 → Negative
      else     → Neutral
    """
    if compound >= 0.05:
        return "Positive"
    if compound <= -0.05:
        return "Negative"
    return "Neutral"


def analyse(text: str) -> dict:
    """
    Run the full pipeline on a single text.

    Returns
    -------
    dict with keys:
        original_text   : the raw input
        processed_text  : cleaned + lemmatised representation
        sentiment_label : Positive | Negative | Neutral
        compound_score  : VADER compound (−1 to 1)
        positive_score  : VADER pos
        negative_score  : VADER neg
        neutral_score   : VADER neu
    """
    original = text
    processed = preprocess(text)
    scores = _vader.polarity_scores(_vader_input(text))

    return {
        "original_text": original,
        "processed_text": processed,
        "sentiment_label": classify_compound(scores["compound"]),
        "compound_score": round(scores["compound"], 4),
        "positive_score": round(scores["pos"], 4),
        "negative_score": round(scores["neg"], 4),
        "neutral_score": round(scores["neu"], 4),
    }


def analyse_many(texts: list[str]) -> list[dict]:
    """Run analyse() on each non-empty text in *texts*."""
    return [analyse(t) for t in texts if t and t.strip()]
