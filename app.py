from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
import openai

app = Flask(__name__)
app.secret_key = "super-secret-key"

# ===== OpenAI CONFIG =====
openai.api_key = os.getenv("OPENAI_API_KEY")

# ===== ROUTES =====

@app.route("/")
def home():
    if not session.get("user"):
        return redirect("/login")
    return render_template("chat.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        if username:
            session["user"] = username
            return redirect("/")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/ask", methods=["POST"])
def ask():
    if not session.get("user"):
        return jsonify({"answer": "❌ Please login first"})

    data = request.get_json()
    question = data.get("question", "")

    if not question:
        return jsonify({"answer": "❌ Empty question"})

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful Hindi + English tutor like ChatGPT and Gemini."},
                {"role": "user", "content": question}
            ],
            temperature=0.7
        )

        answer = response["choices"][0]["message"]["content"]
        return jsonify({"answer": answer})

    except Exception as e:
        return jsonify({"answer": f"❌ AI Error: {str(e)}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
