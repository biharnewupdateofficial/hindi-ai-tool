from flask import Flask, render_template, request, redirect, session
import os
from openai import OpenAI

app = Flask(__name__)
app.secret_key = "super-secret-key"

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session["user"] = request.form.get("name")
        session["chat"] = []
        return redirect("/")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/", methods=["GET", "POST"])
def index():
    if "user" not in session:
        return redirect("/login")

    chat = session.get("chat", [])

    if request.method == "POST":
        question = request.form.get("question")

        chat.append({"role": "user", "content": question})

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful AI tutor. Answer in simple Hindi, exam focused."},
                *chat
            ]
        )

        answer = response.choices[0].message.content
        chat.append({"role": "assistant", "content": answer})

        session["chat"] = chat

    return render_template(
        "index.html",
        chat=chat,
        loading=False
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
