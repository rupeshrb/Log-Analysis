import os
import sys
import traceback
import time

# Save the original excepthook
original_excepthook = sys.excepthook

def exception_hook(exc_type, exc_value, exc_traceback):
    """
    Custom exception handler that writes errors to a file
    and keeps the console window open
    """
    # First call the original exception hook
    original_excepthook(exc_type, exc_value, exc_traceback)
    
    # Write the error to a log file
    with open('error_log.txt', 'a') as f:
        f.write(f"\n\n--- Error at {time.strftime('%Y-%m-%d %H:%M:%S')} ---\n")
        traceback.print_exception(exc_type, exc_value, exc_traceback, file=f)
    
    # Keep the console window open
    print("\nApplication crashed. Error has been logged to error_log.txt")
    print("Press Enter to exit...")
    input()

# Set the custom exception hook
sys.excepthook = exception_hook

# Try to import and run the main application
try:
    # Path setup for PyInstaller bundled app
    if getattr(sys, 'frozen', False):
        # If we're running as a bundled exe, use the sys._MEIPASS path
        bundle_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
        os.chdir(bundle_dir)
        print(f"Running from bundle directory: {bundle_dir}")
        
        # Add the bundle directory to the system path
        if bundle_dir not in sys.path:
            sys.path.insert(0, bundle_dir)
    
    # Print information that could help with debugging
    print("Python version:", sys.version)
    print("Platform:", sys.platform)
    print("Current working directory:", os.getcwd())
    print("System path:", sys.path)
    
    # Try to import critical components
    print("\nImporting critical components...")
    try:
        import PySide6
        print("PySide6 loaded successfully")
        print("PySide6 version:", PySide6.__version__)
        print("PySide6 location:", PySide6.__file__)
        
        # Test specific PySide6 imports
        from PySide6 import QtWidgets, QtCore
        print("QtWidgets and QtCore loaded successfully")
        
        from PySide6 import QtWebEngineWidgets
        print("QtWebEngineWidgets loaded successfully")
    except ImportError as e:
        print(f"Failed to import PySide6 components: {e}")
    
    try:
        from Custom_Widgets import *
        print("Custom_Widgets loaded successfully")
    except ImportError as e:
        print(f"Failed to import Custom_Widgets: {e}")
    
    try:
        import sklearn
        print("sklearn loaded successfully")
        print("sklearn version:", sklearn.__version__)
    except ImportError as e:
        print(f"Failed to import sklearn: {e}")
    
    try:
        import numpy
        print("numpy loaded successfully")
    except ImportError as e:
        print(f"Failed to import numpy: {e}")
    
    try:
        import pandas
        print("pandas loaded successfully")
    except ImportError as e:
        print(f"Failed to import pandas: {e}")
    
    # Try to import the main application
    print("\nImporting main application...")
    try:
        from main import MainWindow
        print("MainWindow class loaded successfully")
    except ImportError as e:
        print(f"Failed to import MainWindow: {e}")
        raise
    
    # Try to create the QApplication
    print("\nCreating QApplication...")
    app = QtWidgets.QApplication(sys.argv)
    print("QApplication created successfully")
    
    # Important: Enable QWebEngineView debugging
    os.environ["QTWEBENGINE_REMOTE_DEBUGGING"] = "9222"
    
    # Try to create the main window
    print("\nCreating main window...")
    window = MainWindow()
    print("Main window created successfully")
    
    # Show the window
    print("\nShowing main window...")
    window.show()
    print("Main window shown successfully")
    
    # Run the application
    print("\nRunning application event loop...")
    sys.exit(app.exec())
    
except Exception as e:
    print(f"\nFATAL ERROR: {e}")
    traceback.print_exc()
    
    # Write to error log
    with open('error_log.txt', 'a') as f:
        f.write(f"\n\n--- Fatal Error at {time.strftime('%Y-%m-%d %H:%M:%S')} ---\n")
        traceback.print_exc(file=f)
    
    print("\nPress Enter to exit...")
    input()