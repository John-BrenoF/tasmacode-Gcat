from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

class Sidebar(QWidget):
    """Barra lateral para explorador de arquivos e ferramentas."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Sidebar") # Para estilização via QSS
        
        layout = QVBoxLayout(self)
        label = QLabel("Explorer")
        label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        label.setStyleSheet("color: #888; font-weight: bold; margin-top: 10px;")
        layout.addWidget(label)
        layout.addStretch()