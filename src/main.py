"""
DumpTools - Main Application Entry Point
"""

import sys
import os

# Add project root and src directory to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

from PyQt6.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.utils.logger import setup_logger


def main():
    """Main application entry point"""
    
    # Setup logger
    logger = setup_logger('dumptools')
    logger.info("Starting DumpTools application")
    
    # Create application
    app = QApplication(sys.argv)
    
    # Set application style
    from src.ui.styles import apply_light_theme
    apply_light_theme(app)
    
    # Create and show main window
    main_window = MainWindow()
    main_window.show()
    
    logger.info("Application window opened")
    
    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
