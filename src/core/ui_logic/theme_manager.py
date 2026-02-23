import json
import os
import logging
from typing import Dict, Any
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtGui import QColor, QPalette

logger = logging.getLogger("ThemeManager")

class ThemeManager:
    """Gerencia o carregamento e aplicação de temas visuais.
    
    Responsável por ler arquivos JSON de configuração e traduzi-los
    para QSS (Qt Style Sheets) e configurações de paleta.
    """

    def __init__(self, themes_dir: str):
        self.themes_dir = themes_dir
        self.current_theme: Dict[str, Any] = {}
        # Tema padrão de fallback
        self._default_theme = {
            "background": "#1e1e1e",
            "foreground": "#d4d4d4",
            "selection": "#264f78",
            "sidebar_bg": "#252526",
            "statusbar_bg": "#007acc",
            "accent": "#007acc",
            "line_highlight": "#282828",
            "indent_guide": "#404040",
            "bracket_match": "rgba(200, 200, 200, 0.5)",
            "minimap_overlay": "rgba(255, 255, 255, 0.1)"
        }

    def load_theme(self, theme_name: str) -> None:
        """Carrega um tema a partir de um arquivo JSON."""
        theme_path = os.path.join(self.themes_dir, f"{theme_name}.json")
        
        if os.path.exists(theme_path):
            try:
                with open(theme_path, 'r') as f:
                    self.current_theme = json.load(f)
                logger.info(f"Tema '{theme_name}' carregado com sucesso.")
            except Exception as e:
                logger.error(f"Erro ao carregar tema '{theme_name}': {e}")
                self.current_theme = self._default_theme.copy()
        else:
            logger.warning(f"Tema '{theme_name}' não encontrado. Usando padrão.")
            self.current_theme = self._default_theme.copy()

    def apply_theme(self, app: QApplication) -> None:
        """Aplica o tema atual à aplicação globalmente."""
        if not self.current_theme:
            self.current_theme = self._default_theme

        bg = self.current_theme.get("background", "#1e1e1e")
        fg = self.current_theme.get("foreground", "#d4d4d4")
        sidebar = self.current_theme.get("sidebar_bg", "#252526")
        sidebar_fg = "#cccccc"
        status = self.current_theme.get("statusbar_bg", "#007acc")
        
        # Gera o QSS Global
        style_sheet = f"""
        QMainWindow {{
            background-color: {bg};
        }}
        QPlainTextEdit {{
            background-color: {bg};
            color: {fg};
            border: none;
            font-family: 'Consolas', 'Monospace';
            font-size: 14px;
        }}
        /* Sidebar Styling */
        QWidget#Sidebar, QTreeView {{
            background-color: {sidebar};
            color: {sidebar_fg};
            border: none;
        }}
        QTreeView::item:hover {{
            background-color: #2a2d2e;
        }}
        QTreeView::item:selected {{
            background-color: #37373d;
            color: white;
        }}
        /* Sidebar Buttons */
        QPushButton#SidebarAction {{
            background-color: transparent;
            border: none;
            color: {sidebar_fg};
        }}
        QPushButton#SidebarAction:hover {{
            background-color: #3e3e42;
        }}
        QStatusBar {{
            background-color: {status};
            color: white;
        }}
        QSplitter::handle {{
            background-color: {sidebar};
        }}
        """
        app.setStyleSheet(style_sheet)

    def get_color(self, key: str) -> str:
        """Retorna uma cor específica do tema atual."""
        return self.current_theme.get(key, "#ff00ff")