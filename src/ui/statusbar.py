from PySide6.QtWidgets import QStatusBar, QLabel, QPushButton, QWidget, QHBoxLayout, QStyle
from PySide6.QtCore import Qt

class StatusBar(QStatusBar):
    """Barra de status customizada."""
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Remove a alça de redimensionamento padrão para visual mais limpo
        self.setSizeGripEnabled(False)
        
        # Container para widgets da direita
        self.right_container = QWidget()
        self.right_layout = QHBoxLayout(self.right_container)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.right_layout.setSpacing(10)
        
        # Widgets
        self.lbl_cursor = self._create_clickable_label("Ln 1, Col 1")
        self.lbl_indent = self._create_clickable_label("Spaces: 4")
        self.lbl_encoding = self._create_clickable_label("UTF-8")
        self.lbl_lang = self._create_clickable_label("Python")
        
        self.btn_bell = QPushButton()
        self.btn_bell.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation))
        self.btn_bell.setFlat(True)
        self.btn_bell.setFixedSize(20, 20)
        self.btn_bell.setStyleSheet("border: none;")

        # Adiciona ao layout
        self.right_layout.addWidget(self.lbl_cursor)
        self.right_layout.addWidget(self.lbl_indent)
        self.right_layout.addWidget(self.lbl_encoding)
        self.right_layout.addWidget(self.lbl_lang)
        self.right_layout.addWidget(self.btn_bell)

        self.addPermanentWidget(self.right_container)
        self.showMessage("Ready")

    def _create_clickable_label(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet("color: white; padding: 0 5px;")
        lbl.setCursor(Qt.CursorShape.PointingHandCursor)
        # TODO: Implementar mousePressEvent para ações (ex: mudar encoding)
        return lbl

    def update_cursor_info(self, line, col):
        self.lbl_cursor.setText(f"Ln {line+1}, Col {col+1}")

    def update_lang(self, lang):
        self.lbl_lang.setText(lang)