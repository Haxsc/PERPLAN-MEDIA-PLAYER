from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QApplication, QGraphicsOpacityEffect
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, Property
from PySide6.QtGui import QPixmap, QFont
import os

class SplashScreen(QWidget):
    """Tela de splash para feedback durante inicialização e atualizações"""
    
    def __init__(self, icon_path=None):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Efeito de opacidade para animações
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0.0)
        
        # Layout principal
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        
        # Container com fundo
        self.container = QWidget()
        self.container.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                border-radius: 15px;
                border: 2px solid #007acc;
            }
        """)
        
        # Habilita antialiasing para bordas suaves
        self.setAttribute(Qt.WA_OpaquePaintEvent, False)
        
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(35, 35, 35, 35)
        container_layout.setSpacing(15)
        
        # Ícone (se fornecido)
        if icon_path and os.path.exists(icon_path):
            icon_label = QLabel()
            pixmap = QPixmap(icon_path).scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_label.setPixmap(pixmap)
            icon_label.setAlignment(Qt.AlignCenter)
            container_layout.addWidget(icon_label)
        
        # Título
        title_label = QLabel("PPL Player")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #ffffff; padding: 12px;")
        title_label.setMinimumHeight(55)
        title_label.setMaximumHeight(80)
        container_layout.addWidget(title_label)
        
        # Label de status
        self.status_label = QLabel("Iniciando...")
        status_font = QFont()
        status_font.setPointSize(10)
        self.status_label.setFont(status_font)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #cccccc; padding: 10px;")
        self.status_label.setWordWrap(True)
        self.status_label.setMinimumHeight(40)
        container_layout.addWidget(self.status_label)
        
        # Barra de progresso
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(0)  # Modo indeterminado
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #2d2d2d;
                border-radius: 4px;
                border: none;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #005a9e, stop:0.5 #007acc, stop:1 #005a9e);
                border-radius: 4px;
            }
        """)
        container_layout.addWidget(self.progress_bar)
        
        # Adiciona container ao layout principal
        layout.addWidget(self.container)
        self.setLayout(layout)
        
        # Tamanho maior para evitar corte de texto
        self.setFixedSize(450, 320)
        
        # Centraliza na tela
        self.center_on_screen()
        
        # Animação de fade-in ao aparecer
        self.fade_in()
    
    def center_on_screen(self):
        """Centraliza a janela na tela"""
        from PySide6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
    
    def fade_in(self):
        """Animação de fade-in suave"""
        self.fade_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_animation.setDuration(300)  # 300ms
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.setEasingCurve(QEasingCurve.OutCubic)
        self.fade_animation.start()
    
    def fade_out(self):
        """Animação de fade-out suave"""
        self.fade_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_animation.setDuration(400)  # 400ms
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.setEasingCurve(QEasingCurve.InCubic)
        self.fade_animation.finished.connect(self.close)
        self.fade_animation.start()
    
    def set_status(self, message: str):
        """Atualiza a mensagem de status com transição suave"""
        self.status_label.setText(message)
        
        # Processa eventos para atualização imediata
        QApplication.processEvents()
        
        # Força repaint para evitar lag visual
        self.status_label.repaint()
    
    def set_progress(self, value: int, maximum: int = 100):
        """Define o progresso (0-100 por padrão)"""
        self.progress_bar.setMaximum(maximum)
        self.progress_bar.setValue(value)
        QApplication.processEvents()
    
    def set_indeterminate(self, enabled: bool = True):
        """Ativa/desativa modo indeterminado"""
        if enabled:
            self.progress_bar.setMaximum(0)
        else:
            self.progress_bar.setMaximum(100)
        QApplication.processEvents()
    
    def close_with_fade(self, delay_ms: int = 300):
        """Fecha a splash screen após um delay com animação"""
        QTimer.singleShot(delay_ms, self.fade_out)


def create_splash(icon_path=None):
    """Função helper para criar splash screen"""
    splash = SplashScreen(icon_path)
    splash.show()
    QApplication.processEvents()
    return splash
