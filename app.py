from flask import Flask, render_template, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os

app = Flask(__name__)

# Rate limit (safe)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["10 per minute"]
)

def format_answer(topic, raw):
    return f"""
🧠 {topic}

📌 Short Answer (Exam ke liye)
{raw['short']}

📖 Easy Explanation (Samajhne ke liye)
{raw['explain']}

🧮 Example / Formula
{raw['example']}

⚠️ Yaad Rakhne Layak Baat
{raw['note']}

🎯 Exam Tip
{raw['tip']}
"""

@app.route("/", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def index():
    answer = ""
    if request.method == "POST":
        topic = request.form.get("question")

        # --- DEMO AI LOGIC (ChatGPT style) ---
        raw = {
            "short": "Quadratic equation ek polynomial equation hoti hai jisme degree 2 hoti hai.",
            "explain": (
                "Quadratic equation ka general form hota hai: ax² + bx + c = 0, "
                "jahan a ≠ 0. Iska use maths, physics aur daily problems me hota hai."
            ),
            "example": (
                "Example: 2x² + 3x − 5 = 0\n"
                "Discriminant D = b² − 4ac = 9 + 40 = 49\n"
                "Roots = (−b ± √49) / 2a"
            ),
            "note": "Discriminant se roots ki nature pata chalti hai.",
            "tip": "Board exam me formula likhna + steps dikhana bahut zaroori hai."
        }

        answer = format_answer(topic, raw)

    return render_template("index.html", answer=answer)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
