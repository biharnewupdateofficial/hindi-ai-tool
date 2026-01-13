from flask import Flask, render_template, request, redirect, session, url_for
from openai import OpenAI
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

# OpenAI client (NEW API)
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

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
    session.pop("user", None)
    return redirect("/login")

@app.route("/", methods=["GET", "POST"])
def index():
    if "user" not in session:
        return redirect("/login")

    answer = None
    error = None

    if request.method == "POST":
        question = request.form.get("question")

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are OpenTutor AI, an exam-focused tutor. "
                            "Explain answers clearly with headings, bullet points, "
                            "examples and emojis where helpful."
                        )
                    },
                    {"role": "user", "content": question}
                ]
            )
            answer = response.choices[0].message.content

        except Exception as e:
            error = str(e)

    return render_template("index.html", answer=answer, error=error)

if __name__ == "__main__":
    app.run(debug=True)
