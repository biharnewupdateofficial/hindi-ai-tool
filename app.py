from flask import Flask, render_template, request, session, redirect, jsonify, Response
import os
from openai import OpenAI

app = Flask(__name__)
app.secret_key = "opentutor-streaming-final"

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are OpenTutor AI.
You behave like ChatGPT + Google Gemini combined.

Rules:
- Be polite, friendly, human-like
- Prefer simple Hindi, mix English if helpful
- Explain step by step for study questions
- Short answers for casual chat
- Ask clarification if question is unclear
- Never mention you are an AI model
"""

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
        return Response("Please login first.", mimetype="text/plain")

    data = request.json
    question = (data.get("question") or "").strip()
    if not question:
        return Response("Kuch likhiye pehle 🙂", mimetype="text/plain")

    session.setdefault("chat", [])
    session["chat"].append({"role": "user", "content": question})

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(session["chat"])

    def stream():
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                stream=True
            )

            full_answer = ""

            for chunk in response:
                if chunk.choices[0].delta.content:
                    text = chunk.choices[0].delta.content
                    full_answer += text
                    yield text

            session["chat"].append(
                {"role": "assistant", "content": full_answer}
            )

        except Exception:
            yield "\n⚠️ Error aaya, dobara try karein."

    return Response(stream(), mimetype="text/plain")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)
