"""
Application Styles Module
Defines the visual theme and usage of QPalette for the application.
"""

from PyQt6.QtGui import QColor, QPalette, QFont
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

def apply_light_theme(app):
    """
    Apply a modern Dark Theme with polished UI elements.
    Focus:
    - "Tidak kaku" (Fluid, rounded, modern)
    - Attractive Buttons & Fonts
    
    Colors:
    - Background: #2B2B2B
    - Accent: #007ACC (Professional Blue)
    """
    app.setStyle("Fusion")
    
    # 1. Set a Modern Font globally
    # Segoe UI is standard for modern Windows apps, fallback to system sans-serif
    font = QFont("Segoe UI", 10)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    app.setFont(font)
    
    palette = QPalette()
    
    # Define colors
    color_window = QColor("#2B2B2B")
    color_window_text = QColor("#F0F0F0")
    color_base = QColor("#323232")            
    color_alternate_base = QColor("#3A3A3A")
    color_text = QColor("#F0F0F0")
    color_button = QColor("#3C3C3C")
    color_button_text = QColor("#F0F0F0")
    color_bright_text = QColor("#FFFFFF")
    color_link = QColor("#64B5F6")
    color_highlight = QColor("#007ACC")
    color_highlighted_text = QColor("#FFFFFF")
    
    # Set palette colors
    palette.setColor(QPalette.ColorRole.Window, color_window)
    palette.setColor(QPalette.ColorRole.WindowText, color_window_text)
    palette.setColor(QPalette.ColorRole.Base, color_base)
    palette.setColor(QPalette.ColorRole.AlternateBase, color_alternate_base)
    palette.setColor(QPalette.ColorRole.Text, color_text)
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#1E1E1E"))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#F0F0F0"))
    palette.setColor(QPalette.ColorRole.Button, color_button)
    palette.setColor(QPalette.ColorRole.ButtonText, color_button_text)
    palette.setColor(QPalette.ColorRole.BrightText, color_bright_text)
    palette.setColor(QPalette.ColorRole.Link, color_link)
    palette.setColor(QPalette.ColorRole.Highlight, color_highlight)
    palette.setColor(QPalette.ColorRole.HighlightedText, color_highlighted_text)
    
    # Disabled state
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor("#6E6E6E"))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor("#6E6E6E"))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor("#6E6E6E"))
    
    app.setPalette(palette)
    
    # MIX of CSS and Palette for that "Modern/Fluid" look
    app.setStyleSheet(f"""
        /* Global Tooltip */
        QToolTip {{ 
            color: #F0F0F0; 
            background-color: #1E1E1E; 
            border: 1px solid #3E3E3E; 
            border-radius: 4px;
        }}
        
        /* Main Tab Container - Rounded & Soft Border */
        QTabWidget::pane {{
            border: 1px solid #3E3E3E;
            top: -1px; 
            background: #2B2B2B;
            border-radius: 4px;
        }}
        
        /* Modern Tabs */
        QTabBar::tab {{
            background: #232323;
            color: #8E8E8E;
            border: 1px solid #3E3E3E;
            padding: 10px 24px;  /* More breathable padding */
            margin-right: 4px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            font-weight: 500;
        }}
        
        QTabBar::tab:selected {{
            background: #2B2B2B;  
            color: #007ACC;      /* Highlight text color */
            border-bottom-color: #2B2B2B; 
            font-weight: bold;
        }}
        
        QTabBar::tab:!selected:hover {{
            background: #333333;
            color: #E0E0E0;
            margin-top: 2px; /* Subtle animation effect */
        }}
        
        /* MODERN FLUID BUTTONS */
        QPushButton {{
            background-color: #3C3C3C;
            color: #F0F0F0;
            border: 1px solid #555555;
            border-radius: 6px;       /* Rounded corners! */
            padding: 8px 16px;        /* Larger touch area */
            font-weight: 600;
        }}
        QPushButton:hover {{
            background-color: #4C4C4C;
            border-color: #007ACC;
            color: #FFFFFF;
        }}
        QPushButton:pressed {{
            background-color: #005F9E; /* Blue tint on press */
            border-color: #005F9E;
        }}
        
        /* Inputs - Rounded & Clean */
        QLineEdit, QTextEdit, QPlainTextEdit, QComboBox {{
            background-color: #323232;
            color: #F0F0F0;
            border: 1px solid #444444;
            border-radius: 5px;
            padding: 6px;
            selection-background-color: #007ACC;
        }}
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus {{
            border: 1px solid #007ACC;
            background-color: #383838;
        }}
        
        /* Group Boxes - Less stiff */
        QGroupBox {{
            border: 1px solid #444444;
            border-radius: 6px;
            margin-top: 1.2em; 
            padding-top: 10px;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 5px;
            color: #007ACC; /* Accent color for titles */
            font-weight: bold;
        }}
        
        /* Scrollbars - Sleek & Minimal */
        QScrollBar:vertical {{
            border: none;
            background: #2B2B2B;
            width: 12px;
            margin: 0px; 0px 0px 0px;
            border-radius: 0px;
        }}
        QScrollBar::handle:vertical {{
            background: #4C4C4C;
            min-height: 30px;
            border-radius: 6px;
            margin: 2px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: #666666;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        
        /* Header Views (Tables) */
        QHeaderView::section {{
            background-color: #323232;
            padding: 6px;
            border: none;
            border-right: 1px solid #444444;
            border-bottom: 1px solid #444444;
            color: #E0E0E0;
            font-weight: bold;
        }}
        
        /* Table/List Views */
        QTableView, QTableWidget, QListView {{
            background-color: #2E2E2E;
            alternate-background-color: #353535;
            selection-background-color: #007ACC;
            selection-color: white;
            border: 1px solid #444444;
            border-radius: 4px;
            gridline-color: #444444;
        }}
    """)
