from flask import Flask, render_template, request, jsonify, session, redirect
import os, datetime
import openai

app = Flask(__name__)
app.secret_key = "super-secret-key"

openai.api_key = os.getenv("OPENAI_API_KEY")

FREE_DAILY_LIMIT = 10  # free users per day

def today():
    return datetime.date.today().isoformat()

@app.route("/")
def home():
    if not session.get("user"):
        return redirect("/login")
    return render_template("chat.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        user=request.form.get("username")
        if user:
            session["user"]=user
            session.setdefault("plan","free")
            session.setdefault("usage",{today():0})
            return redirect("/")
    return render_template("login.html")

@app.route("/upgrade")
def upgrade():
    return render_template("upgrade.html")

@app.route("/set-paid")
def set_paid():
    session["plan"]="paid"
    return redirect("/")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/ask", methods=["POST"])
def ask():
    if not session.get("user"):
        return jsonify({"answer":"❌ Login required"})

    usage=session.setdefault("usage",{})
    usage.setdefault(today(),0)

    if session.get("plan")=="free" and usage[today()]>=FREE_DAILY_LIMIT:
        return jsonify({"answer":"🚫 Daily free limit reached. Upgrade to Pro."})

    q=request.json.get("question","")
    if not q:
        return jsonify({"answer":"❌ Empty question"})

    try:
        res=openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role":"system","content":"You are a helpful AI tutor like ChatGPT and Gemini."},
                {"role":"user","content":q}
            ]
        )
        ans=res["choices"][0]["message"]["content"]
        usage[today()]+=1
        session["usage"]=usage
        return jsonify({"answer":ans})
    except Exception as e:
        return jsonify({"answer":f"❌ AI Error: {e}"})

@app.route("/status")
def status():
    usage=session.get("usage",{})
    left=FREE_DAILY_LIMIT-usage.get(today(),0)
    return jsonify({
        "plan":session.get("plan","free"),
        "left":left if left>0 else 0
    })

if __name__=="__main__":
    app.run(host="0.0.0.0",port=10000)
