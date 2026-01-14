from flask import Flask, render_template, request, session, redirect, url_for
import os
from openai import OpenAI

app = Flask(__name__)
app.secret_key = "opentutor-secret-key"

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are OpenTutor AI, a smart multilingual tutor like ChatGPT.

Rules:
- Detect the language of the user's question automatically
- Reply in the SAME language (Hindi / English / Hinglish)
- Keep answers clear, structured, and friendly
- If teaching, explain step by step
- Do not change topic unless user changes it
"""


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session["user"] = request.form.get("username", "User")
        session["chat"] = []
        return redirect(url_for("index"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/", methods=["GET", "POST"])
def index():
    if "user" not in session:
        return redirect(url_for("login"))

    answer = ""
    if "chat" not in session:
        session["chat"] = []

    if request.method == "POST":
        user_question = request.form.get("question")

        session["chat"].append({"role": "user", "content": user_question})

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(session["chat"])

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7
        )

        answer = response.choices[0].message.content

        session["chat"].append({"role": "assistant", "content": answer})
        session.modified = True

    return render_template(
        "index.html",
        answer=answer,
        chat=session["chat"],
        username=session["user"]
    )

if __name__ == "__main__":
    app.run(debug=True)
from flask import jsonify

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"answer": "❌ Sawaal khali hai"})

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are OpenTutor AI. Explain clearly in Hindi."},
                {"role": "user", "content": question}
            ]
        )

        answer = response.choices[0].message.content
        return jsonify({"answer": answer})

    except Exception as e:
        return jsonify({"answer": f"Error: {str(e)}"})
