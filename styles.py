def apply_styles(player):
    """Aplica os estilos da interface gráfica."""
    player.setStyleSheet(
        """
        QMainWindow {
            background-color: #181818;
            color: #ffffff;
        }
        QPushButton {
            background-color: #262626;
            border: none;
            color: #ffffff;
            padding: 6px 12px;
            border-radius: 5px;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: #3A3A3A;
        }
        QSlider::groove:horizontal {
            height: 6px;
            background-color: #404040;
            border-radius: 3px;
        }
        QSlider::handle:horizontal {
            background-color: #ffffff;
            border: none;
            width: 16px;
            height: 16px;
            border-radius: 8px;
            margin: -5px 0;
        }
        QFrame {
            background-color: #27272a;
        }
    """
    )
