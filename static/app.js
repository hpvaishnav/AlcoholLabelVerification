// TTB Label Compliance Review Assistant - Accessible UI App Logic (Spinner & Disabled Button State)

let selectedImageFile = null;
let selectedCsvFile = null;

let selectedBatchImageFiles = [];
let selectedBatchZipFile = null;
let selectedBatchCsvFile = null;

let activeBatchJobId = null;
let batchPollInterval = null;
let activeBatchResults = [];
let currentBatchFilter = "ALL";
let auditOverridesList = [];
let allSampleCases = [];

document.addEventListener("DOMContentLoaded", () => {
    fetchSampleCases();
});

async function fetchSampleCases() {
    try {
        const res = await fetch("/api/sample-data");
        const data = await res.json();
        allSampleCases = data.sample_cases || [];
        populateAdminScenarioMenus();
    } catch (err) {
        console.error("Failed to fetch 50 sample cases:", err);
    }
}

function populateAdminScenarioMenus() {
    const passMenu = document.getElementById("pass-scenarios-menu");
    const failMenu = document.getElementById("fail-scenarios-menu");
    const reviewMenu = document.getElementById("review-scenarios-menu");
    const warnMenu = document.getElementById("warning-scenarios-menu");

    if (!passMenu || allSampleCases.length === 0) return;

    passMenu.innerHTML = "";
    failMenu.innerHTML = "";
    reviewMenu.innerHTML = "";
    warnMenu.innerHTML = "";

    allSampleCases.forEach(item => {
        const btn = document.createElement("button");
        btn.className = "dropdown-item scenario-item";
        btn.innerText = item.scenario_title;
        btn.onclick = () => loadDemoScenario(item.scenario_id);

        if (item.scenario_id.startsWith("pass")) {
            passMenu.appendChild(btn);
        } else if (item.scenario_id.startsWith("fail")) {
            failMenu.appendChild(btn);
        } else if (item.scenario_id.startsWith("caps")) {
            reviewMenu.appendChild(btn);
        } else if (item.scenario_id.startsWith("warning")) {
            warnMenu.appendChild(btn);
        }
    });
}

// Mode Toggle Switch (Single vs Batch)
function setMode(mode) {
    document.getElementById("btn-mode-single").classList.remove("active");
    document.getElementById("btn-mode-batch").classList.remove("active");
    document.getElementById("mode-single-section").classList.remove("active");
    document.getElementById("mode-batch-section").classList.remove("active");

    if (mode === "single") {
        document.getElementById("btn-mode-single").classList.add("active");
        document.getElementById("mode-single-section").classList.add("active");
    } else {
        document.getElementById("btn-mode-batch").classList.add("active");
        document.getElementById("mode-batch-section").classList.add("active");
    }
}

// Admin Dropdown Menu Toggle
function toggleAdminMenu() {
    const box = document.getElementById("admin-dropdown-box");
    box.classList.toggle("hidden");
}

document.addEventListener("click", (e) => {
    const container = document.querySelector(".admin-menu-container");
    if (container && !container.contains(e.target)) {
        document.getElementById("admin-dropdown-box").classList.add("hidden");
    }
});

// Single File Selection Handlers
function handleImageSelect(event) {
    const file = event.target.files[0];
    if (file) {
        selectedImageFile = file;
        document.getElementById("img-file-label").innerText = `📷 Selected Image: ${file.name}`;
    }
}

function handleCsvSelect(event) {
    const file = event.target.files[0];
    if (file) {
        selectedCsvFile = file;
        document.getElementById("csv-file-label").innerText = `📄 Selected CSV: ${file.name}`;
    }
}

// Batch File Selection Handlers (Multiple Images / ZIP / CSV)
function handleBatchImagesSelect(event) {
    const files = Array.from(event.target.files);
    if (!files || files.length === 0) return;

    selectedBatchImageFiles = [];
    selectedBatchZipFile = null;

    if (files.length === 1 && files[0].name.toLowerCase().endsWith(".zip")) {
        selectedBatchZipFile = files[0];
        document.getElementById("batch-images-label").innerText = `📦 Selected ZIP Archive: ${files[0].name}`;
    } else {
        selectedBatchImageFiles = files;
        document.getElementById("batch-images-label").innerText = `📁 Selected ${files.length} Image File(s)`;
    }
}

function handleBatchCsvSelect(event) {
    const file = event.target.files[0];
    if (file) {
        selectedBatchCsvFile = file;
        document.getElementById("batch-csv-label").innerText = `📄 Selected Batch CSV: ${file.name}`;
    }
}

// User Single Upload Submission with Loading Spinner & Button Disabling
async function submitUserSingleUpload() {
    if (!selectedImageFile) {
        alert("Please select a label artwork image file to verify.");
        return;
    }

    const btn = document.getElementById("btn-single-verify");
    const spinner = document.getElementById("spinner-single");
    const btnText = document.getElementById("btn-single-text");
    const loadingCard = document.getElementById("single-loading-card");
    const resultsSection = document.getElementById("results-section");

    btn.disabled = true;
    spinner.classList.remove("hidden");
    btnText.innerText = "⏳ Running Verification...";
    loadingCard.classList.remove("hidden");
    resultsSection.classList.add("hidden");

    const formData = new FormData();
    formData.append("image", selectedImageFile);
    if (selectedCsvFile) {
        formData.append("metadata_csv", selectedCsvFile);
    }

    try {
        const verifyRes = await fetch("/api/verify-single", {
            method: "POST",
            body: formData
        });
        const evalData = await verifyRes.json();
        
        const reader = new FileReader();
        reader.onload = (e) => {
            document.getElementById("label-image-view").src = e.target.result;
        };
        reader.readAsDataURL(selectedImageFile);

        document.getElementById("single-app-id").innerText = evalData.application_id || selectedImageFile.name;
        renderSingleResults(evalData, "User uploaded artwork verification.");

    } catch (err) {
        console.error("Error submitting single upload:", err);
        alert("Verification failed. Please check image file.");
    } finally {
        btn.disabled = false;
        spinner.classList.add("hidden");
        btnText.innerText = "🔍 Run Compliance Verification";
        loadingCard.classList.add("hidden");
    }
}

// Submit Batch File Upload (Images / ZIP / CSV)
async function submitBatchUpload() {
    if (selectedBatchImageFiles.length === 0 && !selectedBatchZipFile && !selectedBatchCsvFile) {
        alert("Please select multiple label images, a ZIP archive, or a CSV file to run batch verification.");
        return;
    }

    const btn = document.getElementById("btn-batch-verify");
    const spinner = document.getElementById("spinner-batch");
    const btnText = document.getElementById("btn-batch-text");

    btn.disabled = true;
    spinner.classList.remove("hidden");
    btnText.innerText = "⏳ Submitting Batch Job...";

    currentBatchFilter = "ALL";
    updateFilterTileVisuals();
    document.getElementById("batch-progress-box").classList.remove("hidden");
    const formData = new FormData();

    if (selectedBatchZipFile) {
        formData.append("zip_file", selectedBatchZipFile);
    } else if (selectedBatchImageFiles.length > 0) {
        selectedBatchImageFiles.forEach(file => {
            formData.append("images", file);
        });
    }

    if (selectedBatchCsvFile) {
        formData.append("csv_file", selectedBatchCsvFile);
    }

    try {
        const startRes = await fetch("/api/verify-batch", {
            method: "POST",
            body: formData
        });
        const startData = await startRes.json();

        if (startRes.status !== 200) {
            alert(startData.detail || "Batch submission failed.");
            return;
        }

        activeBatchJobId = startData.job_id;

        if (batchPollInterval) clearInterval(batchPollInterval);
        batchPollInterval = setInterval(pollBatchProgress, 300);

    } catch (err) {
        console.error("Failed to run batch upload:", err);
    } finally {
        btn.disabled = false;
        spinner.classList.add("hidden");
        btnText.innerText = "🚀 Start Batch Processing";
    }
}

// Load Specific Demo Scenario (from 50 Scenarios)
async function loadDemoScenario(scenarioId) {
    document.getElementById("admin-dropdown-box").classList.add("hidden");
    setMode("single");

    const loadingCard = document.getElementById("single-loading-card");
    const resultsSection = document.getElementById("results-section");

    loadingCard.classList.remove("hidden");
    resultsSection.classList.add("hidden");

    try {
        const targetCase = allSampleCases.find(c => c.scenario_id === scenarioId || c.application_id.toLowerCase() === scenarioId.toLowerCase()) || allSampleCases[0];

        document.getElementById("single-app-id").innerText = targetCase.application_id;
        document.getElementById("label-image-view").src = targetCase.image_url;

        const formData = new FormData();
        formData.append("sample_filename", targetCase.image_filename);
        formData.append("metadata_json", JSON.stringify(targetCase));

        const verifyRes = await fetch("/api/verify-single", {
            method: "POST",
            body: formData
        });
        const evalData = await verifyRes.json();
        renderSingleResults(evalData, targetCase.demo_description);

    } catch (err) {
        console.error("Error loading scenario:", err);
    } finally {
        loadingCard.classList.add("hidden");
    }
}

// Inspect Specific Batch Item Result in Overlay Modal
function inspectBatchItem(index) {
    const res = activeBatchResults[index];
    if (!res) return;

    document.getElementById("inspect-app-id").innerText = res.application_id;

    if (res.image_url) {
        document.getElementById("inspect-image-view").src = res.image_url;
    } else if (res.image_filename) {
        document.getElementById("inspect-image-view").src = `/labels/${res.image_filename}`;
    }

    renderInspectResults(res);
    document.getElementById("inspect-modal").classList.remove("hidden");
}

function closeInspectModal() {
    document.getElementById("inspect-modal").classList.add("hidden");
}

// Filter Batch Table by clicking Stat Tiles (PASS, NEEDS REVIEW, REJECT, ALL)
function filterBatchTable(statusFilter) {
    if (currentBatchFilter === statusFilter) {
        currentBatchFilter = "ALL";
    } else {
        currentBatchFilter = statusFilter;
    }

    updateFilterTileVisuals();
    renderBatchTable(activeBatchResults);
}

function updateFilterTileVisuals() {
    const passCard = document.getElementById("stat-card-pass");
    const reviewCard = document.getElementById("stat-card-review");
    const rejectCard = document.getElementById("stat-card-reject");
    const resetBtn = document.getElementById("filter-reset-btn");
    const titleText = document.getElementById("table-filter-title");

    passCard.classList.remove("active-filter");
    reviewCard.classList.remove("active-filter");
    rejectCard.classList.remove("active-filter");

    if (currentBatchFilter === "PASS") {
        passCard.classList.add("active-filter");
        titleText.innerText = "Batch Review Findings Table (Filtered: Passing Items Only)";
        resetBtn.classList.remove("hidden");
    } else if (currentBatchFilter === "NEEDS REVIEW") {
        reviewCard.classList.add("active-filter");
        titleText.innerText = "Batch Review Findings Table (Filtered: Needs Human Review Only)";
        resetBtn.classList.remove("hidden");
    } else if (currentBatchFilter === "REJECT") {
        rejectCard.classList.add("active-filter");
        titleText.innerText = "Batch Review Findings Table (Filtered: Rejected Items Only)";
        resetBtn.classList.remove("hidden");
    } else {
        titleText.innerText = "Batch Review Findings Table (All Items)";
        resetBtn.classList.add("hidden");
    }
}

// Render Results inside the Inspect Overlay Modal (Focuses & Highlights First Rejected/Review Item)
function renderInspectResults(evalData) {
    const banner = document.getElementById("inspect-status-banner");
    const icon = document.getElementById("inspect-banner-icon");
    const statusText = document.getElementById("inspect-banner-status-text");
    const summaryText = document.getElementById("inspect-banner-summary-text");
    const speedTag = document.getElementById("inspect-speed-tag");

    speedTag.innerText = `Processing Speed: ${evalData.processing_time_seconds || evalData.item_processing_time || 0.18}s`;

    banner.className = "giant-banner";

    if (evalData.overall_status === "PASS") {
        banner.classList.add("banner-pass");
        icon.innerText = "✓";
        statusText.innerText = "PASS - FULLY COMPLIANT";
    } else if (evalData.overall_status === "REJECT") {
        banner.classList.add("banner-reject");
        icon.innerText = "✕";
        statusText.innerText = "REJECT - REGULATORY/METADATA MISMATCH";
    } else {
        banner.classList.add("banner-review");
        icon.innerText = "👁";
        statusText.innerText = "NEEDS REVIEW - HUMAN AGENT ATTENTION REQUIRED";
    }

    summaryText.innerText = evalData.summary_reason;

    const container = document.getElementById("inspect-fields-matrix-container");
    container.innerHTML = "";

    const fieldDisplayNames = {
        "brand_name": "Brand Name",
        "class_type": "Class / Type",
        "alcohol_content": "Alcohol Content",
        "proof": "Proof",
        "net_contents": "Net Contents",
        "bottler_producer": "Bottler / Producer",
        "country_of_origin": "Country of Origin",
        "government_warning": "Government Warning (27 CFR 16)"
    };

    let firstFocusCard = null;

    Object.keys(fieldDisplayNames).forEach(key => {
        const fieldData = evalData.field_results[key];
        if (!fieldData) return;

        let badgeClass = "badge-pass";
        let isFocus = false;

        if (fieldData.status === "REJECT") {
            badgeClass = "badge-reject";
            if (!firstFocusCard) isFocus = true;
        } else if (fieldData.status === "NEEDS REVIEW") {
            badgeClass = "badge-review";
            if (!firstFocusCard && evalData.overall_status !== "REJECT") isFocus = true;
        }

        const card = document.createElement("div");
        card.className = "field-card";

        if (isFocus) {
            card.classList.add("focused-rejected-card");
            firstFocusCard = card;
        }

        card.innerHTML = `
            <div class="field-header">
                <span class="field-name">${fieldDisplayNames[key]}</span>
                <span class="field-badge ${badgeClass}">${fieldData.status}</span>
            </div>
            <div class="field-body">
                <div>
                    <div class="value-label">Application Metadata:</div>
                    <div class="value-box">${fieldData.expected}</div>
                </div>
                <div>
                    <div class="value-label">Extracted Label Artwork Text:</div>
                    <div class="value-box">${fieldData.extracted}</div>
                </div>
            </div>
            <div class="field-footer">
                <span>Confidence: ${Math.round(fieldData.confidence * 100)}% | ${fieldData.explanation}</span>
                <button class="btn-override" onclick="openOverrideModal('${evalData.application_id}', '${fieldDisplayNames[key]}', '${fieldData.status}')">Override</button>
            </div>
        `;
        container.appendChild(card);
    });

    if (firstFocusCard) {
        setTimeout(() => {
            firstFocusCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }, 150);
    }
}

// Render Single Results & Reveal Results Section (for Single Review mode)
function renderSingleResults(evalData, demoDesc) {
    document.getElementById("results-section").classList.remove("hidden");

    const banner = document.getElementById("giant-status-banner");
    const icon = document.getElementById("banner-icon");
    const statusText = document.getElementById("banner-status-text");
    const summaryText = document.getElementById("banner-summary-text");
    const speedTag = document.getElementById("single-speed-tag");

    speedTag.innerText = `Processing Speed: ${evalData.processing_time_seconds || evalData.item_processing_time || 0.18}s`;

    banner.className = "giant-banner";

    if (evalData.overall_status === "PASS") {
        banner.classList.add("banner-pass");
        icon.innerText = "✓";
        statusText.innerText = "PASS - FULLY COMPLIANT";
    } else if (evalData.overall_status === "REJECT") {
        banner.classList.add("banner-reject");
        icon.innerText = "✕";
        statusText.innerText = "REJECT - REGULATORY/METADATA MISMATCH";
    } else {
        banner.classList.add("banner-review");
        icon.innerText = "👁";
        statusText.innerText = "NEEDS REVIEW - HUMAN AGENT ATTENTION REQUIRED";
    }

    summaryText.innerText = demoDesc || evalData.summary_reason;

    const container = document.getElementById("fields-matrix-container");
    container.innerHTML = "";

    const fieldDisplayNames = {
        "brand_name": "Brand Name",
        "class_type": "Class / Type",
        "alcohol_content": "Alcohol Content",
        "proof": "Proof",
        "net_contents": "Net Contents",
        "bottler_producer": "Bottler / Producer",
        "country_of_origin": "Country of Origin",
        "government_warning": "Government Warning (27 CFR 16)"
    };

    let firstFocusCard = null;

    Object.keys(fieldDisplayNames).forEach(key => {
        const fieldData = evalData.field_results[key];
        if (!fieldData) return;

        let badgeClass = "badge-pass";
        let isFocus = false;

        if (fieldData.status === "REJECT") {
            badgeClass = "badge-reject";
            if (!firstFocusCard) isFocus = true;
        } else if (fieldData.status === "NEEDS REVIEW") {
            badgeClass = "badge-review";
            if (!firstFocusCard && evalData.overall_status !== "REJECT") isFocus = true;
        }

        const card = document.createElement("div");
        card.className = "field-card";

        if (isFocus) {
            card.classList.add("focused-rejected-card");
            firstFocusCard = card;
        }

        card.innerHTML = `
            <div class="field-header">
                <span class="field-name">${fieldDisplayNames[key]}</span>
                <span class="field-badge ${badgeClass}">${fieldData.status}</span>
            </div>
            <div class="field-body">
                <div>
                    <div class="value-label">Application Metadata:</div>
                    <div class="value-box">${fieldData.expected}</div>
                </div>
                <div>
                    <div class="value-label">Extracted Label Artwork Text:</div>
                    <div class="value-box">${fieldData.extracted}</div>
                </div>
            </div>
            <div class="field-footer">
                <span>Confidence: ${Math.round(fieldData.confidence * 100)}% | ${fieldData.explanation}</span>
                <button class="btn-override" onclick="openOverrideModal('${evalData.application_id}', '${fieldDisplayNames[key]}', '${fieldData.status}')">Override</button>
            </div>
        `;
        container.appendChild(card);
    });

    document.getElementById("results-section").scrollIntoView({ behavior: 'smooth' });

    if (firstFocusCard) {
        setTimeout(() => {
            firstFocusCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }, 200);
    }
}

// 50-Item Bulk Batch Demo Trigger
async function loadDemoBatchDemo() {
    document.getElementById("admin-dropdown-box").classList.add("hidden");
    setMode("batch");
    currentBatchFilter = "ALL";
    updateFilterTileVisuals();
    document.getElementById("batch-progress-box").classList.remove("hidden");

    try {
        const headers = ["application_id", "brand_name", "class_type", "alcohol_content", "proof", "net_contents", "bottler_producer", "country_of_origin", "government_warning", "image_filename"];
        let csvRows = [headers.join(",")];
        allSampleCases.forEach(base => {
            const row = [
                base.application_id,
                `"${base.brand_name}"`,
                `"${base.class_type}"`,
                `"${base.alcohol_content}"`,
                `"${base.proof}"`,
                `"${base.net_contents}"`,
                `"${base.bottler_producer}"`,
                `"${base.country_of_origin}"`,
                `"${base.government_warning}"`,
                `"${base.image_filename}"`
            ];
            csvRows.push(row.join(","));
        });

        const blob = new Blob([csvRows.join("\n")], { type: "text/csv" });
        const formData = new FormData();
        formData.append("csv_file", blob, "applications_metadata.csv");

        const startRes = await fetch("/api/verify-batch", {
            method: "POST",
            body: formData
        });
        const startData = await startRes.json();
        activeBatchJobId = startData.job_id;

        if (batchPollInterval) clearInterval(batchPollInterval);
        batchPollInterval = setInterval(pollBatchProgress, 300);

    } catch (err) {
        console.error("Failed to run 50-item demo batch:", err);
    }
}

async function pollBatchProgress() {
    if (!activeBatchJobId) return;

    try {
        const res = await fetch(`/api/batch-status/${activeBatchJobId}`);
        const data = await res.json();

        document.getElementById("batch-status-text").innerText = `Status: ${data.status}`;
        document.getElementById("batch-speed-text").innerText = `Processing Speed: ${data.average_time_per_label || 0.05}s / label`;

        const pct = Math.round((data.processed_items / data.total_items) * 100);
        document.getElementById("batch-progress-fill").style.width = `${pct}%`;

        document.getElementById("stat-pass").innerText = data.passed_count;
        document.getElementById("stat-review").innerText = data.review_count;
        document.getElementById("stat-reject").innerText = data.rejected_count;

        activeBatchResults = data.results || [];
        renderBatchTable(activeBatchResults);

        if (data.status === "COMPLETED") {
            clearInterval(batchPollInterval);
        }

    } catch (err) {
        console.error("Error polling batch progress:", err);
    }
}

function renderBatchTable(results) {
    const tbody = document.getElementById("batch-table-body");
    if (!results || results.length === 0) return;

    tbody.innerHTML = "";
    
    let filteredList = results;
    if (currentBatchFilter !== "ALL") {
        filteredList = results.filter(item => item.overall_status === currentBatchFilter);
    }

    if (filteredList.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" class="text-center">No batch items found with status '${currentBatchFilter}'.</td></tr>`;
        return;
    }

    filteredList.forEach((res) => {
        const originalIndex = activeBatchResults.indexOf(res);
        let badgeClass = "badge-pass";
        if (res.overall_status === "REJECT") badgeClass = "badge-reject";
        else if (res.overall_status === "NEEDS REVIEW") badgeClass = "badge-review";

        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td><strong>${res.application_id}</strong></td>
            <td><span class="field-badge ${badgeClass}">${res.overall_status}</span></td>
            <td>${res.summary_reason}</td>
            <td>${res.processing_time_seconds || res.item_processing_time || 0.05}s</td>
            <td><button class="btn-override" onclick="inspectBatchItem(${originalIndex})">Inspect</button></td>
        `;
        tbody.appendChild(tr);
    });
}

// Admin Modal Display Logic
async function openAdminModal(tab) {
    document.getElementById("admin-dropdown-box").classList.add("hidden");
    const modal = document.getElementById("admin-modal");
    const title = document.getElementById("admin-modal-title");
    const content = document.getElementById("admin-modal-content");
    modal.classList.remove("hidden");

    if (tab === "config") {
        title.innerText = "📋 System Configuration";
        const res = await fetch("/api/config");
        const data = await res.json();
        content.innerHTML = `
            <div style="font-size: 1rem; line-height: 1.8;">
                <p><strong>App Name:</strong> ${data.app_name}</p>
                <p><strong>OCR Engine Mode:</strong> <span style="color: #38bdf8;">${data.ocr_mode}</span></p>
                <p><strong>Target Processing Time:</strong> ${data.target_processing_time}</p>
                <p><strong>Fuzzy Pass Threshold:</strong> ${data.fuzzy_pass_threshold * 100}%</p>
                <p><strong>Fuzzy Review Threshold:</strong> ${data.fuzzy_review_threshold * 100}%</p>
            </div>
        `;
    } else if (tab === "bom") {
        title.innerText = "📦 Software Bill of Materials (BOM) & Licenses";
        const res = await fetch("/api/config");
        const data = await res.json();
        let rows = data.bom_summary.map(item => `
            <tr>
                <td><strong>${item.library}</strong></td>
                <td><code>${item.version}</code></td>
                <td><span class="field-badge badge-pass">${item.license}</span></td>
                <td>Approved (Federal Compliance Audited)</td>
            </tr>
        `).join("");

        content.innerHTML = `
            <table class="simple-table">
                <thead>
                    <tr><th>Library</th><th>Version</th><th>License</th><th>Compliance Status</th></tr>
                </thead>
                <tbody>${rows}</tbody>
            </table>
        `;
    } else if (tab === "docs") {
        title.innerText = "📖 System Documentation";
        const res = await fetch("/REQUIREMENTS.md");
        const text = await res.text();
        content.innerHTML = `<pre style="font-family: var(--font-mono); font-size: 0.85rem; white-space: pre-wrap; background: #090f1d; padding: 1rem; border-radius: 8px;">${text}</pre>`;
    } else if (tab === "audit") {
        title.innerText = "📜 Human Override Audit Log";
        if (auditOverridesList.length === 0) {
            content.innerHTML = `<p style="text-align: center; padding: 2rem;">No human agent overrides recorded in current session.</p>`;
        } else {
            let rows = auditOverridesList.map(item => `
                <tr>
                    <td><strong>${item.application_id}</strong></td>
                    <td>${item.field_name}</td>
                    <td><span class="field-badge badge-pass">${item.new_status}</span></td>
                    <td>${item.reason}</td>
                </tr>
            `).join("");
            content.innerHTML = `
                <table class="simple-table">
                    <thead>
                        <tr><th>App ID</th><th>Field</th><th>Overridden Status</th><th>Rationale</th></tr>
                    </thead>
                    <tbody>${rows}</tbody>
                </table>
            `;
        }
    }
}

function closeAdminModal() {
    document.getElementById("admin-modal").classList.add("hidden");
}

function openOverrideModal(appId, fieldName, currentStatus) {
    document.getElementById("modal-app-id").innerText = appId;
    document.getElementById("modal-field-name").innerText = fieldName;
    document.getElementById("override-modal").classList.remove("hidden");
}

function closeModal() {
    document.getElementById("override-modal").classList.add("hidden");
}

async function submitOverride() {
    const appId = document.getElementById("modal-app-id").innerText;
    const fieldName = document.getElementById("modal-field-name").innerText;
    const newStatus = document.getElementById("modal-new-status").value;
    const reason = document.getElementById("modal-reason").value;

    if (!reason.trim()) {
        alert("Please enter a reason for the human agent override.");
        return;
    }

    try {
        const res = await fetch("/api/override", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                application_id: appId,
                field_name: fieldName,
                previous_status: "AUTOMATED",
                new_status: newStatus,
                reason: reason
            })
        });

        const data = await res.json();
        auditOverridesList.push(data.audit_record);
        closeModal();
        alert(`Override saved into audit trail for field '${fieldName}'.`);

    } catch (err) {
        console.error("Failed to submit override:", err);
    }
}

function exportBatch(format) {
    if (!activeBatchJobId) {
        alert("No batch job executed yet. Please run a batch first.");
        return;
    }
    window.location.href = `/api/export/${activeBatchJobId}/${format}`;
}
