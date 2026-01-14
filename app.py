from flask import Flask, render_template, request, redirect, session, url_for
import os
from openai import OpenAI

app = Flask(__name__)
app.secret_key = "opentutor-secret-key"

# OpenAI client (NEW API)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        if not username:
            return render_template("login.html", error="Naam likhna zaroori hai")
        session["user"] = username
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

    answer = None

    if request.method == "POST":
        question = request.form.get("question")

        if question:
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are OpenTutor AI. Explain clearly in Hindi."},
                        {"role": "user", "content": question}
                    ]
                )
                answer = response.choices[0].message.content
            except Exception as e:
                answer = f"Error: {str(e)}"

    return render_template("index.html", answer=answer)

if __name__ == "__main__":
    app.run(debug=True)
