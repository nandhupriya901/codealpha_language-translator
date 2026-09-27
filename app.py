"""
app.py
------
Flask web server exposing:
  GET  /            -> chat UI
  POST /chat        -> {"message": "..."} -> {"answer": "...", "score": 0.0-1.0, "matched_question": "..."}

Run with:
    python app.py
Then open http://127.0.0.1:5000 in your browser.
"""

from flask import Flask, jsonify, render_template, request

from matcher import FAQMatcher

app = Flask(__name__)
matcher = FAQMatcher("faqs.json")

FALLBACK_ANSWER = (
    "I'm not confident I have the right answer for that yet. "
    "Try rephrasing, or ask about watering, pests, soil, fertilizer, "
    "harvesting, or plant diseases."
)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()

    if not user_message:
        return jsonify({"answer": "Please type a question.", "score": 0, "matched_question": None})

    result = matcher.find_best_match(user_message)

    if result is None:
        return jsonify({"answer": FALLBACK_ANSWER, "score": 0, "matched_question": None})

    return jsonify(
        {
            "answer": result.answer,
            "score": round(result.score, 3),
            "matched_question": result.question,
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
