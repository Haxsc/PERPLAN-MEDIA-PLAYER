from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QSpacerItem,
    QSizePolicy,
)
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QIcon
import os

icon_path = os.path.join(os.path.dirname(__file__), "icons")


class SettingsModal(QDialog):
    def __init__(self, parent, keybinds):
        super().__init__(parent)
        self.setWindowTitle("Configurações de Teclas")
        self.setWindowIcon(QIcon(os.path.join(icon_path, "settings.png")))
        self.setFixedSize(450, 450)
        self.setStyleSheet(
            """
            QDialog {
                background-color: #1E1E1E;
                border-radius: 10px;
            }
            QLabel {
                color: white;
                font-size: 14px;
                font-weight: semibold;
                background-color: transparent;
            }
            QLineEdit {
                background-color: #2D2D2D;
                color: white;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 5px;
                text-align: center;
                font-size: 14px;
                min-height: 25px;
            }
            QLineEdit:hover {
                border: 1px solid #0078D7;
            }
            QLineEdit:focus {
                border: 1px solid #00AFFF;
            }
            QPushButton {
                background-color: #0078D7;
                color: white;
                font-size: 14px;
                font-weight: semibold;
                padding: 8px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #005A9E;
            }
            QPushButton:pressed {
                background-color: #00407A;
            }
            """
        )

        self.keybinds = keybinds  # Dicionário de binds atuais
        self.new_keybinds = keybinds.copy()  # Cópia para editar

        # Layout principal
        layout = QVBoxLayout()

        # Criar campos para cada ação
        self.inputs = {}  # Armazena os campos para cada ação
        self.labels = {}  # Armazena as labels para capturar clique

        for action, key in self.keybinds.items():
            row = QHBoxLayout()

            label = QLabel(action)  # Nome da ação
            label.setFixedWidth(170)  # Mantém o alinhamento das labels
            label.setCursor(Qt.PointingHandCursor)  # Cursor indica que é clicável

            key_input = QLineEdit(key)  # Campo de entrada manual
            key_input.setReadOnly(True)  # Impede digitação manual
            key_input.setFixedWidth(120)  # Define tamanho adequado
            key_input.installEventFilter(
                self
            )  # Captura eventos de tecla (precisa clicar antes)
            key_input.setProperty("action", action)  # Salva a ação correspondente

            self.inputs[action] = key_input
            self.labels[action] = label

            row.addWidget(label)
            row.addWidget(key_input)
            layout.addLayout(row)

        # Adicionando espaço antes do botão
        layout.addSpacerItem(
            QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )

        # Botão para salvar configurações
        save_button = QPushButton(" Salvar")
        save_button.setIcon(QIcon(os.path.join(icon_path, "save.png")))
        save_button.setFixedWidth(120)
        save_button.clicked.connect(self.accept)  # Fecha e salva

        layout.addWidget(save_button, alignment=Qt.AlignCenter)
        self.setLayout(layout)

    def enable_editing(self, action):
        """Habilita a edição do campo correspondente quando o usuário clica na label."""
        key_input = self.inputs[action]
        key_input.setReadOnly(False)  # Permite editar
        key_input.setFocus()  # Dá foco no input para capturar tecla
        key_input.clear()  # Remove o texto anterior

    def eventFilter(self, obj, event):
        """Captura eventos de tecla para os inputs (somente quando o usuário clicar primeiro)."""
        if event.type() == QEvent.KeyPress and isinstance(obj, QLineEdit):
            action = obj.property("action")  # Obtém a ação vinculada ao campo
            if action:
                key_name = self.get_key_name(
                    event.key()
                )  # Converte o código da tecla para um nome legível
                self.new_keybinds[action] = key_name  # Atualiza os binds
                obj.setText(key_name)  # Exibe a tecla no input
                obj.setReadOnly(True)  # ❌ Bloqueia edição após a seleção
            return True
        return super().eventFilter(obj, event)

    def get_key_name(self, key):
        """Converte o código da tecla em um nome legível."""
        if key == Qt.Key_Space:
            return "Space"
        elif key == Qt.Key_Return or key == Qt.Key_Enter:
            return "Enter"
        elif key == Qt.Key_Backspace:
            return "Backspace"
        elif key == Qt.Key_Shift:
            return "Shift"
        elif key == Qt.Key_Control:
            return "Ctrl"
        elif key == Qt.Key_Alt:
            return "Alt"
        elif key == Qt.Key_Escape:
            return "Escape"
        elif key == Qt.Key_Tab:
            return "Tab"
        else:
            return (
                chr(key).upper() if 32 <= key <= 126 else ""
            )  # Retorna a tecla em maiúscula
