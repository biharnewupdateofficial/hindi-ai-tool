from flask import Flask, render_template, request, session, redirect, url_for
import os
from openai import OpenAI

app = Flask(__name__)
app.secret_key = "opentutor-secret-key"

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are OpenTutor AI, a friendly, intelligent, multilingual AI tutor like ChatGPT.

Rules:
- Remember previous messages in the conversation
- Answer naturally and politely
- Reply in the same language as the user
- Explain step by step when teaching
- If user changes topic, smoothly continue conversation
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
