from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "opentutor_secret_key"

DB_FILE = "database.db"

# ---------- DATABASE ----------
def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()

    # users table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    # chats table
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
def home():
    if "user_id" in session:
        return redirect("/chat")
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    conn = get_db()
    cur = conn.cursor()

    if request.method == "POST":
        if "login" in request.form:
            u = request.form["username"]
            p = request.form["password"]
            cur.execute("SELECT * FROM users WHERE username=? AND password=?", (u, p))
            user = cur.fetchone()
            if user:
                session["user_id"] = user["id"]
                return redirect("/chat")

        if "signup" in request.form:
            u = request.form["new_username"]
            p = request.form["new_password"]
            try:
                cur.execute("INSERT INTO users (username,password) VALUES (?,?)", (u, p))
                conn.commit()
            except:
                pass

    conn.close()
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/chat")
def chat():
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT role,message FROM chats WHERE user_id=?", (session["user_id"],))
    chats = cur.fetchall()
    conn.close()
    return render_template("chat.html", chats=chats)

@app.route("/ask", methods=["POST"])
def ask():
    if "user_id" not in session:
        return jsonify({"answer": "Login required"})

    user_msg = request.json.get("question")

    # SIMPLE AI RESPONSE (stable base)
    ai_msg = f"आपने पूछा: {user_msg}\n\nमैं OpenTutor AI हूँ 🙂"

    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO chats (user_id,role,message) VALUES (?,?,?)",
                (session["user_id"], "user", user_msg))
    cur.execute("INSERT INTO chats (user_id,role,message) VALUES (?,?,?)",
                (session["user_id"], "ai", ai_msg))
    conn.commit()
    conn.close()

    return jsonify({"answer": ai_msg})

if __name__ == "__main__":
    app.run(debug=True)
