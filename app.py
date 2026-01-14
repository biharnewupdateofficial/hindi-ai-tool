from flask import Flask, render_template, request, jsonify, session
from openai import OpenAI
import os

app = Flask(__name__)
app.secret_key = "opentutor-secret-key"

# OpenAI client (NEW API)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/")
def index():
    if "mode" not in session:
        session["mode"] = "tutor"
    if "history" not in session:
        session["history"] = []
    return render_template("index.html")

@app.route("/set-mode", methods=["POST"])
def set_mode():
    data = request.get_json()
    session["mode"] = data.get("mode", "tutor")
    session["history"] = []
    return jsonify({"status": "ok"})

@app.route("/clear", methods=["POST"])
def clear():
    session["history"] = []
    return jsonify({"status": "cleared"})

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"answer": "❌ Empty question"})

    system_prompt = (
        "You are OpenTutor AI. "
        "Explain clearly in simple Hindi-English mix. "
        "If in exam mode, give short and direct answers."
    )

    messages = [{"role": "system", "content": system_prompt}]

    for q, a in session.get("history", []):
        messages.append({"role": "user", "content": q})
        messages.append({"role": "assistant", "content": a})

    messages.append({"role": "user", "content": question})

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )

        answer = response.choices[0].message.content

        history = session.get("history", [])
        history.append((question, answer))
        session["history"] = history[-5:]

        return jsonify({"answer": answer})

    except Exception as e:
        return jsonify({"answer": f"❌ OpenAI Error: {str(e)}"})


if __name__ == "__main__":
    app.run(debug=True)
