from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os, time
from openai import OpenAI

app = Flask(__name__)
app.secret_key = "opentutor-launch-key"

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


# ---------- LANDING PAGE ----------
@app.route("/")
def landing():
    return render_template("landing.html")


# ---------- CHAT PAGE ----------
@app.route("/chat")
def chat():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    if is_rate_limited():
        return jsonify({
            "answer": "⏳ Thoda ruk jaiye. Aap bahut zyada request bhej rahe hain."
        })

    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()
    mode = data.get("mode", "tutor")

    if not question:
        return jsonify({"answer": "❌ Kripya koi sawal likhiye."})

    session.setdefault("chat", [])
    messages = []

    if mode == "exam":
        system_prompt = (
            "You are in EXAM MODE.\n"
            "- Short, direct, exam-ready answers.\n"
            "- No extra explanation.\n"
        )
        max_tokens = 180
        temperature = 0.2
        messages.append({"role": "system", "content": system_prompt})
    else:
        system_prompt = (
            "You are OpenTutor AI in TUTOR MODE.\n"
            "- Explain step by step.\n"
            "- Stay on topic.\n"
            "- Use simple language.\n"
            "- Remember context.\n"
        )
        max_tokens = 500
        temperature = 0.35
        messages.append({"role": "system", "content": system_prompt})

        for m in session["chat"][-MAX_MEMORY:]:
            messages.append(m)

    messages.append({"role": "user", "content": question})

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
            raise ValueError("Empty")

        if mode != "exam":
            session["chat"].append({"role": "user", "content": question})
            session["chat"].append({"role": "assistant", "content": answer})
            session["chat"] = session["chat"][-MAX_MEMORY * 2:]

        return jsonify({"answer": answer})

    except Exception:
        return jsonify({
            "answer": "⚠️ Abhi system busy hai. Thodi der baad try karein."
        })


@app.route("/clear", methods=["POST"])
def clear_chat():
    session.clear()
    return jsonify({"status": "cleared"})


if __name__ == "__main__":
    app.run(debug=True)
