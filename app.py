from flask import Flask, render_template, request, session, send_file
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import openai, os, io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

app = Flask(__name__)
app.secret_key = "ultimate-chatgpt-style-secret"

limiter = Limiter(get_remote_address, app=app, default_limits=["10 per minute"])
openai.api_key = os.getenv("OPENAI_API_KEY")

# ---------- SUBJECT DETECTION ----------
def detect_subject(q):
    q = q.lower()
    if any(w in q for w in ["equation","formula","math","x²","root"]): return "Maths 🧮"
    if any(w in q for w in ["science","physics","chemistry","photosynthesis"]): return "Science 🔬"
    if any(w in q for w in ["history","freedom","mughal","rajya"]): return "History 🏛️"
    if any(w in q for w in ["capital","currency","gk","president"]): return "GK 🌍"
    return "General 📘"

# ---------- PROMPT ----------
def build_prompt(q, prev):
    follow = f"\nPrevious question: {prev}\nUse context.\n" if prev else ""
    return f"""
You are a ChatGPT-like AI tutor.

Subject: {detect_subject(q)}

Rules:
- Hindi + Hinglish
- Exam + understanding
- Very clear, structured
- Emojis for clarity only

FORMAT:

🧠 Topic
📌 Short Answer
📖 Easy Explanation
🧮 Example / Formula
⚠️ Yaad Rakhne Layak
🎯 Exam Tip

{follow}
Question: {q}
"""

# ---------- MAIN ----------
@app.route("/", methods=["GET","POST"])
@limiter.limit("5 per minute")
def index():
    answer = ""
    if request.method == "POST":
        q = request.form["question"]
        prev = session.get("last_q")

        res = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role":"user","content":build_prompt(q,prev)}],
            temperature=0.3,
            max_tokens=650
        )

        answer = res.choices[0].message.content
        session["last_q"] = q
        session["last_answer"] = answer

    return render_template("index.html", answer=answer)

# ---------- PDF DOWNLOAD ----------
@app.route("/download")
def download():
    text = session.get("last_answer","")
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    y = 800
    for line in text.split("\n"):
        c.drawString(40, y, line[:100])
        y -= 15
        if y < 50:
            c.showPage()
            y = 800
    c.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="AI_Notes.pdf")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
