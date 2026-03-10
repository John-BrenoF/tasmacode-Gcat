from PySide6.QtWidgets import QMenu
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QStyle

class EditorContextMenu(QMenu):
    """
    Widget visual para o menu de contexto do editor.
    Configura a aparência e os itens do menu.
    """
    def __init__(self, logic, theme_manager, parent=None):
        super().__init__(parent)
        self.logic = logic
        self.theme_manager = theme_manager
        self._setup_ui()
        self._apply_theme()

    def _setup_ui(self):
        # Ações de Edição
        self._add_action("Selecionar Tudo", self.logic.select_all, QStyle.StandardPixmap.SP_FileDialogDetailedView, "Ctrl+A")
        self.addSeparator()
        self._add_action("Copiar", self.logic.copy, QStyle.StandardPixmap.SP_FileIcon, "Ctrl+C")
        self._add_action("Recortar", self.logic.cut, QStyle.StandardPixmap.SP_FileIcon, "Ctrl+X")
        self._add_action("Colar", self.logic.paste, QStyle.StandardPixmap.SP_FileIcon, "Ctrl+V")
        self._setup_clipboard_history()
        self.addSeparator()
        
        # Ações de Arquivo
        self._add_action("Salvar", self.logic.save, QStyle.StandardPixmap.SP_DialogSaveButton, "Ctrl+S")
        self._add_action("Fechar Aba", self.logic.close_tab, QStyle.StandardPixmap.SP_TitleBarCloseButton, "Ctrl+W")

    def _add_action(self, text, callback, icon_pixmap=None, shortcut=None):
        action = QAction(text, self)
        if icon_pixmap:
            action.setIcon(self.style().standardIcon(icon_pixmap))
        if shortcut:
            action.setShortcut(shortcut)
        
        action.triggered.connect(callback)
        self.addAction(action)

    def _setup_clipboard_history(self):
        """Cria o submenu para o histórico da área de transferência."""
        if not self.logic.clipboard_manager:
            return

        history = self.logic.clipboard_manager.get_history()
        if not history:
            return

        history_menu = self.addMenu("Histórico de Cópia")
        history_menu.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogResetButton))

        for i, text in enumerate(history):
            # Limita o texto exibido para não quebrar o layout do menu
            display_text = text.strip().replace('\n', ' ↵ ')
            if len(display_text) > 50:
                display_text = display_text[:50] + "..."
            
            action = history_menu.addAction(f"{i+1}. {display_text}")
            action.triggered.connect(lambda checked=False, t=text: self.logic.paste_from_history(t))

    def _apply_theme(self):
        """Aplica o tema atual ao menu."""
        if not self.theme_manager or not self.theme_manager.current_theme:
            return
            
        theme = self.theme_manager.current_theme
        bg = theme.get("sidebar_bg", "#252526")
        fg = theme.get("foreground", "#cccccc")
        border = theme.get("border_color", "#3e3e42")
        accent = theme.get("accent", "#007acc")
        
        self.setStyleSheet(f"""
            QMenu {{
                background-color: {bg};
                color: {fg};
                border: 1px solid {border};
                padding: 5px;
            }}
            QMenu::item {{
                padding: 5px 20px;
                border-radius: 4px;
            }}
            QMenu::item:selected {{
                background-color: {accent};
                color: white;
            }}
            QMenu::separator {{
                height: 1px;
                background: {border};
                margin: 5px 0;
            }}
        """)