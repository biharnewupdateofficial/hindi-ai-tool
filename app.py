from flask import Flask, render_template, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import openai
import os

app = Flask(__name__)

# Rate limiting (basic protection)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["10 per minute"]
)

# OpenAI API Key (Render env variable)
openai.api_key = os.getenv("OPENAI_API_KEY")

def format_prompt(question):
    return f"""
You are an expert Indian school teacher (Class 6–12).

Rules:
- Language: Simple Hindi + Hinglish
- Style: Exam-oriented, clean, structured
- Use topic-based emojis automatically
- Clear separation: important vs extra

Emoji mapping:
Maths → 🧮 ➕ ➗ 📐
Science → 🔬 ⚡ 🌱 🧪
History → 🏛️ 📜 🗺️
Geography → 🌍 🧭 ⛰️
Civics → 🏛️ ⚖️
Economics → 💰 📊
Computer → 💻 🤖

STRICT FORMAT ONLY:

📌 Topic Overview
(short intro – 2 lines)

📘 Definition
(clear & exam-ready)

🧮 Important Formula / Key Points
(if applicable)

✍️ Step-by-Step Explanation
(numbered points only)

📝 Solved Example / Illustration
(simple, clean)

📌 Exam Tips ⭐
(2–3 must-remember points)

Question:
{question}
"""

@app.route("/", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def index():
    answer = ""
    if request.method == "POST":
        question = request.form.get("question")

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": format_prompt(question)}
            ]
        )

        answer = response.choices[0].message.content

    return render_template("index.html", answer=answer)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)