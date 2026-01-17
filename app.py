from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3

app = Flask(__name__)
app.secret_key = "opentutor_secret"

DB = "database.db"

# ======================
# DATABASE AUTO CREATE
# ======================
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    c.execute("""
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

# ======================
# ROUTES
# ======================

@app.route("/")
def home():
    if "user_id" in session:
        return redirect("/chat")
    return redirect("/login")

@app.route("/login", methods=["GET","POST"])
def login():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    if request.method == "POST":
        action = request.form.get("action")
        username = request.form.get("username")
        password = request.form.get("password")

        if action == "login":
            c.execute("SELECT id FROM users WHERE username=? AND password=?", (username,password))
            user = c.fetchone()
            if user:
                session["user_id"] = user[0]
                conn.close()
                return redirect("/chat")

        if action == "signup":
            try:
                c.execute("INSERT INTO users (username,password) VALUES (?,?)",(username,password))
                conn.commit()
            except:
                pass

    conn.close()
    return render_template("login.html")

@app.route("/chat")
def chat():
    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT role,message FROM chats WHERE user_id=?", (session["user_id"],))
    chats = c.fetchall()
    conn.close()

    return render_template("chat.html", chats=chats)

@app.route("/ask", methods=["POST"])
def ask():
    if "user_id" not in session:
        return jsonify({"answer":"Login first"})

    q = request.json.get("question")

    a = f"आपने पूछा: {q}\n\n(OpenTutor AI demo response)"

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("INSERT INTO chats (user_id,role,message) VALUES (?,?,?)",(session["user_id"],"user",q))
    c.execute("INSERT INTO chats (user_id,role,message) VALUES (?,?,?)",(session["user_id"],"ai",a))

    conn.commit()
    conn.close()

    return jsonify({"answer":a})

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run()
