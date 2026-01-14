from flask import Flask, render_template, request, jsonify, session
import openai
import os

app = Flask(__name__)
app.secret_key = "opentutor-secret-key"

openai.api_key = os.getenv("OPENAI_API_KEY")

BASE_SYSTEM_PROMPT = """
You are OpenTutor AI, similar to ChatGPT.
Rules:
- Polite, helpful
- Maintain conversation context
- Language same as user (Hindi / English / Hinglish)
"""

TUTOR_PROMPT = BASE_SYSTEM_PROMPT + """
Mode: Tutor
- Explain step by step
- Give examples
- Teach like a teacher
"""

EXAM_PROMPT = BASE_SYSTEM_PROMPT + """
Mode: Exam
- Give short and direct answers
- No extra explanation
- No hints
- Board-exam style
"""

@app.route("/")
def index():
    if "mode" not in session:
        session["mode"] = "tutor"

    if "messages" not in session:
        system_prompt = TUTOR_PROMPT if session["mode"] == "tutor" else EXAM_PROMPT
        session["messages"] = [{"role": "system", "content": system_prompt}]

    return render_template("index.html", mode=session["mode"])

@app.route("/set-mode", methods=["POST"])
def set_mode():
    data = request.json
    mode = data.get("mode")

    if mode not in ["tutor", "exam"]:
        return jsonify({"status": "invalid mode"})

    session["mode"] = mode
    system_prompt = TUTOR_PROMPT if mode == "tutor" else EXAM_PROMPT
    session["messages"] = [{"role": "system", "content": system_prompt}]

    return jsonify({"status": "ok", "mode": mode})

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    question = data.get("question")

    if not question:
        return jsonify({"answer": "❌ Question empty hai"})

    messages = session.get("messages", [])
    messages.append({"role": "user", "content": question})

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.6
        )

        answer = response["choices"][0]["message"]["content"]
        messages.append({"role": "assistant", "content": answer})
        session["messages"] = messages

        return jsonify({"answer": answer})

    except Exception as e:
        return jsonify({"answer": f"❌ Error: {str(e)}"})

@app.route("/clear", methods=["POST"])
def clear():
    session.clear()
    return jsonify({"status": "cleared"})

if __name__ == "__main__":
    app.run()
