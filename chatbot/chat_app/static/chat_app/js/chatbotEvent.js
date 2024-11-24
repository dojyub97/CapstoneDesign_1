// chatbotEvent.js
let token = null;

document.addEventListener("DOMContentLoaded", function () {
    // DOM 로드 후 토큰을 가져온다.
    const token = localStorage.getItem("access_token");
    let currentChatroomTopic = null; // 현재 선택된 토픽
    let currentChatroomId = null;   // 현재 ChatRoom ID

    if (!token) {
        console.error("No access token found. Please log in again.");
        return;
    }

    // 초기 URL 확인 및 페이지 로드
    const currentPath = window.location.pathname.split('/').filter(Boolean); // URL path 분해
    if (currentPath.length === 0 || currentPath[1] === "home") {
        loadHomePage();
    } else {
        const topic = decodeURIComponent(currentPath[0]);
        loadChatroomByTopic(topic);
    }

    // 브라우저 뒤로/앞으로 이동 이벤트 처리
    window.addEventListener("popstate", function () {
        const currentPath = window.location.pathname.split('/').filter(Boolean);
        if (currentPath.length === 0 || currentPath[0] === "home") {
            loadHomePage();
        } else {
            const topic = decodeURIComponent(currentPath[0]);
            loadChatroomByTopic(topic);
        }
    });

    // 사이드바 버튼 클릭 이벤트 처리
    document.getElementById("menu-buttons").addEventListener("click", function (event) {
        const button = event.target.closest("button");
        if (!button) return; // 클릭한 대상이 버튼이 아니면 무시

        const category = button.innerText.trim(); // 버튼 텍스트로 토픽 추출
        if (category === "홈") {
            loadHomePage();
            window.history.pushState({}, '', '/home/');
        } else {
            loadChatroomByTopic(category);
            window.history.pushState({}, '', `/${encodeURIComponent(category)}/`);
        }
    });

    // 홈 화면 로드
    function loadHomePage() {
        currentChatroomTopic = null;
        currentChatroomId = null;

        const messageContainer = document.getElementById("message-container");
        messageContainer.innerHTML = `<h1 class="text-left text-2xl font-bold">홈화면test</h1>`;
    }

    // 특정 토픽의 ChatRoom과 메시지 로드
    function loadChatroomByTopic(topic) {
        fetch(`/api/chatroom/${encodeURIComponent(topic)}/`, {
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
                const messageContainer = document.getElementById("message-container");
                messageContainer.innerHTML = `<h3>${data.chatroom.topic}</h3>`;

                data.messages.forEach(message => {
                    displayMessage("User", message.user_message);
                    displayMessage("Bot", message.bot_message);
                });
            })
            .catch(error => console.error("Error loading chatroom:", error));
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

        displayMessage("user", chatInput);
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

        if (sender === "user") {
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
});

// localstorage에 추가 key값을 넣어서 previous 대화내역을 저장
//

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