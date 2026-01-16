const chatBox = document.getElementById("chat-box");
const input = document.getElementById("question");

function addMessage(text, cls) {
    const div = document.createElement("div");
    div.className = cls;
    div.innerText = text;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function sendMessage() {
    const q = input.value.trim();
    if (!q) return;

    addMessage(q, "user");
    input.value = "";

    fetch("/ask", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({question: q})
    })
    .then(r => r.json())
    .then(d => addMessage(d.answer, "ai"));
}

input.addEventListener("keydown", e => {
    if (e.key === "Enter") {
        e.preventDefault();
        sendMessage();
    }
});

// PDF Upload
function uploadPDF() {
    const file = document.getElementById("pdf").files[0];
    const fd = new FormData();
    fd.append("pdf", file);

    fetch("/upload", {
        method: "POST",
        body: fd
    })
    .then(r => r.json())
    .then(d => addMessage(d.summary, "ai"));
}

// Clear Chat
function clearChat() {
    fetch("/clear")
    .then(() => {
        chatBox.innerHTML = "";
    });
}
