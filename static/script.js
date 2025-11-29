async function sendMessage() {
    const input = document.getElementById("user-input");
    const chat = document.getElementById("chat-window");
    const userText = input.value.trim();

    if (!userText) return;

    // poruka korisnika
    const userMsg = document.createElement("div");
    userMsg.className = "message user";
    userMsg.textContent = userText;
    chat.appendChild(userMsg);

    input.value = "";
    chat.scrollTop = chat.scrollHeight;

    // slanje poruke backendu
    const response = await fetch("/api/message", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userText })
    });

    const data = await response.json();

    // poruka bota
    const botMsg = document.createElement("div");
    botMsg.className = "message bot";
    botMsg.textContent = data.answer;
    chat.appendChild(botMsg);

    chat.scrollTop = chat.scrollHeight;
}

// submit forme
document.getElementById("chat-form").addEventListener("submit", function (e) {
    e.preventDefault();
    sendMessage();
});

// Enter u input polju
document.getElementById("user-input").addEventListener("keypress", function (e) {
    if (e.key === "Enter") {
        e.preventDefault();
        sendMessage();
    }
});
