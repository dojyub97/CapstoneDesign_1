function goToChatPage() {
    // 로그인 상태 확인을 위한 토큰 가져오기
    const token = localStorage.getItem('authToken');  // 예를 들어, 로컬스토리지에 토큰 저장 시
    
    if (token) {
        // 토큰이 있을 경우 채팅 페이지로 이동
        window.location.href = '/chatbot/';
    } else {
        // 토큰이 없으면 로그인 페이지로 이동
        window.location.href = '/login/';
    }
}
