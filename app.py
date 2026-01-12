from flask import Flask, render_template, request, redirect, session
import os
import openai
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = "exam-secret-key"

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/", methods=["GET", "POST"])
def index():
    if "user" not in session:
        return redirect("/login")

    answer = None

    if request.method == "POST":
        question = request.form.get("question")

        if question:
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an exam-focused Hindi + Hinglish AI tutor. Answer in clear headings, bullet points, emojis only in headings, exam-friendly language."
                        },
                        {"role": "user", "content": question}
                    ],
                    temperature=0.4,
                    max_tokens=500
                )

                answer = response.choices[0].message.content

            except Exception as e:
                answer = f"⚠️ Error: {str(e)}"

    return render_template("index.html", answer=answer)

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

if __name__ == "__main__":
    app.run(debug=True)
