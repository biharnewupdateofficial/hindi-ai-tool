from flask import Flask, render_template, request, session, redirect, Response
import sqlite3, os
from openai import OpenAI

app = Flask(__name__)
app.secret_key = "opentutor-history-final"

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are OpenTutor AI.
Behave like ChatGPT + Google Gemini.
Use simple Hindi mixed with English.
Explain step by step when teaching.
"""

# ---------- DATABASE ----------
def get_db():
    conn = sqlite3.connect("chat.db")
    conn.row_factory = sqlite3.Row
    return conn

with get_db() as db:
    db.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            role TEXT,
            content TEXT
        )
    """)
    db.commit()

# ---------- ROUTES ----------
@app.route("/")
def home():
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        if username:
            session["user"] = username
            return redirect("/chat")
    return render_template("login.html")

@app.route("/chat")
def chat():
    if "user" not in session:
        return redirect("/login")

    db = get_db()
    messages = db.execute(
        "SELECT role, content FROM chats WHERE username=?",
        (session["user"],)
    ).fetchall()

    return render_template(
        "chat.html",
        username=session["user"],
        history=messages
    )

@app.route("/new-chat")
def new_chat():
    if "user" in session:
        db = get_db()
        db.execute(
            "DELETE FROM chats WHERE username=?",
            (session["user"],)
        )
        db.commit()
    return redirect("/chat")

@app.route("/ask", methods=["POST"])
def ask():
    if "user" not in session:
        return Response("Login required", mimetype="text/plain")

    question = (request.json.get("question") or "").strip()
    if not question:
        return Response("", mimetype="text/plain")

    db = get_db()
    db.execute(
        "INSERT INTO chats (username, role, content) VALUES (?,?,?)",
        (session["user"], "user", question)
    )
    db.commit()

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    rows = db.execute(
        "SELECT role, content FROM chats WHERE username=?",
        (session["user"],)
    ).fetchall()

    for r in rows:
        messages.append({"role": r["role"], "content": r["content"]})

    def stream():
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                stream=True
            )

            full = ""
            for chunk in response:
                if chunk.choices[0].delta.content:
                    text = chunk.choices[0].delta.content
                    full += text
                    yield text

            db.execute(
                "INSERT INTO chats (username, role, content) VALUES (?,?,?)",
                (session["user"], "assistant", full)
            )
            db.commit()

        except:
            yield "\n⚠️ Error aaya"

    return Response(stream(), mimetype="text/plain")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)
