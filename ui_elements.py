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

icon_path = os.path.join(os.path.dirname(__file__), "icons")


def create_ui(player):
    """Cria a interface gráfica do player e retorna os elementos."""
    videoframe = QFrame()
    videoframe.setMinimumHeight(500)

    # Botões
    open_button = QPushButton(" Abrir Vídeo")
    open_button.setIcon(QIcon(os.path.join(icon_path, "file.png")))
    open_button.clicked.connect(player.open_file_dialog)
    open_button.setFocusPolicy(Qt.NoFocus)

    playlist_button = QPushButton(" Playlist")
    playlist_button.setIcon(QIcon(os.path.join(icon_path, "playlist.png")))
    playlist_button.clicked.connect(player.open_playlist_dialog)
    playlist_button.setFocusPolicy(Qt.NoFocus)

    settings_button = QPushButton(" Configurações")
    settings_button.setIcon(QIcon(os.path.join(icon_path, "settings.png")))
    settings_button.clicked.connect(player.open_settings_dialog)
    settings_button.setFocusPolicy(Qt.NoFocus)

    zoom_button = QPushButton(" Zoom")
    zoom_button.setIcon(QIcon(os.path.join(icon_path, "zoom.png")))
    zoom_button.clicked.connect(player.open_zoom_dialog)
    zoom_button.setFocusPolicy(Qt.NoFocus)

    paint_buton = QPushButton(" Pintar")
    paint_buton.setIcon(QIcon(os.path.join(icon_path, "brush.png")))
    # paint_buton.clicked.connect(player.open_paint_dialog)
    paint_buton.setFocusPolicy(Qt.NoFocus)

    play_button = QPushButton()
    play_button.setIcon(QIcon(os.path.join(icon_path, "play.png")))
    play_button.clicked.connect(player.play_pause)
    play_button.setFocusPolicy(Qt.NoFocus)

    skip_button = QPushButton()
    skip_button.setIcon(QIcon(os.path.join(icon_path, "skip.png")))
    skip_button.clicked.connect(player.play_next)
    skip_button.setFocusPolicy(Qt.NoFocus)

    rewind_button = QPushButton()
    rewind_button.setIcon(QIcon(os.path.join(icon_path, "rewind.png")))
    rewind_button.clicked.connect(player.play_previous)
    rewind_button.setFocusPolicy(Qt.NoFocus)

    speed_button = QPushButton()
    speed_button.setIcon(QIcon(os.path.join(icon_path, "speed.png")))
    speed_button.clicked.connect(player.open_speed_menu)
    speed_button.setFocusPolicy(Qt.NoFocus)

    # Slider
    position_slider = QSlider(Qt.Horizontal)
    position_slider.sliderMoved.connect(player.set_position)
    position_slider.setFocusPolicy(Qt.NoFocus)

    # Label do timer
    timer_label = QLabel("00:00 / 00:00")
    timer_label.setAlignment(Qt.AlignCenter)
    timer_label.setFocusPolicy(Qt.NoFocus)
    timer_label.setStyleSheet(
        "color: white; background-color: transparent; font-size: 14px; font-weight: semibold;"
    )

    # Layout dos botões
    controls_layout = QHBoxLayout()
    controls_layout.addWidget(play_button)
    controls_layout.addWidget(rewind_button)
    controls_layout.addWidget(skip_button)
    controls_layout.addWidget(position_slider)
    controls_layout.addWidget(timer_label)
    controls_layout.addWidget(speed_button)

    # Header
    header_layout = QHBoxLayout()
    header_layout.setAlignment(Qt.AlignLeft)  # Alinha todos os botões à esquerda
    header_layout.addWidget(open_button)
    header_layout.addWidget(playlist_button)
    header_layout.addWidget(settings_button)
    header_layout.addWidget(zoom_button)
    header_layout.addWidget(paint_buton)

    # Layout principal
    main_layout = QVBoxLayout()
    main_layout.addLayout(header_layout)
    main_layout.addWidget(videoframe)
    main_layout.addLayout(controls_layout)

    widget = QWidget()
    widget.setLayout(main_layout)
    player.setCentralWidget(widget)

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
