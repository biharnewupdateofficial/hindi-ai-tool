from flask import Flask, render_template, request, jsonify
import os
from openai import OpenAI

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def detect_language(text):
    # very simple & effective
    hindi_chars = sum(1 for c in text if '\u0900' <= c <= '\u097F')
    return "hindi" if hindi_chars > 5 else "english"

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

    lang = detect_language(question)

    if mode == "exam":
        system_prompt = (
            "You are an EXAM MODE AI.\n"
            "- Short, direct answers\n"
            "- No extra explanation\n"
        )
    else:
        system_prompt = (
            "You are a TUTOR MODE AI.\n"
            "- Explain step by step\n"
            "- Friendly tone\n"
        )

    if lang == "hindi":
        system_prompt += "Reply in Hindi or Hinglish.\n"
    else:
        system_prompt += "Reply in simple English.\n"

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            temperature=0.3,
            max_tokens=500
        )

        answer = response.choices[0].message.content.strip()
        return jsonify({"answer": answer})

    except Exception as e:
        return jsonify({"answer": f"❌ AI Error: {str(e)}"})

if __name__ == "__main__":
    app.run(debug=True)
