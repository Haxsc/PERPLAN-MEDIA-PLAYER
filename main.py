import sys
from PySide6.QtWidgets import QApplication
from video_player import ModernVideoPlayer
from PySide6.QtGui import QIcon
import os

icon_path = os.path.join(os.path.dirname(__file__), "icons")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(os.path.join(icon_path, "road.png")))
    player = ModernVideoPlayer()
    player.show()
    sys.exit(app.exec())
