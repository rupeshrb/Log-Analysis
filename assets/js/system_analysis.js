// Initialize QWebChannel connection to the Python backend
let backend;

new QWebChannel(qt.webChannelTransport, function (channel) {
    backend = channel.objects.backend;


    // Set up button event listener
    setupEventListeners();
});

// Setup event listeners for UI elements
function setupEventListeners() {
    const fetchLogButton = document.getElementById("fetchLog");
    if (fetchLogButton) {
        fetchLogButton.addEventListener("click", function() {
            fetchSystemLogs();
        });
    }
}

// Function to fetch system logs
function fetchSystemLogs() {
    if (!backend) {
        showNotification("Backend not connected yet. Please try again.", "error");
        return;
    }

    // Show loading overlay
    showLoadingOverlay("Starting system log collection...");

    // Call the Python method to start log collection
    backend.fetch_logs().then(function(result) {
        try {
            const response = JSON.parse(result);
            if (response.status === "started") {
                // The log collection is running in background thread
                // Progress updates will come through the progressSignal
                showNotification("Log collection started in background", "info");
            } else {
                // This would be unexpected, but handle it just in case
                hideLoadingOverlay();
                showNotification("Unknown response from backend", "error");
            }
        } catch (e) {
            hideLoadingOverlay();
            showNotification("Error parsing backend response: " + e, "error");
        }
    }).catch(function(error) {
        hideLoadingOverlay();
        showNotification("Error fetching system logs: " + error, "error");
    });
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
    
    // Hide after 5 seconds
    setTimeout(() => {
        notification.style.display = "none";
    }, 5000);
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
        
        // If progress is 100%, show completion message and hide after delay
        if (percentage >= 100) {
            setTimeout(() => {
                hideLoadingOverlay();
                
                // Try to get the last collected files info
                try {
                    // Display completion notification
                    showNotification("System log collection completed successfully!", "success");
                } catch (e) {
                    console.error("Error handling completion:", e);
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

