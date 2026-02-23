from PySide6.QtWidgets import QStatusBar, QLabel

class StatusBar(QStatusBar):
    """Barra de status customizada."""
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.left_label = QLabel("Ready")
        self.right_label = QLabel("Ln 1, Col 1  UTF-8  Python")
        
        self.left_label.setStyleSheet("padding: 0 10px;")
        self.right_label.setStyleSheet("padding: 0 10px;")
        
        self.addWidget(self.left_label, 1) # Stretch
        self.addPermanentWidget(self.right_label)

    def set_message(self, msg: str):
        self.left_label.setText(msg)

    def update_info(self, line, col, encoding="UTF-8", lang="Text"):
        self.right_label.setText(f"Ln {line+1}, Col {col+1}  {encoding}  {lang}")