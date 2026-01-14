import os
from flask import Flask, render_template, request, redirect, session
from openai import OpenAI

# =========================
# BASIC APP SETUP
# =========================
app = Flask(__name__)
app.secret_key = "opentutor-secret-key"

# =========================
# OPENAI CLIENT (NEW SDK)
# =========================
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# =========================
# LOGIN PAGE
# =========================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form.get("name")
        if not name:
            return "Name required", 400
        session["user"] = name
        return redirect("/")
    return render_template("login.html")


# =========================
# LOGOUT
# =========================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# =========================
# HOME / CHAT PAGE
# =========================
@app.route("/", methods=["GET", "POST"])
def index():
    if "user" not in session:
        return redirect("/login")

    answer = ""

    if request.method == "POST":
        question = request.form.get("question")

        if not question:
            return "Bad Request: question missing", 400

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are OpenTutor AI. Explain clearly in simple Hindi."
                    },
                    {
                        "role": "user",
                        "content": question
                    }
                ]
            )
            answer = response.choices[0].message.content

        except Exception as e:
            answer = f"Error: {str(e)}"

    return render_template("index.html", answer=answer)


# =========================
# RUN APP
# =========================
if __name__ == "__main__":
    app.run(debug=True)
