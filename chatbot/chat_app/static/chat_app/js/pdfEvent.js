
export function renderPDFGenerator() {
    const token = localStorage.getItem("access_token");
    if (!token) {
        console.error("No access token found. Please log in again.");
        return;
    }

    let topic = "pdf-QnA";
    let currentChatroomId = null;
    window.history.pushState({}, '', `/${topic}/`);

    fetch(`/api/chatroom/${topic}/`, {
        method: "GET",
        headers: {
            "Authorization": `Bearer ${token}`,
        },
    })
        .then(response => response.json())
        .then(data => {
            currentChatroomId = data.chatroom_id;
            const mainContainer = document.getElementById("main-container");
            mainContainer.innerHTML = `
                <div id="pdf-container" class="w-1/3 bg-gray-100 rounded-lg p-4">
                    <h2 class="text-lg font-bold mb-4 text-gray-700">Upload PDF</h2>
                    <div class="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center cursor-pointer">
                        <label for="pdf-upload" class="block text-gray-500">
                            <i class="fas fa-file-upload text-gray-400 text-3xl mb-2"></i>
                            <span>Upload PDF</span>
                        </label>
                        <input id="pdf-upload" type="file" accept="application/pdf" class="hidden" />
                    </div>
                    <div id="pdf-preview" class="mt-4">
                        <img src="https://via.placeholder.com/150" alt="PDF preview" class="w-full rounded-lg border border-gray-200" />
                    </div>
                </div>

                <!-- Chat Section -->
                <div id="chat-container" class="flex-1 bg-gray-100 rounded-lg p-4">
                    <div class="flex flex-col h-full">
                    <!-- message container -->
                    <div id="message-container" class="flex-1 overflow-y-auto">
                        <div class="mb-2">
                        <!-- Chat messages will appear here -->
                        </div>
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
            </div>
            `;
            // PDF 업로드 이벤트 연결
            document.getElementById("pdf-upload").addEventListener("change", function (event) {
                const file = event.target.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = function (e) {
                        extractPDFText(e.target.result)
                            .then(pdfText => {
                                const pdfPreview = document.getElementById("pdf-preview");
                                pdfPreview.textContent = pdfText;

                                // Store extracted text for later API submission
                                document.getElementById("send-button").onclick = function () {
                                    sendMessage(pdfText);
                                };
                                document.getElementById('chat-input').addEventListener('keypress', function (event) {
                                    if (event.key === 'Enter' && !event.shiftKey) {
                                        event.preventDefault(); // 기본 엔터 동작 방지
                                        sendMessage();
                                    }
                                });
                            })
                            .catch(err => {
                                console.error("Error extracting text from PDF:", err);
                            });
                    };
                    reader.readAsDataURL(file);
                }
            });
        })
        .catch(error => console.error("Error loading chatroom:", error));

    function sendMessage(pdfText) {
        console.log(token);
        const chatInputElement = document.getElementById("chat-input");
        const chatInputValue = chatInputElement.value.trim();
        if (chatInputValue === '') return; // 빈 메시지 전송 방지

        displayMessage("user", chatInputValue);
        chatInputElement.value = "";

        fetch(`/api/chatmessage/${topic}/${currentChatroomId}/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`,
            },
            body: JSON.stringify({
                "chat_data": {
                    "chatroom_id": currentChatroomId,
                    "sender": "user",
                    "text": chatInputValue
                },
                "file_data": {
                    "file_name": "example.pdf",
                    "content": pdfText
                }
            }),
        })
            .then(response => response.json())
            .then(data => {
                console.log(data);
                const botMessage = data.bot_message ? data.bot_message.text : "No response from bot.";
                displayMessage("Bot", botMessage);
            })
            .catch(error => console.error("Error:", error));
    }

    function displayMessage(sender, message) {
        const messageElement = document.createElement("div");
        const messageContainer = document.getElementById("message-container");

        if (sender === "user") {
            messageElement.className = "flex justify-end mb-4";
            messageElement.innerHTML = `
                    <div class="mr-2 py-3 px-4 bg-indigo-100 text-gray-800 rounded-xl">${message}</div>
                    <div class="flex items-center justify-center h-10 w-10 rounded-full bg-indigo-500 text-white">U</div>
                `;
        } else {
            messageElement.className = "flex items-start mb-4";
            messageElement.innerHTML = `
                    <div class="ml-2 py-3 px-4 bg-gray-200 rounded-xl">${message}</div>
                    <div class="flex items-center justify-center h-10 w-10 rounded-full bg-indigo-500 text-white">B</div>
                `;
        }
        messageContainer.appendChild(messageElement);
        messageContainer.scrollTop = messageContainer.scrollHeight;
    }
}