import os
from flask import Flask, render_template, request
from openai import OpenAI

app = Flask(__name__)

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Chat memory (session-like, simple)
messages = [
    {
        "role": "system",
        "content": (
            "You are OpenTutor AI, a helpful, polite, intelligent tutor like ChatGPT. "
            "You ONLY answer based on the user's question. "
            "Never change the topic on your own. "
            "Explain clearly, step by step, in simple language. "
            "If the user asks in Hindi, reply in Hindi. "
            "If the user asks in English, reply in English."
        )
    }
]

@app.route("/", methods=["GET", "POST"])
def index():
    global messages

    if request.method == "POST":
        user_input = request.form.get("question")

        if user_input:
            messages.append({
                "role": "user",
                "content": user_input
            })

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages
            )

            ai_reply = response.choices[0].message.content

            messages.append({
                "role": "assistant",
                "content": ai_reply
            })

    # send only user + assistant messages to UI
    display_messages = [
        {
            "role": "user" if m["role"] == "user" else "ai",
            "content": m["content"]
        }
        for m in messages
        if m["role"] != "system"
    ]

    return render_template("index.html", messages=display_messages)

if __name__ == "__main__":
    app.run(debug=True)
