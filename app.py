from flask import Flask, render_template, request, redirect, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = "opentutor-super-secret"

DB_PATH = "database.db"

# ---------- DATABASE ----------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        role TEXT,
        message TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------- ROUTES ----------
@app.route("/")
def index():
    if "user_id" in session:
        return redirect("/chat")
    return redirect("/login")

@app.route("/login", methods=["GET"])
def login_page():
    return render_template("login.html", error=None)

@app.route("/login", methods=["POST"])
def login_post():
    username = request.form.get("username")
    password = request.form.get("password")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, password FROM users WHERE username=?", (username,))
    user = cur.fetchone()
    conn.close()

    if user and check_password_hash(user[1], password):
        session["user_id"] = user[0]
        session["username"] = username
        return redirect("/chat")

    return render_template("login.html", error="❌ Invalid username or password")

@app.route("/signup", methods=["POST"])
def signup_post():
    username = request.form.get("new_username")
    password = request.form.get("new_password")

    if not username or not password:
        return render_template("login.html", error="❌ All fields required")

    hashed = generate_password_hash(password)

    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("INSERT INTO users (username,password) VALUES (?,?)", (username, hashed))
        conn.commit()
        conn.close()
        return render_template("login.html", error="✅ Signup successful, now login")
    except:
        return render_template("login.html", error="❌ Username already exists")

@app.route("/chat", methods=["GET", "POST"])
def chat():
    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    if request.method == "POST":
        msg = request.form.get("message")
        if msg:
            cur.execute("INSERT INTO chats VALUES (NULL,?,?,?)",
                        (session["user_id"], "user", msg))
            cur.execute("INSERT INTO chats VALUES (NULL,?,?,?)",
                        (session["user_id"], "ai", "🤖 Main OpenTutor AI hoon."))
            conn.commit()

    cur.execute("SELECT role, message FROM chats WHERE user_id=?",
                (session["user_id"],))
    chats = cur.fetchall()
    conn.close()

    return render_template("chat.html", chats=chats, username=session["username"])

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")
