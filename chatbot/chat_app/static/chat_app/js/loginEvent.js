document.getElementById('login-form').addEventListener('submit', function(event) {
    event.preventDefault();

    const user_name = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const errorMessage = document.getElementById('error-message');

    // Clear previous error messages
    errorMessage.style.display = 'none';

    fetch('/api/login/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ user_name, password }),
        })
        .then(response => {
            if (!response.ok) {
                // 응답이 2xx가 아니면 에러를 처리
                return response.json().then(data => {
                    throw data;  // JSON 데이터를 에러로 던짐
                });
            }
            return response.json();  // JSON 파싱
        })
        .then(data => {
            // JSON 응답 처리
            if (data.authToken) {
                localStorage.setItem('authToken', data.authToken);
                window.location.href = '/chatbot/';
            }else{
                errorMessage.style.display = 'block';
                errorMessage.textContent = '로그인에 실패했습니다. 다시 시도해주세요.';
            }
        })
        .catch(errorData => {
            // 서버에서 반환된 오류 메시지를 화면에 표시
            errorMessage.style.display = 'block';
            if (errorData.non_field_errors) {
                errorMessage.textContent = '가입되지 않은 사용자이거나 비밀번호가 잘못되었습니다.';
            } else {
                errorMessage.textContent = '서버에 문제가 발생했습니다. 다시 시도해주세요.';
            }
        });
});
