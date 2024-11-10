// 채팅방 초기 로딩 시 메시지 불러오기
document.addEventListener("DOMContentLoaded", function() {
    loadChatRooms();
});

function loadChatRooms(){
    fetch('/api/chatrooms/',{
        method: 'GET',
        headers: {
            'Authorization': `Token {$localStorage.getItem('authToken')}`
        }
    })
    .then(response => response.json())
    .then(chatrooms => {
        const chatRoomsContainer = document.getElementById('chat-rooms');
        chatrooms.forEach(room => {
            const button = document.createElement('button');
            button.className = 'btn chatroom-btn';
            button.textContent = room.name; // 채팅방 이름 표시
            button.onclick = () => selectChatRoom(room.id);
            chatRoomsContainer.appendChild(button);
        });

        if (chatrooms.length > 0) {
            // 첫 번째 채팅방을 기본으로 로드
            selectChatRoom(chatrooms[0].id);
        }
    })
    .catch(error => {
        console.error('Error loading chatrooms:', error);
    });
}

let currentChatRoomId=null;
// 새로운 채팅방 선택 기능 추가
function selectChatRoom(chatroomId) {
    currentChatRoomId = chatroomId;
    document.getElementById('output-container').innerHTML = '';
    loadChatMessages(currentChatRoomId);
}

// 채팅방 사이드바
document.getElementById('toggle-chat-rooms').onclick=function(){
    const sidebar = document.querySelector('.sidebar');
    const chatContainer = document.querySelector('.chat-container');
    
    sidebar.classList.toggle('hidden'); // 사이드바 숨기기
    chatContainer.classList.toggle('shifted'); // 채팅 컨테이너 이동
};

// 채팅방의 기존 메시지 불러오기
function loadChatMessages(currentChatRoomId) {
    fetch(`/api/chat/${currentChatRoomId}/messages/`, {
        method: 'GET',
        headers: {
            'Authorization': `Token ${localStorage.getItem('authToken')}`,
            'Content-Type': 'application/json'
        },
    })
    .then(response => response.json())
    .then(messages => {
        const outputContainer = document.getElementById('output-container');
        messages.forEach(msg => {
            const messageDiv = document.createElement('div');
            messageDiv.className = msg.sender === 'user' ? 'message user-message' : 'message bot-message';
            messageDiv.textContent = msg.text;
            outputContainer.appendChild(messageDiv);
        });
        outputContainer.scrollTop = outputContainer.scrollHeight;
    })
    .catch(error => {
        console.error('Error loading messages:', error);
    });
}

document.getElementById('send-button').onclick = function() {
    sendMessage();
};

document.getElementById('input-message').addEventListener('keypress', function(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault(); // 기본 엔터 동작 방지
        sendMessage();
    }
});

function sendMessage() {
    const inputMessage = document.getElementById('input-message').value;
    if (inputMessage.trim() === '') return; // 빈 메시지 전송 방지

    const outputContainer = document.getElementById('output-container');
    const messageDiv = document.createElement('div');

    // User 메시지 스타일 적용
    messageDiv.className = 'message user-message';
    messageDiv.textContent = inputMessage;
    outputContainer.appendChild(messageDiv);
    
    // REST API로 메시지 전송
    fetch(`/api/chat/${currentChatRoomId}/messages/`, {
        method: 'POST',
        headers: {
            'Authorization': `Token ${localStorage.getItem('authToken')}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text: inputMessage})
    })
    .then(response => response.json())
    .then(data => {
        if(data.bot_message&&data.bot_message.text){
            displayBotMessage(data.bot_message.text);
        }else{
            console.error("Bot message not found in response:", data);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });

    document.getElementById('input-message').value = '';
    outputContainer.scrollTop = outputContainer.scrollHeight;
}

function displayBotMessage(message) {
    const outputContainer = document.getElementById('output-container');
    const messageDiv = document.createElement('div');

    messageDiv.className = 'message bot-message';
    messageDiv.textContent = message;
    outputContainer.appendChild(messageDiv);
    outputContainer.scrollTop = outputContainer.scrollHeight;
}


// 로그아웃 버튼 이벤트 리스너
document.addEventListener("DOMContentLoaded", function() {
    const logoutButton = document.getElementById("logout-button");

    logoutButton.addEventListener("click", function() {
        // 세션에서 토큰을 삭제하는 API 호출
        fetch('/api/logout/', {
            method: 'POST',
            headers: {
                'Authorization': `Token ${localStorage.getItem('authToken')}`,
                'Content-Type': 'application/json'
            },
        })
        .then(response => {
            if (response.ok) {
                // 토큰 삭제 및 메인 페이지로 리다이렉트
                localStorage.removeItem('authToken');  // 로컬 스토리지에서 토큰 삭제
                window.location.href = '/';  // 메인 페이지로 이동
            } else {
                console.error("Logout failed:", response.statusText);
            }
        })
        .catch(error => {
            console.error("Error:", error);
        });
    });
});
