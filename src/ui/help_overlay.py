from PySide6.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

class HelpOverlay(QDialog):
    """
    A semi-transparent overlay that displays available keyboard shortcuts.
    """
    def __init__(self, keybindings: dict, parent=None):
        super().__init__(parent)

        # Ensure the widget is deleted when closed to prevent memory leaks
        self.setAttribute(Qt.WA_DeleteOnClose)

        # --- Window Style ---
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Popup)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background-color: rgba(30, 30, 30, 0.9); color: #cccccc; border-radius: 8px;")
        self.setFixedSize(500, 600)

        # --- Layout and Widgets ---
        self.layout = QVBoxLayout(self)
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Command", "Shortcut"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setStyleSheet("""
            QTableWidget { background-color: transparent; border: none; }
            QHeaderView::section { background-color: #3c3c3c; padding: 4px; border: none; }
        """)

        self.layout.addWidget(self.table)
        self.populate_shortcuts(keybindings)
        self.center_on_parent()

    def populate_shortcuts(self, keybindings: dict):
        # Invert the dictionary for display: { 'command_id': 'shortcut' }
        command_to_shortcut = {v: k for k, v in keybindings.items()}
        self.table.setRowCount(len(command_to_shortcut))
        for i, (command, shortcut) in enumerate(sorted(command_to_shortcut.items())):
            self.table.setItem(i, 0, QTableWidgetItem(command))
            self.table.setItem(i, 1, QTableWidgetItem(shortcut))

    def center_on_parent(self):
        if self.parent():
            parent_rect = self.parent().geometry()
            self.move(parent_rect.x() + (parent_rect.width() - self.width()) // 2, parent_rect.y() + (parent_rect.height() - self.height()) // 2)

    def keyPressEvent(self, event):
        # Close on Escape or F1 again
        if event.key() in (Qt.Key_Escape, Qt.Key_F1):
            self.close()
        else:
            super().keyPressEvent(event)