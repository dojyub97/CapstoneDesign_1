const socket = new WebSocket('ws://127.0.0.1:8000/ws/chat/');

socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    const message = data.message;
    const outputContainer = document.getElementById('output-container');
    const messageDiv = document.createElement('div');

    // Bot 메시지 스타일 적용
    messageDiv.className = 'message bot-message';
    messageDiv.textContent = message;
    outputContainer.appendChild(messageDiv);
    outputContainer.scrollTop = outputContainer.scrollHeight; // 스크롤을 맨 아래로
};

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
    
    // WebSocket으로 메시지 전송
    socket.send(JSON.stringify({ message: inputMessage })); 
    document.getElementById('input-message').value = ''; // 입력 필드 초기화
    outputContainer.scrollTop = outputContainer.scrollHeight; // 스크롤을 맨 아래로
}

/* 채팅방 분리에 따른 함수 */
// function loadChat(room){
// }

document.getElementById('toggle-chat-rooms').onclick=function(){
    const sidebar = document.querySelector('.sidebar');
    const chatContainer = document.querySelector('.chat-container');
    
    sidebar.classList.toggle('hidden'); // 사이드바 숨기기
    chatContainer.classList.toggle('shifted'); // 채팅 컨테이너 이동
};

document.addEventListener("DOMContentLoaded", function() {
    // 로그아웃 버튼 이벤트 리스너
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
