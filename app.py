from flask import Flask, render_template, request, jsonify, redirect, session
import sqlite3, hashlib, os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)
app.secret_key = "opentutor-secret"

DB = "users.db"

def connect():
    return sqlite3.connect(DB)

@app.route("/ask", methods=["POST"])
def ask():
    if "user" not in session:
        return jsonify({"answer":"Login required"})

    q = request.json.get("question","")

    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role":"system","content":"You are OpenTutor AI, helpful, Hindi-English mix."},
                {"role":"user","content":q}
            ]
        )
        return jsonify({"answer":res.choices[0].message.content})

    except Exception as e:
        return jsonify({"answer":f"AI Error: {str(e)}"})
@app.route("/image", methods=["POST"])
def image_generate():
    if "user" not in session:
        return jsonify({"error": "Login required"})

    prompt = request.json.get("prompt", "")

    try:
        img = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1024"
        )
        return jsonify({"image_url": img.data[0].url})

    except Exception as e:
        return jsonify({"error": str(e)})

