from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor

class VideoSurface(QVideoWidget):
    """
    Responsável exclusivamente pela renderização do vídeo na tela.
    Atua como a 'View' no padrão MVC.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Configuração visual padrão
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("background-color: black;")
        
        # Define proporção de aspecto padrão (pode ser alterado dinamicamente)
        self.setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatio)

    def set_full_screen(self, enabled: bool):
        """Alterna modo tela cheia."""
        self.setFullScreen(enabled)

    def set_aspect_ratio(self, mode: Qt.AspectRatioMode):
        """
        Define como o vídeo deve se ajustar à janela.
        Ex: Qt.KeepAspectRatio, Qt.IgnoreAspectRatio
        """
        self.setAspectRatioMode(mode)