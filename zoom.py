import os
from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QVBoxLayout,
    QSlider,
    QPushButton,
    QFrame,
    QHBoxLayout,
)
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QPixmap, QIcon

icon_path = os.path.join(os.path.dirname(__file__), "icons")


class ZoomModal(QDialog):
    def __init__(
        self,
        parent,
        mediaplayer,
        zoom_value=10,
        zoom_scale_x=80,
        zoom_scale_y=45,
        zoom_area_pos=QPoint(0, 0),
    ):
        super().__init__(parent)
        self.setWindowTitle("Controle de Zoom")
        self.setFixedSize(500, 400)
        self.setWindowIcon(QIcon(os.path.join(icon_path, "zoom-title.png")))
        self.mediaplayer = mediaplayer

        # Aplica tema escuro ao modal
        self.setStyleSheet(
            """
            QDialog {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: #B0B0B0;
                margin: 0px;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #0078D7;
                border: 1px solid #5c5c5c;
                width: 20px;
                margin: -5px 0;
            }
            QSlider::sub-page:horizontal {
                background: #0078D7;
                border: 1px solid #777777;
                height: 8px;
                border-radius: 4px;
            }
            QSlider::add-page:horizontal {
                background: #B0B0B0;
                border: 1px solid #777777;
                height: 8px;
                border-radius: 4px;
            }
            QPushButton {
                background-color: #0078D7;
                color: white;
                padding: 8px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005bb5;
            }
        """
        )

        # 🔹 Layout principal
        layout = QVBoxLayout()

        # 🖥️ Frame de preview do vídeo
        self.video_preview = QFrame(self)
        self.video_preview.setStyleSheet(
            "background-color: black; border: 2px solid white;"
        )
        self.video_preview.setFixedSize(320, 180)
        self.video_preview.setMouseTracking(True)

        # 🔸 Label onde exibiremos o snapshot
        self.snapshot_label = QLabel(self.video_preview)
        self.snapshot_label.setAlignment(Qt.AlignCenter)
        self.snapshot_label.setScaledContents(True)
        self.snapshot_label.resize(320, 180)

        # 🔍 Área de zoom (movível)
        self.zoom_area = QLabel("ZOOM", self.video_preview)
        self.zoom_area.setStyleSheet(
            """
            QLabel {
                background-color: rgba(50, 50, 50, 150);  /* Fundo escuro semitransparente */
                color: #ffffff;                         /* Texto branco */
                font-weight: bold;
                border: 2px solid #ffffff;               /* Borda azul */
                border-radius: 5px;
                padding: 5px;
            }
        """
        )
        self.zoom_area.setAlignment(Qt.AlignCenter)

        # Recebemos os valores e definimos no diálogo
        self.zoom_value = zoom_value
        self.zoom_scale_x = zoom_scale_x
        self.zoom_scale_y = zoom_scale_y

        self.zoom_area.setFixedSize(self.zoom_scale_x, self.zoom_scale_y)
        self.zoom_area.move(zoom_area_pos)

        # Para movimentar a área de zoom
        self.zoom_offset = QPoint(0, 0)
        self.zoom_moving = False

        # 📏 Slider de nível de Zoom
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setMinimum(10)  # 1.0x zoom
        self.zoom_slider.setMaximum(40)  # 4.0x zoom
        self.zoom_slider.setValue(self.zoom_value)
        self.zoom_slider.setTickInterval(5)
        self.zoom_slider.setTickPosition(QSlider.TicksBelow)
        self.zoom_slider.valueChanged.connect(self.update_zoom)

        # 🔘 Botão Aplicar Zoom
        self.apply_button = QPushButton(" Aplicar Zoom")
        self.apply_button.setIcon(QIcon(os.path.join(icon_path, "zoom.png")))

        # 🔘 Botão Resetar Zoom
        self.reset_button = QPushButton(" Resetar Zoom")
        self.reset_button.setIcon(QIcon(os.path.join(icon_path, "rotate.png")))

        self.apply_button.clicked.connect(self.apply_zoom)
        self.reset_button.clicked.connect(self.reset_zoom)

        # 🔹 Organização dos elementos
        layout.addWidget(self.video_preview, alignment=Qt.AlignCenter)
        layout.addWidget(self.zoom_slider)

        # Cria um layout horizontal para os botões
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.apply_button)
        buttons_layout.addWidget(self.reset_button)

        # Adiciona o layout horizontal ao layout principal
        layout.addLayout(buttons_layout)

        self.setLayout(layout)

        self.update_snapshot()

    def update_zoom(self, value):
        """Atualiza a área de zoom conforme o usuário move o slider"""
        self.zoom_value = value
        self.zoom_scale_x = int(value / 10 * 80)
        self.zoom_scale_y = int(value / 10 * 45)
        self.zoom_area.setFixedSize(self.zoom_scale_x, self.zoom_scale_y)
        self.limit_zoom_area()

    def apply_zoom(self):
        """Aplica o zoom ao vídeo no VLC e fecha o modal com Accept"""
        zoom_pos = self.zoom_area.pos()
        zoom_size = self.zoom_area.size()
        pos_x = zoom_pos.x()
        pos_y = zoom_pos.y()
        width = zoom_size.width()
        height = zoom_size.height()

        # Exemplo de crop usando VLC
        self.mediaplayer.video_set_crop_geometry(
            f"{pos_x * 4 + (width * 4)}x{pos_y * 4 + (height * 4)}+{pos_x * 4}+{pos_y * 4}"
        )

        self.accept()

    def reset_zoom(self):
        """Redefine para valores 'padrão' (ou defina como preferir)"""
        self.zoom_value = 40
        self.zoom_scale_x = 80
        self.zoom_scale_y = 45
        self.zoom_area.setFixedSize(self.zoom_scale_x, self.zoom_scale_y)
        self.zoom_area.move(0, 0)
        self.zoom_slider.setValue(self.zoom_value)

    def limit_zoom_area(self):
        """Garante que a área de zoom não saia do preview"""
        max_x = self.video_preview.width() - self.zoom_area.width()
        max_y = self.video_preview.height() - self.zoom_area.height()
        self.zoom_area.move(
            max(0, min(self.zoom_area.x(), max_x)),
            max(0, min(self.zoom_area.y(), max_y)),
        )

    def update_snapshot(self):
        """Captura um snapshot do player principal e exibe no QLabel."""
        import tempfile

        snapshot_dir = tempfile.gettempdir()
        snapshot_path = os.path.join(snapshot_dir, "temp_preview.png")
        # Tira snapshot do player principal; tamanho 320x180
        if self.zoom_value == 40 or self.zoom_value == 0:
            self.mediaplayer.video_take_snapshot(0, snapshot_path, 320, 180)
        if os.path.exists(snapshot_path):
            pixmap = QPixmap(snapshot_path)
            if not pixmap.isNull():
                self.snapshot_label.setPixmap(pixmap)

    # Eventos de mouse para arrastar a área de zoom
    def mousePressEvent(self, event):
        video_pos = self.video_preview.pos()
        relative_pos = event.pos() - video_pos
        if self.zoom_area.geometry().contains(relative_pos):
            self.zoom_moving = True
            self.zoom_offset = relative_pos - self.zoom_area.pos()

    def mouseMoveEvent(self, event):
        if self.zoom_moving:
            video_pos = self.video_preview.pos()
            relative_pos = event.pos() - video_pos
            new_pos = relative_pos - self.zoom_offset
            self.zoom_area.move(new_pos)
            self.limit_zoom_area()

    def mouseReleaseEvent(self, event):
        self.zoom_moving = False
