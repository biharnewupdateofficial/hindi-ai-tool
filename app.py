from flask import Flask, render_template, request, redirect, session
import sqlite3, os, hashlib

app = Flask(__name__)
app.secret_key = "opentutor-secret"

DB = "users.db"

def connect():
    return sqlite3.connect(DB)

def init_db():
    con = connect()
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS profile(
        user_id INTEGER,
        bio TEXT DEFAULT '',
        memory TEXT DEFAULT ''
    )
    """)
    con.commit()

init_db()

def hash_pw(p):
    return hashlib.sha256(p.encode()).hexdigest()

@app.route("/", methods=["GET"])
def home():
    if "user" not in session:
        return redirect("/login")
    return redirect("/chat")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        u = request.form.get("username")
        p = hash_pw(request.form.get("password"))

        con = connect(); cur = con.cursor()
        cur.execute("SELECT id FROM users WHERE username=? AND password=?", (u,p))
        row = cur.fetchone()

        if row:
            session["user"] = row[0]
            return redirect("/chat")
        else:
            return "❌ Invalid Login"

    return render_template("login.html")

@app.route("/signup", methods=["POST"])
def signup():
    u = request.form.get("new_username")
    p = hash_pw(request.form.get("new_password"))

    try:
        con = connect(); cur = con.cursor()
        cur.execute("INSERT INTO users(username,password) VALUES(?,?)",(u,p))
        uid = cur.lastrowid
        cur.execute("INSERT INTO profile(user_id) VALUES(?)",(uid,))
        con.commit()
        return redirect("/login")
    except:
        return "❌ Username already exists"

@app.route("/chat")
def chat():
    if "user" not in session:
        return redirect("/login")
    return render_template("chat.html")

@app.route("/profile", methods=["GET","POST"])
def profile():
    if "user" not in session:
        return redirect("/login")

    con=connect(); cur=con.cursor()

    if request.method=="POST":
        bio=request.form.get("bio")
        mem=request.form.get("memory")
        cur.execute("UPDATE profile SET bio=?, memory=? WHERE user_id=?",
                    (bio,mem,session["user"]))
        con.commit()

    cur.execute("SELECT bio,memory FROM profile WHERE user_id=?",(session["user"],))
    data=cur.fetchone()
    return render_template("profile.html",bio=data[0],memory=data[1])

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__=="__main__":
    app.run(debug=True)
