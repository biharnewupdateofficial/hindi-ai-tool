import os
from flask import Flask, render_template, request, redirect, session, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from openai import OpenAI

# ---------------- CONFIG ----------------
app = Flask(__name__)
app.secret_key = "super-secret-key-change-later"

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["20 per minute"]
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form.get("name")
        if name:
            session["user"] = name
            return redirect("/")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ---------------- MAIN CHAT ----------------
@app.route("/", methods=["GET", "POST"])
@limiter.limit("10 per minute")
def index():
    if "user" not in session:
        return redirect("/login")

    answer = None
    if request.method == "POST":
        question = request.form.get("question")

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are OpenTutor AI. Explain clearly in simple language with emojis and exam-focused points."
                    },
                    {
                        "role": "user",
                        "content": question
                    }
                ]
            )
            answer = response.choices[0].message.content

        except Exception as e:
            answer = f"⚠️ Error: {str(e)}"

    return render_template("index.html", answer=answer)

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
