from flask import Flask, render_template, request, jsonify, session
import os, time
from openai import OpenAI

app = Flask(__name__)
app.secret_key = "opentutor-chatgpt-gemini-final"

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --------- Limits & Safety ----------
RATE_LIMIT = 10
RATE_WINDOW = 60
MAX_MEMORY = 8
MAX_QUESTION_LENGTH = 800


def is_rate_limited():
    now = time.time()
    session.setdefault("requests", [])
    session["requests"] = [t for t in session["requests"] if now - t < RATE_WINDOW]
    if len(session["requests"]) >= RATE_LIMIT:
        return True
    session["requests"].append(now)
    return False


@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/chat")
def chat():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    # ---------- Rate limit ----------
    if is_rate_limited():
        return jsonify({
            "answer": "⏳ थोड़ा रुक जाइए, आप बहुत तेज़ सवाल भेज रहे हैं।"
        })

    data = request.get_json(silent=True) or {}
    raw_question = data.get("question") or ""
    question = raw_question.strip()
    mode = data.get("mode", "tutor")

    # ---------- Input safety ----------
    if not question:
        return jsonify({"answer": "❌ कृपया कोई सवाल लिखिए।"})

    if len(question) > MAX_QUESTION_LENGTH:
        return jsonify({
            "answer": "⚠️ सवाल थोड़ा ज़्यादा लंबा है, कृपया छोटा करके पूछिए।"
        })

    session.setdefault("chat", [])
    messages = []

    # ---------- CORE BRAIN (ChatGPT + Gemini style) ----------
    if mode == "exam":
        system_prompt = """
You are OpenTutor AI in STRICT EXAM MODE.

Rules:
- Give only the exact answer asked.
- Short, crisp, exam-ready.
- No extra explanation.
- No options unless asked.
- No conversation.
"""
        temperature = 0.15
        max_tokens = 180
        messages.append({"role": "system", "content": system_prompt})

    else:
        system_prompt = """
You are OpenTutor AI with ChatGPT + Gemini style intelligence.

Your behavior:
- Talk like a helpful human tutor.
- If the question is unclear or too broad, ASK A CLARIFYING QUESTION instead of guessing.
- If multiple meanings are possible, give clear OPTIONS (numbered).
- Understand follow-up questions using conversation context.
- Explain simply, step-by-step.
- Use Hindi / Hinglish / English based on user's language.
- Stay strictly on topic.
- Do NOT hallucinate facts.
- Do NOT over-explain unless needed.
"""
        temperature = 0.35
        max_tokens = 520
        messages.append({"role": "system", "content": system_prompt})

        # conversation memory
        for m in session["chat"][-MAX_MEMORY:]:
            messages.append(m)

    # user message
    messages.append({"role": "user", "content": question})

    # ---------- AI Call ----------
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=20
        )

        answer = response.choices[0].message.content.strip()
        if not answer:
            raise ValueError("Empty response")

        # save memory only in tutor mode
        if mode != "exam":
            session["chat"].append({"role": "user", "content": question})
            session["chat"].append({"role": "assistant", "content": answer})
            session["chat"] = session["chat"][-MAX_MEMORY * 2:]

        return jsonify({"answer": answer})

    except Exception:
        return jsonify({
            "answer": (
                "⚠️ अभी सिस्टम थोड़ा व्यस्त है।\n"
                "कृपया 10–20 सेकंड बाद फिर से कोशिश करें।"
            )
        })


@app.route("/clear", methods=["POST"])
def clear_chat():
    session.clear()
    return jsonify({"status": "cleared"})


if __name__ == "__main__":
    app.run(debug=True)
