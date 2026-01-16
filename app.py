from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "opentutor-secret-key"

DB_FILE = "database.db"

# -----------------------------
# DATABASE INIT (AUTO FIX)
# -----------------------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    # Users table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    # Chats table (🔥 THIS FIXES YOUR ERROR)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        role TEXT,
        text TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# -----------------------------
# ROUTES
# -----------------------------

@app.route("/")
def home():
    if "user_id" in session:
        return redirect("/chat")
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE username=? AND password=?", (username, password))
    user = cur.fetchone()
    conn.close()

    if user:
        session["user_id"] = user[0]
        return redirect("/chat")

    return "❌ Invalid login"

@app.route("/signup", methods=["POST"])
def signup():
    username = request.form["username"]
    password = request.form["password"]

    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("INSERT INTO users (username, password) VALUES (?,?)", (username, password))
        conn.commit()
        conn.close()
        return redirect("/")
    except:
        return "❌ Username already exists"

@app.route("/chat")
def chat():
    if "user_id" not in session:
        return redirect("/")

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT role, text FROM chats WHERE user_id=?", (session["user_id"],))
    chats = cur.fetchall()
    conn.close()

    return render_template("chat.html", chats=chats)

@app.route("/ask", methods=["POST"])
def ask():
    if "user_id" not in session:
        return jsonify({"answer": "Login required"})

    question = request.json.get("question", "")

    # SAVE USER MESSAGE
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("INSERT INTO chats (user_id, role, text) VALUES (?,?,?)",
                (session["user_id"], "user", question))

    # 🔥 TEMP AI LOGIC (LLM later replace)
    answer = f"आपने पूछा: {question}\n\n(अभी AI demo mode में है)"

    cur.execute("INSERT INTO chats (user_id, role, text) VALUES (?,?,?)",
                (session["user_id"], "ai", answer))

    conn.commit()
    conn.close()

    return jsonify({"answer": answer})

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")
