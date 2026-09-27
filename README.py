# FAQ Chatbot (NLTK + TF-IDF Cosine Similarity)

A small FAQ chatbot that matches a user's question to the closest FAQ using
classic NLP + IR techniques — no LLM required. Seeded with a **crop care**
FAQ set, but built so you can swap in any topic.

## How it works (matches the assignment steps)

| Step | File | What it does |
|---|---|---|
| 1. Collect FAQs | `faqs.json` | List of `{question, answer}` pairs |
| 2. Preprocess text | `nlp_utils.py` | NLTK: lowercase → tokenize → remove stopwords/punctuation → lemmatize |
| 3. Match question | `matcher.py` | scikit-learn `TfidfVectorizer` + `cosine_similarity` to find the closest FAQ question |
| 4. Return answer | `app.py` | Flask `/chat` endpoint returns the matched answer (or a fallback if similarity is too low) |
| 5. Chat UI | `templates/index.html`, `static/` | Simple browser chat interface |

### Why TF-IDF + cosine similarity (vs. just keyword matching)
Each FAQ question is turned into a vector of word-importance weights
(TF-IDF). A user's message is turned into the same kind of vector, and
cosine similarity measures the angle between them — closer to 1 means more
similar in meaning-bearing words. This lets phrasing vary ("when do I pick
my crop?" vs. "when is the right time to harvest crops?") while still
matching correctly, which plain exact-string matching cannot do.

A `DEFAULT_THRESHOLD = 0.25` in `matcher.py` avoids confidently answering
questions that don't actually match anything in the FAQ set — below that
score, the bot returns a fallback message instead of a wrong-but-plausible
answer. Tune this number based on how strict/lenient you want matching.

## Setup

```bash
pip install -r requirements.txt
```

The first run auto-downloads the small NLTK data it needs (`punkt`,
`stopwords`, `wordnet`) — this requires internet access once.

## Run

**Command-line version** (no browser needed):
```bash
python matcher.py
```

**Web chat UI**:
```bash
python app.py
```
Then open **http://127.0.0.1:5000** in your browser.

## Using your own FAQs

Replace the contents of `faqs.json` with your own topic's questions and
answers, in the same `{"question": "...", "answer": "..."}` format. Nothing
else needs to change — the vectorizer refits automatically on whatever is
in the file at startup.

## Project structure

```
faq_chatbot/
├── faqs.json          # FAQ data (swap this for your own topic)
├── nlp_utils.py        # Preprocessing pipeline (NLTK)
├── matcher.py           # TF-IDF + cosine similarity matching engine
├── app.py               # Flask server (UI + /chat API)
├── requirements.txt
├── templates/
│   └── index.html
└── static/
    ├── style.css
    └── script.js
```

## Extending this

- **Better matching**: swap TF-IDF for sentence embeddings (e.g.
  `sentence-transformers`) if you want semantic matching beyond shared
  vocabulary.
- **Intent matching**: group FAQs into intents and classify the user's
  message into an intent first, then return that intent's answer(s).
- **Logging unmatched questions**: log every fallback case to a file so you
  can see which FAQs are missing and grow the dataset over time.
