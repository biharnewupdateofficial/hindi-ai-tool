import os
from flask import Flask, render_template, request, redirect, session
from openai import OpenAI

app = Flask(__name__)
app.secret_key = "opentutor-secret-key"

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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

@app.route("/", methods=["GET", "POST"])
def index():
    if "user" not in session:
        return redirect("/login")

    answer = None
    if request.method == "POST":
        question = request.form.get("question")

        prompt = f"""
Tum ek exam-focused teacher ho.
Answer simple Hindi me do.
Board exam ke liye suitable ho.
Headings, points, examples use karo.
Maths formula simple text me likho.
Emojis topic ke hisaab se use karo.

Question:
{question}
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        answer = response.choices[0].message.content

    return render_template("index.html", answer=answer)

if __name__ == "__main__":
    app.run(debug=True)
