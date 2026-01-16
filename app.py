from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3, os, requests

app = Flask(__name__)
app.secret_key = "opentutor_secret"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def db():
    return sqlite3.connect("users.db")

@app.route("/")
def root():
    return redirect("/chat")

@app.route("/chat")
def chat():
    if "user" not in session:
        session["user"] = 1

    cur = db().cursor()
    cur.execute("SELECT role,text FROM chats WHERE user_id=1")
    chat = cur.fetchall()
    return render_template("chat.html", chat=chat)

@app.route("/ask", methods=["POST"])
def ask():
    q = request.json["question"]

    res = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization":f"Bearer {OPENAI_API_KEY}",
            "Content-Type":"application/json"
        },
        json={
            "model":"gpt-4o-mini",
            "messages":[{"role":"user","content":q}]
        }
    ).json()

    ans = res["choices"][0]["message"]["content"]

    with db() as con:
        con.execute("INSERT INTO chats VALUES(?,?,?)",(1,"user",q))
        con.execute("INSERT INTO chats VALUES(?,?,?)",(1,"assistant",ans))

    return jsonify({"answer":ans})

if __name__ == "__main__":
    app.run()
