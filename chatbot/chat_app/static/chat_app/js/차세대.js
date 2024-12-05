export function render차세대() {
    console.log("시발")
    const token = localStorage.getItem('access_token');
    if (!token) {
        console.error("No access token found. Please log in again.");
        return;
    }
    else{
        console.log("톸큰:",token)
    }

    let topic = "차세대";
    let currentChatroomId = null;
    window.history.pushState({}, '', `/${topic}/`);
    console.log('pushState 까지는 지났음 ')


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
    console.log('된건가?');

    
    document.getElementById('send-button').onclick = function () {
        console.log('send눌렸음')
        sendMessage();
    };

    document.getElementById('chat-input').addEventListener('keypress', function (event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault(); // 기본 엔터 동작 방지
            sendMessage();
        }
    });   
           

    async function sendMessage() {
        const chatInputElement = document.getElementById("chat-input");
        const chatInputValue = chatInputElement.value.trim();
        if (chatInputValue === '') return; // 빈 메시지 전송 방지

        displayMessage("user", chatInputValue);
        chatInputElement.value = "";

        const 봇의대답=await 서버와통신(chatInputValue);
        console.log("봇의 대답 : ",봇의대답)
        if (봇의대답) {
            console.log("if문 안으로 들어오나?")
            console.log("봇의 대답의 자료형 :",typeof(봇의대답))
            displayMessage("system", 봇의대답);
        }
    }

    // 서버로 문자열 보내기
    async function 서버와통신(사용자의질문) {
        console.log("서버와통신 함수로 들어오기는 했나?")
        try {
            const 서버로부터의응답 = await fetch("/api/차세대/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ string: 사용자의질문 }),
            });

            if (!서버로부터의응답.ok) {
                throw new Error("Error in server response");
            }

            const 서버응답json으로 = await 서버로부터의응답.json();
            console.log("서버로부터의응답 :", 서버응답json으로.result); // 결과 출력
            return 서버응답json으로.result; // 받은 결과를 반환
        } catch (error) {
            console.error("오오류 :", error);
        }
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
            console.log("displayMessage까지 들어오나?");
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