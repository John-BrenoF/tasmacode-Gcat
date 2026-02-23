from PySide6.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QKeySequence
from src.core.ui_logic.shortcuts import Shortcuts

class HelpWindow(QDialog):
    """Janela de ajuda sólida listando atalhos e comandos."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Atalhos do JCode")
        self.resize(600, 500)
        
        # Estilo Sólido (Dark Theme Base)
        self.setStyleSheet("""
            QDialog { background-color: #252526; color: #cccccc; }
            QTableWidget { background-color: #1e1e1e; border: 1px solid #3e3e42; gridline-color: #3e3e42; }
            QHeaderView::section { background-color: #333333; color: #cccccc; padding: 4px; border: none; }
            QLabel { font-weight: bold; font-size: 14px; margin-top: 10px; color: #007acc; }
        """)

        self.layout = QVBoxLayout(self)
        
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Ação", "Atalho"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.NoSelection)
        
        self.layout.addWidget(self.table)
        
        self._populate_shortcuts()
        
    def _populate_shortcuts(self):
        """Preenche a tabela com os atalhos definidos."""
        # Mapeamento organizado por seções
        sections = {
            "Arquivos": [
                ("Novo Arquivo", Shortcuts.NEW_FILE),
                ("Nova Pasta", Shortcuts.NEW_FOLDER),
                ("Abrir Arquivo", Shortcuts.OPEN_FILE),
                ("Salvar", Shortcuts.SAVE_FILE),
                ("Salvar Como", Shortcuts.SAVE_AS),
                ("Fechar Aba", Shortcuts.CLOSE_TAB),
            ],
            "Edição": [
                ("Desfazer", Shortcuts.UNDO),
                ("Refazer", Shortcuts.REDO),
                ("Copiar", Shortcuts.COPY),
                ("Colar", Shortcuts.PASTE),
                ("Localizar", Shortcuts.FIND),
            ],
            "Interface & Navegação": [
                ("Alternar Sidebar", Shortcuts.TOGGLE_SIDEBAR),
                ("Atualizar Explorer", Shortcuts.REFRESH_EXPLORER),
                ("Próxima Aba", Shortcuts.NEXT_TAB),
                ("Aba Anterior", Shortcuts.PREV_TAB),
                ("Paleta de Comandos", Shortcuts.COMMAND_PALETTE),
            ],
            "Geral": [
                ("Ajuda", Shortcuts.HELP)
            ]
        }
        
        row = 0
        self.table.setRowCount(sum(len(items) for items in sections.values()) + len(sections))
        
        font_mono = QFont("Consolas")
        font_mono.setStyleHint(QFont.Monospace)

        for section, items in sections.items():
            # Cabeçalho de Seção (Simulado)
            self.table.setItem(row, 0, QTableWidgetItem(f"--- {section} ---"))
            self.table.item(row, 0).setForeground(Qt.gray)
            row += 1
            
            for label, shortcut in items:
                self.table.setItem(row, 0, QTableWidgetItem(label))
                
                if not isinstance(shortcut, QKeySequence):
                    shortcut = QKeySequence(shortcut)
                
                shortcut_str = shortcut.toString(QKeySequence.NativeText)
                item_shortcut = QTableWidgetItem(shortcut_str)
                item_shortcut.setFont(font_mono)
                item_shortcut.setTextAlignment(Qt.AlignCenter)
                
                self.table.setItem(row, 1, item_shortcut)
                row += 1