export const run = () => {
    const messageContainer = document.getElementById("message-container");
    const htmlContent = `
        <h1 class="text-center text-2xl font-bold">Upload PDF</h1>
        <input type="file" id="fileInput" accept=".pdf" style="display: block; margin: 20px auto;">
        <div id="pdfContainer"></div>
        <div id="selectedPages">
            <button id="showSelectedPages">Show Selected Pages</button>
            <button id="showAllPages">Show All Pages</button>
            <button id="downloadSelected">Download Selected Pages</button>
            <p id="result"></p>
        </div>
    `;
    messageContainer.innerHTML = htmlContent;

    // Add PDF container dynamically
    const chatSection = document.querySelector('.flex-col.flex-auto.h-full');
    const pdfContainer = document.createElement('div');
    pdfContainer.id = 'pdfContainer';
    pdfContainer.className = 'mt-4 bg-white p-4 rounded-lg shadow';
    chatSection.appendChild(pdfContainer);

    // File upload event listener
    fileUploadButton.addEventListener('change', handleFileUpload);

    const handleFileUpload = (event) => {
        const file = event.target.files[0];
        if (file && file.type === 'application/pdf') {
            const reader = new FileReader();
            reader.onload = function () {
                renderPDF(reader.result);
            };
            reader.readAsDataURL(file);
        } else {
            alert('Please upload a valid PDF file.');
        }
    };

    const renderPDF = (pdfDataUrl) => {
        const pdfContainer = document.getElementById('pdfContainer');
        pdfContainer.innerHTML = ''; // Clear previous content

        pdfjsLib.getDocument(pdfDataUrl).promise.then((pdf) => {
            for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
                pdf.getPage(pageNum).then((page) => {
                    const canvas = document.createElement('canvas');
                    canvas.className = 'mb-4';
                    const context = canvas.getContext('2d');
                    pdfContainer.appendChild(canvas);

                    const viewport = page.getViewport({ scale: 1.5 });
                    canvas.height = viewport.height;
                    canvas.width = viewport.width;

                    page.render({
                        canvasContext: context,
                        viewport: viewport,
                    });
                });
            }
        });
    };
};