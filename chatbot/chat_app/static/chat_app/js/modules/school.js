export const run = () => {

    const token = localStorage.getItem("access_token");
    let currentChatroomTopic = null; // 현재 선택된 토픽
    let currentChatroomId = null;   // 현재 ChatRoom ID

    if (!token) {
        console.error("No access token found. Please log in again.");
        return;
    }

    const messageContainer = document.getElementById("message-container");
    messageContainer.innerHTML = `<h1 class="text-left text-2xl font-bold">학교정보</h1>`;

    fetch(`/api/chatroom/school-info/`, {
        method: "GET",
        headers: {
            "Authorization": `Bearer ${token}`,
        },
    })
        .then(response => response.json())
        .then(data => {
            currentChatroomTopic = topic;
            currentChatroomId = data.chatroom_id;

            // UI 업데이트 - 메시지 컨테이너 초기화 및 새 메시지 로드
            data.messages.forEach(message => {
                displayMessage("User", message.user_message);
                displayMessage("Bot", message.bot_message);
            });
        })
        .catch(error => console.error("Error loading chatroom:", error));

    document.getElementById('send-button').onclick = function () {
        sendMessage();
    };

    document.getElementById('chat-input').addEventListener('keypress', function (event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault(); // 기본 엔터 동작 방지
            sendMessage();
        }
    });

    function sendMessage() {
        console.log(token);
        const chatInput = document.getElementById("chat-input").value;
        if (chatInput.trim() === '') return; // 빈 메시지 전송 방지

        displayMessage("User", chatInput);
        chatInput.value = "";

        fetch(`/api/chatroom/${currentChatroomId}/message/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`,
            },
            body: JSON.stringify({ chatroom_id: currentChatroomId, sender: 'user', text: chatInput }),
        })
            .then(response => response.json())
            .then(data => {
                console.log(data);
                const botMessage = data.bot_message ? data.bot_message.text : "No response from bot.";
                displayMessage("Bot", botMessage);
            })
            .catch(error => console.error("Error:", error));
        document.getElementById('chat-input').value = '';
    }

    function displayMessage(sender, message) {
        const messageElement = document.createElement("div");
        const messageContainer = document.getElementById("message-container");

        if (sender === "User") {
            messageElement.className = "flex justify-end";
            messageElement.innerHTML = `
                    <div class="mr-2 py-3 px-4 bg-indigo-100 text-gray-800 rounded-xl">${message}</div>
                    <div class="flex items-center justify-center h-10 w-10 rounded-full bg-indigo-500 text-white">A</div>
                `;
        } else {
            messageElement.className = "flex items-start";
            messageElement.innerHTML = `
                    <div class="flex items-center justify-center h-10 w-10 rounded-full bg-indigo-500 text-white">A</div>
                    <div class="ml-2 py-3 px-4 bg-gray-200 rounded-xl">${message}</div>
                `;
        }

        messageContainer.appendChild(messageElement);
        messageContainer.scrollTop = messageContainer.scrollHeight;
    }
}