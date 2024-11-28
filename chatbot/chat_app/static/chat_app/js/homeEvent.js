export function renderHome() {
    window.history.pushState({}, '', `/`);
    const mainContainer = document.getElementById("main-container");
    mainContainer.innerHTML = `
    <div class="flex flex-col w-full h-full flex-auto flex-shrink-0 rounded-2xl bg-gray-100 overflow-x-auto mb-4 items-center justify-center">
        <h1 class="text-center text-2xl font-bold">홈화면test</h1>
    </div>
        `;
}