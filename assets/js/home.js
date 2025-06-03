// Initialize global variables
let backend;
let capturing = false;
let charts = {};
let lastLogCount = 0;
let isUpdating = false;
let lastUpdateTime = 0;
let resizeTimeout = null;
let autoUpdateEnabled = false;
let autoUpdateInterval = null;
let chartJsLoaded = false;
let isOnline = navigator.onLine;

// Create color palette for charts
const chartColors = {
    background: [
        'rgba(138, 43, 226, 0.7)',  // Purple (accent)
        'rgba(255, 99, 132, 0.7)',   // Red
        'rgba(54, 162, 235, 0.7)',   // Blue
        'rgba(255, 206, 86, 0.7)',   // Yellow
        'rgba(75, 192, 192, 0.7)',   // Teal
        'rgba(153, 102, 255, 0.7)',  // Purple
        'rgba(255, 159, 64, 0.7)',   // Orange
        'rgba(199, 199, 199, 0.7)',  // Gray
    ],
    border: [
        'rgba(138, 43, 226, 1)',     // Purple (accent)
        'rgba(255, 99, 132, 1)',     // Red
        'rgba(54, 162, 235, 1)',     // Blue
        'rgba(255, 206, 86, 1)',     // Yellow
        'rgba(75, 192, 192, 1)',     // Teal
        'rgba(153, 102, 255, 1)',    // Purple
        'rgba(255, 159, 64, 1)',     // Orange
        'rgba(199, 199, 199, 1)',    // Gray
    ]
};

// Add global styles for modern UI elements
function addGlobalStyles() {
    const styleEl = document.createElement('style');
    styleEl.textContent = `
        .modern-button {
            background-color: #290a30;
            color: white;
            border: none;
            padding: 10px 18px;
            border-radius: 6px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            margin: 5px;
        }
        
        .modern-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        }
        
        .modern-button:active {
            transform: translateY(0);
            box-shadow: 0 1px 3px rgba(0,0,0,0.2);
        }
        
        .modern-button.active {
            background-color: #8a2be2;
        }
        
        .modern-button .icon {
            margin-right: 8px;
        }
        
        .overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(5px);
            z-index: 1000;
            display: flex;
            align-items: center;
            justify-content: center;
            opacity: 0;
            transition: opacity 0.3s ease;
            pointer-events: none;
        }
        
        .overlay.visible {
            opacity: 1;
            pointer-events: auto;
        }
        
        .popup {
            background-color: #fff;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            max-width: 90%;
            width: 450px;
            transform: translateY(20px);
            opacity: 0;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }
        
        .overlay.visible .popup {
            transform: translateY(0);
            opacity: 1;
        }
        
        .popup-header {
            display: flex;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .popup-header .icon {
            background-color: #f44336;
            color: white;
            width: 36px;
            height: 36px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 12px;
            font-size: 18px;
        }
        
        .popup-title {
            font-size: 18px;
            font-weight: 600;
            color: #333;
            margin: 0;
        }
        
        .popup-content {
            color: #555;
            margin-bottom: 20px;
            line-height: 1.5;
        }
        
        .popup-actions {
            display: flex;
            justify-content: flex-end;
        }
        
        .popup-button {
            background-color: #f44336;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .popup-button:hover {
            background-color: #e53935;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }
        
        .network-status {
            display: flex;
            align-items: center;
            padding: 8px 12px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 500;
            margin: 10px;
            transition: all 0.3s ease;
        }
        
        .network-status.online {
            background-color: rgba(76, 175, 80, 0.15);
            color: #2e7d32;
            border: 1px solid rgba(76, 175, 80, 0.3);
        }
        
        .network-status.offline {
            background-color: rgba(244, 67, 54, 0.15);
            color: #c62828;
            border: 1px solid rgba(244, 67, 54, 0.3);
        }
        
        .network-status-icon {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 8px;
        }
        
        .network-status.online .network-status-icon {
            background-color: #4caf50;
            box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.3);
        }
        
        .network-status.offline .network-status-icon {
            background-color: #f44336;
            box-shadow: 0 0 0 3px rgba(244, 67, 54, 0.3);
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        
        .pulse {
            animation: pulse 2s infinite;
        }
    `;
    document.head.appendChild(styleEl);
}

// Wait for document to load
document.addEventListener('DOMContentLoaded', function() {
    // Add modern UI styles
    addGlobalStyles();
    // setTimeout(addTestAlertButton, 1000);
    // Add network status indicator
    createNetworkStatusIndicator();
    
    // Setup online/offline event listeners
    window.addEventListener('online', handleNetworkStatusChange);
    window.addEventListener('offline', handleNetworkStatusChange);
    
    // Check if Chart.js is loaded
    checkChartJsLoaded();
    
    // Initialize WebChannel to communicate with backend
    new QWebChannel(qt.webChannelTransport, function (channel) {
        backend = channel.objects.backend;
        
        // Set up event listeners for capture and auto-update buttons
        setupButtonListeners();
        createSoundToggleButton();
        // Connect signals from backend
        connectBackendSignals();
        
        // Initialize charts with performance optimizations
        if (chartJsLoaded) {
            initCharts();
        }
        
        // Add window resize handler with debounce to prevent performance issues
        window.addEventListener('resize', debounce(handleResize, 250));
        
        // Initial data load with a slight delay to ensure UI is ready
        setTimeout(updateAllData, 100);
    });
});

// Create network status indicator
function createNetworkStatusIndicator() {
    const networkPageContainer = document.querySelector('.network-page') || document.body;
    
    const statusElement = document.createElement('div');
    statusElement.id = 'networkStatus';
    statusElement.className = `network-status ${isOnline ? 'online' : 'offline'}`;
    
    statusElement.innerHTML = `
        <span class="network-status-icon"></span>
        <span class="network-status-text">${isOnline ? 'Online' : 'Offline'}</span>
    `;
    
    // Insert at beginning of network page
    if (networkPageContainer.firstChild) {
        networkPageContainer.insertBefore(statusElement, networkPageContainer.firstChild);
    } else {
        networkPageContainer.appendChild(statusElement);
    }
}

// Handle network status changes
function handleNetworkStatusChange() {
    isOnline = navigator.onLine;
    
    // Update network status indicator
    const statusElement = document.getElementById('networkStatus');
    if (statusElement) {
        statusElement.className = `network-status ${isOnline ? 'online' : 'offline'}`;
        statusElement.querySelector('.network-status-text').textContent = isOnline ? 'Online' : 'Offline';
    }
    
    // Show warning if offline
    if (!isOnline) {
        showInternetConnectionWarning();
    } else {
        // If we're back online, show a success notification
        showOnlineNotification();
        
        // Try to reload Chart.js if it wasn't loaded before
        if (!chartJsLoaded) {
            loadChartJs();
        }
    }
}

// Show notification when back online
function showOnlineNotification() {
    const existingOverlay = document.getElementById('notificationOverlay');
    if (existingOverlay) {
        document.body.removeChild(existingOverlay);
    }
    
    const overlay = document.createElement('div');
    overlay.id = 'notificationOverlay';
    overlay.className = 'overlay';
    
    overlay.innerHTML = `
        <div class="popup" style="border-top: 4px solid #4caf50;">
            <div class="popup-header">
                <div class="icon" style="background-color: #4caf50;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                        <polyline points="22 4 12 14.01 9 11.01"></polyline>
                    </svg>
                </div>
                <h3 class="popup-title">Back Online</h3>
            </div>
            <div class="popup-content">
                Your internet connection has been restored. The application will now function normally.
            </div>
            <div class="popup-actions">
                <button class="popup-button" style="background-color: #4caf50;">Continue</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(overlay);
    
    // Show with animation
    setTimeout(() => {
        overlay.classList.add('visible');
    }, 10);
    
    // Add click event to close
    const button = overlay.querySelector('.popup-button');
    button.addEventListener('click', function() {
        overlay.classList.remove('visible');
        setTimeout(() => {
            document.body.removeChild(overlay);
        }, 300);
    });
    
    // Auto close after 5 seconds
    setTimeout(() => {
        if (document.body.contains(overlay)) {
            overlay.classList.remove('visible');
            setTimeout(() => {
                if (document.body.contains(overlay)) {
                    document.body.removeChild(overlay);
                }
            }, 300);
        }
    }, 5000);
}

// Check if Chart.js is loaded and handle accordingly
function checkChartJsLoaded() {
    if (typeof Chart !== 'undefined') {
        chartJsLoaded = true;
    } else {
        // Show a notification about missing Chart.js
        showInternetConnectionWarning();
        
        // Try to load Chart.js dynamically with a fallback
        loadChartJs();
    }
}

// Show warning about internet connection with modern UI
function showInternetConnectionWarning() {
    // Remove existing overlay if any
    const existingOverlay = document.getElementById('internetWarningOverlay');
    if (existingOverlay) {
        document.body.removeChild(existingOverlay);
    }
    
    const overlay = document.createElement('div');
    overlay.id = 'internetWarningOverlay';
    overlay.className = 'overlay';
    
    overlay.innerHTML = `
        <div class="popup" style="border-top: 4px solid #f44336;">
            <div class="popup-header">
                <div class="icon">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="12" cy="12" r="10"></circle>
                        <line x1="12" y1="8" x2="12" y2="12"></line>
                        <line x1="12" y1="16" x2="12.01" y2="16"></line>
                    </svg>
                </div>
                <h3 class="popup-title">Connection Issue</h3>
            </div>
            <div class="popup-content">
                Internet connection issue detected. Chart.js could not be loaded. Please check your connection for full functionality.
            </div>
            <div class="popup-actions">
                <button class="popup-button pulse">Retry</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(overlay);
    
    // Show with animation
    setTimeout(() => {
        overlay.classList.add('visible');
    }, 10);
    
    // Add retry button functionality
    const retryButton = overlay.querySelector('.popup-button');
    retryButton.addEventListener('click', function() {
        overlay.classList.remove('visible');
        setTimeout(() => {
            document.body.removeChild(overlay);
            location.reload();
        }, 300);
    });
}

// Try to load Chart.js dynamically
function loadChartJs() {
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js';
    script.integrity = 'sha256-+8RZJua0aEWg+QVVKg4LEzETLBqzChG9Vy7LaF1Ip2k=';
    script.crossOrigin = 'anonymous';
    
    script.onload = function() {
        chartJsLoaded = true;
        console.log('Chart.js loaded successfully');
        
        // Hide warning if it exists
        const overlay = document.getElementById('internetWarningOverlay');
        if (overlay) {
            overlay.classList.remove('visible');
            setTimeout(() => {
                if (document.body.contains(overlay)) {
                    document.body.removeChild(overlay);
                }
            }, 300);
        }
        
        // Initialize charts
        initCharts();
        
        // Update data
        updateAllData();
    };
    
    script.onerror = function() {
        console.error('Failed to load Chart.js from CDN, trying fallback');
        
        // Try fallback CDN
        const fallbackScript = document.createElement('script');
        fallbackScript.src = 'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js';
        
        fallbackScript.onload = function() {
            chartJsLoaded = true;
            console.log('Chart.js loaded from fallback CDN');
            
            // Hide warning if it exists
            const overlay = document.getElementById('internetWarningOverlay');
            if (overlay) {
                overlay.classList.remove('visible');
                setTimeout(() => {
                    if (document.body.contains(overlay)) {
                        document.body.removeChild(overlay);
                    }
                }, 300);
            }
            
            // Initialize charts
            initCharts();
            
            // Update data
            updateAllData();
        };
        
        document.head.appendChild(fallbackScript);
    };
    
    document.head.appendChild(script);
    
    // Also load moment.js if needed
    if (typeof moment === 'undefined') {
        const momentScript = document.createElement('script');
        momentScript.src = 'https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.29.4/moment.min.js';
        document.head.appendChild(momentScript);
    }
}

// Setup all button event listeners safely
function setupButtonListeners() {
    // Setup capture button
    
    const captureButton = document.getElementById('startCapture');
    if (captureButton) {
        // Convert to modern button if needed
        if (!captureButton.classList.contains('modern-button')) {
            captureButton.className = 'modern-button';
            
            // Update icon if present
            const icon = captureButton.querySelector('.icon');
            if (icon) {
                icon.style.marginRight = '8px';
            }
        }
        
        // Safe way to connect click handler (prevents disconnection errors)
        if (captureButton.onclick) {
            captureButton.onclick = null;
        }
        captureButton.addEventListener('click', toggleCapture);
    }
    
    // Add auto-update toggle button if it doesn't exist
    addAutoUpdateButton();
}

// Connect backend signals safely
function connectBackendSignals() {
    if (backend) {
        // Safely connect signals with error handling
        try {
            // For alerts
            if (typeof backend.updateAlerts !== 'undefined') {
                backend.updateAlerts.connect(handleNewAlert);
            }
            
            // For network log updates
            if (typeof backend.updateNetworkLog !== 'undefined') {
                backend.updateNetworkLog.connect(debounce(handleDatabaseUpdate, 500));
            }
        } catch (error) {
            console.error("Error connecting backend signals:", error);
        }
    }
}

// Debounce function to limit how often a function can be called
function debounce(func, wait) {
    let timeout;
    return function(...args) {
        const context = this;
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(context, args), wait);
    };
}

// Add auto-update toggle button to the UI with modern styling
function addAutoUpdateButton() {
    // Look for existing button first
    let autoUpdateButton = document.getElementById('autoUpdateButton');
    
    if (!autoUpdateButton) {
        // Create button if it doesn't exist
        autoUpdateButton = document.createElement('button');
        autoUpdateButton.id = 'autoUpdateButton';
        autoUpdateButton.className = 'modern-button';
        autoUpdateButton.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon">
                <path d="M23 4v6h-6"></path>
                <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>
            </svg>
            Auto Update: OFF
        `;
        
        // Insert into DOM - find a good place to insert it
        const captureButton = document.getElementById('startCapture');
        if (captureButton && captureButton.parentNode) {
            captureButton.parentNode.insertBefore(autoUpdateButton, captureButton.nextSibling);
        } else {
            // Fallback - add to top level
            const headerArea = document.querySelector('.header-area') || document.body;
            headerArea.appendChild(autoUpdateButton);
        }
    }
    
    // Update styling to match modern design
    autoUpdateButton.style.backgroundColor = '#290a30'; // Dark purple when inactive
    
    // Set up click handler
    autoUpdateButton.addEventListener('click', toggleAutoUpdate);
}

// Toggle auto-update functionality
function toggleAutoUpdate() {
    autoUpdateEnabled = !autoUpdateEnabled;
    
    const autoUpdateButton = document.getElementById('autoUpdateButton');
    if (autoUpdateButton) {
        // Update button text and icon
        autoUpdateButton.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon">
                <path d="M23 4v6h-6"></path>
                <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>
            </svg>
            Auto Update: ${autoUpdateEnabled ? 'ON' : 'OFF'}
        `;
        
        if (autoUpdateEnabled) {
            // Update styles for active state
            autoUpdateButton.style.backgroundColor = '#8a2be2'; // Purple when active
            autoUpdateButton.classList.add('active');
            
            // Add subtle pulse animation
            const icon = autoUpdateButton.querySelector('.icon');
            if (icon) {
                icon.classList.add('pulse');
            }
            
            // Start auto-update interval
            if (autoUpdateInterval) {
                clearInterval(autoUpdateInterval);
            }
            
            autoUpdateInterval = setInterval(() => {
                // Only update if not already updating
                if (!isUpdating) {
                    updateAllData();
                }
            }, 5000); // 5 seconds interval
        } else {
            // Update styles for inactive state
            autoUpdateButton.style.backgroundColor = '#290a30'; // Dark when inactive
            autoUpdateButton.classList.remove('active');
            
            // Remove pulse animation
            const icon = autoUpdateButton.querySelector('.icon');
            if (icon) {
                icon.classList.remove('pulse');
            }
            
            // Clear interval
            if (autoUpdateInterval) {
                clearInterval(autoUpdateInterval);
                autoUpdateInterval = null;
            }
        }
    }
}

// Handle window resize - rebuild charts if needed
function handleResize() {
    if (!charts || !chartJsLoaded) return;
    
    // Only update when not currently updating data
    if (!isUpdating) {
        Object.values(charts).forEach(chart => {
            if (chart && typeof chart.resize === 'function') {
                chart.resize();
            }
        });
    }
}

// Initialize charts with performance optimizations
function initCharts() {
    if (!chartJsLoaded) {
        console.log("Chart.js not loaded yet, cannot initialize charts");
        return;
    }
    
    try {
        // Configure Chart.js defaults for better performance
        Chart.defaults.animation = false;
        Chart.defaults.responsive = true;
        Chart.defaults.maintainAspectRatio = false;
        Chart.defaults.plugins.tooltip.enabled = true;
        Chart.defaults.plugins.legend.labels.color = '#f0f0f0';
        
        // Fix for the grid color properties - make sure to set them properly
        if (Chart.defaults.scales.x) {
            Chart.defaults.scales.x.grid = Chart.defaults.scales.x.grid || {};
            Chart.defaults.scales.x.grid.color = 'rgba(255, 255, 255, 0.1)';
            Chart.defaults.scales.x.ticks = Chart.defaults.scales.x.ticks || {};
            Chart.defaults.scales.x.ticks.color = '#f0f0f0';
        }
        
        if (Chart.defaults.scales.y) {
            Chart.defaults.scales.y.grid = Chart.defaults.scales.y.grid || {};
            Chart.defaults.scales.y.grid.color = 'rgba(255, 255, 255, 0.1)';
            Chart.defaults.scales.y.ticks = Chart.defaults.scales.y.ticks || {};
            Chart.defaults.scales.y.ticks.color = '#f0f0f0';
        }
        
        // Initialize each chart with try-catch for error handling
        initTimelineChart();
        initProtocolChart();
        initSourceIPChart();
        initServicesChart();
        
    } catch (error) {
        console.error("Error initializing charts:", error);
    }
}

// Initialize timeline chart
function initTimelineChart() {
    try {
        const timelineCanvas = document.getElementById('timelineChart');
        if (!timelineCanvas) {
            console.warn("Timeline chart canvas not found");
            return;
        }
        
        charts.timeline = new Chart(timelineCanvas, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Network Traffic',
                    data: [],
                    borderColor: chartColors.border[0],
                    backgroundColor: chartColors.background[0],
                    tension: 0.1,
                    fill: true,
                    pointRadius: 0,
                    borderWidth: 1.5
                }]
            },
            options: {
                animation: false,
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'nearest',
                    axis: 'x',
                    intersect: false
                },
                scales: {
                    x: {
                        ticks: { 
                            maxRotation: 0, 
                            autoSkip: true,
                            maxTicksLimit: 8,
                            color: '#f0f0f0'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    },
                    y: {
                        beginAtZero: true,
                        ticks: {
                            color: '#f0f0f0'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        backgroundColor: 'rgba(41, 10, 48, 0.8)',
                        titleColor: '#f0f0f0',
                        bodyColor: '#f0f0f0',
                        borderColor: 'rgba(138, 43, 226, 0.8)',
                        borderWidth: 1
                    }
                },
                elements: {
                    line: {
                        borderWidth: 1.5
                    }
                }
            }
        });
    } catch (error) {
        console.error("Error initializing timeline chart:", error);
    }
}

// Initialize protocol chart
function initProtocolChart() {
    try {
        const protocolCanvas = document.getElementById('protocolChart');
        if (!protocolCanvas) {
            console.warn("Protocol chart canvas not found");
            return;
        }
        
        charts.protocol = new Chart(protocolCanvas, {
            type: 'doughnut',
            data: {
                labels: [],
                datasets: [{
                    data: [],
                    backgroundColor: chartColors.background,
                    borderColor: chartColors.border,
                    borderWidth: 1
                }]
            },
            options: {
                animation: false,
                responsive: true,
                maintainAspectRatio: false,
                cutout: '60%',
                plugins: {
                    legend: {
                        position: 'right',
                        labels: { 
                            color: '#f0f0f0', 
                            font: { size: 11 },
                            boxWidth: 12,
                            padding: 10
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(41, 10, 48, 0.8)',
                        titleColor: '#f0f0f0',
                        bodyColor: '#f0f0f0',
                        borderColor: 'rgba(138, 43, 226, 0.8)',
                        borderWidth: 1
                    }
                }
            }
        });
    } catch (error) {
        console.error("Error initializing protocol chart:", error);
    }
}

// Initialize source IP chart
function initSourceIPChart() {
    try {
        const sourceIPCanvas = document.getElementById('sourceIPChart');
        if (!sourceIPCanvas) {
            console.warn("Source IP chart canvas not found");
            return;
        }
        
        charts.sourceIP = new Chart(sourceIPCanvas, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{
                    label: 'Packet Count',
                    data: [],
                    backgroundColor: chartColors.background[0],
                    borderColor: chartColors.border[0],
                    borderWidth: 1
                }]
            },
            options: {
                animation: false,
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: '#f0f0f0'
                        }
                    },
                    y: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: '#f0f0f0'
                        }
                    }
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: 'rgba(41, 10, 48, 0.8)',
                        titleColor: '#f0f0f0',
                        bodyColor: '#f0f0f0',
                        borderColor: 'rgba(138, 43, 226, 0.8)',
                        borderWidth: 1
                    }
                }
            }
        });
    } catch (error) {
        console.error("Error initializing source IP chart:", error);
    }
}

// Initialize services chart
function initServicesChart() {
    try {
        const servicesCanvas = document.getElementById('servicesChart');
        if (!servicesCanvas) {
            console.warn("Services chart canvas not found");
            return;
        }
        
        charts.services = new Chart(servicesCanvas, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{
                    label: 'Packet Count',
                    data: [],
                    backgroundColor: chartColors.background[2],
                    borderColor: chartColors.border[2],
                    borderWidth: 1
                }]
            },
            options: {
                animation: false,
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: '#f0f0f0'
                        }
                    },
                    y: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: '#f0f0f0'
                        }
                    }
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: 'rgba(41, 10, 48, 0.8)',
                        titleColor: '#f0f0f0',
                        bodyColor: '#f0f0f0',
                        borderColor: 'rgba(138, 43, 226, 0.8)',
                        borderWidth: 1
                    }
                }
            }
        });
    } catch (error) {
        console.error("Error initializing services chart:", error);
    }
}

// Toggle network capture
function toggleCapture() {
    if (!backend) {
        console.error("Backend not initialized");
        return;
    }
    
    const captureButton = document.getElementById('startCapture');
    const captureStatus = document.getElementById('captureStatus');
    
    if (!captureButton || !captureStatus) {
        console.error("Required UI elements not found");
        return;
    }
    
    const statusText = captureStatus.querySelector('.status-text');
    
    if (!capturing) {
        // Use Promise handling with error detection
        backend.start_capture()
            .then(function(success) {
                if (success) {
                    capturing = true;
                    captureButton.innerHTML = '<span class="icon icon-monitor"></span> Stop Capture';
                    
                    if (statusText) {
                        statusText.innerHTML = '&nbsp;Running';
                        statusText.classList.add('active-capture');
                    }
                    
                    // Force an update of data
                    updateAllData();
                } else {
                    showNotification('Capture Error', 'Failed to start network capture', 'error');
                }
            })
            .catch(function(error) {
                console.error("Error starting capture:", error);
                showNotification('Capture Error', 'Exception while starting capture', 'error');
            });
    } else {
        backend.stop_capture()
            .then(function(success) {
                if (success) {
                    capturing = false;
                    captureButton.innerHTML = '<span class="icon icon-monitor"></span> Network Monitor';
                    
                    if (statusText) {
                        statusText.innerHTML = '&nbsp;Stopped';
                        statusText.classList.remove('active-capture');
                    }
                } else {
                    showNotification('Capture Error', 'Failed to stop network capture', 'error');
                }
            })
            .catch(function(error) {
                console.error("Error stopping capture:", error);
                showNotification('Capture Error', 'Exception while stopping capture', 'error');
            });
    }
}

// Handler for database updates - this is called whenever network logs are updated
function handleDatabaseUpdate(logData) {
    try {
        const data = JSON.parse(logData);
        
        // Update log count if it's different
        if (data.count && data.count !== lastLogCount) {
            lastLogCount = data.count;
            const countElement = document.getElementById('entryCount');
            if (countElement) {
                countElement.textContent = lastLogCount;
            }
            
            // Throttle updates to prevent performance issues
            const now = Date.now();
            if (now - lastUpdateTime > 2000 || autoUpdateEnabled) { // Update when auto-update enabled
                updateAllData();
                lastUpdateTime = now;
            }
        }
    } catch (e) {
        console.error("Error handling database update:", e);
    }
}

// Update all chart data from the backend
function updateAllData() {
    // Prevent multiple updates at once or if charts aren't ready
    if (isUpdating || !chartJsLoaded) return;
    
    isUpdating = true;
    lastUpdateTime = Date.now();
    
    // Show loaders
    showLoaders(true);
    
    // Create a promise array for all data fetches
    const promises = [
        fetchLogCount(),
        fetchNetworkData(),
        fetchTrafficSummary(),
        fetchAlertData()
    ];
    
    // Wait for all promises to resolve
    Promise.allSettled(promises)
        .then((results) => {
            // Process results with error handling
            results.forEach((result, index) => {
                if (result.status === 'rejected') {
                    console.error(`Promise ${index} failed:`, result.reason);
                }
            });
            
            // Hide loaders
            showLoaders(false);
            isUpdating = false;
        })
        .catch(error => {
            console.error("Error updating data:", error);
            showLoaders(false);
            isUpdating = false;
        });
}

// Fetch log count
function fetchLogCount() {
    if (!backend) {
        return Promise.reject("Backend not initialized");
    }
    
    return backend.get_log_count()
        .then(function(count) {
            const countElement = document.getElementById('entryCount');
            if (countElement) {
                countElement.textContent = count;
            }
            lastLogCount = count;
            return count;
        })
        .catch(error => {
            console.error("Error fetching log count:", error);
            return Promise.reject(error);
        });
}

// Fetch network data for timeline chart with sampling and throttling
function fetchNetworkData() {
    if (!backend) {
        return Promise.reject("Backend not initialized");
    }
    
    if (!chartJsLoaded || !charts.timeline) {
        return Promise.reject("Chart.js not loaded or timeline chart not initialized");
    }
    
    return backend.get_network_data()
        .then(function(data) {
            try {
                const parsedData = JSON.parse(data);
                updateTimelineChart(parsedData);
                
                const timelineLoading = document.getElementById('timelineLoading');
                if (timelineLoading) {
                    timelineLoading.style.display = 'none';
                }
                
                return parsedData;
            } catch (e) {
                console.error("Error parsing network data:", e);
                return Promise.reject(e);
            }
        })
        .catch(error => {
            console.error("Error fetching network data:", error);
            return Promise.reject(error);
        });
}

// Fetch traffic summary data with error handling
function fetchTrafficSummary() {
    if (!backend) {
        return Promise.reject("Backend not initialized");
    }
    
    if (!chartJsLoaded) {
        return Promise.reject("Chart.js not loaded");
    }
    
    return backend.get_traffic_summary()
        .then(function(data) {
            try {
                const summary = JSON.parse(data);
                
                // Update charts only if valid data is available
                if (summary && Object.keys(summary).length > 0) {
                    if (summary.protocol_distribution && charts.protocol) {
                        updateProtocolChart(summary.protocol_distribution);
                    }
                    if (summary.top_sources && charts.sourceIP) {
                        updateSourceIPChart(summary.top_sources);
                    }
                    if (summary.top_services && charts.services) {
                        updateServicesChart(summary.top_services);
                    }
                }
                
                // Hide loading indicators
                const protocolLoading = document.getElementById('protocolLoading');
                const sourceIPLoading = document.getElementById('sourceIPLoading');
                const servicesLoading = document.getElementById('servicesLoading');
                
                if (protocolLoading) protocolLoading.style.display = 'none';
                if (sourceIPLoading) sourceIPLoading.style.display = 'none';
                if (servicesLoading) servicesLoading.style.display = 'none';
                
                return summary;
            } catch (e) {
                console.error("Error parsing traffic summary:", e);
                return Promise.reject(e);
            }
        })
        .catch(error => {
            console.error("Error fetching traffic summary:", error);
            return Promise.reject(error);
        });
}

// Fetch alert data with error handling
function fetchAlertData() {
    if (!backend) {
        return Promise.reject("Backend not initialized");
    }
    
    return backend.get_alert_data()
        .then(function(data) {
            try {
                const alerts = JSON.parse(data);
                updateAlertsList(alerts);
                
                const alertsLoading = document.getElementById('alertsLoading');
                if (alertsLoading) {
                    alertsLoading.style.display = 'none';
                }
                
                return alerts;
            } catch (e) {
                console.error("Error parsing alert data:", e);
                return Promise.reject(e);
            }
        })
        .catch(error => {
            console.error("Error fetching alert data:", error);
            return Promise.reject(error);
        });
}

// Show/hide loaders on charts
function showLoaders(show) {
    const loaders = document.querySelectorAll('.loading');
    loaders.forEach(loader => {
        if (loader) {
            loader.style.display = show ? 'block' : 'none';
        }
    });
}

// Update timeline chart with data reduction for large datasets
function updateTimelineChart(logs) {
    if (!logs || logs.length === 0 || !charts.timeline) return;
    
    let labels = [];
    let data = [];
    
    // Apply downsampling if dataset is large (more than 60 points)
    if (logs.length > 60) {
        // Calculate step size to get ~30-60 points
        const step = Math.max(1, Math.ceil(logs.length / 50));
        
        for (let i = 0; i < logs.length; i += step) {
            const log = logs[i];
            const timestamp = new Date(log.timestamp);
            labels.push(moment(timestamp).format('HH:mm'));
            data.push(log.count);
        }
    } else {
        // Use all data points if dataset is small
        labels = logs.map(log => {
            const timestamp = new Date(log.timestamp);
            return moment(timestamp).format('HH:mm');
        });
        data = logs.map(log => log.count);
    }
    
    // Check if data has changed before updating
    const currentLabels = charts.timeline.data.labels || [];
    const currentData = charts.timeline.data.datasets[0].data || [];
    
    // Only update if data has changed
    const labelsChanged = labels.length !== currentLabels.length || 
                          !labels.every((v, i) => v === currentLabels[i]);
    
    const dataChanged = data.length !== currentData.length || 
                         !data.every((v, i) => v === currentData[i]);
    
    if (labelsChanged || dataChanged) {
        // Use the batch update pattern for better performance
        charts.timeline.data.labels = labels;
        charts.timeline.data.datasets[0].data = data;
        
        // Only update the chart once after all data changes
        charts.timeline.update('none');
    }
}

// Update protocol distribution chart with optimized rendering
function updateProtocolChart(protocolData) {
    if (!protocolData || !charts.protocol) return;
    
    // Sort protocols by count
    const sortedProtocols = Object.entries(protocolData)
        .sort((a, b) => b[1] - a[1]);
    
    // Get labels and data
    const labels = sortedProtocols.map(item => item[0]);
    const data = sortedProtocols.map(item => item[1]);
    
    // Check if data has changed before updating
    const currentLabels = charts.protocol.data.labels || [];
    const currentData = charts.protocol.data.datasets[0].data || [];
    
    const dataString = JSON.stringify(data);
    const currentDataString = JSON.stringify(currentData);
    
    if (JSON.stringify(labels) !== JSON.stringify(currentLabels) || 
        dataString !== currentDataString) {
        
        // Batch update
        charts.protocol.data.labels = labels;
        charts.protocol.data.datasets[0].data = data;
        charts.protocol.update('none');
    }
}

// Update source IP chart with optimized rendering and memoization
function updateSourceIPChart(sourceData) {
    if (!sourceData || !charts.sourceIP) return;
    
    // Sort by count and limit to top 8 (fewer for better readability)
    const sortedEntries = Object.entries(sourceData)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 8);
    
    const labels = sortedEntries.map(entry => entry[0]);
    const data = sortedEntries.map(entry => entry[1]);
    
    // Check if data has changed
    const currentLabels = charts.sourceIP.data.labels || [];
    const currentData = charts.sourceIP.data.datasets[0].data || [];
    
    if (JSON.stringify(labels) !== JSON.stringify(currentLabels) || 
        JSON.stringify(data) !== JSON.stringify(currentData)) {
        
        // Batch update
        charts.sourceIP.data.labels = labels;
        charts.sourceIP.data.datasets[0].data = data;
        charts.sourceIP.update('none');
    }
}

// Update services chart with optimized rendering
function updateServicesChart(servicesData) {
    if (!servicesData || !charts.services) return;
    
    // Sort by count and limit to top 8
    const sortedEntries = Object.entries(servicesData)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 8);
    
    const labels = sortedEntries.map(entry => getPortServiceName(parseInt(entry[0])));
    const data = sortedEntries.map(entry => entry[1]);
    
    // Check if data has changed
    const currentLabels = charts.services.data.labels || [];
    const currentData = charts.services.data.datasets[0].data || [];
    
    if (JSON.stringify(labels) !== JSON.stringify(currentLabels) || 
        JSON.stringify(data) !== JSON.stringify(currentData)) {
        
        // Batch update
        charts.services.data.labels = labels;
        charts.services.data.datasets[0].data = data;
        charts.services.update('none');
    }
}

// Cache for port to service name mapping
const portServiceCache = {};

// Get service name for well-known ports (with caching)
function getPortServiceName(port) {
    // Return from cache if available
    if (portServiceCache[port]) {
        return portServiceCache[port];
    }
    
    const commonPorts = {
        20: 'FTP Data (20)',
        21: 'FTP (21)',
        22: 'SSH (22)',
        23: 'Telnet (23)',
        25: 'SMTP (25)',
        53: 'DNS (53)',
        67: 'DHCP (67)',
        68: 'DHCP (68)',
        80: 'HTTP (80)',
        110: 'POP3 (110)',
        123: 'NTP (123)',
        143: 'IMAP (143)',
        161: 'SNMP (161)',
        162: 'SNMP (162)',
        389: 'LDAP (389)',
        443: 'HTTPS (443)',
        445: 'SMB (445)',
        465: 'SMTPS (465)',
        587: 'SMTP (587)',
        993: 'IMAPS (993)',
        995: 'POP3S (995)',
        1433: 'MSSQL (1433)',
        1521: 'Oracle (1521)',
        3306: 'MySQL (3306)',
        3389: 'RDP (3389)',
        5060: 'SIP (5060)',
        5061: 'SIP (5061)',
        5432: 'PostgreSQL (5432)',
        8080: 'HTTP Alt (8080)',
        8443: 'HTTPS Alt (8443)'
    };
    
    // Cache the result before returning
    const result = commonPorts[port] || `Port ${port}`;
    portServiceCache[port] = result;
    
    return result;
}

// Update alerts list with memory-efficient DOM updates
function updateAlertsList(alerts) {
    if (!alerts || alerts.length === 0) return;
    
    const alertList = document.getElementById('alertList');
    if (!alertList) return;
    
    // Create a document fragment for batch DOM updates
    const fragment = document.createDocumentFragment();
    
    // Limit to 15 alerts for better performance
    const limitedAlerts = alerts.slice(0, 15);
    
    // Memory-efficient alert creation using innerHTML
    limitedAlerts.forEach(alert => {
        const alertElement = document.createElement('div');
        alertElement.className = `alert-item alert-${alert.severity.toLowerCase()}`;
        
        // Set innerHTML once to minimize reflows
        alertElement.innerHTML = `
            <div class="alert-details">
                <div class="alert-type">${escapeHTML(alert.alert_type)}</div>
                <div class="alert-description">${escapeHTML(alert.description)}</div>
            </div>
            <div class="alert-meta">
                <div class="alert-source">${escapeHTML(alert.source_ip)}</div>
                <div class="alert-time">${formatTime(alert.timestamp)}</div>
            </div>
        `;
        
        fragment.appendChild(alertElement);
    });
    
    // Use replaceChildren for better performance if supported
    if (alertList.replaceChildren) {
        alertList.replaceChildren(fragment);
    } else {
        // Fallback for older browsers
        alertList.innerHTML = '';
        alertList.appendChild(fragment);
    }
}

// Escape HTML to prevent XSS
function escapeHTML(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

// Handle new alert from backend
function handleNewAlert(alertData) {
    try {
        const alert = JSON.parse(alertData);
        
        // Show notification
        showNotification(alert.alert_type, alert.description, alert.severity);
        
        // Only update the alerts list, not all charts
        fetchAlertData().catch(error => {
            console.error("Error fetching alert data after new alert:", error);
        });
    } catch (e) {
        console.error("Error handling new alert:", e);
    }
}


// Add sound toggle functionality to the UI
function createSoundToggleButton() {
    // Look for existing button first
    let soundToggleButton = document.getElementById('sound-toggle-button');
    
    if (!soundToggleButton) {
        // Create the toggle button
        soundToggleButton = document.createElement('button');
        soundToggleButton.id = 'sound-toggle-button';
        soundToggleButton.className = 'modern-button';
        
        // Create icon element
        const iconElement = document.createElement('span');
        iconElement.className = 'icon';
        iconElement.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path></svg>';
        
        // Create text span
        const textElement = document.createElement('span');
        textElement.textContent = 'Sound: ON';
        
        // Add icon and text to button
        soundToggleButton.appendChild(iconElement);
        soundToggleButton.appendChild(textElement);
        
        // Insert next to auto update button
        const autoUpdateButton = document.getElementById('autoUpdateButton');
        if (autoUpdateButton && autoUpdateButton.parentNode) {
            autoUpdateButton.parentNode.insertBefore(soundToggleButton, autoUpdateButton.nextSibling);
        } else {
            // Fallback - add to header area
            const headerArea = document.querySelector('.header-area') || document.body;
            headerArea.appendChild(soundToggleButton);
        }
    }
    
    // Initialize the button state
    updateSoundButtonState();
    
    // Add click event listener
    soundToggleButton.addEventListener('click', toggleAlertSound);
}

// Update the button appearance based on current sound state
function updateSoundButtonState() {
    if (!backend) return;
    
    backend.get_sound_status().then(enabled => {
        const soundToggleButton = document.getElementById('sound-toggle-button');
        if (!soundToggleButton) return;
        
        const iconElement = soundToggleButton.querySelector('.icon');
        const textElement = soundToggleButton.querySelector('span:not(.icon)');
        
        if (enabled) {
            soundToggleButton.classList.add('active');
            iconElement.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path></svg>';
            textElement.textContent = 'Sound: ON';
            soundToggleButton.style.backgroundColor = '#8a2be2'; // Purple when active
        } else {
            soundToggleButton.classList.remove('active');
            iconElement.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><line x1="23" y1="9" x2="17" y2="15"></line><line x1="17" y1="9" x2="23" y2="15"></line></svg>';
            textElement.textContent = 'Sound: OFF';
            soundToggleButton.style.backgroundColor = '#290a30'; // Dark when inactive
        }
    });
}

// Toggle alert sound
function toggleAlertSound() {
    if (!backend) return;
    
    backend.get_sound_status().then(currentStatus => {
        backend.toggle_alert_sound(!currentStatus).then(() => {
            // Update button state after toggle
            updateSoundButtonState();
            
            // Show notification
            showNotification(
                !currentStatus ? 'Alert Sound Enabled' : 'Alert Sound Disabled',
                !currentStatus ? 'You will now hear sound notifications for alerts.' : 'Sound notifications have been turned off.'
            );
        });
    });
}

// Show notification with RAM-friendly animation
function showNotification(title, message, severity) {
    const notification = document.getElementById('notification');
    if (!notification) return;
    
    // Set notification content
    const notificationTitle = notification.querySelector('.notification-title');
    const notificationMessage = notification.querySelector('.notification-message');
    
    if (notificationTitle) notificationTitle.textContent = title || '';
    if (notificationMessage) notificationMessage.textContent = message || '';
    
    // Set notification class based on severity
    notification.className = `notification-${(severity || 'info').toLowerCase()}`;
    
    // Show notification
    notification.style.display = 'flex';
    notification.style.opacity = '0';
    notification.style.transform = 'translateX(100%)';
    
    // Use requestAnimationFrame for smoother animation
    requestAnimationFrame(() => {
        notification.style.opacity = '1';
        notification.style.transform = 'translateX(0)';
    });
    
    // Hide notification after 5 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(100%)';
        
        // Remove from DOM after animation
        setTimeout(() => {
            notification.style.display = 'none';
        }, 300);
    }, 5000);
}

// function addTestAlertButton() {
//     // Create test button (small button for development purposes)
//     const testButton = document.createElement('button');
//     testButton.id = 'test-alert-button';
//     testButton.className = 'modern-button';
//     testButton.style.backgroundColor = '#6c757d';  // Gray color to distinguish it
//     testButton.style.fontSize = '12px';           // Smaller font size
//     testButton.style.padding = '5px 10px';        // Smaller padding
    
//     // Add icon and text
//     testButton.innerHTML = `
//         <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" 
//             stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon">
//             <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
//             <line x1="12" y1="9" x2="12" y2="13"></line>
//             <line x1="12" y1="17" x2="12.01" y2="17"></line>
//         </svg>
//         Test Alert
//     `;
    
//     // Add click event listener
//     testButton.addEventListener('click', () => {
//         testAlertSound();
        
//         // Add visual feedback
//         testButton.style.backgroundColor = '#007bff';
//         setTimeout(() => {
//             testButton.style.backgroundColor = '#6c757d';
//         }, 300);
//     });
    
//     // Add to the page in a developer-friendly area
//     // Option 1: Add to header-area
//     const headerArea = document.querySelector('.header-area');
//     if (headerArea) {
//         // Create a small container for the test button
//         const testContainer = document.createElement('div');
//         testContainer.style.marginLeft = 'auto';  // Push to the right
//         testContainer.appendChild(testButton);
//         headerArea.appendChild(testContainer);
//     } else {
//         // Option 2: Add to the body
//         testButton.style.position = 'fixed';
//         testButton.style.right = '10px';
//         testButton.style.bottom = '10px';
//         testButton.style.zIndex = '9999';
//         document.body.appendChild(testButton);
//     }
// }
// // Function to connect the Test Alert button to the Python backend
// function testAlertSound() {
//     // Check if backend is available
//     if (typeof backend !== 'undefined') {
//         // Call the backend's test_alert method
//         backend.test_alert(function(alertJson) {
//             try {
//                 // Parse the returned alert data
//                 const alert = JSON.parse(alertJson);
//                 console.log("Test alert created:", alert);
                
//                 // You could show a confirmation message if needed
//                 showToast(`Created ${alert.severity} test alert: ${alert.description}`);
//             } catch (e) {
//                 console.error("Error processing test alert response:", e);
//             }
//         });
//     } else {
//         console.error("Backend not available. Cannot create test alert.");
//         showToast("Backend not available", "error");
//     }
// }


// // Helper function to show a toast notification
// function showToast(message, type = "info") {
//     // Create toast element if it doesn't exist
//     let toast = document.getElementById('toast-notification');
//     if (!toast) {
//         toast = document.createElement('div');
//         toast.id = 'toast-notification';
//         toast.style.position = 'fixed';
//         toast.style.bottom = '20px';
//         toast.style.right = '20px';
//         toast.style.minWidth = '250px';
//         toast.style.padding = '15px';
//         toast.style.borderRadius = '5px';
//         toast.style.boxShadow = '0 4px 8px rgba(0,0,0,0.2)';
//         toast.style.zIndex = '10000';
//         toast.style.transition = 'opacity 0.5s ease';
//         toast.style.fontFamily = 'Arial, sans-serif';
//         document.body.appendChild(toast);
//     }
    
//     // Set style based on message type
//     switch(type) {
//         case "error":
//             toast.style.backgroundColor = '#dc3545';
//             toast.style.color = 'white';
//             break;
//         case "warning":
//             toast.style.backgroundColor = '#ffc107';
//             toast.style.color = 'black';
//             break;
//         case "success":
//             toast.style.backgroundColor = '#28a745';
//             toast.style.color = 'white';
//             break;
//         case "info":
//         default:
//             toast.style.backgroundColor = '#17a2b8';
//             toast.style.color = 'white';
//     }
    
//     // Set message and show toast
//     toast.textContent = message;
//     toast.style.opacity = '1';
    
//     // Hide after 3 seconds
//     setTimeout(() => {
//         toast.style.opacity = '0';
//     }, 3000);
// }




// Format timestamp for display with caching
const timeFormatCache = {};

function formatTime(timestamp) {
    if (!timestamp) return '';
    
    // Check cache first
    if (timeFormatCache[timestamp]) {
        return timeFormatCache[timestamp];
    }
    
    // Format and cache the result
    const formatted = moment(timestamp).format('HH:mm:ss');
    
    // Only cache up to 100 timestamps to avoid memory issues
    if (Object.keys(timeFormatCache).length > 100) {
        // Clear half the cache when it gets too large
        const keys = Object.keys(timeFormatCache);
        for (let i = 0; i < 50; i++) {
            delete timeFormatCache[keys[i]];
        }
    }
    
    timeFormatCache[timestamp] = formatted;
    return formatted;
}