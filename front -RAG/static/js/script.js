document.addEventListener("DOMContentLoaded", function () {
    setTimeout(() => {
        addMessage("Bem-vindo ao chatbot, o que você quer saber?", "bot");
    }, 500);
});

document.getElementById("send-button").addEventListener("click", sendMessage);
document.getElementById("user-input").addEventListener("keypress", function (e) {
    if (e.key === "Enter") sendMessage();
});

function sendMessage() {
    const inputField = document.getElementById("user-input");
    const userInput = inputField.value.trim();

    if (userInput) {
        addMessage(userInput, "user");
        inputField.value = '';
        setTimeout(() => {
            addMessage(generateBotResponse(userInput), "bot");
        }, 1000);
    }
}

function addMessage(message, sender) {
    const chatBox = document.getElementById("chat-box");
    const messageContainer = document.createElement("div");
    messageContainer.classList.add("message-container", sender === "user" ? "user-container" : "bot-container");
    const messageBubble = document.createElement("div");
    messageBubble.classList.add("message", sender === "user" ? "user-message" : "bot-message");
    messageBubble.textContent = message;
    messageContainer.appendChild(messageBubble);
    chatBox.appendChild(messageContainer);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function generateBotResponse(input) {
    return "Desculpe, não entendi sua pergunta.";
}
