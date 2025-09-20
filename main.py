#!/usr/bin/env python3
"""
Black-Scholes Price Movement Simulator
A visualization tool for Monte Carlo simulation of stock price paths using the Black-Scholes model.
"""

import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPalette, QColor

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.ui.main_window import MainWindow
from src.utils.config import APP_NAME, COLORS


def setup_application():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion("1.0.0")

    # Set application icon (if available)
    # app.setWindowIcon(QIcon("resources/icons/app_icon.png"))

    # Apply dark theme globally
    app.setStyle('Fusion')

    # Create dark palette
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(COLORS['background']))
    palette.setColor(QPalette.WindowText, QColor(COLORS['text']))
    palette.setColor(QPalette.Base, QColor(COLORS['surface']))
    palette.setColor(QPalette.AlternateBase, QColor(COLORS['background']))
    palette.setColor(QPalette.ToolTipBase, QColor(COLORS['text']))
    palette.setColor(QPalette.ToolTipText, QColor(COLORS['background']))
    palette.setColor(QPalette.Text, QColor(COLORS['text']))
    palette.setColor(QPalette.Button, QColor(COLORS['surface']))
    palette.setColor(QPalette.ButtonText, QColor(COLORS['text']))
    palette.setColor(QPalette.BrightText, QColor('#ff0000'))
    palette.setColor(QPalette.Link, QColor(COLORS['accent']))
    palette.setColor(QPalette.Highlight, QColor(COLORS['accent']))
    palette.setColor(QPalette.HighlightedText, QColor('#ffffff'))

    app.setPalette(palette)

    return app


def main():
    try:
        # Create and setup application
        app = setup_application()

        # Create and show main window
        window = MainWindow()
        window.show()

        # Start the event loop
        sys.exit(app.exec())

    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()