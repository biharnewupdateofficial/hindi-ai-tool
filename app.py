from flask import Flask, render_template, request, jsonify, session
import os
from openai import OpenAI

app = Flask(__name__)
app.secret_key = "opentutor-secret-key"

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Default mode
@app.before_request
def set_default_mode():
    if "mode" not in session:
        session["mode"] = "tutor"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/set_mode", methods=["POST"])
def set_mode():
    data = request.json
    session["mode"] = data.get("mode", "tutor")
    return jsonify({"status": "ok"})


@app.route("/clear", methods=["POST"])
def clear():
    session.clear()
    return jsonify({"status": "cleared"})


def build_system_prompt(mode):
    if mode == "exam":
        return (
            "You are OpenTutor AI in EXAM MODE.\n"
            "- Answer strictly based on the question.\n"
            "- No extra information.\n"
            "- Short, accurate, exam-ready answers.\n"
            "- If question is unclear, ask to clarify."
        )
    else:
        return (
            "You are OpenTutor AI in TUTOR MODE.\n"
            "- Explain clearly step by step.\n"
            "- Match the user's language (Hindi/English/Hinglish).\n"
            "- Stay strictly on the asked topic.\n"
            "- Do NOT change the topic on your own."
        )


@app.route("/ask", methods=["POST"])
def ask():
    try:
        user_question = request.json.get("question", "").strip()
        if not user_question:
            return jsonify({"answer": "❌ Question empty hai."})

        mode = session.get("mode", "tutor")

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": build_system_prompt(mode)},
                {"role": "user", "content": user_question}
            ],
            temperature=0.4
        )

        answer = response.choices[0].message.content
        return jsonify({"answer": answer})

    except Exception as e:
        return jsonify({"answer": f"❌ AI Error: {str(e)}"})


if __name__ == "__main__":
    app.run(debug=True)
