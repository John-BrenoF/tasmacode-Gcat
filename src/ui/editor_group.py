from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QLabel
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtCore import Qt, Signal
from .editor import CodeEditor
import os

class EditorGroup(QWidget):
    """
    A container that manages multiple CodeEditor widgets in a tabbed interface.
    """
    active_editor_changed = Signal(object) # Emits the new active CodeEditor or None

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
        
        self.layout.addWidget(self.tab_widget)
        
        self._show_placeholder()

    def _show_placeholder(self):
        """Exibe um placeholder com um ícone e texto de boas-vindas."""
        placeholder_widget = QWidget()
        placeholder_layout = QVBoxLayout(placeholder_widget)
        placeholder_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder_layout.setSpacing(20)

        # --- Ícone SVG ---
        icon_path = '/home/johnb/JCODE/icon/JCODE.svg'

        if os.path.exists(icon_path):
            svg_widget = QSvgWidget(icon_path)
            svg_widget.setFixedSize(650, 510)
            placeholder_layout.addWidget(svg_widget)
        else:
            icon_missing_label = QLabel(f"[Ícone não encontrado: {icon_path}]")
            icon_missing_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            placeholder_layout.addWidget(icon_missing_label)

        # --- Título ---
        titulo_label = QLabel(" ")
        titulo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder_layout.addWidget(titulo_label)

        # --- Dicas ---
        dicas = [
            "                 Ctrl + B →          Mostrar/Ocultar barra lateral",
            "                 Ctrl + S →          Salvar",
            "                 F1 →                 Ajuda"
        ]

        for dica in dicas:
            dica_label = QLabel(dica)
            dica_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            placeholder_layout.addWidget(dica_label)

        self.placeholder = placeholder_widget
        self.tab_widget.addTab(self.placeholder, "")
        self.tab_widget.setTabsClosable(False)

    def add_editor(self, editor_widget: CodeEditor, file_path: str) -> None:
        """Adds a new editor to a tab."""
        if self.tab_widget.widget(0) == self.placeholder:
            self.tab_widget.removeTab(0)
            self.tab_widget.setTabsClosable(True)
            
        file_name = os.path.basename(file_path)
        index = self.tab_widget.addTab(editor_widget, file_name)
        self.tab_widget.setCurrentIndex(index)

    def close_tab(self, index: int) -> None:
        # TODO: Check for unsaved changes before closing
        widget = self.tab_widget.widget(index)
        self.tab_widget.removeTab(index)
        if widget:
            widget.deleteLater()
        
        if self.tab_widget.count() == 0:
            self._show_placeholder()
            self.active_editor_changed.emit(None)

    def get_active_editor(self) -> CodeEditor | None:
        widget = self.tab_widget.currentWidget()
        return widget if isinstance(widget, CodeEditor) else None

    def _on_tab_changed(self, index: int) -> None:
        editor = self.tab_widget.widget(index)
        if isinstance(editor, CodeEditor):
            self.active_editor_changed.emit(editor)
        else:
            self.active_editor_changed.emit(None)