from flask import Flask, render_template, request
import os
from openai import OpenAI
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

# Rate limit (Free plan safe)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["10 per hour"]
)

# OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/", methods=["GET", "POST"])
@limiter.limit("10/hour")
def index():
    answer = None

    if request.method == "POST":
        question = request.form.get("question")

        if question:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a helpful teacher who explains concepts in Hindi + Hinglish.\n"
                            "Always structure answers like this:\n"
                            "1. Short introduction\n"
                            "2. Definition\n"
                            "3. Step-by-step explanation\n"
                            "4. Examples\n"
                            "5. Quick summary\n\n"
                            "Use bullet points, headings, and simple language for students."
                        )
                    },
                    {
                        "role": "user",
                        "content": question
                    }
                ]
            )

            answer = response.choices[0].message.content

    return render_template("index.html", answer=answer)

if __name__ == "__main__":
    app.run(debug=True)
