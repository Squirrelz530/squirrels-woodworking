#!/usr/bin/env python3
"""AI Animation Studio - Main entry point.

A PySide6 desktop application for generating animation frames using cloud AI.
Uses Pollinations.ai for image generation (free, no authentication required).
"""

import sys
from pathlib import Path

from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QApplication

from app.api import ImageGenerationAPI
from app.storage import AssetStorage
from app.main_window import MainWindow


def main():
    """Main application entry point."""
    # Set up Qt application
    app = QApplication(sys.argv)
    
    # Set application metadata
    app.setApplicationName("AI Animation Studio")
    app.setOrganizationName("Squirrels Woodworking")
    app.setApplicationVersion("0.1.0")
    
    # Get the base directory (where this script is located)
    base_dir = Path(__file__).parent
    
    # Initialize API client
    api = ImageGenerationAPI(timeout=60)
    
    # Initialize storage
    storage = AssetStorage(base_dir)
    
    # Create and show the main window
    window = MainWindow(api, storage)
    window.show()
    
    # Start the application
    return_code = app.exec()
    
    # Clean up
    return return_code


if __name__ == "__main__":
    sys.exit(main())
