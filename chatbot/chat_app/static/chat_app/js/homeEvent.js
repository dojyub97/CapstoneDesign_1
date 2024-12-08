export function renderHome() {
    window.history.pushState({}, '', `/`);
    const mainContainer = document.getElementById("main-container");
    mainContainer.innerHTML = `
        <div class="flex flex-col flex-auto flex-shrink-0 rounded-2xl bg-gray-100 w-2/3 overflow-x-auto mb-4 items-center">
            <h1 class="text-center text-2xl font-bold">홈화면</h1>
        </div>
        `;
}