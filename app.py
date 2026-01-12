from flask import Flask, render_template, request
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def format_answer(text):
    """
    AI ke jawab ko clean, readable format me convert karta hai
    """
    lines = text.split("\n")
    formatted = []

    for line in lines:
        line = line.strip()

        if line.startswith("###"):
            formatted.append(f"<h3>{line.replace('###','').strip()}</h3>")
        elif line.startswith("##"):
            formatted.append(f"<h2>{line.replace('##','').strip()}</h2>")
        elif line.startswith("#"):
            formatted.append(f"<h1>{line.replace('#','').strip()}</h1>")
        elif line.startswith("-"):
            formatted.append(f"<li>{line[1:].strip()}</li>")
        elif line == "":
            formatted.append("<br>")
        else:
            formatted.append(f"<p>{line}</p>")

    return "".join(formatted)

@app.route("/", methods=["GET", "POST"])
def index():
    answer = ""
    if request.method == "POST":
        question = request.form["question"]

        prompt = f"""
Tum ek Indian school teacher ho.
Jawab Hindi + Hinglish me do.
Simple language, exam-oriented, clean structure ke sath samjhao.

Question:
{question}

Format:
- Short introduction
- Clear definition
- Step-by-step explanation
- Example
- Quick summary
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )

        raw_answer = response.choices[0].message.content
        answer = format_answer(raw_answer)

    return render_template("index.html", answer=answer)

if __name__ == "__main__":
    app.run(debug=True)
