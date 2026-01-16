from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3, os, requests

app = Flask(__name__)
app.secret_key = "opentutor_secret"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ---------- DATABASE ----------
def db():
    return sqlite3.connect("users.db")

with db() as con:
    con.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)
    con.execute("""
    CREATE TABLE IF NOT EXISTS chats (
        user_id INTEGER,
        role TEXT,
        text TEXT
    )
    """)

# ---------- LOGIN ----------
@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        cur = db().cursor()
        cur.execute("SELECT id FROM users WHERE username=? AND password=?", (u,p))
        user = cur.fetchone()

        if user:
            session["user"] = user[0]
            return redirect("/chat")
        else:
            return render_template("login.html", error="Invalid login")

    return render_template("login.html")

# ---------- SIGNUP ----------
@app.route("/signup", methods=["POST"])
def signup():
    u = request.form["username"]
    p = request.form["password"]

    try:
        with db() as con:
            con.execute("INSERT INTO users(username,password) VALUES(?,?)",(u,p))
        return redirect("/")
    except:
        return render_template("login.html", error="User exists")

# ---------- CHAT ----------
@app.route("/chat")
def chat():
    if "user" not in session:
        return redirect("/")

    cur = db().cursor()
    cur.execute("SELECT role,text FROM chats WHERE user_id=?", (session["user"],))
    history = cur.fetchall()

    return render_template("chat.html", chat=history)

# ---------- ASK ----------
@app.route("/ask", methods=["POST"])
def ask():
    q = request.json["question"]
    uid = session["user"]

    cur = db().cursor()
    cur.execute("SELECT role,text FROM chats WHERE user_id=?", (uid,))
    history = cur.fetchall()

    messages = [{"role":"system","content":"You are a helpful Hindi AI tutor."}]
    for r,t in history[-10:]:
        messages.append({"role":r,"content":t})
    messages.append({"role":"user","content":q})

    res = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization":f"Bearer {OPENAI_API_KEY}",
            "Content-Type":"application/json"
        },
        json={"model":"gpt-4o-mini","messages":messages}
    ).json()

    ans = res["choices"][0]["message"]["content"]

    with db() as con:
        con.execute("INSERT INTO chats VALUES(?,?,?)",(uid,"user",q))
        con.execute("INSERT INTO chats VALUES(?,?,?)",(uid,"assistant",ans))

    return jsonify({"answer":ans})

# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run()
