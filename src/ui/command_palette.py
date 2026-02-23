from PySide6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem
from PySide6.QtCore import Qt, Signal

class CommandPalette(QDialog):
    """Janela flutuante para busca e execução de comandos (Ctrl+Shift+P)."""
    
    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.FramelessWindowHint | Qt.WindowType.Popup)
        self.resize(500, 300)
        self.setStyleSheet("background-color: #252526; border: 1px solid #454545; color: #cccccc;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type a command...")
        self.search_input.setStyleSheet("background-color: #3c3c3c; border: none; padding: 5px; color: white;")
        self.search_input.textChanged.connect(self._filter_commands)
        
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("background-color: #252526; border: none;")
        self.list_widget.itemActivated.connect(self._execute_command)
        
        layout.addWidget(self.search_input)
        layout.addWidget(self.list_widget)
        
        self.commands = {} # "Nome": callback

    def register_command(self, name, callback):
        self.commands[name] = callback

    def show_palette(self):
        self.search_input.clear()
        self._populate_list()
        # Centraliza na janela pai
        if self.parent():
            geo = self.parent().geometry()
            x = geo.x() + (geo.width() - self.width()) // 2
            y = geo.y() + 50 # Um pouco abaixo do topo
            self.move(x, y)
        self.show()
        self.search_input.setFocus()

    def _populate_list(self):
        self.list_widget.clear()
        for name in self.commands:
            self.list_widget.addItem(name)

    def _filter_commands(self, text):
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item.setHidden(text.lower() not in item.text().lower())

    def _execute_command(self, item):
        cmd_name = item.text()
        if cmd_name in self.commands:
            self.commands[cmd_name]()
            self.close()