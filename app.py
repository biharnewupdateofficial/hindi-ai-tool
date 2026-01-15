from flask import Flask, render_template, request, jsonify
import os
from openai import OpenAI

app = Flask(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question", "").strip()
    mode = data.get("mode", "tutor")

    if not question:
        return jsonify({"answer": "❌ Please enter a question."})

    if mode == "exam":
        system_prompt = (
            "You are an exam-focused AI tutor. "
            "Answer briefly, clearly, and to the point. "
            "Do not add extra explanation or conversation."
        )
    else:
        system_prompt = (
            "You are a friendly AI tutor. "
            "Explain step by step in simple Hindi + English mix. "
            "Use examples if helpful."
        )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            temperature=0.4,
            max_tokens=500
        )

        answer = response.choices[0].message.content.strip()
        return jsonify({"answer": answer})

    except Exception as e:
        return jsonify({"answer": f"❌ AI Error: {str(e)}"})

if __name__ == "__main__":
    app.run(debug=True)
