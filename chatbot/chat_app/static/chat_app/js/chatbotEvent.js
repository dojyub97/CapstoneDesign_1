// chatbotEvent.js
let chatroomId = window.location.pathname.split('/')[2];
let token = null;

document.addEventListener("DOMContentLoaded", function () {
    // DOM 로드 후 토큰을 가져옵니다.
    token = localStorage.getItem("access_token");

    if (!token) {
        console.error("No access token found. Please log in again.");
        return;
    }

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

        fetch(`/api/chatroom/${chatroomId}/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`,
            },
            body: JSON.stringify({ chatroom_id: chatroomId, sender: 'user', text: chatInput }),
        })
            .then(response => response.json())
            .then(data => {
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
        messageContainer.scrollTop = messageContainer.scrollHeight; // Auto-scroll to the latest message
    }
});

// 로그아웃 버튼 이벤트 리스너
// document.addEventListener("DOMContentLoaded", function () {
//     const logoutButton = document.getElementById("logout-button");

//     logoutButton.addEventListener("click", function () {
//         // 세션에서 토큰을 삭제하는 API 호출
//         fetch('/api/logout/', {
//             method: 'POST',
//             headers: {
//                 'Authorization': `Token ${token}`,
//                 'Content-Type': 'application/json'
//             },
//         })
//             .then(response => {
//                 if (response.ok) {
//                     // 토큰 삭제 및 메인 페이지로 리다이렉트
//                     localStorage.removeItem('authToken');  // 로컬 스토리지에서 토큰 삭제
//                     window.location.href = '/';  // 메인 페이지로 이동
//                 } else {
//                     console.error("Logout failed:", response.statusText);
//                 }
//             })
//             .catch(error => {
//                 console.error("Error:", error);
//             });
//     });
// });