import os
import sys

from PySide6.QtCore import QUrl, QTimer, Qt, QPropertyAnimation, QEasingCurve, QRect
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtWidgets import QApplication, QMainWindow

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
        # === MANUAL WINDOW TITLE AND ICON SETUP ===
        try:
            # Set window title
            self.setWindowTitle("Log Analysis")
            print("Window title set to: Log Analysis")
            
            # Set window icon using resource path
            icon_path = resource_path("log.ico")  # Remove :/ prefix for file path
            if os.path.exists(icon_path):
                from PySide6.QtGui import QIcon
                self.setWindowIcon(QIcon(icon_path))
                print(f"Window icon set from: {icon_path}")
            else:
                print(f"WARNING: Icon file not found at: {icon_path}")
                # Try alternative path
                alt_icon_path = resource_path("assets/images/log.png")
                if os.path.exists(alt_icon_path):
                    from PySide6.QtGui import QIcon
                    self.setWindowIcon(QIcon(alt_icon_path))
                    print(f"Window icon set from alternative path: {alt_icon_path}")
                else:
                    print("WARNING: Icon file not found at alternative path either")
                    
        except Exception as e:
            print(f"Error setting window title/icon: {e}")
        # Debug: Print available UI elements
        print(f"UI elements available: {dir(self.ui)}")
        
        # Set window flags for custom title bar
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Initialize drag position for window movement
        self.dragPos = None
        
        # Initialize menu states
        self.leftMenuExpanded = False
        self.centerMenuExpanded = False
        
        # Skip JSON style loading - use manual connections only
        print("Skipping JSON style loading - using manual connections")
        
        # Initialize webviews with error handling
        self.setup_home_webview()
        self.setup_log_webview()
        self.setup_system_webview()
        
        # Setup manual button connections (this replaces JSON style functionality)
        self.setup_all_manual_connections()
        
        # Setup window dragging
        self.setup_window_dragging()
        
        # Initialize menu sizes
        self.setup_initial_menu_states()
        
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

    def setup_all_manual_connections(self):
        """Setup all manual button connections to replace JSON style system"""
        try:
            print("Setting up all manual button connections...")
            
            # === NAVIGATION BUTTONS - Main Menu ===
            self.setup_main_navigation_buttons()
            
            # === WINDOW CONTROL BUTTONS ===
            self.setup_window_control_buttons()
            
            # === MENU TOGGLE BUTTONS ===
            self.setup_menu_toggle_buttons()
            
            # === CENTER MENU BUTTONS ===
            self.setup_center_menu_buttons()
            
            # === BUTTON GROUPS FOR STYLING ===
            self.setup_button_groups()
            
            print("All manual button connections completed successfully!")
            
        except Exception as e:
            print(f"Error setting up manual connections: {e}")

    def setup_main_navigation_buttons(self):
        """Setup main navigation buttons (Home, Log, System)"""
        try:
            print("Setting up main navigation buttons...")
            
            # Home button
            if hasattr(self.ui, 'homeBtn'):
                print("Connecting homeBtn")
                self.ui.homeBtn.clicked.connect(lambda: self.navigate_to_main_page('page_6', 'homeBtn'))
                
            # Log button  
            if hasattr(self.ui, 'logBtn'):
                print("Connecting logBtn")
                self.ui.logBtn.clicked.connect(lambda: self.navigate_to_main_page('page_7', 'logBtn'))
                
            # System button
            if hasattr(self.ui, 'systemBtn'):
                print("Connecting systemBtn")
                self.ui.systemBtn.clicked.connect(lambda: self.navigate_to_main_page('page_9', 'systemBtn'))
                
            # Set initial page to Home
            if hasattr(self.ui, 'mainPages') and hasattr(self.ui, 'page_6'):
                self.ui.mainPages.setCurrentWidget(self.ui.page_6)
                self.update_main_navigation_styles('homeBtn')
                
        except Exception as e:
            print(f"Error setting up main navigation buttons: {e}")

    def setup_window_control_buttons(self):
        """Setup window control buttons (minimize, maximize, close)"""
        try:
            print("Setting up window control buttons...")
            
            # Minimize button
            if hasattr(self.ui, 'minimizeBtn'):
                print("Connecting minimizeBtn")
                self.ui.minimizeBtn.clicked.connect(self.showMinimized)
            elif hasattr(self.ui, 'minimizeAppBtn'):
                print("Connecting minimizeAppBtn")
                self.ui.minimizeAppBtn.clicked.connect(self.showMinimized)
                
            # Close button
            if hasattr(self.ui, 'closeBtn'):
                print("Connecting closeBtn")
                self.ui.closeBtn.clicked.connect(self.close)
            elif hasattr(self.ui, 'closeAppBtn'):
                print("Connecting closeAppBtn")
                self.ui.closeAppBtn.clicked.connect(self.close)
                
            # Restore/Maximize button
            if hasattr(self.ui, 'restoreBtn'):
                print("Connecting restoreBtn")
                self.ui.restoreBtn.clicked.connect(self.toggle_maximize_restore)
            elif hasattr(self.ui, 'maximizeAppBtn'):
                print("Connecting maximizeAppBtn")
                self.ui.maximizeAppBtn.clicked.connect(self.toggle_maximize_restore)
                
        except Exception as e:
            print(f"Error setting up window control buttons: {e}")

    def setup_menu_toggle_buttons(self):
        """Setup menu toggle buttons"""
        try:
            print("Setting up menu toggle buttons...")
            
            # Left menu toggle button
            if hasattr(self.ui, 'menuBtn'):
                print("Connecting menuBtn for left menu toggle")
                self.ui.menuBtn.clicked.connect(self.toggle_left_menu)
                
            # Center menu close button
            if hasattr(self.ui, 'closeCenterMenuBtn'):
                print("Connecting closeCenterMenuBtn")
                self.ui.closeCenterMenuBtn.clicked.connect(self.close_center_menu)
                
        except Exception as e:
            print(f"Error setting up menu toggle buttons: {e}")

    def setup_center_menu_buttons(self):
        """Setup center menu navigation buttons"""
        try:
            print("Setting up center menu buttons...")
            
            # Info button
            if hasattr(self.ui, 'infoBtn'):
                print("Connecting infoBtn")
                self.ui.infoBtn.clicked.connect(lambda: self.navigate_to_center_page('page_2', 'infoBtn'))
                
            # Help button
            if hasattr(self.ui, 'helpBtn'):
                print("Connecting helpBtn")
                self.ui.helpBtn.clicked.connect(lambda: self.navigate_to_center_page('page_3', 'helpBtn'))
                
        except Exception as e:
            print(f"Error setting up center menu buttons: {e}")

    def setup_button_groups(self):
        """Setup button group styling"""
        try:
            print("Setting up button groups...")
            
            # Main navigation button group
            self.main_nav_buttons = ['homeBtn', 'logBtn', 'systemBtn']
            
            # Center menu button group  
            self.center_menu_buttons = ['infoBtn', 'helpBtn']
            
            # Apply initial styles
            self.reset_main_navigation_styles()
            self.reset_center_menu_styles()
            
        except Exception as e:
            print(f"Error setting up button groups: {e}")

    def setup_window_dragging(self):
        """Setup window dragging functionality"""
        try:
            print("Setting up window dragging...")
            
            # Try different header/titlebar names
            header_candidates = ['header', 'titleBar', 'topBar']
            
            for header_name in header_candidates:
                if hasattr(self.ui, header_name):
                    print(f"Setting up drag functionality for {header_name}")
                    header_widget = getattr(self.ui, header_name)
                    header_widget.mousePressEvent = self.mousePressEvent
                    header_widget.mouseMoveEvent = self.moveWindow
                    break
            else:
                print("WARNING: No header/titleBar found for window dragging!")
                
        except Exception as e:
            print(f"Error setting up window dragging: {e}")

    def setup_initial_menu_states(self):
        """Setup initial menu states and sizes"""
        try:
            print("Setting up initial menu states...")
            
            # Left menu - start collapsed
            if hasattr(self.ui, 'leftMenu'):
                self.ui.leftMenu.setFixedWidth(45)
                self.leftMenuExpanded = False
                print("Left menu set to collapsed state (45px)")
                
            # Center menu - start collapsed
            if hasattr(self.ui, 'centerMenu'):
                self.ui.centerMenu.setFixedWidth(0)
                self.centerMenuExpanded = False
                print("Center menu set to collapsed state (0px)")
                
        except Exception as e:
            print(f"Error setting up initial menu states: {e}")

    # === NAVIGATION METHODS ===
    
    def navigate_to_main_page(self, page_name, button_name):
        """Navigate to a specific page in mainPages stack"""
        try:
            if hasattr(self.ui, 'mainPages') and hasattr(self.ui, page_name):
                page_widget = getattr(self.ui, page_name)
                self.ui.mainPages.setCurrentWidget(page_widget)
                print(f"Navigated to {page_name}")
                
                # Update button styles for active state
                self.update_main_navigation_styles(button_name)
            else:
                print(f"ERROR: Cannot navigate to {page_name} - widget not found")
        except Exception as e:
            print(f"Error navigating to {page_name}: {e}")
    
    def navigate_to_center_page(self, page_name, button_name):
        """Navigate to a center menu page and expand center menu"""
        try:
            if hasattr(self.ui, 'centerMenuPages') and hasattr(self.ui, page_name):
                page_widget = getattr(self.ui, page_name)
                self.ui.centerMenuPages.setCurrentWidget(page_widget)
                print(f"Navigated to center page {page_name}")
                
                # Expand center menu
                self.expand_center_menu()
                
                # Update button styles
                self.update_center_menu_styles(button_name)
                
            else:
                print(f"ERROR: Cannot navigate to center page {page_name} - widget not found")
        except Exception as e:
            print(f"Error navigating to center page {page_name}: {e}")

    # === MENU CONTROL METHODS ===
    
    def toggle_left_menu(self):
        """Toggle left menu expansion with animation"""
        try:
            if hasattr(self.ui, 'leftMenu'):
                if self.leftMenuExpanded:
                    self.collapse_left_menu()
                else:
                    self.expand_left_menu()
        except Exception as e:
            print(f"Error toggling left menu: {e}")
    
    def expand_left_menu(self):
        """Expand left menu"""
        try:
            if hasattr(self.ui, 'leftMenu'):
                self.ui.leftMenu.setFixedWidth(150)
                self.leftMenuExpanded = True
                print("Left menu expanded to 150px")
                
                # Update menu button icon if needed
                self.update_menu_button_icon(True)
                
        except Exception as e:
            print(f"Error expanding left menu: {e}")
    
    def collapse_left_menu(self):
        """Collapse left menu"""
        try:
            if hasattr(self.ui, 'leftMenu'):
                self.ui.leftMenu.setFixedWidth(45)
                self.leftMenuExpanded = False
                print("Left menu collapsed to 45px")
                
                # Update menu button icon if needed
                self.update_menu_button_icon(False)
                
        except Exception as e:
            print(f"Error collapsing left menu: {e}")
    
    def expand_center_menu(self):
        """Expand center menu"""
        try:
            if hasattr(self.ui, 'centerMenu'):
                self.ui.centerMenu.setFixedWidth(250)
                self.centerMenuExpanded = True
                print("Center menu expanded to 250px")
        except Exception as e:
            print(f"Error expanding center menu: {e}")
    
    def close_center_menu(self):
        """Close center menu"""
        try:
            if hasattr(self.ui, 'centerMenu'):
                self.ui.centerMenu.setFixedWidth(0)
                self.centerMenuExpanded = False
                print("Center menu closed")
                
                # Reset center menu button styles
                self.reset_center_menu_styles()
                
        except Exception as e:
            print(f"Error closing center menu: {e}")

    def update_menu_button_icon(self, expanded):
        """Update menu button icon based on expansion state"""
        try:
            if hasattr(self.ui, 'menuBtn'):
                # You can update the icon here if needed
                # For now, just print the state
                state = "expanded" if expanded else "collapsed"
                print(f"Menu button state: {state}")
        except Exception as e:
            print(f"Error updating menu button icon: {e}")

    # === STYLING METHODS ===
    
    def update_main_navigation_styles(self, active_button):
        """Update main navigation button styles"""
        try:
            # Reset all main navigation buttons
            self.reset_main_navigation_styles()
            
            # Set active button style
            if hasattr(self.ui, active_button):
                active_btn = getattr(self.ui, active_button)
                active_btn.setStyleSheet("background-color: #750080; color: white;")
                print(f"Set active style for {active_button}")
                
        except Exception as e:
            print(f"Error updating main navigation styles: {e}")
    
    def reset_main_navigation_styles(self):
        """Reset all main navigation button styles"""
        try:
            for btn_name in self.main_nav_buttons:
                if hasattr(self.ui, btn_name):
                    btn = getattr(self.ui, btn_name)
                    btn.setStyleSheet("background-color: transparent; color: white;")
        except Exception as e:
            print(f"Error resetting main navigation styles: {e}")
    
    def update_center_menu_styles(self, active_button):
        """Update center menu button styles"""
        try:
            # Reset all center menu buttons
            self.reset_center_menu_styles()
            
            # Set active button style
            if hasattr(self.ui, active_button):
                active_btn = getattr(self.ui, active_button)
                active_btn.setStyleSheet("background-color: #750080; color: white;")
                print(f"Set active style for center menu {active_button}")
                
        except Exception as e:
            print(f"Error updating center menu styles: {e}")
    
    def reset_center_menu_styles(self):
        """Reset all center menu button styles"""
        try:
            for btn_name in self.center_menu_buttons:
                if hasattr(self.ui, btn_name):
                    btn = getattr(self.ui, btn_name)
                    btn.setStyleSheet("background-color: #290a30; color: white;")
        except Exception as e:
            print(f"Error resetting center menu styles: {e}")

    # === WINDOW CONTROL METHODS ===
    
    def toggle_maximize_restore(self):
        """Toggle between maximized and normal window state"""
        try:
            if self.isMaximized():
                self.showNormal()
                print("Window restored to normal")
            else:
                self.showMaximized()
                print("Window maximized")
        except Exception as e:
            print(f"Error toggling maximize/restore: {e}")

    def mousePressEvent(self, event):
        """Record the drag position when mouse is pressed"""
        if event.button() == Qt.LeftButton:
            self.dragPos = event.globalPosition().toPoint()
    
    def moveWindow(self, event):
        """Move the window when dragged by titleBar"""
        try:
            # Check if left mouse button is pressed and we have a drag position
            if event.buttons() == Qt.LeftButton and self.dragPos is not None:
                # Move window
                self.move(self.pos() + event.globalPosition().toPoint() - self.dragPos)
                self.dragPos = event.globalPosition().toPoint()
                event.accept()
        except Exception as e:
            print(f"Error moving window: {e}")

    # === WEBVIEW SETUP METHODS ===
    
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
            self.backend_home = BackendClass_hom()
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
            self.webview_home.page().runJavaScript(
                "console.log('Page loaded from Python side!'); document.body.innerHTML;",
                0,
                lambda result: print(f"HTML content length: {len(result) if result else 'empty'}")
            )
        else:
            print("Failed to load home page!")
            self.webview_home.page().runJavaScript(
                "console.error('Failed to load properly'); document.documentElement.outerHTML;",
                0,
                lambda result: print(f"Failed HTML content: {result[:100] if result else 'None'}...")
            )


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
