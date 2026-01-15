from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3, os, time, hashlib
from openai import OpenAI

app = Flask(__name__)
app.secret_key = "opentutor-login-final"

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ------------------ DB SETUP ------------------
def get_db():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    return conn

with get_db() as db:
    db.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        password TEXT
    )
    """)
    db.commit()

# ------------------ HELPERS ------------------
def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

def is_logged_in():
    return "user_id" in session

# ------------------ ROUTES ------------------

@app.route("/")
def home():
    if is_logged_in():
        return redirect("/chat")
    return render_template("welcome.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email","").strip()
        password = request.form.get("password","").strip()

        if not email or not password:
            return render_template("login.html", error="सभी फ़ील्ड भरना ज़रूरी है")

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, hash_password(password))
        ).fetchone()

        if user:
            session["user_id"] = user["id"]
            session["chat"] = []
            return redirect("/chat")

        return render_template("login.html", error="गलत Email या Password")

    return render_template("login.html")


@app.route("/signup", methods=["POST"])
def signup():
    email = request.form.get("email","").strip()
    password = request.form.get("password","").strip()

    if not email or not password:
        return render_template("login.html", error="सभी फ़ील्ड भरना ज़रूरी है")

    try:
        db = get_db()
        db.execute(
            "INSERT INTO users (email,password) VALUES (?,?)",
            (email, hash_password(password))
        )
        db.commit()
        return render_template("login.html", success="Account बन गया, अब Login करें")

    except:
        return render_template("login.html", error="Email पहले से मौजूद है")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/chat")
def chat():
    if not is_logged_in():
        return redirect("/login")
    return render_template("index.html")


# ------------------ AI CHAT ------------------

RATE_LIMIT = 10
RATE_WINDOW = 60

def is_rate_limited():
    now = time.time()
    session.setdefault("req", [])
    session["req"] = [t for t in session["req"] if now - t < RATE_WINDOW]
    if len(session["req"]) >= RATE_LIMIT:
        return True
    session["req"].append(now)
    return False


@app.route("/ask", methods=["POST"])
def ask():
    if not is_logged_in():
        return jsonify({"answer":"⚠️ कृपया Login करें"})

    if is_rate_limited():
        return jsonify({"answer":"⏳ थोड़ा रुकिए"})

    q = (request.json.get("question") or "").strip()
    if not q:
        return jsonify({"answer":"❌ सवाल लिखिए"})

    session.setdefault("chat", [])
    messages = [{
        "role":"system",
        "content":(
            "You are OpenTutor AI.\n"
            "Behave like ChatGPT + Gemini.\n"
            "Ask clarification if question is vague.\n"
            "Give options if needed.\n"
            "Explain clearly.\n"
        )
    }]

    for m in session["chat"][-8:]:
        messages.append(m)

    messages.append({"role":"user","content":q})

    try:
        r = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.35,
            max_tokens=500
        )
        ans = r.choices[0].message.content.strip()

        session["chat"].append({"role":"user","content":q})
        session["chat"].append({"role":"assistant","content":ans})

        return jsonify({"answer":ans})

    except:
        return jsonify({"answer":"⚠️ अभी समस्या है, बाद में प्रयास करें"})


if __name__ == "__main__":
    app.run(debug=True)
