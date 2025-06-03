let backend = null;
let openFiles = new Set(); // Track currently open files
let searchTimeout = null;
const DEBOUNCE_DELAY = 300; // milliseconds

// Connect to the Python backend when page loads
document.addEventListener("DOMContentLoaded", () => {
    // Connect to the Python backend
    new QWebChannel(qt.webChannelTransport, function (channel) {
        backend = channel.objects.backend;
        console.log("Backend connected successfully");
        
    });

    // UI Elements
    const uploadBtn = document.getElementById("uploadBtn");
    const viewBtn = document.getElementById("viewBtn");
    const uploadSection = document.getElementById("uploadSection");
    const viewSection = document.getElementById("viewSection");
    const dropZone = document.getElementById("dropZone");
    const fileInput = document.getElementById("fileInput");
    const fileUploadStatus = document.getElementById("fileUploadStatus");
    const searchInput = document.getElementById("searchInput");
    const anomalyScanBtn = document.getElementById("anomalyScanBtn");
    const analysisBtn = document.getElementById("analysisBtn");
    const backBtn = document.getElementById("backBtn");

    // Section toggle
    uploadBtn.onclick = () => {
        uploadSection.style.display = "block";
        viewSection.style.display = "none";
        document.querySelector(".buttons").style.display = "none"; // Hide main buttons
    };
    
    // Back button handler for upload section
    uploadBackBtn.onclick = () => {
        uploadSection.style.display = "none";
        document.querySelector(".buttons").style.display = "flex"; // Show main buttons again
    };
    
    viewBtn.onclick = () => {
        viewSection.style.display = "block";
        uploadSection.style.display = "none";
        document.querySelector(".buttons").style.display = "none"; // Hide main buttons
        loadFolderList();
    };

    backBtn.onclick = () => {
        viewSection.style.display = "none";
        document.querySelector(".buttons").style.display = "flex"; // Show main buttons again
        // Clear any opened files when going back
        openFiles.clear();
    };

    // Drag and drop support
    dropZone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropZone.style.borderColor = "#fff";
    });

    dropZone.addEventListener("dragleave", (e) => {
        e.preventDefault();
        dropZone.style.borderColor = "#aaa";
    });

    dropZone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropZone.style.borderColor = "#aaa";
        const files = e.dataTransfer.files;
        handleFileUpload(files);
    });

    fileInput.addEventListener("change", (e) => {
        handleFileUpload(e.target.files);
    });

// Search input handler with debounce
searchInput.addEventListener("input", (e) => {
    const searchTerm = e.target.value.toLowerCase().trim();
    
    // Clear previous timeout
    if (searchTimeout) {
        clearTimeout(searchTimeout);
        // Hide loading indicator if search is canceled
        showSearchLoading(false);
    }
    
    // Skip search if term is too short or empty
    if (searchTerm.length < 2) {
        resetHighlighting();
        showSearchLoading(false); // Ensure loading indicator is hidden
        return;
    }
    
    // Show loading indicator immediately
    showSearchLoading(true);
    
    // Use debouncing to prevent UI freezing
    searchTimeout = setTimeout(() => {
        // Create a Web Worker for the search operation
        const searchWorker = createSearchWorker();
        
        // Collect data from all open files
        const openFileCards = document.querySelectorAll('.log-card');
        const fileData = [];
        
        openFileCards.forEach(card => {
            const logLines = card.querySelectorAll('.log-line');
            const lines = Array.from(logLines).map(line => 
                line.querySelector('.line-content').textContent
            );
            
            fileData.push({
                cardId: card.id,
                lines: lines
            });
        });
        
        // Set up worker response handler
        searchWorker.onmessage = function(e) {
            const results = e.data;
            let totalMatches = 0;
            
            // Reset all highlighting first
            resetHighlighting();
            
            // Process results for each file
            results.forEach(fileResult => {
                const card = document.getElementById(fileResult.cardId);
                if (!card) return;
                
                const logLines = card.querySelectorAll('.log-line');
                
                // Hide all lines initially
                logLines.forEach(line => {
                    line.style.display = 'none';
                });
                
                // Update card header
                const cardHeader = card.querySelector('.log-card-header h4');
                const originalTitle = cardHeader.textContent.split(' (')[0];
                
                if (fileResult.matches.length === 0) {
                    // No matches in this file
                    cardHeader.textContent = originalTitle;
                    
                    // Show "No results found" message
                    let noResultsMsg = card.querySelector('.no-results-message');
                    if (!noResultsMsg) {
                        noResultsMsg = document.createElement('div');
                        noResultsMsg.className = 'no-results-message';
                        const content = card.querySelector('.log-card-content');
                        content.appendChild(noResultsMsg);
                    }
                    noResultsMsg.textContent = `No results found for "${searchTerm}"`;
                    noResultsMsg.style.display = 'block';
                } else {
                    // Update header with match count
                    cardHeader.innerHTML = `${originalTitle} <span class="match-count">(${fileResult.matches.length} matches)</span>`;
                    totalMatches += fileResult.matches.length;
                    
                    // Hide any "No results" message
                    const noResultsMsg = card.querySelector('.no-results-message');
                    if (noResultsMsg) {
                        noResultsMsg.style.display = 'none';
                    }
                    
                    // Highlight and show matching lines
                    fileResult.matches.forEach(match => {
                        if (match.lineIndex >= 0 && match.lineIndex < logLines.length) {
                            const lineElement = logLines[match.lineIndex];
                            const lineContent = lineElement.querySelector('.line-content');
                            const regex = new RegExp(`(${searchTerm.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
                            lineContent.innerHTML = match.text.replace(
                                regex,
                                '<span class="highlight">$1</span>'
                            );
                            lineElement.style.display = 'flex'; // Show this line
                        }
                    });
                }
            });
            
            // Update notification if available
            if (typeof showNotification === 'function') {
                if (searchTerm && totalMatches > 0) {
                    showNotification(`Found ${totalMatches} matches for "${searchTerm}"`, "success");
                } else if (searchTerm) {
                    showNotification(`No matches found for "${searchTerm}"`, "info");
                }
            }
            
            // Hide loading indicator
            showSearchLoading(false);
            
            // Terminate the worker after use
            searchWorker.terminate();
        };
        
        // Send search data to worker
        searchWorker.postMessage({
            searchTerm: searchTerm,
            fileData: fileData
        });
    }, DEBOUNCE_DELAY);
});

    document.getElementById("anomalyScanBtn").onclick = () => {
        // Get current folder and files
        const currentFolder = getCurrentFolder();
        if (!currentFolder) {
            showNotification("Please select a folder first", "error");
            return;
        }
        
        // Get all opened files
        const openedFiles = Array.from(openFiles).map(path => {
            const parts = path.split('/');
            return parts[parts.length - 1];
        });
        
        if (openedFiles.length === 0) {
            showNotification("Please open files to analyze", "error");
            return;
        }
        
        // Disable buttons during process
        document.getElementById("anomalyScanBtn").disabled = true;
        document.getElementById("analysisBtn").disabled = true;
        
        // Show initial loading overlay
        showLoadingOverlay("Starting Anomaly Scan");
        
        // Call backend function
        backend.detect_anomalies(currentFolder, JSON.stringify(openedFiles))
            .then(responseJson => {
                try {
                    const response = JSON.parse(responseJson);
                    
                    if (response.status === "started") {
                        // Process has started in background
                        // Progress updates will come via progressSignal
                        showNotification("Anomaly scan started in background", "info");
                    } else if (response.success) {
                        // If we got immediate results (should not happen with threaded implementation)
                        hideLoadingOverlay();
                        displayAnomalyResults(response, currentFolder);
                        document.getElementById("anomalyScanBtn").disabled = false;
                        document.getElementById("analysisBtn").disabled = false;
                    } else {
                        hideLoadingOverlay();
                        showNotification(`Anomaly scan failed: ${response.message}`, "error");
                        document.getElementById("anomalyScanBtn").disabled = false;
                        document.getElementById("analysisBtn").disabled = false;
                    }
                } catch (e) {
                    hideLoadingOverlay();
                    showNotification(`Error parsing response: ${e.message}`, "error");
                    document.getElementById("anomalyScanBtn").disabled = false;
                    document.getElementById("analysisBtn").disabled = false;
                }
            })
            .catch(err => {
                hideLoadingOverlay();
                showNotification(`Error during anomaly scan: ${err}`, "error");
                document.getElementById("anomalyScanBtn").disabled = false;
                document.getElementById("analysisBtn").disabled = false;
            });
    };
    
    // Deep analysis button handler
    document.getElementById("analysisBtn").onclick = () => {
        // Get current folder and files
        const currentFolder = getCurrentFolder();
        if (!currentFolder) {
            showNotification("Please select a folder first", "error");
            return;
        }
        
        // Get all opened files
        const openedFiles = Array.from(openFiles).map(path => {
            const parts = path.split('/');
            return parts[parts.length - 1];
        });
        
        if (openedFiles.length === 0) {
            showNotification("Please open files to analyze", "error");
            return;
        }
        
        // Disable buttons during process
        document.getElementById("anomalyScanBtn").disabled = true;
        document.getElementById("analysisBtn").disabled = true;
        
        // Show initial loading overlay
        showLoadingOverlay("Starting Deep Analysis");
        
        // Call backend function
        backend.perform_deep_analysis(currentFolder, JSON.stringify(openedFiles))
            .then(responseJson => {
                try {
                    const response = JSON.parse(responseJson);
                    
                    if (response.status === "started") {
                        // Process has started in background
                        // Progress updates will come via progressSignal
                        showNotification("Deep analysis started in background", "info");
                    } else if (response.success) {
                        // If we got immediate results (should not happen with threaded implementation)
                        hideLoadingOverlay();
                        displayAnalysisResults(response, currentFolder);
                        document.getElementById("anomalyScanBtn").disabled = false;
                        document.getElementById("analysisBtn").disabled = false;
                    } else {
                        hideLoadingOverlay();
                        showNotification(`Deep analysis failed: ${response.message}`, "error");
                        document.getElementById("anomalyScanBtn").disabled = false;
                        document.getElementById("analysisBtn").disabled = false;
                    }
                } catch (e) {
                    hideLoadingOverlay();
                    showNotification(`Error parsing response: ${e.message}`, "error");
                    document.getElementById("anomalyScanBtn").disabled = false;
                    document.getElementById("analysisBtn").disabled = false;
                }
            })
            .catch(err => {
                hideLoadingOverlay();
                showNotification(`Error during deep analysis: ${err}`, "error");
                document.getElementById("anomalyScanBtn").disabled = false;
                document.getElementById("analysisBtn").disabled = false;
            });
    };

});



// Helper function to get current folder from opened files
function getCurrentFolder() {
    if (openFiles.size === 0) return null;
    
    // Get first item in the set
    const firstItem = Array.from(openFiles)[0];
    // Get the folder part (before the last slash)
    return firstItem.substring(0, firstItem.lastIndexOf('/'));
}

// Create a Web Worker for search operations
function createSearchWorker() {
    const workerBlob = new Blob([`
        self.onmessage = function(e) {
            const { searchTerm, fileData } = e.data;
            const results = [];
            
            fileData.forEach(file => {
                const matches = [];
                
                file.lines.forEach((line, lineIndex) => {
                    if (line.toLowerCase().includes(searchTerm.toLowerCase())) {
                        matches.push({
                            lineIndex: lineIndex,
                            text: line
                        });
                    }
                });
                
                results.push({
                    cardId: file.cardId,
                    matches: matches
                });
            });
            
            self.postMessage(results);
        };
    `], { type: 'application/javascript' });
    
    return new Worker(URL.createObjectURL(workerBlob));
}

// Helper function to show loading indicator
function showSearchLoading(isLoading) {
    const searchInput = document.getElementById('searchInput');
    
    // Always remove any existing spinner first to avoid duplicates
    const existingSpinner = document.getElementById('searchSpinner');
    if (existingSpinner) {
        existingSpinner.remove();
    }
    
    if (isLoading) {
        // Add a loading spinner next to the search box only if we're actively loading
        const spinner = document.createElement('div');
        spinner.id = 'searchSpinner';
        spinner.className = 'search-spinner';
        spinner.innerHTML = '🔄';
        spinner.style.animation = 'spin 1s linear infinite';
        
        // Add the spinner after the search input
        searchInput.parentNode.insertBefore(spinner, searchInput.nextSibling);
        
        // Add the spinning animation if not already in CSS
        if (!document.getElementById('spinnerAnimation')) {
            const style = document.createElement('style');
            style.id = 'spinnerAnimation';
                style.textContent = `
                    @keyframes spin {
                        0% { transform: rotate(0deg); }
                        100% { transform: rotate(360deg); }
                    }
                    .search-spinner {
                        display: inline-block;
                        margin-left: 8px;
                        vertical-align: middle;
                    }
                    .no-results-message {
                        padding: 15px;
                        text-align: center;
                        color: white;
                        font-style: italic;
                        background: #750080;
                        border-radius: 4px;
                        margin: 10px;
                    }
                `;
                document.head.appendChild(style);
            }
        }
    }
    
// Reset all highlighting in log cards
function resetHighlighting() {
    const openFileCards = document.querySelectorAll('.log-card');
    
    openFileCards.forEach(card => {
        const logLines = card.querySelectorAll('.log-line');
        
        // Reset all highlights and show all lines
        logLines.forEach(line => {
            const lineContent = line.querySelector('.line-content');
            lineContent.innerHTML = lineContent.textContent; // Remove highlights
            line.style.display = 'flex'; // Show all lines
        });
        
        // Reset card header
        const cardHeader = card.querySelector('.log-card-header h4');
        const originalTitle = cardHeader.textContent.split(' (')[0];
        cardHeader.textContent = originalTitle;
        
        // Hide any "No results" message
        const noResultsMsg = card.querySelector('.no-results-message');
        if (noResultsMsg) {
            noResultsMsg.style.display = 'none';
        }
    });
}

function showLoadingOverlay(message) {
    // Update existing overlay or create a new one
    const existingOverlay = document.getElementById('loadingOverlay');
    
    if (existingOverlay) {
        // Update the existing overlay with loading content
        existingOverlay.classList.remove('buffer-state');
        existingOverlay.innerHTML = `
            <div class="loading-content">
                <div class="spinner"></div>
                <div class="loading-message">${message}</div>
                <div class="progress-container">
                    <div class="progress-bar" id="loadingProgressBar"></div>
                </div>
                <div class="progress-text" id="loadingProgressText">0%</div>
            </div>
        `;
    } else {
        // Create a new overlay
        const overlay = document.createElement('div');
        overlay.id = 'loadingOverlay';
        overlay.className = 'loading-overlay';
        
        overlay.innerHTML = `
            <div class="loading-content">
                <div class="spinner"></div>
                <div class="loading-message">${message}</div>
                <div class="progress-container">
                    <div class="progress-bar" id="loadingProgressBar"></div>
                </div>
                <div class="progress-text" id="loadingProgressText">0%</div>
            </div>
        `;
        
        document.body.appendChild(overlay);
    }
     // Only register progress handler if backend is defined
     if (backend && typeof backend.progressSignal !== 'undefined' && !window.progressHandlerRegistered) {
        try {
            backend.progressSignal.connect((percentage, message) => {
                updateLoadingProgress(percentage, message);
            });
            window.progressHandlerRegistered = true;
        } catch (e) {
            console.error("Error connecting to progressSignal:", e);
        }
    }
}

// Function to handle progress updates from the backend
function updateLoadingProgress(percentage, message) {
    const progressBar = document.getElementById('loadingProgressBar');
    const progressText = document.getElementById('loadingProgressText');
    const loadingMessage = document.querySelector('.loading-message');
    
    if (progressBar && progressText) {
        progressBar.style.width = `${percentage}%`;
        progressText.textContent = `${percentage}%`;
        
        if (message && loadingMessage) {
            loadingMessage.textContent = message;
        }
        
        // If progress is 100%, show completion and hide overlay after delay
        if (percentage >= 100) {
            setTimeout(() => {
                hideLoadingOverlay();
                
                // Show completion notification based on message content
                if (message.includes("Error:")) {
                    showNotification(message, "error");
                } else {
                    showNotification("Process completed successfully", "success");
                }
            }, 1000);  // Give user a moment to see 100%
        }
    }
}

function hideLoadingOverlay() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        // Add fade-out class
        overlay.classList.add('fade-out');
        
        // Remove after animation completes
        setTimeout(() => {
            if (overlay.parentNode) {
                overlay.parentNode.removeChild(overlay);
            }
        }, 500);
    }
}

// Results display functions
function displayAnomalyResults(results, folderPath) {
    // Create or get output container
    const outputContainer = getOrCreateOutputContainer();
    
    // Store the results data for potential download
    outputContainer.dataset.anomalyResults = JSON.stringify(results);
    outputContainer.dataset.folderPath = folderPath;
    
    // Set container mode to anomaly
    outputContainer.dataset.mode = 'anomaly';
    
    // Create header with title and controls
    const header = createOutputHeader('Anomaly Detection Results', folderPath, false);
    
    // Create content area
    const content = document.createElement('div');
    content.className = 'output-content';
    
    // Add summary stats
    const stats = results.stats;
    const summaryHtml = `
        <div class="results-summary">
            <div class="summary-item">
                <span class="summary-label">Total Files:</span>
                <span class="summary-value">${stats.total_files}</span>
            </div>
            <div class="summary-item">
                <span class="summary-label">Total Anomalies:</span>
                <span class="summary-value ${stats.total_anomalies > 0 ? 'warning' : ''}">${stats.total_anomalies}</span>
            </div>
            <div class="summary-item danger-levels">
                <span class="summary-label">Danger Levels:</span>
                <div class="danger-counts">
                  &nbsp;  ${stats.danger_levels.High > 0 ? `<span class="danger-high">High: ${stats.danger_levels.High}</span>` : ''}
                  &nbsp;  ${stats.danger_levels.Medium > 0 ? `<span class="danger-medium">Medium: ${stats.danger_levels.Medium}</span>` : ''}
                  &nbsp;  ${stats.danger_levels.Low > 0 ? `<span class="danger-low">Low: ${stats.danger_levels.Low}</span>` : ''}
                  &nbsp;  ${stats.total_anomalies === 0 ? '<span class="no-danger">No anomalies detected</span>' : ''}
                </div>
            </div>
        </div>
    `;
    
    content.innerHTML = summaryHtml;
    // Show notification for anomaly results
    showNotification(
        `Total Anomalies Found: ${stats.total_anomalies} (${stats.danger_levels.High} High, ${stats.danger_levels.Medium} Medium, ${stats.danger_levels.Low} Low)`,
        "warning",
        stats.total_anomalies > 0 ? "high" : "low" // Assuming that if anomalies exist, it will be high risk, else low
    );
    
    // Create results table if there are anomalies
    if (results.results && results.results.length > 0) {
        const tableContainer = document.createElement('div');
        tableContainer.className = 'table-container';
        
        const table = document.createElement('table');
        table.className = 'results-table anomaly-table';
        
        // Create table header
        const thead = document.createElement('thead');
        thead.innerHTML = `
            <tr>
                <th>Anomaly Type</th>
                <th>Level</th>
                <th>File</th>
                <th>Line</th>
                <th>Content</th>
            </tr>
        `;
        table.appendChild(thead);
        
        // Create table body
        const tbody = document.createElement('tbody');
        results.results.forEach(anomaly => {
            const tr = document.createElement('tr');
            tr.className = `danger-level-${anomaly.danger_level.toLowerCase()}`;
            
            tr.innerHTML = `
                <td>${anomaly.anomaly_name}</td>
                <td><span class="badge badge-${anomaly.danger_level.toLowerCase()}">${anomaly.danger_level}</span></td>
                <td>${anomaly.file_name}</td>
                <td>${anomaly.line_number}</td>
                <td class="log-content">${anomaly.log_content}</td>
            `;
            
            // Add click handler to highlight the line in the file
            tr.addEventListener('click', () => {
                highlightLineInFile(anomaly.file_name, anomaly.line_number);
            });
            
            tbody.appendChild(tr);
        });
        
        table.appendChild(tbody);
        tableContainer.appendChild(table);
        content.appendChild(tableContainer);
    } else {
        // No anomalies found
        const noResults = document.createElement('div');
        noResults.className = 'no-results';
        noResults.innerHTML = `
            <div class="success-icon">✓</div>
            <p>No anomalies detected in the analyzed files.</p>
        `;
        content.appendChild(noResults);
    }
    
    // Add content to container
    outputContainer.innerHTML = '';
    outputContainer.appendChild(header);
    outputContainer.appendChild(content);
    updateAfterDisplaying();
    // Show the container
    outputContainer.style.display = 'flex';
}

function displayAnalysisResults(results, folderPath) {
    // Create or get output container
    const outputContainer = getOrCreateOutputContainer();
    
    // Store the results data for potential download
    outputContainer.dataset.analysisResults = JSON.stringify(results);
    outputContainer.dataset.folderPath = folderPath;
    
    // Set container mode to analysis
    outputContainer.dataset.mode = 'analysis';
    
    // Create header with title and controls
    const header = createOutputHeader('Deep Analysis Results', folderPath, true);
    
    // Create content area
    const content = document.createElement('div');
    content.className = 'output-content';
    
    // Add summary stats
    const stats = results.stats;
    const overallRiskClass = getRiskLevelClass(stats.overall_risk);
    
    const summaryHtml = `
        <div class="results-summary">
            <div class="summary-item">
                <span class="summary-label">Total Files:</span>
                <span class="summary-value">${stats.total_files}</span>
            </div>
            <div class="summary-item">
                <span class="summary-label">Overall Risk:</span>
                <span class="summary-value ${overallRiskClass}">${stats.overall_risk}</span>
            </div>
            <div class="summary-item risk-levels">
                <span class="summary-label">Risk Breakdown:</span>
                <div class="risk-counts">
                &nbsp;    ${stats.risk_counts.Critical > 0 ? `<span class="risk-critical">Critical: ${stats.risk_counts.Critical}</span>` : ''}
                &nbsp;    ${stats.risk_counts.High > 0 ? `<span class="risk-high">High: ${stats.risk_counts.High}</span>` : ''}
                &nbsp;    ${stats.risk_counts.Medium > 0 ? `<span class="risk-medium">Medium: ${stats.risk_counts.Medium}</span>` : ''}
                &nbsp;    ${stats.risk_counts.Low > 0 ? `<span class="risk-low">Low: ${stats.risk_counts.Low}</span>` : ''}
                </div>
            </div>
        </div>
    `;
    
    content.innerHTML = summaryHtml;
    // Show notification for analysis results
    showNotification(`Overall Risk Level: ${stats.overall_risk}`, "info", stats.overall_risk.toLowerCase());
    
    // Create file results accordions
    if (results.file_results && results.file_results.length > 0) {
        const accordionContainer = document.createElement('div');
        accordionContainer.className = 'accordion-container';
        
        results.file_results.forEach((fileResult, index) => {
            const accordion = document.createElement('div');
            accordion.className = 'accordion';
            
            // Risk indicator color
            const riskClass = getRiskLevelClass(fileResult.overall_risk);
            
            // Create header
            const header = document.createElement('div');
            header.className = `accordion-header ${riskClass}`;
            header.innerHTML = `
                <div class="accordion-title">
                    <span class="file-name">${fileResult.file_name}</span>
                    <span class="risk-badge ${riskClass}">${fileResult.overall_risk}</span>
                </div>
                <div class="accordion-counts">
                    ${Object.entries(fileResult.risk_prediction)
                        .filter(([level, count]) => count > 0 && level !== 'Normal')
                        .map(([level, count]) => `<span class="risk-${level.toLowerCase()}">${level}: ${count}</span>`)
                        .join(' ')}
                </div>
                <div class="accordion-icon">▼</div>
            `;
            
            // Create content panel (initially hidden)
            const panel = document.createElement('div');
            panel.className = 'accordion-panel';
            panel.style.display = index === 0 ? 'block' : 'none'; // Open first panel by default
            
            // Create table for line analysis
            if (fileResult.line_analysis && fileResult.line_analysis.length > 0) {
                const table = document.createElement('table');
                table.className = 'results-table analysis-table';
                
                // Create table header
                const thead = document.createElement('thead');
                thead.innerHTML = `
                    <tr>
                         <th>Risk</th>
                        <th>Line</th>
                        <th>Type</th>
                        <th>Indicators</th>
                        <th>Content</th>
                    </tr>
                `;
                table.appendChild(thead);
                
                // Create table body
                const tbody = document.createElement('tbody');
                fileResult.line_analysis.forEach(line => {
                    const tr = document.createElement('tr');
                    tr.className = `risk-level-${line.risk_level.toLowerCase()}`;
                    
                    // Format confidence as percentage
                    const confidence = Math.round(line.confidence * 100);
                    
                    tr.innerHTML = `
                        <td><span class="badge badge-${line.risk_level.toLowerCase()}">${line.risk_level} (${confidence}%)</span></td>
                        <td>${line.line_number}</td>
                        <td>${line.risk_type || 'Unclassified'}</td>
                        <td>${line.indicators ? line.indicators.join(', ') : '-'}</td>
                        <td class="log-content">${line.log_content}</td>
                    `;
                    
                    // Add click handler to highlight the line in the file
                    tr.addEventListener('click', () => {
                        highlightLineInFile(fileResult.file_name, line.line_number);
                    });
                    
                    tbody.appendChild(tr);
                });
                
                table.appendChild(tbody);
                panel.appendChild(table);
            } else {
                panel.innerHTML = '<p class="no-issues">No issues detected in this file.</p>';
            }
            
            // Add toggle functionality
            header.addEventListener('click', () => {
                header.classList.toggle('active');
                const icon = header.querySelector('.accordion-icon');
                
                if (panel.style.display === 'block') {
                    panel.style.display = 'none';
                    icon.textContent = '▼';
                } else {
                    panel.style.display = 'block';
                    icon.textContent = '▲';
                }
            });
            
            accordion.appendChild(header);
            accordion.appendChild(panel);
            accordionContainer.appendChild(accordion);
        });
        
        content.appendChild(accordionContainer);
    } else {
        // No results found
        const noResults = document.createElement('div');
        noResults.className = 'no-results';
        noResults.innerHTML = `
            <div class="success-icon">✓</div>
            <p>No issues detected in the analyzed files.</p>
        `;
        content.appendChild(noResults);
    }
    
    // Add content to container
    outputContainer.innerHTML = '';
    outputContainer.appendChild(header);
    outputContainer.appendChild(content);
    updateAfterDisplaying();
    // Show the container
    outputContainer.style.display = 'flex';
}

function getOrCreateOutputContainer() {
    let outputContainer = document.getElementById('analysisOutputContainer');
    
    if (!outputContainer) {
        outputContainer = document.createElement('div');
        outputContainer.id = 'analysisOutputContainer';
        outputContainer.className = 'analysis-output-container';
        
        // Append to the end of logFilesContainer
        const logFilesContainer = document.getElementById('logFilesContainer');
        if (logFilesContainer) {
            // Create a wrapper div that spans all grid columns
            const wrapperDiv = document.createElement('div');
            wrapperDiv.className = 'full-width-grid-item';
            wrapperDiv.style.gridColumn = '1 / -1'; // Make it span all columns
            wrapperDiv.appendChild(outputContainer);
            
            logFilesContainer.appendChild(wrapperDiv);
            
            // Trigger layout update to handle case with single file
            setTimeout(() => {
                updateLogContainerLayout();
            }, 50);
        } else {
            // If logFilesContainer doesn't exist, append to logGrid
            const logGrid = document.getElementById('logGrid');
            logGrid.appendChild(outputContainer);
        }
    }
    
    return outputContainer;
}

// Add this to the end of both displayAnomalyResults and displayAnalysisResults functions
function updateAfterDisplaying() {
    // After displaying results, update the layout
    setTimeout(() => {
        updateLogContainerLayout();
    }, 50);
}

function createOutputHeader(title, folderPath, showAnomalyButton) {
    const header = document.createElement('div');
    header.className = 'output-header';
    
    // Create mode switcher buttons if needed
    let modeSwitcher = '';
    if (showAnomalyButton) {
        modeSwitcher = `<button id="switchToAnomalyBtn" class="mode-switch-btn">Switch to Anomaly Scan</button>`;
    }
    
    // Check if we have both results available to show analysis button
    const outputContainer = document.getElementById('analysisOutputContainer');
    if (outputContainer && outputContainer.dataset.anomalyResults && !showAnomalyButton) {
        modeSwitcher = `<button id="switchToAnalysisBtn" class="mode-switch-btn">Switch to Deep Analysis</button>`;
    }
    
    header.innerHTML = `
        <div class="output-title-section">
            ${modeSwitcher}&nbsp;
            <h3>&nbsp;${title}</h3>
        </div>
        <div class="output-controls">
            <button id="downloadResultsBtn" class="download-btn">Download Results</button>
            <button id="closeOutputBtn" class="close-btn">✖</button>
        </div>
    `;
    
    // Add event listeners after adding to DOM
    setTimeout(() => {
        // Mode switch buttons
        const switchToAnomalyBtn = document.getElementById('switchToAnomalyBtn');
        if (switchToAnomalyBtn) {
            switchToAnomalyBtn.addEventListener('click', () => {
                if (outputContainer && outputContainer.dataset.anomalyResults) {
                    displayAnomalyResults(JSON.parse(outputContainer.dataset.anomalyResults), folderPath);
                } else {
                    showNotification("No anomaly scan results available", "info");
                }
            });
        }
        
        const switchToAnalysisBtn = document.getElementById('switchToAnalysisBtn');
        if (switchToAnalysisBtn) {
            switchToAnalysisBtn.addEventListener('click', () => {
                if (outputContainer && outputContainer.dataset.analysisResults) {
                    displayAnalysisResults(JSON.parse(outputContainer.dataset.analysisResults), folderPath);
                } else {
                    showNotification("No analysis results available", "info");
                }
            });
        }
        
        // Download button
        const downloadBtn = document.getElementById('downloadResultsBtn');
        if (downloadBtn) {
            downloadBtn.addEventListener('click', () => {
                downloadResults(folderPath);
            });
        }
        
        // Close button
        const closeBtn = document.getElementById('closeOutputBtn');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                closeOutputContainer();
            });
        }
    }, 0);
    
    return header;
}

function getRiskLevelClass(riskLevel) {
    switch (riskLevel) {
        case 'Critical': return 'risk-critical';
        case 'High': return 'risk-high';
        case 'Medium': return 'risk-medium';
        case 'Low': return 'risk-low';
        default: return 'risk-normal';
    }
}

function closeOutputContainer() {
    const outputContainer = document.getElementById('analysisOutputContainer');
    if (outputContainer) {
        outputContainer.style.display = 'none';
    }
}

function downloadResults(folderPath) {
    const outputContainer = document.getElementById('analysisOutputContainer');
    if (!outputContainer) return;
    
    const mode = outputContainer.dataset.mode;
    let data = null;
    let analysisType = null;
    
    if (mode === 'anomaly' && outputContainer.dataset.anomalyResults) {
        data = outputContainer.dataset.anomalyResults;
        analysisType = 'anomaly';  // This matches the backend's expectation
    } else if (mode === 'analysis' && outputContainer.dataset.analysisResults) {
        data = outputContainer.dataset.analysisResults;
        analysisType = 'deep_analysis';  // Change this to match what the backend expects
    } else {
        showNotification("No data available for download", "error");
        return;
    }
    
    // Call backend export function with the correct analysis type
    backend.export_analysis_to_csv(analysisType, folderPath, data)
        .then(responseJson => {
            try {
                const response = JSON.parse(responseJson);
                
                if (response.success) {
                    showNotification(response.message, "success");
                } else {
                    showNotification(`Export failed: ${response.message}`, "error");
                }
            } catch (e) {
                showNotification(`Error parsing response: ${e.message}`, "error");
            }
        })
        .catch(err => {
            showNotification(`Error during export: ${err}`, "error");
        });
}

function highlightLineInFile(fileName, lineNumber) {
    // Find the file card for this file
    const fileCards = document.querySelectorAll('.log-card');
    
    for (const card of fileCards) {
        const cardHeader = card.querySelector('.log-card-header h4');
        if (cardHeader && cardHeader.textContent.includes(fileName)) {
            // Found the card, now find the line
            const lineElement = card.querySelector(`.log-line:nth-child(${lineNumber})`);
            
            if (lineElement) {
                // Scroll to line
                lineElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
                
                // Highlight line
                lineElement.classList.add('highlight-line');
                setTimeout(() => {
                    lineElement.classList.remove('highlight-line');
                }, 3000);
                
                // Focus the card
                card.classList.add('highlight-card');
                setTimeout(() => {
                    card.classList.remove('highlight-card');
                }, 1000);
                
                break;
            }
        }
    }
}


// Upload logic
function handleFileUpload(files) {
    if (!backend) {
        showNotification("Backend not connected", "error");
        return;
    }

    const fileUploadStatus = document.getElementById("fileUploadStatus");
    let fileNames = [];
    let total = files.length;
    let processed = 0;
    
    showNotification(`Processing ${total} files...`, "info");

    for (let i = 0; i < total; i++) {
        const file = files[i];
        const reader = new FileReader();

        reader.onload = function () {
            const base64Data = reader.result.split(',')[1];
            // Send file name + content to backend
            backend.save_log_file(file.name, base64Data).then(result => {
                processed++;
                if (processed === total) {
                    showNotification(`Successfully uploaded ${total} files!`, "success");
                }
            }).catch(err => {
                showNotification(`Error uploading ${file.name}: ${err}`, "error");
            });
        };

        reader.readAsDataURL(file);
        fileNames.push(file.name);
    }

    fileUploadStatus.innerHTML = `
        ✅ Uploading <strong>${total}</strong> file(s): <br>
        ${fileNames.map((f) => `<code>${f}</code>`).join("<br>")}
        <p>Files will be stored in today's date folder</p>
    `;
}

function loadFolderList() {
    const folderList = document.getElementById("folderList");
    const logGrid = document.getElementById("logGrid");
    
    // Hide analysis buttons when viewing folder list
    toggleAnalysisButtons(false);
    
    if (!backend) {
        showNotification("Backend not connected", "error");
        return;
    }

    folderList.innerHTML = '<p>Loading folders...</p>';
    
    backend.list_folders().then((foldersJson) => {
        try {
            // Parse the JSON string into an array
            const folders = JSON.parse(foldersJson);
            
            if (folders && Array.isArray(folders) && folders.length > 0) {
                folderList.innerHTML = `
                    <div class="modern-list">
                        <h3>📅 Log Folders</h3>
                        <div class="folder-list">
                            ${folders.map((folder) => `
                                <div class="folder-item" onclick="loadFilesInFolder('${folder}')">
                                    <div class="folder-icon">📁</div>
                                    <div class="folder-name">${folder}</div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                `;
                
                // Automatically open the first folder
                if (folders.length > 0) {
                    setTimeout(() => loadFilesInFolder(folders[0]), 300);
                }
            } else {
                folderList.innerHTML = '<p>No log folders found</p>';
            }
            logGrid.innerHTML = ''; // Clear previous content
            openFiles.clear(); // Clear tracked open files
        } catch (e) {
            console.error("Error parsing folders:", e);
            folderList.innerHTML = `<p>Error parsing folder list: ${e.message}</p>`;
        }
    }).catch(err => {
        folderList.innerHTML = `<p>Error loading folders: ${err}</p>`;
    });
}

// Helper function to toggle visibility of analysis buttons
function toggleAnalysisButtons(show) {
    const anomalyScanBtn = document.getElementById("anomalyScanBtn");
    const analysisBtn = document.getElementById("analysisBtn");
    const searchInput = document.getElementById("searchInput");
    if (anomalyScanBtn) {
        anomalyScanBtn.style.display = show ? "inline-block" : "none";
    }
    
    if (analysisBtn) {
        analysisBtn.style.display = show ? "inline-block" : "none";
    }
    if (searchInput) {
        searchInput.style.display = show ? "inline-block" : "none";
    }
}


// Load files inside selected folder
function loadFilesInFolder(folderName) {
    const logGrid = document.getElementById("logGrid");
    const anomalyScanBtn = document.getElementById("anomalyScanBtn");
    const analysisBtn = document.getElementById("analysisBtn");
    
    // Highlight the selected folder
    const folderItems = document.querySelectorAll('.folder-item');
    folderItems.forEach(item => {
        item.classList.remove('active');
        if (item.querySelector('.folder-name').textContent === folderName) {
            item.classList.add('active');
        }
    });
    
    if (!backend) {
        showNotification("Backend not connected", "error");
        return;
    }

    // Store current folder in button data attributes for later use
    anomalyScanBtn.dataset.currentFolder = folderName;
    analysisBtn.dataset.currentFolder = folderName;
    
    logGrid.innerHTML = '<p>Loading files...</p>';
    openFiles.clear(); // Clear tracked open files
    
    backend.list_files_in_folder(folderName).then((responseJson) => {
        try {
            const response = JSON.parse(responseJson);
            
            if (response.success) {
                const files = response.files;
                if (files && files.length > 0) {
                    // Add "Open All" button if there are multiple files
                    const openAllBtn = files.length > 1 ? 
                        `<button class="normal-btn" onclick="openAllFiles('${folderName}', ${JSON.stringify(files).replace(/"/g, '&quot;')})">
                            📂 Open All Files
                         </button>` : '';
                    
                    logGrid.innerHTML = `
                        <div class="files-header">
                            <h3>📂 ${folderName}</h3>
                            <div>
                                <span>${files.length} log file(s)</span>
                                ${openAllBtn}
                            </div>
                        </div>
                        <div class="notepad-grid">
                            ${files.map((file) => `
                                <div class="notepad-item file-item" data-filename="${file}" onclick="viewLogFile('${folderName}', '${file}')">
                                    <div class="file-icon">📄</div>
                                    <div class="file-name">${file}</div>
                                </div>
                            `).join('')}
                        </div>
                        <div id="logFilesContainer" class="log-files-container"></div>
                    `;
                } else {
                    logGrid.innerHTML = '<div class="empty-state">No files found in this folder</div>';
                }
            } else {
                logGrid.innerHTML = `<p class="error-message">Error: ${response.message}</p>`;
            }
        } catch (e) {
            console.error("Error parsing file list:", e);
            logGrid.innerHTML = `<p class="error-message">Error parsing file list: ${e.message}</p>`;
        }
    }).catch(err => {
        logGrid.innerHTML = `<p class="error-message">Error loading files: ${err}</p>`;
    });
}

// Improved openAllFiles function with proper spacing
function openAllFiles(folderName, files) {
    // If already opened, don't reopen them
    if (files.every(file => openFiles.has(`${folderName}/${file}`))) {
        showNotification("All files are already open", "info");
        return;
    }
    
    showNotification(`Opening ${files.length} files...`, "info");
    
    // Hide the files header, file list, and folder list
    const logGrid = document.getElementById("logGrid");
    const filesHeader = logGrid.querySelector('.files-header');
    const notepadGrid = logGrid.querySelector('.notepad-grid');
    const folderList = document.getElementById("folderList");
    
    if (filesHeader) filesHeader.style.display = 'none';
    if (notepadGrid) notepadGrid.style.display = 'none';
    if (folderList) folderList.style.display = 'none';
    
    // Add "Back to Files" button if not already present
    const backToFilesBtn = document.getElementById('backToFilesBtn');
    if (!backToFilesBtn) {
        const topControls = document.querySelector('.top-controls');
        if (topControls) {
            const newBackBtn = document.createElement('button');
            newBackBtn.id = 'backToFilesBtn';
            newBackBtn.className = 'back-to-files-btn';
            newBackBtn.innerHTML = '↩ Back to Files';
            newBackBtn.onclick = () => backToFilesList(folderName);
            
            // Insert after back button
            const backBtn = document.getElementById('backBtn');
            if (backBtn && backBtn.parentNode) {
                backBtn.parentNode.insertBefore(newBackBtn, backBtn.nextSibling);
            }
        }
    }
    
    // Clear any currently open files
    openFiles.clear();
    
    // Create or clear log files container
    let logFilesContainer = document.getElementById('logFilesContainer');
    if (!logFilesContainer) {
        logFilesContainer = document.createElement('div');
        logFilesContainer.id = 'logFilesContainer';
        logFilesContainer.className = 'log-files-container';
        logFilesContainer.style.marginTop = '5rem'; // Increased margin to prevent overlap
        logGrid.appendChild(logFilesContainer);
    } else {
        logFilesContainer.innerHTML = '';
    }
    
    // Open each file one by one
    files.forEach(file => {
        viewLogFile(folderName, file, true); // true = being opened as part of batch
    });
    
    // After all files are added, update the layout
    setTimeout(() => {
        updateLogContainerLayout();
    }, 100);
}
function updateLogContainerLayout() {
    const logFilesContainer = document.getElementById('logFilesContainer');
    if (!logFilesContainer) return;
    
    // Count actual file cards (excluding output containers)
    const fileCards = logFilesContainer.querySelectorAll('.log-card:not(.analysis-output)');
    const fileCount = fileCards.length;
    
    // Check if analysis output container exists
    const analysisOutput = document.getElementById('analysisOutputContainer');
    const hasAnalysisOutput = analysisOutput && (analysisOutput.style.display !== 'none');
    
    // For single file with no analysis output, use centered layout with max width
    if (fileCount === 1 && !hasAnalysisOutput) {
        logFilesContainer.className = 'log-files-container single-file';
        const singleCard = logFilesContainer.querySelector('.log-card');
        if (singleCard) {
            singleCard.style.maxWidth = '800px';
            singleCard.style.width = '100%';
            singleCard.style.margin = '0 auto';
            singleCard.style.gridColumn = 'auto'; // Reset any grid column spanning
        }
        return;
    }
    
    // For single file WITH analysis output, use special layout
    if (fileCount === 1 && hasAnalysisOutput) {
        logFilesContainer.className = 'log-files-container';
        // Set grid to have two rows - file on top, analysis on bottom
        logFilesContainer.style.gridTemplateColumns = '1fr';
        
        // Style the single file card to be centered and full width
        const singleCard = fileCards[0];
        if (singleCard) {
            singleCard.style.maxWidth = '800px';
            singleCard.style.width = '100%';
            singleCard.style.margin = '0 auto';
            singleCard.style.gridColumn = 'auto'; // Reset any grid column spanning
        }
        
        // Make sure analysis output is full width
        if (analysisOutput) {
            // Ensure the wrapper is properly styled
            const wrapper = analysisOutput.closest('.full-width-grid-item');
            if (wrapper) {
                wrapper.style.gridColumn = '1 / -1';
                wrapper.style.width = '100%';
                analysisOutput.style.maxWidth = '800px'; // Match single file width
                analysisOutput.style.margin = '0 auto';
            }
        }
        
        return;
    }
    
    // For multiple files, use grid layout
    logFilesContainer.className = 'log-files-container';
    
    // Check screen width to determine responsive layout
    const screenWidth = window.innerWidth;
    if (screenWidth <= 768) {
        logFilesContainer.style.gridTemplateColumns = '1fr'; // Single column on mobile
        return;
    }
    
    // Calculate optimal grid layout
    let columns;
    if (fileCount <= 2) {
        columns = fileCount;
    } else {
        // For most cases, use maximum of 2 columns for better readability
        columns = 2;
    }
    
    // Set grid template columns
    logFilesContainer.style.gridTemplateColumns = `repeat(${columns}, minmax(300px, 1fr))`;
    
    // Set proper justification and alignment
    logFilesContainer.style.justifyContent = 'center'; // Center the grid itself
    
    // For odd number of files where the last one should be centered
    if (fileCount % columns !== 0) {
        // Apply special styling to the last card to center it
        const lastCard = fileCards[fileCards.length - 1];
        if (lastCard) {
            // Make the last card look like a "single file" when it's alone in its row
            lastCard.style.maxWidth = '800px';
            lastCard.style.width = '100%';
            lastCard.style.gridColumn = '1 / -1'; // Span all columns
            lastCard.style.margin = '0 auto';
        }
    }
    
    // Reset individual card styles except the last one in odd-count scenarios
    fileCards.forEach((card, index) => {
        // Don't reset the last card if it's an odd count
        if (fileCount % columns !== 0 && index === fileCards.length - 1) {
            return;
        }
        
        card.style.maxWidth = '600px';
        card.style.width = '100%';
        card.style.margin = '0 auto'; // Center each card in its grid cell
        card.style.gridColumn = 'auto'; // Reset any grid column spanning
    });
    
    // Ensure analysis output is always full width
    if (hasAnalysisOutput) {
        const wrapper = analysisOutput.closest('.full-width-grid-item');
        if (wrapper) {
            wrapper.style.gridColumn = '1 / -1';
            wrapper.style.width = '100%';
        }
    }
    
    // Ensure proper left margin for all files
    logFilesContainer.style.marginLeft = '0'; // Reset any previous margin
    logFilesContainer.style.padding = '0 1rem'; // Add padding instead for consistent spacing
}

function viewLogFile(folderName, filename, isBatch = false) {
    const logGrid = document.getElementById("logGrid");
    const logFilesContainer = document.getElementById("logFilesContainer") || document.createElement('div');
    const fileKey = `${folderName}/${filename}`;
    const folderList = document.getElementById("folderList");
    
    // Show analysis buttons when viewing log files
    toggleAnalysisButtons(true);
    
    // Check if the file is already open
    if (openFiles.has(fileKey)) {
        // Scroll to the existing file card
        const existingCard = document.getElementById(`log-card-${fileKey.replace(/[/\\?%*:|"<>]/g, '-')}`);
        if (existingCard) {
            existingCard.scrollIntoView({ behavior: 'smooth' });
            existingCard.classList.add('highlight-card');
            setTimeout(() => existingCard.classList.remove('highlight-card'), 1000);
        }
        return;
    }
    
    // Add to tracking set
    openFiles.add(fileKey);
    
    // If this is the first file being opened (not batch)
    if (!isBatch && openFiles.size === 1) {
        // Hide the files header, file list, and folder list
        const filesHeader = logGrid.querySelector('.files-header');
        const notepadGrid = logGrid.querySelector('.notepad-grid');
        
        if (filesHeader) filesHeader.style.display = 'none';
        if (notepadGrid) notepadGrid.style.display = 'none';
        if (folderList) folderList.style.display = 'none';
        
        // Add "Back to Files" button next to main back button
        const topControls = document.querySelector('.top-controls');
        if (topControls) {
            // Ensure top controls are visible above everything
            topControls.style.zIndex = '100';
            
            const backToFilesBtn = document.createElement('button');
            backToFilesBtn.id = 'backToFilesBtn';
            backToFilesBtn.className = 'back-to-files-btn';
            backToFilesBtn.innerHTML = '↩ Back to Files';
            backToFilesBtn.onclick = () => backToFilesList(folderName);
            
            // Insert after back button
            const backBtn = document.getElementById('backBtn');
            if (backBtn && backBtn.parentNode) {
                backBtn.parentNode.insertBefore(backToFilesBtn, backBtn.nextSibling);
            }
        }
        
        // Setup the log files container with proper spacing
        logFilesContainer.id = 'logFilesContainer';
        logFilesContainer.className = 'log-files-container';
        logFilesContainer.style.marginTop = '1rem'; // Add margin to prevent overlap with controls
        logGrid.appendChild(logFilesContainer);
    }
    
    if (!backend) {
        showNotification("Backend not connected", "error");
        return;
    }

    // Create a placeholder for this file
    const cardId = `log-card-${fileKey.replace(/[/\\?%*:|"<>]/g, '-')}`;
    const newCard = document.createElement('div');
    newCard.className = 'log-card';
    newCard.id = cardId;
    newCard.innerHTML = `
        <div class="log-card-header">
            <h4>📄 ${filename}</h4>
            <button class="close-btn" onclick="closeLogFile('${cardId}', '${fileKey}', '${folderName}')">✖</button>
        </div>
        <div class="log-card-content">Loading file content...</div>
        <div class="log-card-footer">
            <span>Loading file information...</span>
        </div>
    `;
    
    logFilesContainer.appendChild(newCard);
    
    // Apply proper layout after adding the new card
    updateLogContainerLayout();
    
    // Scroll the new card into view (if not batch loading) with additional spacing
    if (!isBatch) {
        // Scroll with offset to account for sticky header
        const topControls = document.querySelector('.top-controls');
        const topControlsHeight = topControls ? topControls.offsetHeight : 0;
        window.scrollTo({
            top: newCard.offsetTop - topControlsHeight - 20,
            behavior: 'smooth'
        });
    }
    
    // Load actual file content
    backend.read_log_file(folderName, filename).then((responseJson) => {
        try {
            const response = JSON.parse(responseJson);
            
            // Inside the .then() callback where you process the response
                if (response.success) {
                    // Use the file creation timestamp from the response
                    const timestamp = response.created_at || "Unknown date";
                    
                    // Format the content with line numbers
                    const contentLines = response.content.split('\n');
                    const formattedContent = contentLines.map((line, index) => {
                        return `<div class="log-line">
                                    <span class="line-number">${index + 1}</span>
                                    <span class="line-content">${line}</span>
                                </div>`;
                    }).join('');
                    
                    // Update the card content
                    newCard.innerHTML = `
                        <div class="log-card-header">
                            <h4>📄 ${filename}</h4>
                            <button class="close-btn" onclick="closeLogFile('${cardId}', '${fileKey}', '${folderName}')">✖</button>
                        </div>
                        <div class="log-card-content">${formattedContent}</div>
                        <div class="log-card-footer">
                            <span>File created: ${timestamp}</span>
                        </div>
                    `;
            }else {
                newCard.innerHTML = `
                    <div class="log-card-header">
                        <h4>📄 ${filename}</h4>
                        <button class="close-btn" onclick="closeLogFile('${cardId}', '${fileKey}', '${folderName}')">✖</button>
                    </div>
                    <div class="log-card-content error-message">Error: ${response.message}</div>
                    <div class="log-card-footer">
                        <span>Failed to load file</span>
                    </div>
                `;
            }
        } catch (e) {
            console.error("Error parsing file content:", e);
            newCard.innerHTML = `
                <div class="log-card-header">
                    <h4>📄 ${filename}</h4>
                    <button class="close-btn" onclick="closeLogFile('${cardId}', '${fileKey}', '${folderName}')">✖</button>
                </div>
                <div class="log-card-content error-message">Error parsing file content: ${e.message}</div>
                <div class="log-card-footer">
                    <span>Failed to load file</span>
                </div>
            `;
        }
    }).catch(err => {
        newCard.innerHTML = `
            <div class="log-card-header">
                <h4>📄 ${filename}</h4>
                <button class="close-btn" onclick="closeLogFile('${cardId}', '${fileKey}', '${folderName}')">✖</button>
            </div>
            <div class="log-card-content error-message">Error reading file: ${err}</div>
            <div class="log-card-footer">
                <span>Failed to load file</span>
            </div>
        `;
    });
}


// Improved closeLogFile function

// Modified closeLogFile to handle UI updates
function closeLogFile(cardId, fileKey, folderName) {
    // Remove from tracking set
    openFiles.delete(fileKey);
    
    // Remove the card
    const card = document.getElementById(cardId);
    if (card) {
        card.remove();
    }
    
    // If no more open files, go back to file list
    if (openFiles.size === 0) {
        backToFilesList(folderName);
    } else {
        // Update layout for remaining files
        updateLogContainerLayout();
    }
}

// Add improved window resize event listener
window.addEventListener('resize', () => {
    // Only update if there are files open
    if (openFiles.size > 0) {
        updateLogContainerLayout();
    }
});
// Go back to files list

// Go back to file list from log view
function backToFilesList(folderName) {
    const logGrid = document.getElementById("logGrid");
    const logFilesContainer = document.getElementById("logFilesContainer");
    const folderList = document.getElementById("folderList");
    const backToFilesBtn = document.getElementById("backToFilesBtn");
    
    // Hide analysis buttons when going back to file list
    toggleAnalysisButtons(false);
    
    // Show folder list and reload files in folder
    if (folderList) folderList.style.display = "block";
    
    // Remove the back to files button
    if (backToFilesBtn) {
        backToFilesBtn.remove();
    }
    
    // Clear the log files container
    if (logFilesContainer) {
        logFilesContainer.innerHTML = "";
    }
    
    // Clear open files tracking
    openFiles.clear();
    
    // Reload the files in this folder
    loadFilesInFolder(folderName);
}


// Show notification messages with color based on risk level
function showNotification(message, type = "info", riskLevel = null) {
    // Create notification element if it doesn't exist
    let notification = document.getElementById("notification");
    if (!notification) {
        notification = document.createElement("div");
        notification.id = "notification";
        notification.style.position = "fixed";
        notification.style.bottom = "20px";
        notification.style.right = "20px";
        notification.style.padding = "10px 20px";
        notification.style.borderRadius = "5px";
        notification.style.color = "#fff";
        notification.style.zIndex = "1000";
        notification.style.maxWidth = "300px";
        notification.style.boxShadow = "0 3px 10px rgba(0,0,0,0.2)";
        document.body.appendChild(notification);
    }
    
    // Set background color based on type or risk level
    if (riskLevel) {
        switch (riskLevel.toLowerCase()) {
            case "high":
                notification.style.backgroundColor = "#F44336"; // Red for High risk
                break;
            case "critical":
                notification.style.backgroundColor = "#F44336"; // Red for High risk
                break;
            case "medium":
                notification.style.backgroundColor = "#FF9800"; // Orange for Medium risk
                break;
            case "low":
                notification.style.backgroundColor = "#4CAF50"; // Green for Low risk
                break;
            default:
                notification.style.backgroundColor = "#2196F3"; // Default blue for unknown risk
                break;
        }
    } else {
        // Default background color based on type
        switch(type) {
            case "success":
                notification.style.backgroundColor = "#4CAF50";
                break;
            case "error":
                notification.style.backgroundColor = "#F44336";
                break;
            case "warning":
                notification.style.backgroundColor = "#FF9800";
                break;
            default:
                notification.style.backgroundColor = "#2196F3";
        }
    }
    
    notification.textContent = message;
    notification.style.display = "block";
    
    // Hide after 3 seconds
    setTimeout(() => {
        notification.style.display = "none";
    }, 3000);
}


