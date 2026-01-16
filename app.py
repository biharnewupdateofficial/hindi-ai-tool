from flask import Flask, render_template, request, jsonify, session
import os, requests
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader

app = Flask(__name__)
app.secret_key = "opentutor_secret"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------- HOME ----------------
@app.route("/")
def home():
    if "chat" not in session:
        session["chat"] = []
    return render_template("index.html", chat=session["chat"])


# ---------------- CHAT ----------------
@app.route("/ask", methods=["POST"])
def ask():
    question = request.json.get("question")

    history = session.get("chat", [])

    messages = [{"role": "system", "content": "You are a helpful Hindi AI tutor."}]
    for msg in history:
        messages.append({"role": msg["role"], "content": msg["text"]})
    messages.append({"role": "user", "content": question})

    payload = {
        "model": "gpt-4o-mini",
        "messages": messages
    }

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    r = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json=payload
    )

    answer = r.json()["choices"][0]["message"]["content"]

    history.append({"role": "user", "text": question})
    history.append({"role": "assistant", "text": answer})

    session["chat"] = history[-20:]  # last 20 messages only

    return jsonify({"answer": answer})


# ---------------- PDF UPLOAD ----------------
@app.route("/upload", methods=["POST"])
def upload_pdf():
    file = request.files["pdf"]
    filename = secure_filename(file.filename)
    path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(path)

    reader = PdfReader(path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "Summarize this PDF in simple Hindi."},
            {"role": "user", "content": text[:12000]}
        ]
    }

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    r = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json=payload
    )

    summary = r.json()["choices"][0]["message"]["content"]
    return jsonify({"summary": summary})


# ---------------- CLEAR CHAT ----------------
@app.route("/clear")
def clear():
    session.pop("chat", None)
    return jsonify({"status": "cleared"})


if __name__ == "__main__":
    app.run()
