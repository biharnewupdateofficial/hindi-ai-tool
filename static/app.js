const chatBox = document.getElementById("chat-box");
const input = document.getElementById("question");
const sendBtn = document.getElementById("send");
const micBtn = document.getElementById("mic");

let voiceEnabled = true;

/* Add message */
function addMessage(text, type) {
    const div = document.createElement("div");
    div.className = type;
    div.innerText = text;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}

/* Send message */
sendBtn.onclick = sendMessage;

function sendMessage() {
    const text = input.value.trim();
    if (!text) return;

    addMessage(text, "user");
    input.value = "";

    const aiMsg = document.createElement("div");
    aiMsg.className = "ai";
    aiMsg.innerText = "OpenTutor AI likh raha hai...";
    chatBox.appendChild(aiMsg);

    fetch("/ask", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({question: text})
    })
    .then(res => res.json())
    .then(data => {
        aiMsg.innerText = data.answer;

        if (voiceEnabled) {
            fetch("/speak", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({text: data.answer})
            });
        }
    });
}

/* ENTER key */
input.addEventListener("keydown", e => {
    if (e.key === "Enter") {
        e.preventDefault();
        sendMessage();
    }
});

/* VOICE INPUT */
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = new SpeechRecognition();
recognition.lang = "hi-IN";

micBtn.onclick = () => recognition.start();

recognition.onresult = e => {
    input.value = e.results[0][0].transcript;
    sendMessage();
};

/* IMAGE GENERATION */
function generateImage(prompt) {
    fetch("/image", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({prompt})
    })
    .then(res => res.json())
    .then(data => {
        const img = document.createElement("img");
        img.src = data.image;
        img.style.maxWidth = "300px";
        chatBox.appendChild(img);
    });
}

/* TOGGLE VOICE */
function toggleVoice() {
    voiceEnabled = !voiceEnabled;
    alert("Voice: " + (voiceEnabled ? "ON" : "OFF"));
}
