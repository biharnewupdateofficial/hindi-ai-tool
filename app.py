from flask import Flask, render_template, request, jsonify, session
import os
import time
from openai import OpenAI

app = Flask(__name__)
app.secret_key = "opentutor-final-safe-key"

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MAX_MEMORY = 6
RATE_LIMIT = 10
RATE_WINDOW = 60


def is_rate_limited():
    now = time.time()
    session.setdefault("requests", [])
    session["requests"] = [t for t in session["requests"] if now - t < RATE_WINDOW]
    if len(session["requests"]) >= RATE_LIMIT:
        return True
    session["requests"].append(now)
    return False


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    # Rate limit
    if is_rate_limited():
        return jsonify({
            "answer": "⏳ Aap bahut zyada request bhej rahe hain. 1 minute ruk kar try karein."
        })

    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()
    mode = data.get("mode", "tutor")

    if not question:
        return jsonify({"answer": "❌ Sawal khali hai. Kripya kuch likhiye."})

    session.setdefault("chat", [])
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
            "- Stay strictly on topic.\n"
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
            max_tokens=600,
            timeout=25
        )

        answer = response.choices[0].message.content.strip()

        if not answer:
            raise ValueError("Empty AI response")

        if mode != "exam":
            session["chat"].append({"role": "user", "content": question})
            session["chat"].append({"role": "assistant", "content": answer})
            session["chat"] = session["chat"][-MAX_MEMORY * 2:]

        return jsonify({"answer": answer})

    except Exception:
        # FINAL FALLBACK (never blank)
        fallback = (
            "⚠️ Abhi thodi technical dikkat aa rahi hai.\n"
            "Kripya 10–20 second baad dobara try karein.\n\n"
            "Aapka sawal safe hai 👍"
        )
        return jsonify({"answer": fallback})


@app.route("/clear", methods=["POST"])
def clear_chat():
    session.clear()
    return jsonify({"status": "cleared"})


if __name__ == "__main__":
    app.run(debug=True)
