"""
Configuration constants for PPL Player.
Centralizes all configuration values to improve maintainability.
"""

import os

# Application Information
APP_NAME = "PPL Player"
APP_VERSION = "1.2"
DEFAULT_SIZE = (1280, 720)

# File Paths
ICON_PATH = os.path.join(os.path.dirname(__file__), "icons")
SUPPORTED_VIDEO_EXTENSIONS = (".mp4", ".avi", ".mkv", ".dav")

# UI Configuration
MINIMUM_VIDEO_HEIGHT = 500
TIMER_DEFAULT_TEXT = "00:00 / 00:00"
TIMER_FONT_SIZE = 14

# Media Player Configuration
DEFAULT_VOLUME = 50
VOLUME_STEP = 10
SPEED_MIN = 0.5
SPEED_MAX = 32
DEFAULT_SPEED = 1.0
SPEED_INCREMENT = 0.1

# Timer Configuration
UI_UPDATE_INTERVAL = 500  # milliseconds
NOTIFICATION_DURATION = 5000  # milliseconds
MOUSE_CHECK_INTERVAL = 500  # milliseconds

# Network Configuration
HOST = "localhost"
MEDIA_PORT = 1337
CONTADOR_PORT = 3000

# Auto-pause settings (for long videos)
AUTO_PAUSE_MIN_DURATION = 50  # minutes
AUTO_PAUSE_POSITIONS = [0.25, 0.5, 0.75]  # 25%, 50%, 75% of video

# Default Keybindings
DEFAULT_KEYBINDS = {
    "Pausar/Reproduzir": "Space",
    "Avancar 1 Frame": "E",
    "Retroceder 1 Frame": "Q",
    "Avançar 1s": "Right",
    "Retroceder 1s": "Left",
    "Aumentar Volume": "Up",
    "Diminuir Volume": "Down",
    "Tela Cheia": "F",
    "Aumentar Velocidade": "+",
    "Diminuir Velocidade": "-",
}

# Zoom Configuration
ZOOM_DEFAULT_VALUE = 10
ZOOM_MIN_VALUE = 10
ZOOM_MAX_VALUE = 40
ZOOM_DEFAULT_SCALE_X = 80
ZOOM_DEFAULT_SCALE_Y = 45

# Speed Menu Options
SPEED_OPTIONS = ["1x", "2x", "4x", "6x", "8x", "10x", "12x", "16x", "32x"]

# File Dialog Configuration
DEFAULT_VIDEO_PATH = "P:/"
VIDEO_FILTER = "Vídeos (*.dav *.mp4 *.avi *.mkv)"

# Notification Colors
NOTIFICATION_COLORS = {
    "info": "rgba(189, 189, 189, 0.5)",
    "success": "green",
    "warning": "orange",
    "error": "red"
}

# Style Configuration
THEME_COLORS = {
    "background": "#181818",
    "text": "#ffffff",
    "button": "#262626",
    "button_hover": "#3A3A3A",
    "slider_groove": "#404040",
    "slider_handle": "#ffffff",
    "video_frame": "#27272a"
}
