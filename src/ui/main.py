import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QSplitter, QFileDialog
from PySide6.QtGui import QKeySequence
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor, QAction, QKeySequence

# Ajuste de Path para garantir que imports funcionem a partir da raiz
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "../../"))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.core.editor_logic.buffer import DocumentBuffer
from src.core.editor_logic.file_manager import FileManager
from src.core.ui_logic.extension_bridge import ExtensionBridge
from src.core.editor_logic.highlighter_engine import HighlighterEngine
from src.core.ui_logic.theme_manager import ThemeManager
from src.core.editor_logic.commands import CommandRegistry
from src.core.ui_logic.input_mapper import InputMapper
from src.core.ui_logic.event_handler import EventHandler
from src.core.ui_logic.viewport_controller import ViewportController
from src.ui.editor import CodeEditor
from src.ui.sidebar import Sidebar
from src.ui.statusbar import StatusBar
from src.ui.command_palette import CommandPalette

class JCodeMainWindow(QMainWindow):
    """Janela principal do editor JCODE.
    
    Responsável por orquestrar a inicialização dos subsistemas Core e UI.
    """

    def __init__(self):
        super().__init__()
        self.current_file_path = None
        
        # --- 1. Inicialização do Core (Lógica de Negócio) ---
        self.buffer = DocumentBuffer()
        
        # --- 2. Inicialização dos Subsistemas de UI Logic ---
        self.highlighter = HighlighterEngine()
        self.extension_bridge = ExtensionBridge()
        
        themes_path = os.path.join(root_dir, "themes")
        self.theme_manager = ThemeManager(themes_path)
        
        self.command_registry = CommandRegistry()
        self.input_mapper = InputMapper(self.command_registry)
        
        self.event_handler = EventHandler(self.extension_bridge, self.buffer)
        self.viewport_controller = ViewportController()
        
        # --- 3. Configuração da UI ---
        self.setWindowTitle("JCode - Modular Editor")
        self.resize(1024, 768)
        
        self._setup_ui()
        self._create_menu_bar()
        self._setup_logic_connections()
        
        # Carrega tema e extensões
        self.theme_manager.load_theme("dark_default") # Tenta carregar tema
        self.theme_manager.apply_theme(QApplication.instance())
        self._load_extensions()
        
        # Hook de inicialização
        self.extension_bridge.trigger_hook("on_app_start")

    def _setup_ui(self):
        """Configura os widgets da interface."""
        # Componentes principais
        self.sidebar = Sidebar()
        self.editor = CodeEditor()
        
        # Injeção de dependências no Editor
        self.editor.set_dependencies(self.buffer, self.theme_manager, self.highlighter)
        self.editor.set_input_mapper(self.input_mapper)
        
        self.custom_statusbar = StatusBar()
        self.setStatusBar(self.custom_statusbar)
        
        self.command_palette = CommandPalette(self)
        self._setup_commands()
        self._register_core_commands()
        
        # Layout com Splitter (Sidebar | Editor)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.sidebar)
        splitter.addWidget(self.editor)
        
        # Define proporção inicial (20% Sidebar, 80% Editor)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 4)
        
        self.setCentralWidget(splitter)

    def _create_menu_bar(self):
        """Cria e popula a barra de menu global."""
        menu_bar = self.menuBar()

        # --- Menu Arquivo ---
        file_menu = menu_bar.addMenu("&Arquivo")
        
        new_file_action = QAction("Novo Arquivo", self)
        new_file_action.setEnabled(False) # Placeholder
        file_menu.addAction(new_file_action)

        open_file_action = QAction("Abrir Arquivo...", self)
        open_file_action.setEnabled(False) # Placeholder
        file_menu.addAction(open_file_action)

        open_folder_action = QAction("Abrir Pasta...", self)
        open_folder_action.triggered.connect(self._open_folder_dialog)
        file_menu.addAction(open_folder_action)

        file_menu.addSeparator()

        self.save_action = QAction("Salvar", self)
        self.save_action.setShortcut(QKeySequence.StandardKey.Save)
        self.save_action.setEnabled(False) # Desabilitado até o buffer ficar 'dirty'
        self.save_action.triggered.connect(lambda: self.command_registry.execute("file.save"))
        file_menu.addAction(self.save_action)

        save_as_action = QAction("Salvar Como...", self)
        save_as_action.triggered.connect(lambda: self.command_registry.execute("file.save_as"))
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        exit_action = QAction("Sair", self)
        exit_action.triggered.connect(QApplication.instance().quit)
        file_menu.addAction(exit_action)

        # --- Menu Editar ---
        edit_menu = menu_bar.addMenu("&Editar")
        undo_action = QAction("Desfazer", self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.triggered.connect(lambda: self.command_registry.execute("edit.undo"))
        edit_menu.addAction(undo_action)

        redo_action = QAction("Refazer", self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.triggered.connect(lambda: self.command_registry.execute("edit.redo"))
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator()
        # Placeholders para funcionalidades futuras
        for name in ["Recortar", "Copiar", "Colar", "Localizar"]:
            action = QAction(name, self)
            action.setEnabled(False)
            edit_menu.addAction(action)

        # --- Menu Exibir ---
        view_menu = menu_bar.addMenu("&Exibir")
        toggle_sidebar_action = QAction("Alternar Barra Lateral", self)
        toggle_sidebar_action.triggered.connect(lambda: self.sidebar.setVisible(not self.sidebar.isVisible()))
        view_menu.addAction(toggle_sidebar_action)

        toggle_fullscreen_action = QAction("Tela Cheia", self)
        toggle_fullscreen_action.setCheckable(True)
        toggle_fullscreen_action.triggered.connect(lambda checked: self.showFullScreen() if checked else self.showNormal())
        view_menu.addAction(toggle_fullscreen_action)

        # --- Outros Menus (Placeholders) ---
        menu_bar.addMenu("&Ferramentas")
        menu_bar.addMenu("&Ajuda")

    def _register_core_commands(self):
        """Registra os comandos fundamentais do editor."""
        # Wrapper para atualizar a UI após comandos que alteram o buffer
        def wrap_edit(func, *args):
            func(*args)
            self._on_buffer_modified()

        r = self.command_registry
        b = self.buffer
        
        r.register("type_char", lambda t: wrap_edit(b.insert_text, t))
        r.register("edit.backspace", lambda: wrap_edit(b.delete_backspace))
        r.register("edit.new_line", lambda: wrap_edit(b.insert_text, "\n"))
        r.register("edit.indent", lambda: wrap_edit(b.insert_text, "    ")) # 4 spaces
        
        r.register("cursor.move_up", lambda: (b.move_cursors(-1, 0), self._on_buffer_modified()))
        r.register("cursor.move_down", lambda: (b.move_cursors(1, 0), self._on_buffer_modified()))
        r.register("cursor.move_left", lambda: (b.move_cursors(0, -1), self._on_buffer_modified()))
        r.register("cursor.move_right", lambda: (b.move_cursors(0, 1), self._on_buffer_modified()))
        
        r.register("cursor.add_up", lambda: (b.add_cursor_relative(-1), self._on_buffer_modified()))
        r.register("cursor.add_down", lambda: (b.add_cursor_relative(1), self._on_buffer_modified()))
        
        r.register("edit.undo", lambda: (self.buffer.undo(), self._on_buffer_modified()))
        r.register("edit.redo", lambda: (self.buffer.redo(), self._on_buffer_modified()))
        
        r.register("view.command_palette", self.command_palette.show_palette)
        r.register("file.save", self._save_file)
        r.register("file.save_as", self._save_file_as)

    def _setup_commands(self):
        """Registra comandos e atalhos."""
        # Atalho para Paleta de Comandos
        action = QAction("Command Palette", self)
        action.setShortcut(QKeySequence("Ctrl+Shift+P"))
        action.triggered.connect(self.command_palette.show_palette)
        self.addAction(action)
        
        # Registra comandos básicos
        self.command_palette.register_command("Editor: Toggle Sidebar", lambda: self.sidebar.setVisible(not self.sidebar.isVisible()))
        self.command_palette.register_command("File: Save", lambda: print("Save triggered"))
        self.command_palette.register_command("File: Open Folder", self._open_folder_dialog)

    def _setup_logic_connections(self):
        """Conecta a lógica de UI aos widgets."""
        # Instala o filtro de eventos no editor
        self.event_handler.install_on(self.editor)
        
        # Conecta o controlador de viewport ao editor
        self.viewport_controller.attach_to(self.editor)
        
        # Exemplo de conexão de sinal: Atualizar statusbar ao scrollar
        self.viewport_controller.visible_lines_changed.connect(
            lambda first, last: self.custom_statusbar.showMessage(f"Linhas visíveis: {first} - {last}")
        )
        
        # CONEXÃO BIDIRECIONAL:
        # Conecta o sinal de modificação do buffer a um slot que atualiza a UI
        self.event_handler.buffer_modified.connect(self._on_buffer_modified)
        
        # Conexões da Sidebar
        self.sidebar.open_folder_clicked.connect(self._open_folder_dialog)
        self.sidebar.file_clicked.connect(self._open_file)
        
        # Inicializa o editor com o texto do buffer
        self._on_buffer_modified() # Usar o mesmo método para a carga inicial

    def _open_folder_dialog(self):
        """Abre diálogo para selecionar pasta."""
        folder = QFileDialog.getExistingDirectory(self, "Abrir Pasta")
        if folder:
            self.sidebar.set_root_path(folder)

    def _save_file(self):
        if not self.current_file_path:
            self._save_file_as()
            return
        
        content = self.buffer.get_text()
        # Usando a versão síncrona do FileManager para simplicidade
        FileManager._write_sync(self.current_file_path, content)
        self.buffer.dirty = False
        self._on_buffer_modified()
        self.custom_statusbar.showMessage(f"Arquivo salvo: {self.current_file_path}", 3000)

    def _save_file_as(self):
        path, _ = QFileDialog.getSaveFileName(self, "Salvar Como...")
        if path:
            self.current_file_path = path
            self._save_file()

    def _open_file(self, path):
        """Abre um arquivo selecionado na sidebar."""
        # Usando a versão síncrona do FileManager para simplicidade na UI
        try:
            content = FileManager._read_sync(path, 'utf-8')
            self.current_file_path = path

            self.buffer = DocumentBuffer(content)
            self.buffer.dirty = False

            # Re-conecta dependências pois o objeto buffer mudou
            self.editor.set_dependencies(self.buffer, self.theme_manager, self.highlighter)
            self.event_handler.buffer = self.buffer
            self._on_buffer_modified()
            self.custom_statusbar.showMessage(f"Arquivo aberto: {os.path.basename(path)}", 5000)
        except Exception as e:
            self.custom_statusbar.showMessage(f"Erro ao abrir o arquivo: {e}", 5000)

    def _on_buffer_modified(self):
        """Atualiza o widget CodeEditor com o conteúdo do DocumentBuffer."""
        # Atualiza scrollbar caso o número de linhas tenha mudado
        self.viewport_controller.update_scrollbar(self.buffer)
        
        # Solicita repaint
        self.editor.viewport().update()

        # Atualiza título da janela para indicar modificações
        title = "JCode - "
        base_name = os.path.basename(self.current_file_path) if self.current_file_path else "Novo Arquivo"
        title += base_name
        if self.buffer.dirty:
            title += "*"
        self.setWindowTitle(title)
        
        # Atualiza Status Bar
        if self.buffer.cursors:
            c = self.buffer.cursors[-1]
            self.custom_statusbar.update_cursor_info(c.line, c.col)
        
        # Atualiza estado da ação 'Salvar'
        if hasattr(self, 'save_action'):
            self.save_action.setEnabled(self.buffer.dirty)
        
    def _load_extensions(self):
        """Carrega plugins e conecta sinais."""
        plugins_path = os.path.join(root_dir, "plugins")
        
        # Cria pasta de plugins se não existir
        if not os.path.exists(plugins_path):
            os.makedirs(plugins_path)
            
        # Conecta sinal da bridge para atualizar a UI
        self.extension_bridge.plugin_loaded.connect(
            lambda name: self.custom_statusbar.showMessage(f"Plugin carregado: {name}", 3000)
        )
        
        self.extension_bridge.load_plugins(plugins_path)

def main():
    """Ponto de entrada da aplicação."""
    app = QApplication(sys.argv)
    app.setApplicationName("JCode")
    
    window = JCodeMainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()