"""
DumpTools - Main Application Entry Point
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from utils.logger import setup_logger


def main():
    """Main application entry point"""
    
    # Setup logger
    logger = setup_logger('dumptools')
    logger.info("Starting DumpTools application")
    
    # Create application
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main window
    main_window = MainWindow()
    main_window.show()
    
    logger.info("Application window opened")
    
    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
