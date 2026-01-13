import os
from flask import Flask, render_template, request, redirect, session, url_for
from openai import OpenAI

app = Flask(__name__)
app.secret_key = "supersecretkey"

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

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful AI tutor. Explain clearly with emojis."},
                    {"role": "user", "content": question}
                ]
            )
            answer = response.choices[0].message.content
        except Exception as e:
            answer = f"❌ Error: {str(e)}"

    return render_template("index.html", answer=answer)

if __name__ == "__main__":
    app.run(debug=True)
