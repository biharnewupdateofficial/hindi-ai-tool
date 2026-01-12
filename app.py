from flask import Flask, render_template, request
from openai import OpenAI
import os

app = Flask(__name__)

# 🔐 OpenAI Client (API key system se lega)
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

SYSTEM_PROMPT = """
Tum ek madadgar Hindi + Hinglish AI assistant ho.
Rules:
- Simple Hindi ya Hinglish me jawab do
- Step-by-step samjhao
- Aise likho jaise bhai/dost samjha raha ho
- Jawab clear, practical aur short ho
"""

@app.route("/", methods=["GET", "POST"])
def index():
    answer = ""
    question = ""

    if request.method == "POST":
        question = request.form.get("question")

        if question:
            response = client.responses.create(
                model="gpt-5-nano",
                input=[
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT
                    },
                    {
                        "role": "user",
                        "content": question
                    }
                ]
            )

            answer = response.output_text

    return render_template("index.html", answer=answer, question=question)

if __name__ == "__main__":
    app.run(debug=True)