from flask import Flask, render_template, request, jsonify, session
from openai import OpenAI
import os

app = Flask(__name__)
app.secret_key = "opentutor-secret"

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

@app.route("/")
def index():
    session.setdefault("mode", "tutor")
    return render_template("index.html")


@app.route("/set_mode", methods=["POST"])
def set_mode():
    session["mode"] = request.json.get("mode", "tutor")
    return jsonify({"status": "ok"})


@app.route("/ask", methods=["POST"])
def ask():
    question = request.json.get("question", "").strip()
    if not question:
        return jsonify({"answer": "❌ Sawal khali hai"})

    mode = session.get("mode", "tutor")

    if mode == "exam":
        prompt = (
            "Answer in EXAM MODE.\n"
            "Short, direct, exam-oriented.\n\n"
            f"Question: {question}"
        )
    else:
        prompt = (
            "Explain like a friendly teacher in Hindi-English mix.\n"
            "Step by step with examples.\n\n"
            f"Question: {question}"
        )

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt
        )

        answer = response.output_text.strip()

    except Exception as e:
        return jsonify({"answer": f"❌ AI Error: {str(e)}"})

    return jsonify({"answer": answer})


@app.route("/clear", methods=["POST"])
def clear():
    session.clear()
    return jsonify({"status": "cleared"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
