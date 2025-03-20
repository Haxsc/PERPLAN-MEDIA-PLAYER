import sys
import vlc
import os
from PySide6.QtWidgets import QMainWindow, QFileDialog, QLabel, QMenu, QDialog
from PySide6.QtCore import Qt, QTimer, QPoint
from PySide6.QtGui import QIcon, QAction, QKeyEvent, QFontMetrics
from playlist import PlaylistModal
from ui_elements import create_ui  # Importa a função para criar a UI
from styles import apply_styles
from zoom import ZoomModal

icon_path = os.path.join(os.path.dirname(__file__), "icons")


class ModernVideoPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PPL Player")
        self.resize(1280, 720)

        # Instância do VLC
        self.instance = vlc.Instance()
        self.mediaplayer = self.instance.media_player_new()

        self.keybinds = {
            "Pausar/Reproduzir": "Space",
            "Avancar 1 Frame": "E",
            "Retroceder 1 Frame": "Q",
            "Avançar 1s": "Right",
            "Retroceder 1s": "Left",
            "Aumentar Volume": "Up",
            "Diminuir Volume": "Down",
            "Tela Cheia": "F",
            "Aumentar Velocidade": "+",
            "Diminuir Velocidade": "-",
        }

        # Configurações
        self.fps = 0
        self.current_frame = 0
        self.max_frames = 0
        self.speed_factor = 1
        self.playlist = []
        self.current_video_index = -1
        self.pauseAt_15 = False
        self.pauseAt_30 = False
        self.pauseAt_45 = False

        # Zoom Configs
        self.stored_zoom_value = 0
        self.stored_zoom_scale_x = 80
        self.stored_zoom_scale_y = 45
        self.stored_zoom_area_pos = QPoint(0, 0)

        # Criando UI
        self.create_ui()
        self.apply_styles()

        # Timer para atualização do slider
        self.timer = QTimer()
        self.timer.setInterval(300)
        self.timer.timeout.connect(self.update_ui)

    def create_ui(self):
        """Cria a interface gráfica, delegando ao `ui_elements.py`."""
        (
            self.open_button,
            self.videoframe,
            self.play_button,
            self.skip_button,
            self.rewind_button,
            self.speed_button,
            self.position_slider,
        ) = create_ui(self)
        # Cria e adiciona o overlay de desenho sobre o videoframe

    def apply_styles(self):
        """Aplica os estilos definidos no `styles.py`"""
        apply_styles(self)

    def open_zoom_dialog(self):
        """Abre o modal para configurar o zoom"""
        if self.current_video_index != -1:
            zoom_modal = ZoomModal(
                parent=self,
                mediaplayer=self.mediaplayer,
                zoom_value=self.stored_zoom_value,
                zoom_scale_x=self.stored_zoom_scale_x,
                zoom_scale_y=self.stored_zoom_scale_y,
                zoom_area_pos=self.stored_zoom_area_pos,
            )
            if zoom_modal.exec():
                self.stored_zoom_value = zoom_modal.zoom_value
                self.stored_zoom_scale_x = zoom_modal.zoom_scale_x
                self.stored_zoom_scale_y = zoom_modal.zoom_scale_y
                self.stored_zoom_area_pos = zoom_modal.zoom_area.pos()
        else:
            self.notification("Nenhum vídeo carregado!", "red")

    def open_playlist_dialog(self):
        """Abre um modal para exibir os vídeos da playlist."""
        if not self.playlist:
            self.notification("Nenhum vídeo na playlist!", "red")
            return

        dialog = PlaylistModal(self, self.playlist)
        if dialog.exec():  # Se o usuário selecionar um vídeo e confirmar
            if dialog.selected_video:
                self.current_video_index = (
                    dialog.selected_index
                )  # Atualiza o índice atual
                self.open_file(dialog.selected_video)  # Reproduz o vídeo escolhido

    def open_file_dialog(self):
        video_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Selecionar Vídeos",
            "P:/",
            "Vídeos (*.dav *.mp4 *.avi *.mkv)",
        )
        if video_paths:
            self.playlist.extend(video_paths)  # Adiciona à playlist
            if (
                self.current_video_index == -1
            ):  # Se nenhum vídeo estiver carregado, inicie o primeiro
                self.current_video_index = 0
                self.open_file(self.playlist[self.current_video_index])

    def open_settings_dialog(self):
        """Abre o modal de configurações de binds"""
        from settings import SettingsModal

        dialog = SettingsModal(self, self.keybinds)
        if dialog.exec():
            self.keybinds = (
                dialog.new_keybinds
            )  # Atualiza os binds escolhidos pelo usuário

    def play_next(self):
        """Reproduz o próximo vídeo na playlist."""
        if self.current_video_index < len(self.playlist) - 1:
            self.current_video_index += 1
            self.open_file(self.playlist[self.current_video_index])
        else:
            self.notification("Fim da playlist!", "red")

    def play_previous(self):
        """Reproduz o vídeo anterior na playlist."""
        if self.current_video_index > 0:
            self.current_video_index -= 1
            self.open_file(self.playlist[self.current_video_index])
        else:
            self.notification("Início da playlist!", "red")

    def open_file(self, filename):
        media = self.instance.media_new(filename)
        self.mediaplayer.set_media(media)

        if sys.platform == "win32":
            self.mediaplayer.set_hwnd(self.videoframe.winId())
        else:
            self.mediaplayer.set_xwindow(self.videoframe.winId())

        self.play_pause()
        self.timer.start()

    def play(self):
        if self.mediaplayer.is_playing():
            return
        self.mediaplayer.play()
        self.play_button.setIcon(QIcon(os.path.join(icon_path, "play.png")))

    def pause(self):
        if not self.mediaplayer.is_playing():
            return
        self.mediaplayer.pause()
        self.play_button.setIcon(QIcon(os.path.join(icon_path, "pause.png")))

    def play_pause(self):
        if self.mediaplayer.is_playing():
            self.mediaplayer.pause()
            self.play_button.setIcon(QIcon(os.path.join(icon_path, "play.png")))
        else:
            self.mediaplayer.play()
            self.play_button.setIcon(QIcon(os.path.join(icon_path, "pause.png")))

    def set_position(self, position):
        self.mediaplayer.set_time(position)

    def set_speed(self, speed):
        self.mediaplayer.set_rate(speed)
        self.speed_factor = speed

    def skip_seconds(self, seconds):
        """Avança ou retrocede o vídeo em segundos"""
        current_time = self.mediaplayer.get_time()
        new_time = max(0, min(self.max_frames, current_time + (seconds * 1000)))
        self.mediaplayer.set_time(new_time)

    def get_correct_fps(self):
        """Obtém o FPS real do vídeo através do tempo total e da contagem de frames."""
        total_time_ms = self.mediaplayer.get_length()  # Obtém duração total (ms)

        if total_time_ms <= 0:
            self.notification("Erro ao obter a duração do vídeo.", "red")
            return 30  # Valor padrão de fallback

        total_frames = self.mediaplayer.get_length() // (
            1000 / 30
        )  # Estima frames pelo tempo

        estimated_fps = total_frames / (
            total_time_ms / 1000
        )  # FPS = Total de frames / Duração em segundos

        return round(estimated_fps)

    def step_frame(self):
        """Avança ou retrocede um frame no vídeo"""
        if self.mediaplayer.is_playing():
            self.pause()

        self.mediaplayer.next_frame()  # 🔴 Força o VLC a exibir o frame correto

    def mspf(self):
        """Milliseconds per frame"""
        return int(1000 // (self.mediaplayer.get_fps() or 30))

    def on_previous_frame(self):
        """Go backward one frame"""
        if self.mediaplayer.is_playing():
            self.pause()
        next_frame_time = self.mediaplayer.get_time() - self.mspf()

        self.mediaplayer.set_time(next_frame_time)

    def change_volume(self, amount):
        """Ajusta o volume do player"""
        current_volume = self.mediaplayer.audio_get_volume()
        new_volume = max(0, min(100, current_volume + amount))
        self.mediaplayer.audio_set_volume(new_volume)

    def change_speed(self, factor):
        """Ajusta a velocidade do vídeo"""
        new_speed = max(
            0.5, min(32, self.speed_factor * factor)
        )  # Mantém entre 0.5x e 4x
        self.mediaplayer.set_rate(new_speed)
        self.speed_factor = new_speed
        self.notification(f"Speed: {new_speed:.2f}x", "rgba(189, 189, 189, 0.5)")

    def increment_speed(self, factor):
        """Ajusta a velocidade do vídeo"""
        new_speed = max(
            0.5, min(32, self.speed_factor + factor)
        )  # Mantém entre 0.5x e 4x
        self.mediaplayer.set_rate(new_speed)
        self.speed_factor = new_speed
        self.notification(f"Speed: {new_speed:.2f}x", "rgba(189, 189, 189, 0.5)")

    def toggle_fullscreen(self, exit_fullscreen=False):
        """Ativa/Desativa modo de tela cheia"""
        if exit_fullscreen or self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def calculate_text_width(self, widget, text):
        """Retorna a largura em pixels do texto, considerando a fonte atual do widget."""
        fm = QFontMetrics(widget.font())
        return fm.horizontalAdvance(text)

    def notification(self, message, color="orange", duration=5000):
        if hasattr(self, "snackbar"):
            self.snackbar.setText(message)
            self.snackbar.setStyleSheet(
                f"""
                QLabel {{
                    background-color: {color};
                    color: white;
                    font-size: 15px;
                    font-weight: bold;
                    padding: 12px 20p
                    x;
                    border-radius: 50px;
                }}
            """
            )

            # Calcular a largura do texto
            text_width = self.calculate_text_width(self.snackbar, message)
            # Acrescentar uma folga para padding (por ex.: 40 pixels)
            text_width += 40

            min_width = 150
            max_width = self.width() * 0.8
            snackbar_width = max(min_width, min(text_width, max_width))

            # Força essa largura
            self.snackbar.setFixedWidth(snackbar_width)
            # Se quiser que a altura seja recalculada com base na nova largura, chame:
            self.snackbar.adjustSize()

            # Centraliza no topo (pegando a nova altura)
            final_width = self.snackbar.width()
            final_height = self.snackbar.height()
            x = (self.width() - final_width) // 2
            y = 20
            self.snackbar.setGeometry(x, y, final_width, final_height)

            self.snackbar.show()
        else:
            # Cria a snackbar pela primeira vez
            self.snackbar = QLabel(message, self)
            self.snackbar.setAlignment(Qt.AlignCenter)
            self.snackbar.setStyleSheet(
                f"""
                QLabel {{
                    background-color: {color};
                    color: white;
                    font-size: 15px;
                    font-weight: bold;
                    padding: 12px 20px;
                    border-radius: 50px;
                }}
            """
            )

            # Calcular a largura do texto
            text_width = self.calculate_text_width(self.snackbar, message) + 40

            min_width = 150
            max_width = self.width() * 0.8
            snackbar_width = max(min_width, min(text_width, max_width))

            self.snackbar.setFixedWidth(snackbar_width)
            self.snackbar.setWordWrap(True)
            self.snackbar.adjustSize()

            final_width = self.snackbar.width()
            final_height = self.snackbar.height()
            x = (self.width() - final_width) // 2
            y = 20
            self.snackbar.setGeometry(x, y, final_width, final_height)
            self.snackbar.show()

        if not hasattr(self, "snackbar_timer"):
            self.snackbar_timer = QTimer()
        self.snackbar_timer.stop()
        self.snackbar_timer.setSingleShot(True)
        self.snackbar_timer.timeout.connect(self.hide_notification)
        self.snackbar_timer.start(duration)

    def hide_notification(self):
        """Esconde a notificação e libera memória"""
        if hasattr(self, "snackbar"):
            self.snackbar.hide()

    def update_snackbar_geometry(self):
        """Atualiza a posição e o tamanho da notificação, se ela estiver visível."""
        if hasattr(self, "snackbar") and self.snackbar.isVisible():
            min_width = 150
            max_width = self.width() * 0.8
            # Recalcula a largura; você pode usar self.snackbar.width() ou self.snackbar.sizeHint().width()
            snackbar_width = max(
                min_width, min(self.snackbar.sizeHint().width(), max_width)
            )
            self.snackbar.setFixedWidth(snackbar_width)
            # Posiciona a notificação no topo, centralizada horizontalmente
            self.snackbar.setGeometry(
                self.width() // 2 - snackbar_width // 2, 20, snackbar_width, 50
            )

    def open_speed_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet(
            """
            QMenu {
                background-color: #202124;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border-radius: 10px;
                padding: 10px;
            }
            QMenu::item {
                padding: 10px 20px;
                border-radius: 5px;
            }
            QMenu::item:selected {
                background-color: #383a3e;
            }
        """
        )

        speeds = ["1x", "2x", "4x", "6x", "8x", "10x", "12x", "16x", "32x"]

        for speed_text in speeds:
            action = QAction(speed_text, self)
            action.triggered.connect(
                lambda checked, s=speed_text: self.set_speed(float(s.replace("x", "")))
            )
            menu.addAction(action)

        button_pos = self.speed_button.mapToGlobal(
            self.speed_button.rect().bottomLeft()
        )
        menu.exec(button_pos)

    def update_ui(self):
        if self.mediaplayer.is_playing():
            self.current_frame = self.mediaplayer.get_time()
            self.max_frames = self.mediaplayer.get_length()
            self.position_slider.setRange(0, int(self.max_frames))
            self.position_slider.setValue(int(self.current_frame))

            if (
                self.current_frame
                >= (self.max_frames * (1 / 4) - (self.speed_factor * 300))
                and self.current_frame
                <= (self.max_frames * (1 / 4) + (self.speed_factor * 300))
                and not self.pauseAt_15
            ):
                self.pauseAt_15 = True
                self.pause()
                self.notification(
                    "Pausado automaticamente, Lembre-se de salvar o progresso.",
                )
            elif (
                self.current_frame
                >= (self.max_frames * (1 / 2) - (self.speed_factor * 300))
                and self.current_frame
                <= (self.max_frames * (1 / 2) + (self.speed_factor * 300))
                and not self.pauseAt_30
            ):
                self.pauseAt_30 = True
                self.pause()
                self.notification(
                    "Pausado automaticamente, Lembre-se de salvar o progresso."
                )
            elif (
                self.current_frame
                >= (self.max_frames * (3 / 4) - (self.speed_factor * 300))
                and self.current_frame
                <= (self.max_frames * (3 / 4) + (self.speed_factor * 300))
                and not self.pauseAt_45
            ):
                self.pauseAt_45 = True
                self.pause()
                self.notification(
                    "Pausado automaticamente, Lembre-se de salvar o progresso."
                )
        elif (
            self.current_video_index != -1
            and self.current_frame >= self.max_frames - 300
        ):
            self.play_next()  # Passa para o próximo vídeo ao terminar

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.resize_video()
        self.update_snackbar_geometry()

    def resize_video(self):
        if sys.platform == "win32":
            self.mediaplayer.set_hwnd(self.videoframe.winId())
        else:
            self.mediaplayer.set_xwindow(self.videoframe.winId())

    def get_key_name(self, key):
        """Converte o código da tecla em um nome legível."""
        if key == Qt.Key_Space:
            return "SPACE"
        elif key == Qt.Key_Return or key == Qt.Key_Enter:
            return "ENTER"
        elif key == Qt.Key_Backspace:
            return "BACKSPACE"
        elif key == Qt.Key_Shift:
            return "SHIFT"
        elif key == Qt.Key_Control:
            return "CTRL"
        elif key == Qt.Key_Alt:
            return "ALT"
        elif key == Qt.Key_Escape:
            return "ESCAPE"
        elif key == Qt.Key_Tab:
            return "TAB"
        elif key == Qt.Key_Left:
            return "LEFT"
        elif key == Qt.Key_Right:
            return "RIGHT"
        elif key == Qt.Key_Up:
            return "UP"
        elif key == Qt.Key_Down:
            return "DOWN"
        else:
            return (
                chr(key).upper() if 32 <= key <= 126 else ""
            )  # Retorna a tecla em maiúscula

    def keyPressEvent(self, event: QKeyEvent):
        """Captura eventos de teclado e executa ações do player com os binds do usuário"""
        key_name = self.get_key_name(event.key())

        if key_name.upper() == self.keybinds["Pausar/Reproduzir"].upper():
            self.play_pause()
        elif key_name == self.keybinds["Avancar 1 Frame"].upper():
            self.step_frame()
        elif key_name == self.keybinds["Retroceder 1 Frame"].upper():
            self.on_previous_frame()
        elif key_name == self.keybinds["Avançar 1s"].upper():
            self.skip_seconds(1)
        elif key_name == self.keybinds["Retroceder 1s"].upper():
            self.skip_seconds(-1)
        elif key_name == self.keybinds["Aumentar Volume"].upper():
            self.change_volume(10)
        elif key_name == self.keybinds["Diminuir Volume"].upper():
            self.change_volume(-10)
        elif key_name == self.keybinds["Tela Cheia"].upper():
            self.toggle_fullscreen()
        elif key_name == self.keybinds["Aumentar Velocidade"].upper():
            self.change_speed(2)
        elif key_name == self.keybinds["Diminuir Velocidade"].upper():
            self.change_speed(0.5)
        elif key_name == "[":
            self.increment_speed(0.1)
        elif key_name == "]":
            self.increment_speed(-0.1)
        else:
            super().keyPressEvent(event)

    def set_zoom(self, scale):
        """Define o nível de zoom no vídeo"""
        self.mediaplayer.video_set_scale(scale)
        self.notification(f"Zoom ajustado para {scale:.1f}x", "green")
