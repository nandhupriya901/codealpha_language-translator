"""
nlp_utils.py
------------
Text preprocessing helpers used to clean and normalize both the FAQ
questions and the user's incoming messages before similarity matching.

Steps applied (classic NLP pipeline):
  1. Lowercase
  2. Tokenize (split into words)
  3. Remove punctuation / non-alphabetic tokens
  4. Remove stopwords ("the", "is", "and", ...)
  5. Lemmatize (reduce words to their base/dictionary form)
"""

import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize


def ensure_nltk_data():
    """Download the small NLTK corpora needed, if not already present."""
    required = [
        ("tokenizers/punkt", "punkt"),
        ("tokenizers/punkt_tab", "punkt_tab"),
        ("corpora/stopwords", "stopwords"),
        ("corpora/wordnet", "wordnet"),
        ("corpora/omw-1.4", "omw-1.4"),
    ]
    for path, pkg in required:
        try:
            nltk.data.find(path)
        except LookupError:
            nltk.download(pkg, quiet=True)


ensure_nltk_data()

_lemmatizer = WordNetLemmatizer()
_stop_words = set(stopwords.words("english"))


def clean_text(text: str) -> str:
    """
    Run the full preprocessing pipeline on a piece of text and return
    a single cleaned string (tokens rejoined with spaces), ready to be
    fed into a vectorizer such as TF-IDF.
    """
    text = text.lower()
    text = re.sub(r"[^a-z\s]", " ", text)  # strip punctuation/numbers

    try:
        tokens = word_tokenize(text)
    except LookupError:
        # Fallback if punkt data isn't available for some reason
        tokens = text.split()

    cleaned_tokens = [
        _lemmatizer.lemmatize(tok)
        for tok in tokens
        if tok not in _stop_words and len(tok) > 1
    ]
    return " ".join(cleaned_tokens)
