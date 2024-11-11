function goToChatPage() {
    // 로그인 상태 확인을 위한 토큰 가져오기 (세션 쿠키에서 가져옴)
    const token = getCookie('authToken');  // 'authToken'은 세션에 저장된 쿠키 이름

    if (token) {
        // 토큰이 있을 경우 채팅 페이지로 이동
        window.location.href = '/chatbot/';
    } else {
        // 토큰이 없으면 로그인 페이지로 이동
        window.location.href = '/login/';
    }
}

// 쿠키에서 토큰을 가져오는 함수
function getCookie(name) {
    const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
    if (match) return match[2];
    return null;
}
