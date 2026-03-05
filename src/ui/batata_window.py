from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

class BatataWindow(QDialog):
    """
    Uma janela de diálogo simples que exibe a palavra 'batata' essa vai se a janela de novidades.
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Batata")
        self.resize(400, 470)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        label = QLabel("batata")
        label.setStyleSheet("font-size: 48px; font-weight: bold;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(label)
