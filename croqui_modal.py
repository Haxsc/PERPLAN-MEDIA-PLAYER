from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QFrame,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QIcon
import os
import ctypes

user32 = ctypes.windll.user32
user32.SetProcessDPIAware()  # Para suportar DPI alto

largura = user32.GetSystemMetrics(0)
altura = user32.GetSystemMetrics(1)

icon_path = os.path.join(os.path.dirname(__file__), "icons")


class CroquiModal(QDialog):
    def __init__(self, parent, croqui_path):
        super().__init__(parent)
        self.setWindowTitle("Croqui")
        self.setWindowIcon(QIcon(os.path.join(icon_path, "road.png")))
        self.setFixedSize(600, int(altura * 0.7)) 
        self.croqui_path = croqui_path
        
        # Aplica tema escuro ao modal
        self.setStyleSheet(
            """
            QDialog {
                background-color: #1E1E1E;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
                background-color: transparent;
            }
            QPushButton {
                background-color: #0078D7;
                color: white;
                padding: 8px 12px;
                border-radius: 5px;
                font-size: 12px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: #005bb5;
            }
            QPushButton:pressed {
                background-color: #004494;
            }
        """
        )

        # Layout principal
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Label para exibir a imagem (ocupa a maior parte do modal)
        image_height = int(altura * 0.7) - 100  # Subtrai espaço para botões e margens
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setFixedSize(570, image_height)
        self.image_label.setScaledContents(True)  # Faz a imagem usar todo o espaço
        self.image_label.setStyleSheet(
            """
            QLabel {
                background-color: #2b2b2b;
                border: 1px solid #404040;
                border-radius: 8px;
            }
        """
        )
        
        # Carrega e exibe a imagem
        self.load_image()
        
        layout.addWidget(self.image_label)

        # Layout horizontal para botões (menores)
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        buttons_layout.setContentsMargins(0, 5, 0, 5)
        
        # Botão Cancelar (menor)
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.setFixedSize(80, 35)
        self.cancel_button.clicked.connect(self.reject)
        
        # Botão Iniciar (menor)
        self.start_button = QPushButton("Iniciar")
        self.start_button.setIcon(QIcon(os.path.join(icon_path, "play.png")))
        self.start_button.setFixedSize(80, 35)
        self.start_button.clicked.connect(self.start_process)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addWidget(self.start_button)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)

    def load_image(self):
        """Carrega a imagem do croqui no label"""
        try:
            # Verifica se o arquivo existe e é uma imagem
            if os.path.exists(self.croqui_path):
                pixmap = QPixmap(self.croqui_path)
                if not pixmap.isNull():
                    # Carrega a imagem diretamente sem redimensionamento
                    # O setScaledContents(True) fará ela usar todo o espaço
                    self.image_label.setPixmap(pixmap)
                else:
                    self.show_error("Arquivo não é uma imagem válida")
            else:
                self.show_error("Arquivo de croqui não encontrado")
        except Exception as e:
            self.show_error(f"Erro ao carregar imagem: {str(e)}")

    def show_error(self, message):
        """Exibe uma mensagem de erro no lugar da imagem"""
        self.image_label.setText(f"❌ {message}")
        self.image_label.setStyleSheet(
            """
            QLabel {
                color: #ff6b6b;
                font-size: 16px;
                font-weight: bold;
                background-color: #2b2b2b;
                border: 2px dashed #ff6b6b;
                border-radius: 8px;
            }
        """
        )

    def start_process(self):
        """Inicia o processo e fecha o modal"""
        print(f"[CROQUI] Iniciando processo com croqui: {self.croqui_path}")
        self.accept()
