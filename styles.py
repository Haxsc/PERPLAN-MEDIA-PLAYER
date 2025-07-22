"""
Stylesheet definitions for PPL Player.
Provides consistent theming across the application.
"""

from config import THEME_COLORS


def apply_styles(player):
    """Applies the complete stylesheet to the video player."""
    stylesheet = f"""
        QMainWindow {{
            background-color: {THEME_COLORS['background']};
            color: {THEME_COLORS['text']};
        }}
        
        QPushButton {{
            background-color: {THEME_COLORS['button']};
            border: none;
            color: {THEME_COLORS['text']};
            padding: 6px 12px;
            border-radius: 5px;
            font-size: 14px;
            font-weight: 500;
        }}
        
        QPushButton:hover {{
            background-color: {THEME_COLORS['button_hover']};
        }}
        
        QPushButton:pressed {{
            background-color: {THEME_COLORS['button']};
            border: 1px solid #555555;
        }}
        
        QSlider::groove:horizontal {{
            height: 6px;
            background-color: {THEME_COLORS['slider_groove']};
            border-radius: 3px;
        }}
        
        QSlider::handle:horizontal {{
            background-color: {THEME_COLORS['slider_handle']};
            border: none;
            width: 16px;
            height: 16px;
            border-radius: 8px;
            margin: -5px 0;
        }}
        
        QSlider::handle:horizontal:hover {{
            background-color: #cccccc;
        }}
        
        QSlider::sub-page:horizontal {{
            background-color: #0078D7;
            border-radius: 3px;
        }}
        
        QFrame {{
            background-color: {THEME_COLORS['video_frame']};
            border-radius: 5px;
        }}
        
        QLabel {{
            color: {THEME_COLORS['text']};
        }}
    """
    
    player.setStyleSheet(stylesheet)
