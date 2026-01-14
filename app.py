from flask import Flask, render_template, request, jsonify, session
import openai
import os

app = Flask(__name__)
app.secret_key = "opentutor-secret-key"

openai.api_key = os.getenv("OPENAI_API_KEY")

SYSTEM_PROMPT = """
You are OpenTutor AI.
You behave like ChatGPT.

Rules:
- Always answer politely
- Maintain conversation context
- If user changes topic, continue normally
- Explain clearly, step-by-step
- Use Hindi if user uses Hindi
- Use English if user uses English
- If mixed language, reply in Hinglish
"""

@app.route("/")
def index():
    if "messages" not in session:
        session["messages"] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    question = data.get("question")

    if not question:
        return jsonify({"answer": "❌ Question empty hai"})

    messages = session.get("messages", [])
    messages.append({"role": "user", "content": question})

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7
        )

        answer = response["choices"][0]["message"]["content"]
        messages.append({"role": "assistant", "content": answer})
        session["messages"] = messages

        return jsonify({"answer": answer})

    except Exception as e:
        return jsonify({"answer": f"❌ Error: {str(e)}"})

@app.route("/clear", methods=["POST"])
def clear():
    session.clear()
    return jsonify({"status": "cleared"})

if __name__ == "__main__":
    app.run()
