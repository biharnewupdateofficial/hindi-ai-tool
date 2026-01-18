from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "opentutor-secret-key"

# ---------- DATABASE ----------
def get_db():
    return sqlite3.connect("database.db")

def init_db():
    db = get_db()
    cur = db.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
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

    db.commit()
    db.close()

init_db()

# ---------- ROUTES ----------
@app.route("/")
def home():
    if "user_id" in session:
        return redirect("/chat")
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    db = get_db()
    cur = db.cursor()

    if request.method == "POST":
        if "login" in request.form:
            username = request.form["username"]
            password = request.form["password"]

            cur.execute("SELECT id, password FROM users WHERE username=?", (username,))
            user = cur.fetchone()

            if user and check_password_hash(user[1], password):
                session["user_id"] = user[0]
                session["username"] = username
                return redirect("/chat")

        if "signup" in request.form:
            username = request.form["new_username"]
            password = generate_password_hash(request.form["new_password"])

            try:
                cur.execute("INSERT INTO users (username, password) VALUES (?,?)", (username, password))
                db.commit()
            except:
                pass

    return render_template("login.html")

@app.route("/chat", methods=["GET", "POST"])
def chat():
    if "user_id" not in session:
        return redirect("/login")

    db = get_db()
    cur = db.cursor()

    if request.method == "POST":
        msg = request.form["message"]

        cur.execute("INSERT INTO chats (user_id, role, message) VALUES (?,?,?)",
                    (session["user_id"], "user", msg))

        # TEMP AI RESPONSE (stable)
        ai_reply = "🤖 Main OpenTutor AI hoon. Aapka sawal mila!"
        cur.execute("INSERT INTO chats (user_id, role, message) VALUES (?,?,?)",
                    (session["user_id"], "ai", ai_reply))

        db.commit()

    cur.execute("SELECT role, message FROM chats WHERE user_id=?",
                (session["user_id"],))
    chats = cur.fetchall()

    return render_template("chat.html", chats=chats, username=session["username"])

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)
