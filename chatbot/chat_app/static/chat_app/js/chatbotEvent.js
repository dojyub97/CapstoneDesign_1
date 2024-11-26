import { renderHome } from "./homeEvent.js"
import { renderSchoolInfo } from "./schoolEvent.js";
import { renderPDFGenerator } from "./pdfEvent.js";

let token = null;

document.addEventListener("DOMContentLoaded", () => {
    const token = localStorage.getItem("access_token");
    if (!token) {
        console.error("No access token found. Please log in again.");
        return;
    }

    document.getElementById("home-button").addEventListener("click", renderHome);
    document.getElementById("school-button").addEventListener("click", renderSchoolInfo);
    document.getElementById("pdf-button").addEventListener("click", renderPDFGenerator);
});