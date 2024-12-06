// Access Token 갱신 함수
function refreshAccessToken() {
    const refreshToken = localStorage.getItem('refresh_token');

    if (!refreshToken) {
        window.location.href = '/login/'; // Refresh Token이 없으면 로그인 페이지로 리다이렉트
        return Promise.reject('No refresh token available');
    }

    return fetch('/api/token/refresh/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh_token: refreshToken }),
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to refresh token');
            }
            return response.json();
        })
        .then(data => {
            if (data.access_token) {
                localStorage.setItem('access_token', data.access_token);
                return data.access_token;
            } else {
                throw new Error('No access token in response');
            }
        })
        .catch(error => {
            console.error('Error refreshing token:', error);
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            window.location.href = '/login/'; // 로그인 페이지로 이동
        });
}

// API 요청 전 토큰 만료 검사
function fetchWithToken(url, options = {}) {
    const accessToken = localStorage.getItem('access_token');

    if (!accessToken) {
        return refreshAccessToken().then(newAccessToken => {
            options.headers = {
                ...options.headers,
                Authorization: `Bearer ${newAccessToken}`,
            };
            return fetch(url, options);
        });
    }

    options.headers = {
        ...options.headers,
        Authorization: `Bearer ${accessToken}`,
    };

    return fetch(url, options).then(response => {
        if (response.status === 401) {
            // Access Token이 만료된 경우
            return refreshAccessToken().then(newAccessToken => {
                options.headers.Authorization = `Bearer ${newAccessToken}`;
                return fetch(url, options);
            });
        }
        return response;
    });
}

document.getElementById('login-form').addEventListener('submit', function (event) {
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
            if (data.refresh_token && data.access_token) {
                localStorage.setItem('access_token', data.access_token);

                // 여러 개의 채팅방일 경우 list로 변경해야 함
                window.location.href = `/home/`;
            } else {
                errorMessage.style.display = 'block';
                errorMessage.textContent = '로그인에 실패했습니다. 다시 시도해주세요.';
            }
        })
        .catch(errorData => {
            // 서버에서 반환된 오류 메시지를 화면에 표시
            console.log(errorData);
            errorMessage.style.display = 'block';
            if (errorData.non_field_errors) {
                errorMessage.textContent = '가입되지 않은 사용자이거나 비밀번호가 잘못되었습니다.';
            } else {
                errorMessage.textContent = '서버에 문제가 발생했습니다. 다시 시도해주세요.';
            }
        });
});
