import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from video_player import ModernVideoPlayer

icon_path = os.path.join(os.path.dirname(__file__), "icons")

if __name__ == "__main__":
    app = QApplication(sys.argv)  # Cria o QApplication antes de qualquer QWidget
    app.setWindowIcon(QIcon(os.path.join(icon_path, "road.png")))

    # Inicia o player normalmente
    player = ModernVideoPlayer()
    player.show()

    if len(sys.argv) > 1:
        video_path = sys.argv[1]
        if os.path.exists(video_path) and video_path.lower().endswith(
            (".mp4", ".avi", ".mkv", ".dav")
        ):
            player.playlist.append(video_path)
            player.current_video_index = 0
            player.open_file(video_path)

    sys.exit(app.exec())
