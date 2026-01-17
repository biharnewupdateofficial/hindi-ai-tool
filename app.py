from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3

app = Flask(__name__)
app.secret_key = "super-secret-key"

DB = "database.db"

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
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

@app.route("/")
def index():
    if "user_id" in session:
        return redirect("/chat")
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    conn = get_db()
    cur = conn.cursor()

    if request.method == "POST":
        action = request.form.get("action")

        if action == "login":
            username = request.form["username"]
            password = request.form["password"]

            cur.execute(
                "SELECT * FROM users WHERE username=? AND password=?",
                (username, password)
            )
            user = cur.fetchone()

            if user:
                session["user_id"] = user["id"]
                session["username"] = user["username"]
                return redirect("/chat")

        if action == "signup":
            username = request.form["username"]
            password = request.form["password"]

            try:
                cur.execute(
                    "INSERT INTO users (username,password) VALUES (?,?)",
                    (username, password)
                )
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
    cur.execute(
        "SELECT role,message FROM chats WHERE user_id=?",
        (session["user_id"],)
    )
    chats = cur.fetchall()
    conn.close()

    return render_template("chat.html", chats=chats)

@app.route("/ask", methods=["POST"])
def ask():
    if "user_id" not in session:
        return jsonify({"answer": "Login required"})

    q = request.json["question"]
    a = f"आपने पूछा: {q}\n\nमैं OpenTutor AI हूँ 🙂"

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO chats (user_id,role,message) VALUES (?,?,?)",
        (session["user_id"], "user", q)
    )
    cur.execute(
        "INSERT INTO chats (user_id,role,message) VALUES (?,?,?)",
        (session["user_id"], "ai", a)
    )

    conn.commit()
    conn.close()

    return jsonify({"answer": a})

if __name__ == "__main__":
    app.run()
