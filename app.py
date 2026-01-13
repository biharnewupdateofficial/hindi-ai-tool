from flask import Flask, render_template, request, redirect, session, url_for
import os
from openai import OpenAI

app = Flask(__name__)
app.secret_key = "super-secret-key-change-this"

# OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form.get("name")
        if name:
            session["user"] = name
            return redirect(url_for("index"))
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ---------------- MAIN PAGE ----------------
@app.route("/", methods=["GET", "POST"])
def index():
    if "user" not in session:
        return redirect(url_for("login"))

    answer = None

    if request.method == "POST":
        question = request.form.get("question")

        if question:
            try:
                prompt = f"""
Tum ek exam-focused teacher ho.
Answer sirf simple Hindi text me do.
Koi markdown (###, ** ) use mat karo.
Koi LaTeX ya formula symbols (\\, $, etc) mat likho.
Formulas ko simple text me likho (jaise: ax2 + bx + c = 0).

Answer points me do, example ke saath.
Tone friendly aur board-exam oriented ho.

Question:
{question}
"""

                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a helpful Hindi teacher."},
                        {"role": "user", "content": prompt}
                    ]
                )

                answer = response.choices[0].message.content

            except Exception as e:
                answer = f"Error aaya hai: {str(e)}"

    return render_template("index.html", answer=answer)


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
