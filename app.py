from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3, os
from config import FEATURES

try:
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
except:
    client = None

app = Flask(__name__)
app.secret_key = "opentutor-secret"

DB = "database.db"

def db():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c

def init():
    c = db()
    cur = c.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS chats(id INTEGER PRIMARY KEY, user_id INTEGER, role TEXT, text TEXT)")
    c.commit()
    c.close()

init()

@app.route("/")
def home():
    return redirect("/chat") if "uid" in session else redirect("/login")

@app.route("/login", methods=["GET","POST"])
def login():
    c = db()
    cur = c.cursor()

    if request.method == "POST":
        if "login" in request.form:
            u,p = request.form["username"], request.form["password"]
            cur.execute("SELECT * FROM users WHERE username=? AND password=?", (u,p))
            r = cur.fetchone()
            if r:
                session["uid"] = r["id"]
                return redirect("/chat")

        if "signup" in request.form:
            try:
                cur.execute("INSERT INTO users(username,password) VALUES(?,?)",
                            (request.form["new_username"], request.form["new_password"]))
                c.commit()
            except:
                pass

    return render_template("login.html")

@app.route("/chat")
def chat():
    if "uid" not in session: return redirect("/login")
    cur = db().cursor()
    cur.execute("SELECT role,text FROM chats WHERE user_id=?", (session["uid"],))
    return render_template("chat.html", messages=cur.fetchall(), features=FEATURES)

@app.route("/ask", methods=["POST"])
def ask():
    if not FEATURES["CHAT"] or client is None:
        return jsonify({"answer":"AI unavailable"})

    q = request.json.get("question")
    cur = db().cursor()
    cur.execute("INSERT INTO chats(user_id,role,text) VALUES(?,?,?)", (session["uid"],"user",q))
    db().commit()

    try:
        r = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":q}]
        )
        ans = r.choices[0].message.content
    except Exception as e:
        ans = str(e)

    cur.execute("INSERT INTO chats(user_id,role,text) VALUES(?,?,?)", (session["uid"],"assistant",ans))
    db().commit()
    return jsonify({"answer":ans})

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run()
