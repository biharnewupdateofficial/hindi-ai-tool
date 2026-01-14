from flask import Flask, render_template, request, jsonify, session
from openai import OpenAI
import os

# ---------------- CONFIG ----------------
app = Flask(__name__)
app.secret_key = "opentutor-secret-key"  # simple session key

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# ---------------- ROUTES ----------------

@app.route("/")
def index():
    if "history" not in session:
        session["history"] = []
    if "mode" not in session:
        session["mode"] = "tutor"
    return render_template("index.html")


@app.route("/set_mode", methods=["POST"])
def set_mode():
    data = request.json
    session["mode"] = data.get("mode", "tutor")
    session["history"] = []  # reset chat on mode change
    return jsonify({"status": "ok", "mode": session["mode"]})


@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"answer": "❌ Sawal khali nahi ho sakta"})

    history = session.get("history", [])
    mode = session.get("mode", "tutor")

    # -------- SYSTEM PROMPT --------
    if mode == "exam":
        system_prompt = (
            "You are OpenTutor AI in EXAM MODE. "
            "Give short, direct, exam-oriented answers. "
            "No extra explanation unless asked."
        )
    else:
        system_prompt = (
            "You are OpenTutor AI in TUTOR MODE. "
            "Explain step by step with examples "
            "in simple Hindi-English mix."
        )

    messages = [{"role": "system", "content": system_prompt}]

    # last 6 messages memory
    for m in history[-6:]:
        messages.append(m)

    messages.append({"role": "user", "content": question})

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=messages
        )

        answer = response.output_text.strip()

    except Exception as e:
        return jsonify({"answer": f"❌ AI Error: {str(e)}"})

    # save memory
    history.append({"role": "user", "content": question})
    history.append({"role": "assistant", "content": answer})
    session["history"] = history

    return jsonify({"answer": answer})


@app.route("/clear", methods=["POST"])
def clear():
    session.clear()
    return jsonify({"status": "cleared"})


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
