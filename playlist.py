from PySide6.QtWidgets import QDialog, QListWidget, QVBoxLayout, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
import os

icon_path = os.path.join(os.path.dirname(__file__), "icons")


class PlaylistModal(QDialog):
    def __init__(self, parent, playlist):
        super().__init__(parent)
        self.setWindowTitle("Playlist")
        self.setWindowIcon(QIcon(os.path.join(icon_path, "playlist.png")))
        self.setFixedSize(550, 600)
        self.setStyleSheet(
            """
        QDialog {
            background-color: #1E1E1E; /* Fundo escuro */
            border-radius: 10px;
        }
        QListWidget {
            background-color: #252526;
            color: white;
            font-size: 14px;
            padding: 5px;
            border-radius: 5px;
            outline: none;
        }
        QListWidget::item {
            padding: 8px;
        }
        QListWidget::item:selected {
            background-color: #0078D7; /* Cor de seleção */
            color: white;
            border-radius: 5px;
            outline: none;
        }
        QListWidget::item:hover {
            background-color: #404040; /* Destaque ao passar o mouse */
        }
        
        /* 🔹 Scrollbar personalizada */
        QListWidget::verticalScrollBar {
            border: none;
            background: #2E2E2E;  /* Cor de fundo da barra */
            width: 10px;  /* Largura da scrollbar */
            margin: 5px 0px 5px 0px;
            border-radius: 5px;
        }
        
        QListWidget::verticalScrollBar::handle {
            background: #0078D7;  /* Cor do controle */
            min-height: 30px;
            border-radius: 5px;
        }
        
        QListWidget::verticalScrollBar::handle:hover {
            background: #005A9E;  /* Cor ao passar o mouse */
        }
        
        QListWidget::verticalScrollBar::handle:pressed {
            background: #00407A;  /* Cor ao clicar */
        }
        
        QListWidget::verticalScrollBar::add-line, 
        QListWidget::verticalScrollBar::sub-line {
            background: none;
            border: none;
        }
        """
        )

        self.playlist = playlist
        self.selected_video = None  # Armazena o vídeo selecionado

        # Criando a lista de vídeos
        self.list_widget = QListWidget(self)
        for video in self.playlist:
            self.list_widget.addItem(
                os.path.basename(video)
            )  # Exibe apenas o nome do arquivo

        # Botão para selecionar um vídeo
        self.select_button = QPushButton(" Reproduzir")
        self.select_button.setIcon(QIcon(os.path.join(icon_path, "play.png")))
        self.select_button.clicked.connect(self.select_video)

        # Layout do modal
        layout = QVBoxLayout()
        layout.addWidget(self.list_widget)
        layout.addWidget(self.select_button)

        self.setLayout(layout)

    def select_video(self):
        """Pega o vídeo selecionado e fecha o modal."""
        selected_item = self.list_widget.currentItem()
        if selected_item:
            video_name = selected_item.text()
            for video in self.playlist:
                if os.path.basename(video) == video_name:
                    self.selected_video = video
                    break
        self.accept()  # Fecha o modal
