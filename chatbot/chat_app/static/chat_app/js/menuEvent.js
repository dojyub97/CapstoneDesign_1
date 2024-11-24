document.addEventListener("DOMContentLoaded", () => {
    // 각 버튼 ID와 해당 모듈 매핑
    const menuModules = {
        "home-button": "./modules/home.js",
        "school-button": "./modules/school.js",
        "pdf-button": "./modules/pdf.js",
    };

    // 모든 버튼에 클릭 이벤트 추가
    Object.keys(menuModules).forEach((buttonId) => {
        const button = document.getElementById(buttonId);

        if (button) {
            button.addEventListener("click", async () => {
                try {
                    const modulePath = menuModules[buttonId];
                    const module = await import(modulePath);
                    document.getElementById('message-container').innerHTML = ''; // 초기화
                    window.history.pushState({}, '', `/${buttonId}/`);
                    module.run(); // 각 모듈의 공통 실행 함수 호출
                } catch (error) {
                    console.error(`Failed to load module for ${buttonId}`, error);
                }
            });
        }
    });
});
