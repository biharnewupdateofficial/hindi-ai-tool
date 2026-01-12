from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
import openai, os

app = Flask(__name__)
app.secret_key = "super-secret-key"

openai.api_key = os.getenv("OPENAI_API_KEY")

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# ---- Dummy user (for now) ----
class User(UserMixin):
    id = "student"

@login_manager.user_loader
def load_user(user_id):
    return User()

def ai_answer(question):
    prompt = f"""
Tum ek expert Indian teacher ho.
Rules:
- Clear headings
- Bullet points
- Emojis
- Exam oriented
- Simple Hindi + Hinglish

Question:
{question}
"""
    res = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role":"user","content":prompt}]
    )
    return res.choices[0].message.content

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        login_user(User())
        return redirect(url_for("index"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    logout_user()
    return redirect("/login")

@app.route("/", methods=["GET","POST"])
@login_required
def index():
    answer = None
    if request.method == "POST":
        q = request.form["question"]
        answer = ai_answer(q)
    return render_template("index.html", answer=answer)

if __name__ == "__main__":
    app.run()
