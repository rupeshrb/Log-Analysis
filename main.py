import os
import sys

from PySide6.QtCore import QUrl, QTimer, Qt
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtWidgets import QApplication

# Import custom modules with better error handling
try:
    from assets.py.home import BackendClass_hom
    from assets.py.log import BackendClass_log
    from assets.py.system_analysis import BackendClass_sys
    from ui_Dashboard_main import *
    from Custom_Widgets import *
except ImportError as e:
    print(f"Error importing module: {e}")
    # Add fallback handling or exit gracefully

# Improved resource path function
def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        full_path = os.path.join(base_path, relative_path)
        # Debug: Print the path being used
        print(f"Loading resource: {full_path}")
        if not os.path.exists(full_path):
            print(f"WARNING: Resource not found: {full_path}")
        return full_path
    except Exception as e:
        print(f"Error resolving path '{relative_path}': {e}")
        return relative_path

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # Debug: Print available UI elements
        print(f"UI elements available: {dir(self.ui)}")
        
        # Set window flags for custom title bar
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Load custom style with error handling
        try:
            print("Loading JSON style...")
            loadJsonStyle(self, self.ui)
            print("JSON style loaded successfully")
        except Exception as e:
            print(f"Error loading JSON style: {e}")
            # Continue without the style rather than crashing
        
        # Initialize webviews with error handling
        self.setup_home_webview()
        self.setup_log_webview()
        self.setup_system_webview()
        
        # Setup UI actions with better error handling
        self.setupActions()
        
        # Make sure the window is visible
        print("Showing main window")
        self.show()
        
        # Add a startup timer to ensure the UI is fully initialized
        QTimer.singleShot(100, self.check_ui_state)

    def check_ui_state(self):
        """Verify UI components are properly initialized"""
        try:
            print("Checking UI state...")
            if hasattr(self.ui, 'leftMenu'):
                print(f"Left menu exists and has size: {self.ui.leftMenu.size()}")
            if hasattr(self.ui, 'mainPages'):
                print(f"Main pages stack exists with count: {self.ui.mainPages.count()}")
        except Exception as e:
            print(f"Error checking UI state: {e}")

    def setup_home_webview(self):
        """Setup home webview with error handling"""
        try:
            print("Setting up home webview")
            self.webview_home = QWebEngineView(self)
            
            # Configure web settings
            settings = self.webview_home.page().settings()
            settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
            
            # Set up web channel
            self.channel_home = QWebChannel()
            self.backend_home = BackendClass_hom()  # Backend class for home page
            self.channel_home.registerObject("backend", self.backend_home)
            self.webview_home.page().setWebChannel(self.channel_home)

            # Load the home HTML using resource_path
            home_html_file = resource_path('assets/html/home.html')
            print(f"Loading home HTML from: {home_html_file}")
            self.webview_home.load(QUrl.fromLocalFile(home_html_file))
            
            # Connect to loadFinished to debug loading issues
            self.webview_home.loadFinished.connect(self.on_home_load_finished)

            # Add the home webview to the layout
            if hasattr(self.ui, 'verticalLayout_16'):
                print("Adding home webview to layout")
                self.ui.verticalLayout_16.addWidget(self.webview_home, stretch=1)
            else:
                print("WARNING: verticalLayout_16 not found!")
        except Exception as e:
            print(f"Error setting up home webview: {e}")

    def setup_log_webview(self):
        """Setup log webview with error handling"""
        try:
            print("Setting up log webview")
            self.webview_log = QWebEngineView(self)
            settings_log = self.webview_log.page().settings()
            settings_log.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
            settings_log.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
            settings_log.setAttribute(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, True)
            settings_log.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
            
            self.channel_log = QWebChannel()
            self.backend_log = BackendClass_log()
            self.channel_log.registerObject("backend", self.backend_log)
            self.webview_log.page().setWebChannel(self.channel_log)
            
            # Load the Log HTML using resource_path
            log_html_file = resource_path('assets/html/log.html')
            print(f"Loading log HTML from: {log_html_file}")
            self.webview_log.load(QUrl.fromLocalFile(log_html_file))
            
            # Add the webview to the layout for page
            if hasattr(self.ui, 'verticalLayout_17'):
                print("Adding log webview to layout")
                self.ui.verticalLayout_17.addWidget(self.webview_log, stretch=1)
            else:
                print("WARNING: verticalLayout_17 not found!")
        except Exception as e:
            print(f"Error setting up log webview: {e}")

    def setup_system_webview(self):
        """Setup system analysis webview with error handling"""
        try:
            print("Setting up system analysis webview")
            self.webview_system = QWebEngineView(self)
            settings_sys = self.webview_system.page().settings()
            settings_sys.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
            settings_sys.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
            settings_sys.setAttribute(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, True)
            settings_sys.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
            
            self.channel_system = QWebChannel()
            self.backend_system = BackendClass_sys()
            self.channel_system.registerObject("backend", self.backend_system)
            self.webview_system.page().setWebChannel(self.channel_system)

            # Load the system analysis HTML using resource_path
            system_html_file = resource_path('assets/html/system_analysis.html')
            print(f"Loading system HTML from: {system_html_file}")
            self.webview_system.load(QUrl.fromLocalFile(system_html_file))

            # Add the system analysis webview to the layout for page_9
            if hasattr(self.ui, 'verticalLayout_19'):
                print("Adding system webview to layout")
                self.ui.verticalLayout_19.addWidget(self.webview_system, stretch=1)
            else:
                print("WARNING: verticalLayout_19 not found!")
        except Exception as e:
            print(f"Error setting up system webview: {e}")

    def on_home_load_finished(self, success):
        """Debug callback to check if the page loaded successfully"""
        if success:
            print("Home page loaded successfully!")
            # You can inspect JavaScript console logs
            self.webview_home.page().runJavaScript(
                "console.log('Page loaded from Python side!'); document.body.innerHTML;",
                0,
                lambda result: print(f"HTML content length: {len(result) if result else 'empty'}")
            )
        else:
            print("Failed to load home page!")
            # Get more error information
            self.webview_home.page().runJavaScript(
                "console.error('Failed to load properly'); document.documentElement.outerHTML;",
                0,
                lambda result: print(f"Failed HTML content: {result[:100] if result else 'None'}...")
            )
   
    def setupActions(self):
        """Set up UI action connections with error handling"""
        try:
            print("Setting up UI actions")
            
            # Connect menu buttons with error handling
            if hasattr(self.ui, 'infoBtn') and hasattr(self.ui, 'centerMenu'):
                print("Connecting infoBtn")
                self.ui.infoBtn.clicked.connect(lambda: self.ui.centerMenu.expandMenu())
            if hasattr(self.ui, 'helpBtn') and hasattr(self.ui, 'centerMenu'):
                print("Connecting helpBtn")
                self.ui.helpBtn.clicked.connect(lambda: self.ui.centerMenu.expandMenu())
            if hasattr(self.ui, 'closeCenterMenuBtn'):
                print("Connecting closeCenterMenuBtn")
                self.ui.closeCenterMenuBtn.clicked.connect(self.closeCenterMenu)
            
            # Setup window control buttons with error handling
            if hasattr(self.ui, 'minimizeAppBtn'):
                print("Connecting minimizeAppBtn")
                self.ui.minimizeAppBtn.clicked.connect(lambda: self.showMinimized())
            if hasattr(self.ui, 'maximizeAppBtn'):
                print("Connecting maximizeAppBtn")
                self.ui.maximizeAppBtn.clicked.connect(lambda: self.toggleMaximized())
            if hasattr(self.ui, 'closeAppBtn'):
                print("Connecting closeAppBtn")
                self.ui.closeAppBtn.clicked.connect(lambda: self.close())
                
            # Setup window dragging with error handling
            if hasattr(self.ui, 'titleBar'):
                print("Setting up titleBar drag functionality")
                self.ui.titleBar.mouseMoveEvent = self.moveWindow
                self.ui.titleBar.mousePressEvent = self.mousePressEvent
            else:
                print("WARNING: titleBar not found!")
        except Exception as e:
            print(f"Error setting up actions: {e}")
   
    def mousePressEvent(self, event):
        """Record the drag position when mouse is pressed"""
        self.dragPos = event.globalPosition().toPoint()
        
    def moveWindow(self, event):
        """Move the window when dragged by titleBar"""
        try:
            # Check if left mouse button is pressed
            if event.buttons() == Qt.LeftButton:
                # Move window
                self.move(self.pos() + event.globalPosition().toPoint() - self.dragPos)
                self.dragPos = event.globalPosition().toPoint()
                event.accept()
        except Exception as e:
            print(f"Error moving window: {e}")
            
    def toggleMaximized(self):
        """Toggle between maximized and normal window state"""
        try:
            if self.isMaximized():
                self.showNormal()
            else:
                self.showMaximized()
        except Exception as e:
            print(f"Error toggling maximized state: {e}")
            
    def closeCenterMenu(self):
        """Close the center menu and update button styles"""
        try:
            # Collapse the center menu
            if hasattr(self.ui, 'centerMenu'):
                print("Collapsing center menu")
                self.ui.centerMenu.collapseMenu()
            
            # Change the color of the buttons
            self.changeButtonColor()
        except Exception as e:
            print(f"Error closing center menu: {e}")
        
    def changeButtonColor(self):
        """Change the color of menu buttons"""
        try:
            # Change the color of the buttons
            if hasattr(self.ui, 'infoBtn'):
                self.ui.infoBtn.setStyleSheet("background-color: #290a30; color:rgb(255, 255, 255) ;")
            if hasattr(self.ui, 'helpBtn'):
                self.ui.helpBtn.setStyleSheet("background-color: #290a30; color:rgb(255, 255, 255) ;")
        except Exception as e:
            print(f"Error changing button colors: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Enable console output for debugging
    print("Application starting...")
    
    # Enable QWebEngineView debugging if needed
    os.environ["QTWEBENGINE_REMOTE_DEBUGGING"] = "9222"
    
    try:
        window = MainWindow()
        window.show()
        print("Main window created and shown")
        sys.exit(app.exec())
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)