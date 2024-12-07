import { fetchWithToken } from "./tokenEvent.js";


export function renderSchoolInfo() {
    const token = localStorage.getItem('access_token');
    if (!token) {
        console.error("No access token found. Please log in again.");
        return;
    }

    console.log(token);
    let topic = "school-info";
    let currentChatroomId = null;
    window.history.pushState({}, '', `/${topic}/`);

    fetchWithToken(`/api/chatroom/${topic}/`, {
        method: "GET",
    })
        .then(response => response.json())
        .then(data => {
            currentChatroomId = data.chatroom_id;
            const mainContainer = document.getElementById("main-container");
            mainContainer.innerHTML = `
                <div id="chat-container" class="flex flex-col flex-shrink-0 rounded-2xl bg-gray-100 w-full max-w-[900px] p-4 ">
                    <div id="message-container" class="flex flex-col p-4 break-words w-full max-w-full h-full overflow-y-auto hide-scrollbar ">
                        <!-- Messages will appear here dynamically -->
                    </div>
                    <!-- Input section -->
                    <div class="flex flex-row items-center h-16 rounded-xl bg-white w-full px-4 mt-4">
                        <div class="flex-grow ml-4">
                            <input id="chat-input" type="text" placeholder="Type a message..." class="flex w-full border rounded-xl focus:outline-none focus:border-indigo-300 pl-4 h-10" />
                        </div>
                        <div class="ml-4">
                            <button id="send-button" class="flex items-center justify-center bg-indigo-500 hover:bg-indigo-600 rounded-xl text-white px-4 py-1">
                                <span>Send</span>
                                <span class="ml-2">
                                    <svg class="w-4 h-4 transform rotate-45 -mt-px" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path>
                                    </svg>
                                </span>
                            </button>
                        </div>
                    </div>
                </div>
            `;

            data.messages.forEach(message => {
                displayMessage(message.sender, message.text);
            });
            // 중복 로직

            document.getElementById('send-button').onclick = function () {
                sendMessage();
            };

            document.getElementById('chat-input').addEventListener('keypress', function (event) {
                if (event.key === 'Enter' && !event.shiftKey) {
                    event.preventDefault(); // 기본 엔터 동작 방지
                    sendMessage();
                }
            });
        })
        .catch(error => console.error("Error loading chatroom:", error));

    function sendMessage() {
        console.log(token);
        const chatInputElement = document.getElementById("chat-input");
        const chatInputValue = chatInputElement.value.trim();
        if (chatInputValue === '') return; // 빈 메시지 전송 방지

        displayMessage("user", chatInputValue);
        chatInputElement.value = "";

        fetchWithToken(`/api/school-info/${currentChatroomId}/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ chatroom_id: currentChatroomId, sender: 'user', text: chatInputValue }),
        })
            .then(response => response.json())
            .then(data => {
                const botMessage = data.sender ? data.text : "No response from bot.";
                displayMessage(data.sender, botMessage);
            })
            .catch(error => console.error("Error:", error));
    }

    function displayMessage(sender, message) {
        const messageElement = document.createElement("div");
        const messageContainer = document.getElementById("message-container");

        if (sender === "user") {
            messageElement.className = "flex justify-end mb-4";
            messageElement.innerHTML = `
                    <div class="mr-2 ml-5 py-3 px-4 bg-indigo-100 text-gray-800 rounded-xl max-w-[calc(100%-2rem)] break-all overflow-y-auto">${message}</div>
                    <div class="flex-shrink-0 flex items-center justify-center h-10 w-10 rounded-full bg-indigo-500 text-white">U</div>
                `;
        } else if (sender === "system") {
            messageElement.className = "flex items-start mb-4";
            messageElement.innerHTML = `
                    <div class="flex-shrink-0 flex items-center justify-center h-10 w-10 rounded-full bg-indigo-500 text-white">B</div>
                    <div class="ml-2 mr-5 py-3 px-4 bg-gray-200 rounded-xl max-w-[calc(100%-2rem)] break-all overflow-y-auto">${message}</div>
                `;
        }

        messageContainer.appendChild(messageElement);
        messageContainer.scrollTop = messageContainer.scrollHeight;
    }
}