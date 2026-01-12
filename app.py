from flask import Flask, render_template, request, redirect, session
import openai
import os
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
app.secret_key = "exam-secret-key"

openai.api_key = os.getenv("OPENAI_API_KEY")

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["10 per minute"]
)

def exam_style_answer(question):
    prompt = f"""
Tum ek expert AI Tutor ho.
Student class 6–12 ke liye exam-ready notes chahta hai.

RULES:
- Simple Hindi + Hinglish
- Clear headings
- Bullet points
- Emojis sirf headings me
- Exam oriented
- Kya padhna hai aur kya important hai clear ho

FORMAT STRICTLY FOLLOW KARO:

📘 Introduction  
✍️ Definition  
🧮 Formula / Rule  
🪜 Step-by-Step Explanation  
📌 Exam Tips  
🔢 Example  
🔁 Quick Revision  

QUESTION:
{question}
"""

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return response.choices[0].message.content


@app.route("/", methods=["GET", "POST"])
def index():
    if "user" not in session:
        return redirect("/login")

    answer = None
    if request.method == "POST":
        question = request.form.get("question")
        answer = exam_style_answer(question)

    return render_template("index.html", answer=answer)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session["user"] = request.form.get("username")
        return redirect("/")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)
