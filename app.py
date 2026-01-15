from flask import Flask, render_template, request, jsonify, session
import os
from openai import OpenAI

app = Flask(__name__)
app.secret_key = "opentutor-memory-key"

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MAX_MEMORY = 6  # last 6 messages only


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question", "").strip()
    mode = data.get("mode", "tutor")

    if not question:
        return jsonify({"answer": "❌ Please enter a question."})

    # Initialize memory
    if "chat" not in session:
        session["chat"] = []

    # Exam mode = no memory
    messages = []

    if mode == "exam":
        system_prompt = (
            "You are in EXAM MODE.\n"
            "- Give short, direct, exam-ready answers.\n"
            "- No extra explanation.\n"
        )
        messages.append({"role": "system", "content": system_prompt})
    else:
        system_prompt = (
            "You are OpenTutor AI in TUTOR MODE.\n"
            "- Explain step by step.\n"
            "- Stay on topic.\n"
            "- Remember the conversation context.\n"
            "- Reply in user's language.\n"
        )
        messages.append({"role": "system", "content": system_prompt})

        # Add memory
        for m in session["chat"][-MAX_MEMORY:]:
            messages.append(m)

    # Add current question
    messages.append({"role": "user", "content": question})

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.4,
            max_tokens=600
        )

        answer = response.choices[0].message.content.strip()

        # Save memory (tutor only)
        if mode != "exam":
            session["chat"].append({"role": "user", "content": question})
            session["chat"].append({"role": "assistant", "content": answer})
            session["chat"] = session["chat"][-MAX_MEMORY * 2:]

        return jsonify({"answer": answer})

    except Exception as e:
        return jsonify({"answer": "❌ Server busy. Please try again."})


@app.route("/clear", methods=["POST"])
def clear_chat():
    session.clear()
    return jsonify({"status": "cleared"})


if __name__ == "__main__":
    app.run(debug=True)
