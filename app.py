from flask import Flask, render_template, request, jsonify, session, redirect
import sqlite3
from openai import OpenAI

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ---------- OpenAI ----------
client = OpenAI(api_key="YOUR_OPENAI_API_KEY")

# ---------- Database ----------
def connect():
    return sqlite3.connect("database.db", check_same_thread=False)

def init_db():
    con = connect()
    cur = con.cursor()

    # users table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    # chat history table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        question TEXT,
        answer TEXT
    )
    """)

    con.commit()
    con.close()

init_db()

# ---------- Routes ----------
@app.route("/")
def home():
    if "user" in session:
        return redirect("/chat")
    return redirect("/login")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        con = connect()
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE username=? AND password=?", (u,p))
        user = cur.fetchone()
        con.close()

        if user:
            session["user"] = u
            return redirect("/chat")

    return render_template("login.html")

@app.route("/signup", methods=["POST"])
def signup():
    u = request.form["username"]
    p = request.form["password"]

    con = connect()
    cur = con.cursor()
    try:
        cur.execute("INSERT INTO users(username,password) VALUES(?,?)",(u,p))
        con.commit()
    except:
        pass
    con.close()

    return redirect("/login")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/chat")
def chat():
    if "user" not in session:
        return redirect("/login")

    con = connect()
    cur = con.cursor()
    cur.execute("SELECT question,answer FROM history WHERE user=?", (session["user"],))
    chats = cur.fetchall()
    con.close()

    return render_template("index.html", chats=chats)

@app.route("/ask", methods=["POST"])
def ask():
    if "user" not in session:
        return jsonify({"error":"login required"})

    q = request.json["question"]

    res = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role":"user","content":q}]
    )

    ans = res.choices[0].message.content

    # SAVE HISTORY
    con = connect()
    cur = con.cursor()
    cur.execute(
        "INSERT INTO history(user,question,answer) VALUES(?,?,?)",
        (session["user"], q, ans)
    )
    con.commit()
    con.close()

    return jsonify({"answer": ans})

if __name__ == "__main__":
    app.run(debug=True)
