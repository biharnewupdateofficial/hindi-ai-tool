from flask import Flask, render_template, request
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def clean_format(text):
    """
    Answer ko proper notes format me todta hai
    """
    html = ""
    lines = text.split("\n")

    for line in lines:
        line = line.strip()

        if line.startswith("INTRODUCTION:"):
            html += "<h3>📘 Introduction</h3>"
        elif line.startswith("DEFINITION:"):
            html += "<h3>📗 Definition</h3>"
        elif line.startswith("POINTS:"):
            html += "<h3>📌 Important Points</h3><ul>"
        elif line.startswith("EXAMPLE:"):
            html += "</ul><h3>🧮 Examples</h3><ul>"
        elif line.startswith("SUMMARY:"):
            html += "</ul><h3>📝 Exam Summary</h3><ul>"
        elif line.startswith("-"):
            html += f"<li>{line[1:].strip()}</li>"
        elif line == "":
            continue
        else:
            html += f"<p>{line}</p>"

    html += "</ul>"
    return html

@app.route("/", methods=["GET", "POST"])
def index():
    answer = ""
    if request.method == "POST":
        question = request.form["question"]

        prompt = f"""
Tum ek experienced Indian school teacher ho.
Jawab sirf NOTES format me do.
Extra baat nahi, sirf padhne layak points.

STRICT FORMAT FOLLOW KARO (mandatory):

INTRODUCTION:
- sirf 2–3 short lines

DEFINITION:
- ekdum exam language me

POINTS:
- sirf yaad karne wale points
- numbering / bullets me

EXAMPLE:
- 1 ya 2 example max

SUMMARY:
- exam ke liye kya yaad rakhe

Question:
{question}
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        raw = response.choices[0].message.content
        answer = clean_format(raw)

    return render_template("index.html", answer=answer)

if __name__ == "__main__":
    app.run(debug=True)