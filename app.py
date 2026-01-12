from flask import Flask, render_template, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import openai
import os

app = Flask(__name__)

# basic safety
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["10 per minute"]
)

openai.api_key = os.getenv("OPENAI_API_KEY")


def build_prompt(question):
    return f"""
You are a helpful AI tutor like ChatGPT.

Rules:
- Language: Simple Hindi + Hinglish
- Style: Clear, structured, student-friendly
- No mixing of points
- Use emojis only for clarity (not overuse)
- Focus on exam + understanding

STRICT FORMAT:

🧠 Topic

📌 Short Answer (Exam ke liye)
(3–5 crisp points)

📖 Easy Explanation (Samajhne ke liye)
(simple language, small paragraphs)

🧮 Example / Formula (if applicable)
(step-wise)

⚠️ Yaad Rakhne Layak
(1–2 very important lines)

🎯 Exam Tip
(what examiner expects)

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
                {"role": "user", "content": build_prompt(question)}
            ],
            temperature=0.3,
            max_tokens=500
        )

        answer = response.choices[0].message.content

    return render_template("index.html", answer=answer)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
