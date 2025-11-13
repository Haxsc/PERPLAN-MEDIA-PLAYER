from PySide6.QtWidgets import (
    QFrame,
    QPushButton,
    QSlider,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QLabel,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
import os
from typing import Tuple
from config import (
    ICON_PATH,
    MINIMUM_VIDEO_HEIGHT,
    TIMER_DEFAULT_TEXT,
    TIMER_FONT_SIZE
)


def create_video_frame() -> QFrame:
    """Creates and configures the video frame."""
    videoframe = QFrame()
    videoframe.setMinimumHeight(MINIMUM_VIDEO_HEIGHT)
    return videoframe


def create_header_buttons(player) -> Tuple[QPushButton, QPushButton, QPushButton, QPushButton, QPushButton]:
    """Creates all header buttons with their icons and connections."""
    
    # File operations button
    open_button = QPushButton(" Abrir Vídeo")
    open_button.setIcon(QIcon(os.path.join(ICON_PATH, "file.png")))
    open_button.clicked.connect(player.open_file_dialog)
    open_button.setFocusPolicy(Qt.NoFocus)

    # Playlist button
    playlist_button = QPushButton(" Playlist")
    playlist_button.setIcon(QIcon(os.path.join(ICON_PATH, "playlist.png")))
    playlist_button.clicked.connect(player.open_playlist_dialog)
    playlist_button.setFocusPolicy(Qt.NoFocus)

    # Settings button
    settings_button = QPushButton(" Configurações")
    settings_button.setIcon(QIcon(os.path.join(ICON_PATH, "settings.png")))
    settings_button.clicked.connect(player.open_settings_dialog)
    settings_button.setFocusPolicy(Qt.NoFocus)

    # Zoom button
    zoom_button = QPushButton(" Zoom")
    zoom_button.setIcon(QIcon(os.path.join(ICON_PATH, "zoom.png")))
    zoom_button.clicked.connect(player.open_zoom_dialog)
    zoom_button.setFocusPolicy(Qt.NoFocus)

    # Paint button
    paint_button = QPushButton(" Croqui")
    paint_button.setIcon(QIcon(os.path.join(ICON_PATH, "paint.png")))
    paint_button.clicked.connect(player.open_croqui_modal)
    paint_button.setFocusPolicy(Qt.NoFocus)

    return open_button, playlist_button, settings_button, zoom_button, paint_button


def create_control_buttons(player) -> Tuple[QPushButton, QPushButton, QPushButton, QPushButton]:
    """Creates media control buttons."""
    
    # Play/Pause button
    play_button = QPushButton()
    play_button.setIcon(QIcon(os.path.join(ICON_PATH, "play.png")))
    play_button.clicked.connect(player.play_pause)
    play_button.setFocusPolicy(Qt.NoFocus)

    # Skip button
    skip_button = QPushButton()
    skip_button.setIcon(QIcon(os.path.join(ICON_PATH, "skip.png")))
    skip_button.clicked.connect(player.play_next)
    skip_button.setFocusPolicy(Qt.NoFocus)

    # Rewind button
    rewind_button = QPushButton()
    rewind_button.setIcon(QIcon(os.path.join(ICON_PATH, "rewind.png")))
    rewind_button.clicked.connect(player.play_previous)
    rewind_button.setFocusPolicy(Qt.NoFocus)

    # Speed control button
    speed_button = QPushButton()
    speed_button.setIcon(QIcon(os.path.join(ICON_PATH, "speed.png")))
    speed_button.clicked.connect(player.open_speed_menu)
    speed_button.setFocusPolicy(Qt.NoFocus)
    
    return play_button, rewind_button, skip_button, speed_button


def create_media_controls(player) -> Tuple[QSlider, QLabel]:
    """Creates media control elements (slider and timer)."""
    
    # Position slider
    position_slider = QSlider(Qt.Horizontal)
    position_slider.sliderMoved.connect(player.set_position)
    position_slider.setFocusPolicy(Qt.NoFocus)

    # Timer label
    timer_label = QLabel(TIMER_DEFAULT_TEXT)
    timer_label.setAlignment(Qt.AlignCenter)
    timer_label.setFocusPolicy(Qt.NoFocus)
    timer_label.setStyleSheet(
        f"color: white; background-color: transparent; font-size: {TIMER_FONT_SIZE}px; font-weight: semibold;"
    )
    
    return position_slider, timer_label


def create_layouts(
    header_buttons: Tuple[QPushButton, ...],
    control_buttons: Tuple[QPushButton, ...],
    position_slider: QSlider,
    timer_label: QLabel,
    videoframe: QFrame
) -> Tuple[QHBoxLayout, QHBoxLayout, QVBoxLayout]:
    """Creates and organizes all layouts."""
    
    open_button, playlist_button, settings_button, zoom_button, paint_button = header_buttons
    play_button, rewind_button, skip_button, speed_button = control_buttons
    
    # Controls layout (bottom controls)
    controls_layout = QHBoxLayout()
    controls_layout.addWidget(play_button)
    controls_layout.addWidget(rewind_button)
    controls_layout.addWidget(skip_button)
    controls_layout.addWidget(position_slider)
    controls_layout.addWidget(timer_label)
    controls_layout.addWidget(speed_button)

    # Header layout (top buttons)
    header_layout = QHBoxLayout()
    header_layout.setAlignment(Qt.AlignLeft)
    header_layout.addWidget(open_button)
    header_layout.addWidget(playlist_button)
    header_layout.addWidget(settings_button)
    header_layout.addWidget(zoom_button)
    header_layout.addWidget(paint_button)

    # Main layout
    main_layout = QVBoxLayout()
    main_layout.addLayout(header_layout)
    main_layout.addWidget(videoframe)
    main_layout.addLayout(controls_layout)
    
    return header_layout, controls_layout, main_layout


def create_ui(player):
    """Creates the complete UI for the video player and returns the main elements.
    
    Args:
        player: The video player instance to connect signals to.
        
    Returns:
        Tuple containing the main UI elements for external access.
    """
    try:
        # Create video frame
        videoframe = create_video_frame()
        
        # Create button groups
        header_buttons = create_header_buttons(player)
        control_buttons = create_control_buttons(player)
        
        # Create media controls
        position_slider, timer_label = create_media_controls(player)
        
        # Create layouts
        header_layout, controls_layout, main_layout = create_layouts(
            header_buttons, control_buttons, position_slider, timer_label, videoframe
        )
        
        # Set up main widget
        widget = QWidget()
        widget.setLayout(main_layout)
        player.setCentralWidget(widget)
        
        # Unpack elements for return
        open_button, playlist_button, settings_button, zoom_button, paint_button = header_buttons
        play_button, rewind_button, skip_button, speed_button = control_buttons
        
        return (
            open_button,
            videoframe,
            play_button,
            skip_button,
            rewind_button,
            speed_button,
            position_slider,
            timer_label,
            header_layout,
        )
        
    except Exception as e:
        print(f"Error creating UI: {e}")
        raise
