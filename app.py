from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, os
from openai import OpenAI

app = Flask(__name__)
app.secret_key = "opentutor-secret-key"

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---------- DATABASE ----------
def get_db():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    return conn

with get_db() as db:
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            password TEXT
        )
    """)

# ---------- AUTH ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        try:
            with get_db() as db:
                db.execute(
                    "INSERT INTO users (email, password) VALUES (?,?)",
                    (email, password)
                )
            return redirect("/login")
        except:
            return "User already exists"

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = get_db().execute(
            "SELECT * FROM users WHERE email=?",
            (email,)
        ).fetchone()

        if user and check_password_hash(user["password"], password):
            session["user"] = email
            session["chat"] = []
            session["lang"] = "hi"
            return redirect("/")
        else:
            return "Invalid login"

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ---------- MAIN APP ----------
@app.route("/set-language", methods=["POST"])
def set_language():
    session["lang"] = request.form.get("lang", "hi")
    return redirect("/")

@app.route("/", methods=["GET", "POST"])
def index():
    if "user" not in session:
        return redirect("/login")

    chat = session.get("chat", [])
    lang = session.get("lang", "hi")

    if request.method == "POST":
        question = request.form["question"]
        chat.append({"role": "user", "content": question})

        system_prompt = (
            "You are OpenTutor AI. Answer in simple Hindi for exams."
            if lang == "hi"
            else "You are OpenTutor AI. Answer in clear English for exams."
        )

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                *chat
            ]
        )

        answer = response.choices[0].message.content
        chat.append({"role": "assistant", "content": answer})

        session["chat"] = chat

    return render_template("index.html", chat=chat, lang=lang)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
