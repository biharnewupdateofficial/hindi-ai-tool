from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3, os
from openai import OpenAI

app = Flask(__name__)
app.secret_key = "opentutor_secret"

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
DB = "database.db"

# ---------- DB ----------
def init_db():
    db = sqlite3.connect(DB)
    c = db.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS chats(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        role TEXT,
        message TEXT
    )""")
    db.commit()
    db.close()

init_db()

# ---------- ROUTES ----------
@app.route("/")
def home():
    return redirect("/login")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]
        db = sqlite3.connect(DB)
        c = db.cursor()
        c.execute("SELECT id FROM users WHERE username=? AND password=?", (u,p))
        r = c.fetchone()
        if r:
            session["uid"] = r[0]
            return redirect("/chat")
        try:
            c.execute("INSERT INTO users(username,password) VALUES (?,?)",(u,p))
            db.commit()
            session["uid"] = c.lastrowid
            return redirect("/chat")
        except:
            pass
    return render_template("login.html")

@app.route("/chat")
def chat():
    if "uid" not in session:
        return redirect("/login")
    db = sqlite3.connect(DB)
    c = db.cursor()
    c.execute("SELECT role,message FROM chats WHERE user_id=?", (session["uid"],))
    chats = c.fetchall()
    return render_template("chat.html", chats=chats)

@app.route("/ask", methods=["POST"])
def ask():
    q = request.json["question"]

    # IMAGE REQUEST
    if q.lower().startswith("image:"):
        img = client.images.generate(
            model="gpt-image-1",
            prompt=q.replace("image:",""),
            size="512x512"
        )
        ans = img.data[0].url
    else:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":q}]
        )
        ans = res.choices[0].message.content

    db = sqlite3.connect(DB)
    c = db.cursor()
    c.execute("INSERT INTO chats(user_id,role,message) VALUES (?,?,?)",(session["uid"],"user",q))
    c.execute("INSERT INTO chats(user_id,role,message) VALUES (?,?,?)",(session["uid"],"ai",ans))
    db.commit()

    return jsonify({"answer":ans})

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run()
