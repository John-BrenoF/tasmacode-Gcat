from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit,
                               QTreeView, QFileSystemModel, QHBoxLayout, 
                               QStackedWidget, QFrame, QStyle)
from PySide6.QtCore import Qt, Signal, QDir, QEvent
from PySide6.QtGui import QIcon
import os
from src.core.editor_logic.file_manager import FileManager

class Sidebar(QWidget):
    """Barra lateral para explorador de arquivos e ferramentas."""
    
    # Sinais para desacoplar a lógica
    open_folder_clicked = Signal()
    file_clicked = Signal(str) # Envia o caminho do arquivo
    file_created = Signal(str) # Novo arquivo criado
    status_message = Signal(str, int) # Mensagem para statusbar (msg, timeout)

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
        
        self.btn_new_file.clicked.connect(lambda: self._start_creation(is_folder=False))
        self.btn_new_folder.clicked.connect(lambda: self._start_creation(is_folder=True))
        self.btn_refresh.clicked.connect(self._refresh_tree)

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
        self.file_model.setRootPath(QDir.homePath())
        
        self.tree = QTreeView()
        self.tree.setModel(self.file_model)
        self.tree.setRootIndex(self.file_model.index(QDir.homePath()))
        self.tree.setHeaderHidden(True)
        self.tree.setColumnHidden(1, True) # Size
        self.tree.setColumnHidden(2, True) # Type
        self.tree.setColumnHidden(3, True) # Date
        self.tree.doubleClicked.connect(self._on_tree_double_click)
        
        self.stack.addWidget(self.tree)
        
        # --- Inline Input para Criação ---
        self.input_edit = QLineEdit(self.tree)
        self.input_edit.hide()
        self.input_edit.returnPressed.connect(self._on_input_return)
        self.input_edit.installEventFilter(self)
        self.input_edit.setStyleSheet("background-color: #3c3c3c; color: white; border: 1px solid #007acc;")
        
        # Estado interno
        self._creating_folder = False
        self._creation_base_path = ""

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

    def _get_current_path(self):
        """Retorna o diretório base para criação (pasta selecionada ou pai do arquivo)."""
        index = self.tree.currentIndex()
        root = self.file_model.rootPath()
        
        if not index.isValid():
            return root
            
        path = self.file_model.filePath(index)
        if self.file_model.isDir(index):
            return path
        else:
            return os.path.dirname(path)

    def _start_creation(self, is_folder: bool):
        """Inicia o processo de criação mostrando o input."""
        if self.stack.currentWidget() != self.tree:
            return # Não faz nada se estiver no estado vazio
            
        self._creating_folder = is_folder
        self._creation_base_path = self._get_current_path()
        
        # Posicionamento do Input
        index = self.tree.currentIndex()
        rect = self.tree.visualRect(index)
        
        # Se não houver seleção ou rect inválido, posiciona no topo
        if not rect.isValid():
            rect = self.tree.viewport().rect()
            rect.setHeight(24)
            y_pos = 0
        else:
            # Posiciona logo abaixo do item selecionado
            y_pos = rect.bottom()
            
        self.input_edit.move(0, y_pos)
        self.input_edit.setFixedSize(self.tree.width(), 24)
        self.input_edit.setPlaceholderText(f"Nome do {'Diretório' if is_folder else 'Arquivo'} (Enter para criar)")
        self.input_edit.clear()
        self.input_edit.show()
        self.input_edit.setFocus()

    def _on_input_return(self):
        """Processa a criação quando Enter é pressionado."""
        name = self.input_edit.text().strip()
        if not name:
            self.input_edit.hide()
            return
            
        try:
            if self._creating_folder:
                FileManager.create_directory(self._creation_base_path, name)
                self.status_message.emit(f"Pasta criada: {name}", 3000)
            else:
                full_path = FileManager.create_file(self._creation_base_path, name)
                self.status_message.emit(f"Arquivo criado: {name}", 3000)
                self.file_created.emit(full_path)
        except PermissionError:
            self.status_message.emit("Erro de Permissão: Acesso negado ao criar neste local.", 5000)
        except Exception as e:
            self.status_message.emit(f"Erro: {str(e)}", 5000)
        
        self.input_edit.hide()

    def _refresh_tree(self):
        # QFileSystemModel atualiza automaticamente, mas podemos forçar re-scan se necessário
        pass

    def eventFilter(self, obj, event):
        if obj == self.input_edit and event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Escape:
                self.input_edit.hide()
                return True
        return super().eventFilter(obj, event)