from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import os
from openai import OpenAI

app = Flask(__name__)
app.secret_key = "super-secret-key"

# OpenAI client (NEW SDK)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---------- DATABASE ----------
def get_db():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ---------- ROUTES ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        if not username:
            return render_template("login.html", error="Naam zaroori hai")

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()

        if not user:
            conn.execute(
                "INSERT INTO users (username) VALUES (?)", (username,)
            )
            conn.commit()

        conn.close()
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

    if request.method == "POST":
        question = request.form["question"]

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "Tum ek helpful AI tutor ho. Simple Hindi + emojis use karo."
                    },
                    {
                        "role": "user",
                        "content": question
                    }
                ]
            )

            answer = response.choices[0].message.content

        except Exception as e:
            answer = f"❌ Error: {str(e)}"

    return render_template("index.html", answer=answer)


if __name__ == "__main__":
    app.run(debug=True)
