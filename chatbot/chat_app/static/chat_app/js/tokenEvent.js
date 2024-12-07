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
export function fetchWithToken(url, options = {}) {
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