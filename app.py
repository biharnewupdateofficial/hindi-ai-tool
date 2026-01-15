from flask import Flask, render_template, request, redirect, session, jsonify
import os
from openai import OpenAI

app = Flask(__name__)
app.secret_key = "opentutor-secret-key"

# OpenAI client (NEW API)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are OpenTutor AI.
You behave like ChatGPT + Google Gemini combined.

Rules:
- Be polite, friendly, human-like
- Prefer simple Hindi, mix English if helpful
- Explain step by step for study questions
- Short answers for casual chat
- If greeting, greet back nicely
- Never mention you are an AI model
"""

# ---------- ROUTES ----------

@app.route("/")
def home():
    return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        if username:
            session["user"] = username
            session["chat"] = []
            return redirect("/chat")
    return render_template("login.html")


@app.route("/chat")
def chat():
    if "user" not in session:
        return redirect("/login")
    return render_template("chat.html", username=session["user"])


@app.route("/ask", methods=["POST"])
def ask():
    if "user" not in session:
        return jsonify({"answer": "Please login first."})

    data = request.json
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"answer": "Kuch likhiye pehle 🙂"})

    if "chat" not in session:
        session["chat"] = []

    session["chat"].append({"role": "user", "content": question})

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(session["chat"])

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        answer = response.choices[0].message.content
    except Exception as e:
        return jsonify({"answer": f"Error: {str(e)}"})

    session["chat"].append({"role": "assistant", "content": answer})

    return jsonify({"answer": answer})


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)
