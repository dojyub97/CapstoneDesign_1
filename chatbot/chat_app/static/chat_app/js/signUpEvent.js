document.getElementById('signup-form').addEventListener('submit', function(event) {
    event.preventDefault();

    const user_name = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const password2 = document.getElementById('password2').value;
    const errorMessageElement = document.getElementById('error-message');

    // Clear previous error messages
    errorMessageElement.style.display = 'none';

    fetch('/api/signup/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_name, password, password2 })
    })
    .then(response => {
        return response.json().then(data => ({ status: response.status, body: data }));  // response 객체를 포함하여 반환
    })
    .then(({ status, body }) => {
        if (status === 201) {  // 성공적으로 생성된 경우 상태 코드가 201
            window.location.href = '/login/';
        } else {
            // 서버에서 반환된 오류 메시지 표시
            let errorMessages = '';
            for (const key in body) {
                if (body.hasOwnProperty(key)) {
                    errorMessages += `${key}: ${body[key].join(' ')}\n`;
                }
            }
            errorMessageElement.style.display = "block";
            errorMessageElement.textContent = errorMessages || "회원가입에 실패했습니다. 다시 시도해주세요.";
        }
    })
    .catch(error => {
        console.error("Fetch error:", error);
        errorMessageElement.style.display = "block";
        errorMessageElement.textContent = "서버와의 연결에 실패했습니다. 잠시 후 다시 시도해주세요.";
    });
});
