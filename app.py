from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3
import os

# ✅ OpenAI safe import
try:
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
except Exception as e:
    client = None
    print("OpenAI not loaded:", e)

app = Flask(__name__)
app.secret_key = "super-secret-key"

DB = "database.db"

# ---------- DATABASE ----------
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
        username TEXT UNIQUE,
        password TEXT
    )
    """)

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

    return render_template("login.html")

@app.route("/chat")
def chat():
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT role,text FROM chats WHERE user_id=?", (session["user_id"],))
    messages = cur.fetchall()
    return render_template("chat.html", messages=messages)

@app.route("/ask", methods=["POST"])
def ask():
    if client is None:
        return jsonify({"answer": "❌ AI service unavailable"})

    data = request.json
    q = data.get("question")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO chats (user_id,role,text) VALUES (?,?,?)",
                (session["user_id"], "user", q))
    conn.commit()

    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": q}]
        )
        ans = res.choices[0].message.content
    except Exception as e:
        ans = "Error: " + str(e)

    cur.execute("INSERT INTO chats (user_id,role,text) VALUES (?,?,?)",
                (session["user_id"], "assistant", ans))
    conn.commit()

    return jsonify({"answer": ans})

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)
