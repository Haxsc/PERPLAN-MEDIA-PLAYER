import sys
import vlc
import os
from PySide6.QtWidgets import QMainWindow, QFileDialog, QLabel, QMenu, QDialog
from PySide6.QtCore import Qt, QTimer, QPoint
from PySide6.QtGui import QIcon, QAction, QKeyEvent, QFontMetrics, QCursor
from playlist import PlaylistModal
from ui_elements import create_ui  # Importa a função para criar a UI
from styles import apply_styles
from zoom import ZoomModal
from utils import format_time_range, clamp
from config import (
    APP_NAME,
    DEFAULT_SIZE,
    ICON_PATH,
    UI_UPDATE_INTERVAL,
    DEFAULT_KEYBINDS,
    SPEED_OPTIONS,
    NOTIFICATION_DURATION,
    NOTIFICATION_COLORS,
    DEFAULT_VIDEO_PATH,
    VIDEO_FILTER,
    SUPPORTED_VIDEO_EXTENSIONS,
    AUTO_PAUSE_MIN_DURATION,
    AUTO_PAUSE_POSITIONS
)


class ModernVideoPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(*DEFAULT_SIZE)

        # Instância do VLC
        self.instance = vlc.Instance()
        self.mediaplayer = self.instance.media_player_new()

        # Configurações de teclas - usando configuração padrão
        self.keybinds = DEFAULT_KEYBINDS.copy()

        # Configurações do player
        self._initialize_player_state()
        
        # Configurações de zoom
        self._initialize_zoom_state()

        # Criando UI
        self.create_ui()
        self.apply_styles()

        # Timer para atualização do slider
        self.timer = QTimer()
        self.timer.setInterval(UI_UPDATE_INTERVAL)
        self.timer.timeout.connect(self.update_ui)

    def _initialize_player_state(self):
        """Initialize player state variables."""
        self.fps = 0
        self.current_frame = 0
        self.max_frames = 0
        self.speed_factor = 1
        self.playlist = []
        self.current_video_index = -1
        
        # Initialize auto-pause flags dynamically based on configuration
        for position in AUTO_PAUSE_POSITIONS:
            setattr(self, f"pauseAt_{int(position * 100)}", False)

    def _initialize_zoom_state(self):
        """Initialize zoom-related state variables."""
        self.stored_zoom_value = 0
        self.stored_zoom_scale_x = 80
        self.stored_zoom_scale_y = 45
        self.stored_zoom_area_pos = QPoint(0, 0)

        # # Controle de interface no fullscreen
        # self.last_mouse_pos = QCursor.pos()

        # self.mouse_check_timer = QTimer()
        # self.mouse_check_timer.setInterval(500)  # Checagem de movimento
        # self.mouse_check_timer.timeout.connect(self.check_mouse_activity)
        # self.mouse_check_timer.start()

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
            self.timer_label,
            self.header_layaout,
        ) = create_ui(self)
        # Cria e adiciona o overlay de desenho sobre o videoframe

    def hide_ui_elements(self):
        self.open_button.hide()
        self.play_button.hide()
        self.skip_button.hide()
        self.rewind_button.hide()
        self.speed_button.hide()
        self.position_slider.hide()
        self.timer_label.hide()

    def show_ui_elements(self):
        self.open_button.show()
        self.play_button.show()
        self.skip_button.show()
        self.rewind_button.show()
        self.speed_button.show()
        self.position_slider.show()
        self.timer_label.show()

    def check_mouse_activity(self):
        current_pos = QCursor.pos()
        if current_pos != self.last_mouse_pos:
            self.last_mouse_pos = current_pos
            print("Mouse se moveu!")
            self.mouse_check_timer.start()  # Reinicia timer de ocultar elementos

    def apply_styles(self):
        """Aplica os estilos definidos no `styles.py`"""
        apply_styles(self)

    def open_croqui_modal(self, croqui_path):
        """Open the croqui modal with the specified image."""
        try:
            from croqui_modal import CroquiModal
            croqui_modal = CroquiModal(self, croqui_path)
            if croqui_modal.exec():
                print("[CROQUI] Modal aceito - processo iniciado")
                return True
            else:
                print("[CROQUI] Modal cancelado")
                return False
        except Exception as e:
            self.notification(f"Erro ao abrir croqui: {e}", NOTIFICATION_COLORS["error"])
            return False

    def open_zoom_dialog(self):
        """Open the zoom configuration modal."""
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
            self.notification("Nenhum vídeo carregado!", NOTIFICATION_COLORS["error"])

    def open_playlist_dialog(self):
        """Open modal to display playlist videos."""
        if not self.playlist:
            self.notification("Nenhum vídeo na playlist!", NOTIFICATION_COLORS["warning"])
            return

        dialog = PlaylistModal(self, self.playlist, self.current_video_index)
        if dialog.exec():
            if dialog.selected_video:
                self.current_video_index = dialog.selected_index
                self.open_file(dialog.selected_video)

    def open_file_dialog(self):
        """Open file dialog to select video files."""
        try:
            video_paths, _ = QFileDialog.getOpenFileNames(
                self,
                "Selecionar Vídeos",
                DEFAULT_VIDEO_PATH,
                VIDEO_FILTER,
            )
            
            if video_paths:
                self.playlist.extend(video_paths)
                if self.current_video_index == -1:
                    # If no video is currently loaded, start with the first one
                    self.current_video_index = 0
                    self.open_file(self.playlist[self.current_video_index])
                    
        except Exception as e:
            self.notification(f"Erro ao abrir arquivo: {e}", NOTIFICATION_COLORS["error"])

    def open_settings_dialog(self):
        """Abre o modal de configurações de binds"""
        from settings import SettingsModal

        dialog = SettingsModal(self, self.keybinds)
        if dialog.exec():
            self.keybinds = (
                dialog.new_keybinds
            )  # Atualiza os binds escolhidos pelo usuário

    def play_next(self):
        """Play the next video in the playlist."""
        if self.current_video_index < len(self.playlist) - 1:
            self.current_video_index += 1
            self.open_file(self.playlist[self.current_video_index])
        else:
            self.notification("Fim da playlist!", NOTIFICATION_COLORS["warning"])

    def play_previous(self):
        """Play the previous video in the playlist."""
        if self.current_video_index > 0:
            self.current_video_index -= 1
            self.open_file(self.playlist[self.current_video_index])
        else:
            self.notification("Início da playlist!", NOTIFICATION_COLORS["warning"])

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
        """Start video playback."""
        if self.mediaplayer.is_playing():
            return
        self.mediaplayer.play()
        self.play_button.setIcon(QIcon(os.path.join(ICON_PATH, "play.png")))

    def pause(self):
        """Pause video playback."""
        if not self.mediaplayer.is_playing():
            return
        self.mediaplayer.pause()
        self.play_button.setIcon(QIcon(os.path.join(ICON_PATH, "pause.png")))

    def play_pause(self):
        """Toggle between play and pause states."""
        if self.mediaplayer.is_playing():
            self.mediaplayer.pause()
            self.play_button.setIcon(QIcon(os.path.join(ICON_PATH, "play.png")))
        else:
            self.mediaplayer.play()
            self.play_button.setIcon(QIcon(os.path.join(ICON_PATH, "pause.png")))

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
        current_frame = self.mediaplayer.get_time()
        new_frame = max(0, current_frame - 30)
        self.mediaplayer.set_time(new_frame)

    def change_volume(self, amount):
        """Adjust player volume.
        
        Args:
            amount (int): Amount to increase/decrease volume by
        """
        try:
            current_volume = self.mediaplayer.audio_get_volume()
            new_volume = max(0, min(100, current_volume + amount))
            self.mediaplayer.audio_set_volume(new_volume)
            
            # Show volume notification
            volume_text = f"Volume: {new_volume}%"
            if new_volume == 0:
                volume_text += " (Mudo)"
            elif new_volume == 100:
                volume_text += " (Máximo)"
                
            self.notification(volume_text, NOTIFICATION_COLORS["info"])
        except Exception as e:
            self.notification(f"Erro ao ajustar volume: {e}", NOTIFICATION_COLORS["error"])

    def change_speed(self, factor):
        """Adjust video speed by multiplication factor.
        
        Args:
            factor (float): Multiplication factor for speed change
        """
        from config import SPEED_MIN, SPEED_MAX
        new_speed = max(SPEED_MIN, min(SPEED_MAX, self.speed_factor * factor))
        self.mediaplayer.set_rate(new_speed)
        self.speed_factor = new_speed
        self.notification(f"Velocidade: {new_speed:.2f}x", NOTIFICATION_COLORS["info"])

    def increment_speed(self, increment):
        """Adjust video speed by adding increment.
        
        Args:
            increment (float): Amount to add/subtract from current speed
        """
        from config import SPEED_MIN, SPEED_MAX, SPEED_INCREMENT
        new_speed = max(SPEED_MIN, min(SPEED_MAX, self.speed_factor + increment))
        self.mediaplayer.set_rate(new_speed)
        self.speed_factor = new_speed
        self.notification(f"Velocidade: {new_speed:.2f}x", NOTIFICATION_COLORS["info"])

    def toggle_fullscreen(self, exit_fullscreen=False):
        """Ativa/Desativa modo de tela cheia"""
        if exit_fullscreen or self.isFullScreen():
            self.showNormal()
        else:
            self.hide_ui_elements()
            self.showFullScreen()

    def calculate_text_width(self, widget, text):
        """Retorna a largura em pixels do texto, considerando a fonte atual do widget."""
        fm = QFontMetrics(widget.font())
        return fm.horizontalAdvance(text)

    def notification(self, message, color=None, duration=None):
        """Display a notification message to the user.
        
        Args:
            message (str): Message to display
            color (str, optional): Color for the notification. Defaults to info color.
            duration (int, optional): Duration in milliseconds. Defaults to configured value.
        """
        if color is None:
            color = NOTIFICATION_COLORS["info"]
        if duration is None:
            duration = NOTIFICATION_DURATION
            
        try:
            if hasattr(self, "snackbar"):
                self.snackbar.setText(message)
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

                # Calculate text width
                text_width = self.calculate_text_width(self.snackbar, message) + 40
                min_width = 150
                max_width = int(self.width() * 0.8)
                snackbar_width = max(min_width, min(text_width, max_width))

                self.snackbar.setFixedWidth(snackbar_width)
                self.snackbar.adjustSize()

                # Position the notification
                final_width = self.snackbar.width()
                final_height = self.snackbar.height()
                x = (self.width() - final_width) // 2
                y = 20
                self.snackbar.setGeometry(x, y, final_width, final_height)
                self.snackbar.show()
            else:
                # Create notification for the first time
                self._create_new_notification(message, color)

            # Set up timer to hide notification
            if not hasattr(self, "snackbar_timer"):
                self.snackbar_timer = QTimer()
            self.snackbar_timer.stop()
            self.snackbar_timer.setSingleShot(True)
            self.snackbar_timer.timeout.connect(self.hide_notification)
            self.snackbar_timer.start(duration)
            
        except Exception as e:
            print(f"Error displaying notification: {e}")

    def _create_new_notification(self, message, color):
        """Create a new notification widget."""
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

        text_width = self.calculate_text_width(self.snackbar, message) + 40
        min_width = 150
        max_width = int(self.width() * 0.8)
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
        """Open speed selection menu."""
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

        for speed_text in SPEED_OPTIONS:
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
        """Update UI elements with current playback information."""
        if not self.mediaplayer.is_playing():
            return
            
        try:
            self.current_frame = self.mediaplayer.get_time()
            self.max_frames = self.mediaplayer.get_length()
            
            if self.max_frames <= 0:
                return
                
            # Update slider
            self.position_slider.setRange(0, int(self.max_frames))
            self.position_slider.setValue(int(self.current_frame))
            
            # Update timer label using utility function
            self.timer_label.setText(format_time_range(self.current_frame, self.max_frames))
            
            # Handle auto-pause for long videos
            self._handle_auto_pause()
            
        except Exception as e:
            print(f"Error updating UI: {e}")

    def _handle_auto_pause(self):
        """Handle automatic pausing for long videos at specific intervals."""
        max_minutes = int(self.max_frames / 1000 / 60)
        
        if max_minutes <= AUTO_PAUSE_MIN_DURATION:
            # For short videos, auto-advance to next video
            current_seconds = int(self.current_frame / 1000)
            max_seconds = int(self.max_frames / 1000)
            
            if (self.current_video_index != -1 and 
                current_seconds + self.speed_factor >= max_seconds):
                self.play_next()
            return
            
        # For long videos, pause at specific intervals
        tolerance = self.speed_factor * 500  # milliseconds
        
        for i, position in enumerate(AUTO_PAUSE_POSITIONS):
            pause_time = self.max_frames * position
            attr_name = f"pauseAt_{int(position * 100)}"
            
            if (self.current_frame >= pause_time - tolerance and 
                self.current_frame <= pause_time + tolerance and
                not getattr(self, attr_name, False)):
                
                # Reset other pause flags
                for j, pos in enumerate(AUTO_PAUSE_POSITIONS):
                    other_attr = f"pauseAt_{int(pos * 100)}"
                    setattr(self, other_attr, j == i)
                
                self.pause()
                self.notification(
                    "Pausado automaticamente, Lembre-se de salvar o progresso.",
                    NOTIFICATION_COLORS["warning"]
                )
                break
            elif (self.current_frame <= pause_time - tolerance and 
                  getattr(self, attr_name, False)):
                setattr(self, attr_name, False)

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
