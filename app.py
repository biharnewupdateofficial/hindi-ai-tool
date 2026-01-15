from flask import Flask, render_template, request, jsonify
import os
from openai import OpenAI

app = Flask(__name__)

# OpenAI client (NEW API)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question", "").strip()
    mode = data.get("mode", "tutor")  # default tutor

    if not question:
        return jsonify({"answer": "❌ Please enter a question."})

    if mode == "exam":
        system_prompt = (
            "You are an exam assistant. "
            "Give short, direct, exam-ready answers. "
            "No extra explanation."
        )
    else:
        system_prompt = (
            "You are a tutor. "
            "Explain step-by-step in simple Hindi-English mix. "
            "Use examples and clarity."
        )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ]
        )

        answer = response.choices[0].message.content.strip()
        return jsonify({"answer": answer})

    except Exception as e:
        return jsonify({"answer": f"❌ AI Error: {str(e)}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
