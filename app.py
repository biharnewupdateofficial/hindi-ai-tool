from flask import Flask, render_template, request, jsonify, session
import os, time
from openai import OpenAI

app = Flask(__name__)
app.secret_key = "opentutor-final-lock-key"

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MAX_MEMORY = 6
RATE_LIMIT = 10
RATE_WINDOW = 60
MAX_QUESTION_LENGTH = 800  # safety limit


def is_rate_limited():
    now = time.time()
    session.setdefault("requests", [])
    session["requests"] = [t for t in session["requests"] if now - t < RATE_WINDOW]
    if len(session["requests"]) >= RATE_LIMIT:
        return True
    session["requests"].append(now)
    return False


@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/chat")
def chat():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    # ---- Rate limit ----
    if is_rate_limited():
        return jsonify({
            "answer": "⏳ Thoda ruk jaiye. Aap bahut zyada request bhej rahe hain."
        })

    data = request.get_json(silent=True) or {}
    raw_question = data.get("question") or ""
    question = raw_question.strip()
    mode = data.get("mode", "tutor")

    # ---- Input safety ----
    if not question:
        return jsonify({"answer": "❌ Kripya koi sawal likhiye."})

    if len(question) > MAX_QUESTION_LENGTH:
        return jsonify({
            "answer": "⚠️ Sawal bahut lamba hai. Kripya thoda chhota karke poochiye."
        })

    session.setdefault("chat", [])
    messages = []

    # ---- Mode logic ----
    if mode == "exam":
        system_prompt = (
            "You are OpenTutor AI in STRICT EXAM MODE.\n"
            "- Short, direct, exam-ready answers only.\n"
            "- No extra explanation.\n"
            "- Stay strictly on the question.\n"
        )
        max_tokens = 180
        temperature = 0.15
        messages.append({"role": "system", "content": system_prompt})
    else:
        system_prompt = (
            "You are OpenTutor AI in ADVANCED TUTOR MODE.\n"
            "- Explain step by step.\n"
            "- Use simple language.\n"
            "- Give examples if useful.\n"
            "- Use context from previous questions.\n"
            "- Stay strictly on topic.\n"
        )
        max_tokens = 520
        temperature = 0.30
        messages.append({"role": "system", "content": system_prompt})

        # memory
        for m in session["chat"][-MAX_MEMORY:]:
            messages.append(m)

    messages.append({"role": "user", "content": question})

    # ---- OpenAI call ----
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=20
        )

        answer = response.choices[0].message.content.strip()
        if not answer:
            raise ValueError("Empty response")

        # save memory (tutor only)
        if mode != "exam":
            session["chat"].append({"role": "user", "content": question})
            session["chat"].append({"role": "assistant", "content": answer})
            session["chat"] = session["chat"][-MAX_MEMORY * 2:]

        return jsonify({"answer": answer})

    except Exception:
        return jsonify({
            "answer": (
                "⚠️ Abhi system thoda busy hai.\n"
                "Kripya 10–20 second baad dobara try karein."
            )
        })


@app.route("/clear", methods=["POST"])
def clear_chat():
    session.clear()
    return jsonify({"status": "cleared"})


if __name__ == "__main__":
    app.run(debug=True)
