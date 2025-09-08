// payments.js

document.addEventListener('DOMContentLoaded', function () {
    // Chat tab and window logic
    const chatTab = document.getElementById('chat-tab');
    const chatWindow = document.getElementById('chat-window');
    chatTab.addEventListener('click', function () {
        chatWindow.classList.toggle('open');
        document.body.classList.toggle('chat-open', chatWindow.classList.contains('open'));
    });

    const chatClose = document.getElementById('chat-close');
    chatClose.addEventListener('click', function () {
        chatWindow.classList.remove('open');
        document.body.classList.remove('chat-open');
    });

    // Simple chat logic (local echo)
    const chatForm = document.getElementById('chatForm');
    const chatInput = document.getElementById('chatInput');
    const chatMessages = document.getElementById('chatMessages');
    chatForm.addEventListener('submit', function (e) {
        e.preventDefault();
        const msg = chatInput.value.trim();
        if (!msg) return;
        const userMsg = document.createElement('div');
        userMsg.textContent = 'Tu: ' + msg;
        userMsg.style.marginBottom = '8px';
        chatMessages.appendChild(userMsg);
        chatInput.value = '';
        // Simulate AI response
        setTimeout(() => {
            const aiMsg = document.createElement('div');
            aiMsg.textContent = 'AI: ' + 'Am primit mesajul tău!';
            aiMsg.style.color = '#2b66c3';
            chatMessages.appendChild(aiMsg);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }, 600);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    });
});
