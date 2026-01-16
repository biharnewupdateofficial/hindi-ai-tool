const chatBox = document.getElementById("chat-box");
const input = document.getElementById("question");
const sendBtn = document.getElementById("send");
const micBtn = document.getElementById("mic");

/* Add message */
function addMessage(text, type) {
    const div = document.createElement("div");
    div.className = type;
    div.innerText = text;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}

/* Send text */
sendBtn.onclick = sendMessage;

function sendMessage() {
    const text = input.value.trim();
    if (!text) return;

    addMessage(text, "user");
    input.value = "";

    addMessage("OpenTutor AI likh raha hai...", "ai");

    fetch("/ask", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({question: text})
    })
    .then(res => res.json())
    .then(data => {
        chatBox.lastChild.innerText = data.answer;
    });
}

/* ENTER key */
input.addEventListener("keydown", e => {
    if (e.key === "Enter") {
        e.preventDefault();
        sendMessage();
    }
});

/* 🎤 VOICE INPUT (PHASE 9) */
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = new SpeechRecognition();

recognition.lang = "hi-IN";

micBtn.onclick = () => {
    recognition.start();
};

recognition.onresult = event => {
    const voiceText = event.results[0][0].transcript;
    input.value = voiceText;
    sendMessage();
};
