from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key="secret"

def db():
    return sqlite3.connect("db.sqlite")

@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login")
    cur=db().cursor()
    cur.execute("SELECT role,text FROM chats WHERE user=?",(session["user"],))
    return render_template("chat.html",messages=[
        {"role":r,"text":t} for r,t in cur.fetchall()
    ])

@app.route("/ask",methods=["POST"])
def ask():
    q=request.json["question"]
    con=db();cur=con.cursor()
    cur.execute("INSERT INTO chats VALUES(?,?,?)",
        (session["user"],"user",q))
    # Fake AI response (safe)
    ans="🤖 AI jawab: "+q
    cur.execute("INSERT INTO chats VALUES(?,?,?)",
        (session["user"],"assistant",ans))
    con.commit()
    return {"ok":True}

@app.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":
        session["user"]=request.form["username"]
        return redirect("/")
    return render_template("login.html")

if __name__=="__main__":
    app.run()
