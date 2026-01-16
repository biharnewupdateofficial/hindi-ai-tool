from flask import Flask, render_template, request, jsonify, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "super-secret-key"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upgrade")
def upgrade():
    return render_template("upgrade.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    question = data.get("question", "")

    if not question:
        return jsonify({"answer": "कृपया प्रश्न लिखें"})

    # Dummy AI response (safe)
    answer = f"आपने पूछा: {question}"

    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(debug=True)
