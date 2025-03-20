from PySide6.QtWidgets import (
    QDialog,
    QListWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QWidget,
    QLabel,
    QListWidgetItem,
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
import os

icon_path = os.path.join(os.path.dirname(__file__), "icons")


class PlaylistModal(QDialog):
    def __init__(self, parent, playlist, current_index):
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
            background-color: #252525;
            color: white;
            font-size: 14px;
            padding: 10px;
            border-radius: 5px;
            outline: none;
        }
        QListWidget::item {
            height: 30px;
            padding: 5px;
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
        self.selected_index = -1
        self.current_index = current_index

        # Criando a lista de vídeos
        self.list_widget = QListWidget(self)
        self.build_list_items()

        # Botão para selecionar um vídeo
        self.select_button = QPushButton(" Reproduzir")
        self.select_button.setIcon(QIcon(os.path.join(icon_path, "play-playlist.png")))
        self.select_button.clicked.connect(self.select_video)

        # Botão para limpar a playlist
        self.clear_button = QPushButton(" Limpar Playlist")
        self.clear_button.setIcon(QIcon(os.path.join(icon_path, "trash.png")))
        self.clear_button.setStyleSheet("color: white;")
        self.clear_button.clicked.connect(self.clear_playlist)

        # Layout do modal
        layout = QVBoxLayout()
        layout.addWidget(self.list_widget)

        # Layout horizontal para os botões
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.select_button)
        buttons_layout.addWidget(self.clear_button)

        layout.addLayout(buttons_layout)
        self.setLayout(layout)

    def build_list_items(self):
        """Recria os itens do QListWidget usando setItemWidget para ter um botão de remoção."""
        self.list_widget.clear()  # limpa tudo
        for i, video in enumerate(self.playlist):
            item = QListWidgetItem(self.list_widget)
            # Guardamos o caminho completo no UserRole (opcional)
            item.setData(Qt.UserRole, video)

            # Cria um widget horizontal com (Label + Botão "remover")
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 0, 0, 0)

            # Label com o nome do arquivo
            label = QLabel(os.path.basename(video))
            label.setStyleSheet(
                "color: white; background-color: transparent;"
            )  # cor do texto
            row_layout.addWidget(label)

            # "Empurra" o botão para a direita
            row_layout.addStretch()

            # Botão de remover
            remove_button = QPushButton()
            remove_button.setIcon(QIcon(os.path.join(icon_path, "remove.png")))
            remove_button.setFixedSize(25, 25)  # Tamanho fixo do botão
            remove_button.setStyleSheet(
                """
                QPushButton {
                    background-color: transparent;
                    color: white;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 30);
                    border-radius: 12px; 
                }
            """
            )

            if i == self.current_index:
                remove_button.setEnabled(False)

            # Conecta o botão a um método que remove este item
            remove_button.clicked.connect(lambda checked, row=i: self.remove_video(row))
            row_layout.addWidget(remove_button)

            # Define o layout do row_widget
            row_widget.setLayout(row_layout)

            # Associa row_widget ao QListWidgetItem
            self.list_widget.setItemWidget(item, row_widget)

    def remove_video(self, row):
        """Remove o vídeo 'row' da playlist e atualiza a lista."""
        if 0 <= row < len(self.playlist):
            if row == self.current_index:
                print("Não é possível remover o vídeo atual!")
                return
            del self.playlist[row]
            self.build_list_items()  # reconstrói a lista

    def select_video(self):
        """Pega o vídeo selecionado e fecha o modal."""
        index = self.list_widget.currentRow()
        if 0 <= index < len(self.playlist):
            self.selected_video = self.playlist[index]
            self.selected_index = index
        self.accept()  # Fecha o modal

    def clear_playlist(self):
        """Remove todos os vídeos da playlist, exceto o vídeo atual (se presente)."""
        if 0 <= self.current_index < len(self.playlist):
            current_video = self.playlist[self.current_index]
            self.playlist.clear()
            self.playlist.append(current_video)
            self.current_index = 0  # O vídeo atual passa a ser o único
        else:
            self.playlist.clear()
            self.current_index = -1
        self.build_list_items()  # Reconstrói a lista exibida
