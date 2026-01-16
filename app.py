from flask import Flask, render_template, request, jsonify, session, redirect
import os, datetime
import openai, razorpay

app = Flask(__name__)
app.secret_key = "super-secret-key"

openai.api_key = os.getenv("OPENAI_API_KEY")

# Razorpay
rzp_client = razorpay.Client(
    auth=(os.getenv("RAZORPAY_KEY_ID"), os.getenv("RAZORPAY_KEY_SECRET"))
)

FREE_DAILY_LIMIT = 10

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
        u=request.form.get("username")
        if u:
            session["user"]=u
            session.setdefault("plan","free")
            session.setdefault("usage",{today():0})
            return redirect("/")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/upgrade")
def upgrade():
    order = rzp_client.order.create({
        "amount": 9900,  # ₹99
        "currency": "INR",
        "payment_capture": 1
    })
    return render_template(
        "upgrade.html",
        order_id=order["id"],
        key=os.getenv("RAZORPAY_KEY_ID")
    )

@app.route("/payment-success", methods=["POST"])
def payment_success():
    session["plan"] = "paid"
    return redirect("/")

@app.route("/ask", methods=["POST"])
def ask():
    if not session.get("user"):
        return jsonify({"answer":"❌ Login required"})

    usage=session.setdefault("usage",{})
    usage.setdefault(today(),0)

    if session.get("plan")=="free" and usage[today()]>=FREE_DAILY_LIMIT:
        return jsonify({"answer":"🚫 Free limit reached. Upgrade to Pro."})

    q=request.json.get("question","")
    if not q:
        return jsonify({"answer":"❌ Empty question"})

    try:
        res=openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role":"system","content":"You are a ChatGPT + Gemini style AI assistant."},
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
