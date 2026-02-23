from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                               QTreeView, QFileSystemModel, QHBoxLayout, 
                               QStackedWidget, QFrame, QStyle)
from PySide6.QtCore import Qt, Signal, QDir
from PySide6.QtGui import QIcon

class Sidebar(QWidget):
    """Barra lateral para explorador de arquivos e ferramentas."""
    
    # Sinais para desacoplar a lógica
    open_folder_clicked = Signal()
    file_clicked = Signal(str) # Envia o caminho do arquivo

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Sidebar") # Para estilização via QSS
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # --- Toolbar de Ações Rápidas ---
        self.toolbar = QFrame()
        self.toolbar.setFixedHeight(30)
        tb_layout = QHBoxLayout(self.toolbar)
        tb_layout.setContentsMargins(5, 0, 5, 0)
        
        # Botões simples (ícones padrão do Qt para garantir compatibilidade)
        self.btn_new_file = self._create_action_btn(QStyle.StandardPixmap.SP_FileIcon, "Novo Arquivo")
        self.btn_new_folder = self._create_action_btn(QStyle.StandardPixmap.SP_DirIcon, "Nova Pasta")
        self.btn_refresh = self._create_action_btn(QStyle.StandardPixmap.SP_BrowserReload, "Recarregar")
        
        tb_layout.addWidget(QLabel("EXPLORER"))
        tb_layout.addStretch()
        tb_layout.addWidget(self.btn_new_file)
        tb_layout.addWidget(self.btn_new_folder)
        tb_layout.addWidget(self.btn_refresh)
        
        self.layout.addWidget(self.toolbar)

        # --- Área Principal (Stack) ---
        self.stack = QStackedWidget()
        self.layout.addWidget(self.stack)

        # Estado 1: Vazio
        self.empty_state = QWidget()
        empty_layout = QVBoxLayout(self.empty_state)
        empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.btn_open = QPushButton("Abrir Pasta")
        self.btn_open.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_open.setStyleSheet("background-color: #007acc; color: white; padding: 8px 16px; border-radius: 4px; border: none;")
        self.btn_open.clicked.connect(self.open_folder_clicked.emit)
        
        empty_layout.addWidget(QLabel("Nenhuma pasta aberta"))
        empty_layout.addWidget(self.btn_open)
        self.stack.addWidget(self.empty_state)

        # Estado 2: Árvore de Arquivos
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath(QDir.rootPath())
        
        self.tree = QTreeView()
        self.tree.setModel(self.file_model)
        self.tree.setRootIndex(self.file_model.index(QDir.rootPath()))
        self.tree.setHeaderHidden(True)
        self.tree.setColumnHidden(1, True) # Size
        self.tree.setColumnHidden(2, True) # Type
        self.tree.setColumnHidden(3, True) # Date
        self.tree.doubleClicked.connect(self._on_tree_double_click)
        
        self.stack.addWidget(self.tree)

    def _create_action_btn(self, icon_std, tooltip):
        btn = QPushButton()
        btn.setIcon(self.style().standardIcon(icon_std))
        btn.setToolTip(tooltip)
        btn.setObjectName("SidebarAction")
        btn.setFixedSize(24, 24)
        return btn

    def set_root_path(self, path: str):
        """Define a pasta raiz da árvore."""
        self.stack.setCurrentWidget(self.tree)
        self.tree.setRootIndex(self.file_model.index(path))

    def _on_tree_double_click(self, index):
        path = self.file_model.filePath(index)
        if not self.file_model.isDir(index):
            self.file_clicked.emit(path)