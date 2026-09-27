"""
matcher.py
----------
Loads a set of FAQs, preprocesses them, and matches incoming user
questions to the closest FAQ using TF-IDF + cosine similarity.
"""

import json
from dataclasses import dataclass
from typing import List, Optional

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from nlp_utils import clean_text

# Below this similarity score, we consider it "no confident match"
# and return a fallback response instead of a poor guess.
DEFAULT_THRESHOLD = 0.25


@dataclass
class MatchResult:
    question: str
    answer: str
    score: float


class FAQMatcher:
    def __init__(self, faq_path: str, threshold: float = DEFAULT_THRESHOLD):
        self.threshold = threshold
        self.faqs = self._load_faqs(faq_path)
        self.questions = [f["question"] for f in self.faqs]
        self.answers = [f["answer"] for f in self.faqs]

        # Preprocess every stored FAQ question once, up front.
        self.cleaned_questions = [clean_text(q) for q in self.questions]

        # Fit TF-IDF over the FAQ question corpus.
        self.vectorizer = TfidfVectorizer()
        self.faq_vectors = self.vectorizer.fit_transform(self.cleaned_questions)

    @staticmethod
    def _load_faqs(path: str) -> List[dict]:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def find_best_match(self, user_message: str) -> Optional[MatchResult]:
        """
        Returns the best-matching FAQ for the given user message, or
        None if nothing clears the similarity threshold.
        """
        cleaned = clean_text(user_message)
        if not cleaned.strip():
            return None

        user_vector = self.vectorizer.transform([cleaned])
        similarities = cosine_similarity(user_vector, self.faq_vectors)[0]

        best_idx = similarities.argmax()
        best_score = float(similarities[best_idx])

        if best_score < self.threshold:
            return None

        return MatchResult(
            question=self.questions[best_idx],
            answer=self.answers[best_idx],
            score=best_score,
        )

    def top_matches(self, user_message: str, k: int = 3) -> List[MatchResult]:
        """Return the top-k matches regardless of threshold (useful for debugging)."""
        cleaned = clean_text(user_message)
        if not cleaned.strip():
            return []

        user_vector = self.vectorizer.transform([cleaned])
        similarities = cosine_similarity(user_vector, self.faq_vectors)[0]
        ranked = sorted(
            range(len(similarities)), key=lambda i: similarities[i], reverse=True
        )[:k]

        return [
            MatchResult(self.questions[i], self.answers[i], float(similarities[i]))
            for i in ranked
        ]


if __name__ == "__main__":
    # Quick command-line test, no Flask/UI needed:
    #   python matcher.py
    matcher = FAQMatcher("faqs.json")
    print("FAQ matcher ready. Type a question (or 'quit').\n")
    while True:
        msg = input("You: ").strip()
        if msg.lower() in ("quit", "exit"):
            break
        result = matcher.find_best_match(msg)
        if result:
            print(f"Bot ({result.score:.2f}): {result.answer}\n")
        else:
            print("Bot: Sorry, I don't have an answer for that yet.\n")
