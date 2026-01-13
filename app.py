import os
from flask import Flask, render_template, request, redirect, session, url_for
from openai import OpenAI

app = Flask(__name__)
app.secret_key = "opentutor-secret-key"

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        if username:
            session["user"] = username
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

    answer = None
    question = None

    if request.method == "POST":
        question = request.form.get("question")

        prompt = f"""
Tum ek AI Tutor ho.
Student ka sawal dhyaan se samjho aur
clear headings, points, examples aur emojis ke saath jawab do.

Sawal:
{question}
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        answer = response.choices[0].message.content

    return render_template("index.html", answer=answer, question=question)

if __name__ == "__main__":
    app.run(debug=True)
