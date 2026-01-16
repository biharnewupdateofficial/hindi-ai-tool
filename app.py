from flask import Flask, render_template, request, jsonify
import os
import requests
import pyttsx3

app = Flask(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ---------- HOME ----------
@app.route("/")
def home():
    return render_template("index.html")

# ---------- CHAT ----------
@app.route("/ask", methods=["POST"])
def ask():
    q = request.json.get("question")

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are a helpful Hindi AI tutor."},
            {"role": "user", "content": q}
        ]
    }

    r = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json=payload
    )

    answer = r.json()["choices"][0]["message"]["content"]
    return jsonify({"answer": answer})


# ---------- TEXT TO IMAGE ----------
@app.route("/image", methods=["POST"])
def image():
    prompt = request.json.get("prompt")

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-image-1",
        "prompt": prompt,
        "size": "1024x1024"
    }

    r = requests.post(
        "https://api.openai.com/v1/images/generations",
        headers=headers,
        json=payload
    )

    img_url = r.json()["data"][0]["url"]
    return jsonify({"image": img_url})


# ---------- TEXT TO SPEECH ----------
@app.route("/speak", methods=["POST"])
def speak():
    text = request.json.get("text")

    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

    return jsonify({"status": "spoken"})


if __name__ == "__main__":
    app.run()
