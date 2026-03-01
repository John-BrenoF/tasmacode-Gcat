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
            "background": "#282a36",
            "foreground": "#f8f8f2",
            "selection": "#44475a",
            "sidebar_bg": "#21222c",
            "statusbar_bg": "#21222c",
            "accent": "#ff79c6",
            "line_highlight": "#44475a70",
            "indent_guide": "#6272a4",
            "bracket_match": "#f8f8f2",
            "minimap_overlay": "#44475a70",
            "gutter_bg": "#282a36",
            "gutter_fg": "#6272a4",
            # Syntax Highlighting Defaults
            "keyword_color": "#ff79c6",
            "builtin_color": "#8be9fd",
            "string_color": "#f1fa8c",
            "comment_color": "#6272a4",
            "class_color": "#50fa7b",
            "function_color": "#50fa7b",
            "operator_color": "#ff79c6"
        }

    def load_theme(self, theme_name: str) -> None:
        """Carrega um tema a partir de um arquivo JSON."""
        theme_path = os.path.join(self.themes_dir, f"{theme_name}.json")
        
        if os.path.exists(theme_path):
            try:
                with open(theme_path, 'r') as f:
                    loaded_data = json.load(f)
                    self.current_theme = self._default_theme.copy()
                    self.current_theme.update(loaded_data)
                logger.info(f"Tema '{theme_name}' carregado com sucesso.")
            except Exception as e:
                logger.error(f"Erro ao carregar tema '{theme_name}': {e}")
                self.current_theme = self._default_theme.copy()
        else:
            logger.warning(f"Tema '{theme_name}' não encontrado. Usando tema padrão.")
            self.current_theme = self._default_theme.copy()

    def get_available_themes(self) -> list[str]:
        """Retorna uma lista com os nomes dos temas disponíveis."""
        if not os.path.exists(self.themes_dir):
            return []
        return sorted([f[:-5] for f in os.listdir(self.themes_dir) if f.endswith(".json")])

    def apply_theme(self, app: QApplication) -> None:
        """Aplica o tema atual à aplicação globalmente."""
        if not self.current_theme:
            self.current_theme = self._default_theme

        logger.debug(f"Applying theme: {self.current_theme}")
        bg = self.current_theme.get("background", "#282a36")
        fg = self.current_theme.get("foreground", "#d4d4d4")
        sidebar = self.current_theme.get("sidebar_bg", "#252526")
        sidebar_fg = "#cccccc"
        status = self.current_theme.get("statusbar_bg", "#007acc")
        accent = self.current_theme.get("accent", "#007acc")
        selection = self.current_theme.get("selection", "#44475a")
        line_highlight = self.current_theme.get("line_highlight", "#2a2d2e")
        
        # Gera o QSS Global
        style_sheet = f"""
        QMainWindow {{
            background-color: {bg};
        }}
        QPlainTextEdit, QAbstractScrollArea {{
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
            background-color: {line_highlight};
        }}
        QTreeView::item:selected {{
            background-color: {selection};
            color: white;
        }}
        /* Sidebar Buttons */
        QPushButton#SidebarAction {{
            background-color: transparent;
            border: none;
            color: {sidebar_fg};
        }}
        QPushButton#SidebarAction:hover {{
            background-color: {selection};
        }}
        QStatusBar {{
            background-color: {status};
            color: white;
        }}
        QSplitter::handle {{
            background-color: {sidebar};
        }}
        /* Menu Bar Styling */
        QMenuBar {{
            background-color: {sidebar};
            color: {sidebar_fg};
        }}
        QMenuBar::item:selected {{
            background-color: {selection};
        }}
        QMenu {{
            background-color: {sidebar};
            color: {sidebar_fg};
        }}
        QMenu::item:selected {{
            background-color: {accent};
        }}
        /* ScrollBar Styling */
        QScrollBar:vertical {{
            border: none;
            background: {sidebar};
            width: 14px;
            margin: 0px 0px 0px 0px;
        }}
        QScrollBar::handle:vertical {{
            background: {selection};
            min-height: 20px;
            border-radius: 7px;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            border: none;
            background: none;
        }}
        QScrollBar:horizontal {{
            height: 14px;
            background: {sidebar};
            border: none;
        }}
        QScrollBar::handle:horizontal {{
            background: {selection};
            min-width: 20px;
            border-radius: 7px;
        }}
        """
        app.setStyleSheet(style_sheet)

    def get_color(self, key: str) -> str:
        logger.debug(f"Getting color for key: {key}, color: {self.current_theme.get(key, '#ff00ff')}")
        """Retorna uma cor específica do tema atual."""
        return self.current_theme.get(key, "#ff00ff")