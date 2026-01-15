from flask import Flask, render_template, request, jsonify, session
import os
import time
from openai import OpenAI

app = Flask(__name__)
app.secret_key = "opentutor-secure-key"

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MAX_MEMORY = 6
RATE_LIMIT = 10          # requests
RATE_WINDOW = 60         # seconds


def is_rate_limited():
    now = time.time()

    if "requests" not in session:
        session["requests"] = []

    # Remove old timestamps
    session["requests"] = [
        t for t in session["requests"] if now - t < RATE_WINDOW
    ]

    if len(session["requests"]) >= RATE_LIMIT:
        return True

    session["requests"].append(now)
    return False


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    if is_rate_limited():
        return jsonify({
            "answer": "⏳ Thoda ruk jaiye. Aap bahut zyada request bhej rahe hain."
        })

    data = request.get_json()
    question = data.get("question", "").strip()
    mode = data.get("mode", "tutor")

    if not question:
        return jsonify({"answer": "❌ Please enter a question."})

    if "chat" not in session:
        session["chat"] = []

    messages = []

    if mode == "exam":
        system_prompt = (
            "You are in EXAM MODE.\n"
            "- Short, direct, exam-ready answers.\n"
            "- No extra explanation.\n"
        )
        messages.append({"role": "system", "content": system_prompt})
    else:
        system_prompt = (
            "You are OpenTutor AI in TUTOR MODE.\n"
            "- Explain step by step.\n"
            "- Stay on topic.\n"
            "- Remember conversation context.\n"
            "- Reply in user's language.\n"
        )
        messages.append({"role": "system", "content": system_prompt})

        for m in session["chat"][-MAX_MEMORY:]:
            messages.append(m)

    messages.append({"role": "user", "content": question})

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.4,
            max_tokens=600
        )

        answer = response.choices[0].message.content.strip()

        if mode != "exam":
            session["chat"].append({"role": "user", "content": question})
            session["chat"].append({"role": "assistant", "content": answer})
            session["chat"] = session["chat"][-MAX_MEMORY * 2:]

        return jsonify({"answer": answer})

    except Exception:
        return jsonify({
            "answer": "⚠️ Server busy hai. Thodi der baad try karein."
        })


@app.route("/clear", methods=["POST"])
def clear_chat():
    session.clear()
    return jsonify({"status": "cleared"})


if __name__ == "__main__":
    app.run(debug=True)
