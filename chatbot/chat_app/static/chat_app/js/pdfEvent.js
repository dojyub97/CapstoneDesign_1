import { fetchWithToken } from "./tokenEvent.js";

export function renderPDFGenerator() {
    let topic = "pdf-QnA";
    let currentChatroomId = null;
    window.history.pushState({}, '', `/${topic}/`);

    fetchWithToken(`/api/chatroom/${topic}/`, {
        method: "GET",
    })
        .then(response => response.json())
        .then(data => {
            currentChatroomId = data.chatroom_id;
            // 문제생성 container
            const mainContainer = document.getElementById("main-container");
            mainContainer.innerHTML = `
                <div id="pdf-container" class="flex flex-col flex-grow basis-1/3 min-w-[400px] overflow-x-hidden bg-gray-100 rounded-lg p-4">
                    <h2 class="text-lg font-bold mb-4 text-gray-700">Upload PDF</h2>
                    <div class="flex flex-col space-y-2 overflow-y-auto border-2 border-dashed border-gray-300 rounded-lg p-6 text-center cursor-pointer">
                        <label for="pdf-upload" class="block text-gray-500">
                            <i class="fas fa-file-upload text-gray-400 text-3xl mb-2"></i>
                            <span>Upload PDF</span>
                        </label>
                        <input id="pdf-upload" type="file" accept="application/pdf" class="hidden" />
                        <div id="pdf-preview" class="flex flex-col mt-4 space-y-4 overflow-y-auto">
                        </div>
                        <button id="process-pages" class="hidden mt-4 bg-indigo-500 hover:bg-indigo-600 text-white py-2 rounded-lg border border-gray-200">
                                Process Selected Pages
                        </button>
                        <button id="delete-file" class="hidden mt-4 bg-red-500 hover:bg-red-600 text-white py-2 px-4 rounded-lg border border-gray-200">
                                Delete PDF
                        </button>
                    </div>
                </div>

                <!-- Chat Section -->
                <div id="chat-container" class="flex flex-col flex-grow basis-2/3 min-w-[700px] overflow-x-hidden bg-gray-100 rounded-lg p-4">
                    <div id="message-container" class="flex flex-col w-full h-full overflow-y-auto overflow-x-hidden mb-4 break-words hide-scrollbar">
                        <!-- Messages will appear here dynamically -->
                    </div>
                    <!-- Input section -->
                    <div class="flex flex-row items-center h-16 rounded-xl bg-white w-full px-4 mt-4 ">
                        <div class="flex-grow ml-4">
                            <input id="chat-input" type="text" placeholder="Type a message..." class="flex w-full border rounded-xl focus:outline-none focus:border-indigo-300 pl-4 h-10" />
                        </div>
                        <div class="ml-4">
                            <button id="send-button" class="flex items-center justify-center bg-indigo-500 hover:bg-indigo-600 rounded-xl text-white px-4 py-1">
                                <span>Send</span>
                                <span class="ml-2">
                                    <svg class="w-4 h-4 transform rotate-45 -mt-px" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path>
                                </svg>
                                </span>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            `;
            setupPDFUpload();
        })
        .catch(error => console.error("Error loading chatroom:", error));

    // pdf file 업로드 함수(pdf-container)
    function setupPDFUpload() {
        const pdfUploadInput = document.getElementById("pdf-upload");
        const pdfPreview = document.getElementById("pdf-preview");
        const pdfLabel = document.querySelector("label[for='pdf-upload']");
        const processPagesButton = document.getElementById("process-pages");
        const deleteButton = document.getElementById("delete-file");

        let loadPdf = null;
        let selectedPagesText = {};
        let fileName = null;

        // pdf file upload event
        pdfUploadInput.addEventListener("change", async (event) => {
            const file = event.target.files[0];
            if (file && file.type === "application/pdf") {
                // Label 숨기기
                pdfLabel.classList.add("hidden");

                // 새로운 PDF를 업로드할 때 selectedPagesText 초기화
                selectedPagesText = {}; 

                // pdf file read->load
                fileName = file.name;
                const reader = new FileReader();
                reader.onload = async function (e) {
                    const typeArray = new Uint8Array(e.target.result);
                    const pdfjsLib = window['pdfjs-dist/build/pdf'];
                    pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.16.105/pdf.worker.min.js';
                    loadPdf = await pdfjsLib.getDocument(typeArray).promise;

                    pdfPreview.innerHTML = "";

                    // render each pdf page
                    for (let i = 1; i <= loadPdf.numPages; i++) {
                        const currentPage = await loadPdf.getPage(i);
                        const viewport = currentPage.getViewport({ scale: 0.5 });
                        // Render canvas
                        const canvas = document.createElement("canvas");
                        canvas.className = "flex flex-col mb-4 shadow border rounded max-w-full h-auto";
                        canvas.height = viewport.height;
                        canvas.width = viewport.width;
                        const context = canvas.getContext("2d");
                        await currentPage.render({ canvasContext: context, viewport: viewport }).promise;
                        // 파일 미리보기(pdf-preview)
                        const pagePreview = document.createElement("div");
                        pagePreview.className = "flex items-center justify-between mb-2 border p-2 rounded-lg bg-white ";
                        const pageLabel = document.createElement("label");
                        pageLabel.className = "flex items-center cursor-pointer";
                        pageLabel.innerHTML = `
                            <input type="checkbox" class="mr-2" data-page="${i}" />
                            <span>Page ${i}</span>
                        `;
                        pagePreview.appendChild(canvas);
                        pagePreview.appendChild(pageLabel);
                        pdfPreview.appendChild(pagePreview);

                        // Extract text for selected pages
                        const pageText = await extractPageText(currentPage);
                        selectedPagesText[i] = pageText;
                    }
                };
                reader.readAsArrayBuffer(file);

                // processPagesButton & deleteBUtton 활성화
                processPagesButton.classList.remove("hidden");
                deleteButton.classList.remove("hidden")
            }
        });

        // pdf page의 text 추출 함수
        async function extractPageText(currentPage) {
            const textContent = await currentPage.getTextContent();
            return textContent.items.map((item) => item.str).join(" ");
        }

        // Delete pdf file
        deleteButton.addEventListener("click", () => {
            // PDF 미리보기 삭제
            pdfPreview.innerHTML = "";
            pdfUploadInput.value = null;
            // Label 다시 표시
            pdfLabel.classList.remove("hidden");
            // processPagesButton 숨기기
            processPagesButton.classList.add("hidden");
            deleteButton.classList.add("hidden");
        });

        // Event handling: extracted pdf text + user message handling
        // process page button을 클릭한 후에 사용자 입력을 받을 수 있도록 함
        processPagesButton.addEventListener("click", () => {
            // 기존 이벤트 리스너 제거
            processPagesButton.replaceWith(processPagesButton.cloneNode(true))

            const checkboxes = pdfPreview.querySelectorAll("input[type='checkbox']:checked");
            const selectedPages = Array.from(checkboxes).map(checkbox => parseInt(checkbox.dataset.page));

            if (selectedPages.length === 0) {
                alert("Please select at least one page to process.");
                return;
            }

            // Set으로 중복 제거 및 텍스트 결합
            const uniquePages = [...new Set(selectedPages)];
            const selectedText = uniquePages.map((page) => selectedPagesText[page]).join("\n\n");

            // Store extracted text for later API submission
            document.getElementById("send-button").onclick = function () {
                sendMessage(selectedText);
            };
            document.getElementById('chat-input').addEventListener('keypress', function (event) {
                if (event.key === 'Enter' && !event.shiftKey) {
                    event.preventDefault(); // 기본 엔터 동작 방지
                    sendMessage(selectedText);
                }
            });

            // send user message
            function sendMessage(selectedText) {
                const chatInputElement = document.getElementById("chat-input");
                const chatInputValue = chatInputElement.value.trim();
                if (chatInputValue === '') return; // 빈 메시지 전송 방지

                displayMessage("user", chatInputValue);
                chatInputElement.value = "";

                fetchWithToken(`/api/${topic}/${currentChatroomId}/`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        "chat_data": {
                            "chatroom_id": currentChatroomId,
                            "sender": "user",
                            "text": chatInputValue
                        },
                        "file_data": {
                            "file_name": fileName,
                            "content": selectedText
                        }
                    }),
                })
                    .then(response => response.json())
                    .then(data => {
                        const botMessage = data.sender ? data.text : "No response from bot.";
                        displayMessage(data.sender, botMessage);
                    })
                    .catch(error => console.error("Error:", error));
            }

            function convertNewlinesToBr(inputText) {
                // Replace all \n with <br>
                return inputText.replace(/\n/g, '<br>');
            }

            // display에 chatting message 출력
            function displayMessage(sender, message) {
                const messageElement = document.createElement("div");
                const messageContainer = document.getElementById("message-container");

                const output_message=convertNewlinesToBr(message);


                if (sender === "user") {
                    messageElement.className = "flex justify-end mb-4";
                    messageElement.innerHTML = `
                    <div class="mr-2 ml-5 py-3 px-4 bg-indigo-100 text-gray-800 rounded-xl max-w-[calc(100%-2rem)] break-all overflow-y-auto">${output_message}</div>
                    <div class="flex-shrink-0 flex items-center justify-center h-10 w-10 rounded-full bg-indigo-500 text-white">U</div>
                `;
                } else if (sender === "system") {
                    messageElement.className = "flex items-start mb-4";
                    messageElement.innerHTML = `
                    <div class="flex-shrink-0 flex items-center justify-center h-10 w-10 rounded-full bg-indigo-500 text-white">B</div>
                    <div class="ml-2 mr-5 py-3 px-4 bg-gray-200 rounded-xl max-w-[calc(100%-2rem)] break-all overflow-y-auto">${output_message}</div>
                `;
                }

                messageContainer.appendChild(messageElement);
                messageContainer.scrollTop = messageContainer.scrollHeight;
            }
        });
    }

}