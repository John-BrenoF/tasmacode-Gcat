from PySide6.QtWidgets import QMenu, QGraphicsDropShadowEffect
from PySide6.QtGui import QAction, QIcon, QColor
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

        # Adiciona uma sombra para um visual mais moderno
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(18)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 160))
        self.setGraphicsEffect(shadow)

        self._setup_ui()
        self._apply_theme()

    def _setup_ui(self):
        # Ações de Edição
        self._add_action("Selecionar Tudo", self.logic.select_all, shortcut="Ctrl+A")
        self.addSeparator()
        self._add_action("Copiar", self.logic.copy, shortcut="Ctrl+C")
        self._add_action("Recortar", self.logic.cut, shortcut="Ctrl+X")
        self._add_action("Colar", self.logic.paste, shortcut="Ctrl+V")
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

        history_menu = self.addMenu("Histórico de Cópia")
        history_menu.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogResetButton))

        if history:
            for i, text in enumerate(history):
                # Limita o texto exibido para não quebrar o layout do menu
                display_text = text.strip().replace('\n', ' ↵ ')
                if len(display_text) > 50:
                    display_text = display_text[:50] + "..."
                
                action = history_menu.addAction(f"{i+1}. {display_text}")
                action.triggered.connect(lambda checked=False, t=text: self.logic.paste_from_history(t))
            history_menu.addSeparator()

        clear_action = history_menu.addAction("Limpar Histórico")
        clear_action.triggered.connect(self.logic.clear_clipboard_history)
        if not history:
            clear_action.setEnabled(False)

    def _apply_theme(self):
        """Aplica o tema atual ao menu."""
        if not self.theme_manager or not self.theme_manager.current_theme:
            return
            
        theme = self.theme_manager.current_theme
        bg_hex = theme.get("sidebar_bg", "#252526")
        fg = theme.get("foreground", "#cccccc")
        border = theme.get("border_color", "#3e3e42")
        accent = theme.get("accent", "#007acc")
        
        # Converte a cor de fundo para RGBA para adicionar translucidez
        bg_color = QColor(bg_hex)
        bg_rgba = f"rgba({bg_color.red()}, {bg_color.green()}, {bg_color.blue()}, 0.95)" # 95% de opacidade

        self.setStyleSheet(f"""
            QMenu {{
                background-color: {bg_rgba};
                color: {fg};
                border: 1px solid {border};
                padding: 6px;
                border-radius: 8px;
            }}
            QMenu::item {{
                padding: 8px 25px;
                border-radius: 4px;
                margin: 2px 0;
            }}
            QMenu::item:selected {{
                background-color: {accent};
                color: white;
            }}
            QMenu::item:disabled {{
                color: #666;
                background-color: transparent;
            }}
            QMenu::separator {{
                height: 1px;
                background: {border};
                margin: 6px 4px;
            }}
            QMenu::right-arrow {{
                width: 16px;
                height: 16px;
                padding-left: 10px;
            }}
        """)