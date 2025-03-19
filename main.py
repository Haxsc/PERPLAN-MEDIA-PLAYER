import sys
from PySide6.QtWidgets import QApplication
from video_player import ModernVideoPlayer

if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = ModernVideoPlayer()
    player.show()
    sys.exit(app.exec())
