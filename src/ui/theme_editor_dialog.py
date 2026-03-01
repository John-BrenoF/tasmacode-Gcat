from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QWidget, QLabel, 
                               QPushButton, QComboBox, QColorDialog, QInputDialog, 
                               QMessageBox, QScrollArea, QFormLayout, QTextEdit)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from src.core.ui_logic.theme_editor_logic import ThemeEditorLogic

class ThemeEditorDialog(QDialog):
    """Janela para edição visual de temas."""
    
    # Sinal emitido para o preview ao vivo
    theme_updated = Signal(dict)

    def __init__(self, theme_manager, parent=None):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.logic = ThemeEditorLogic(theme_manager)
        
        self.setWindowTitle("Editor de Temas")
        self.resize(800, 600)
        self.setStyleSheet("background-color: #252526; color: #cccccc;")

        # --- Layout Principal ---
        main_layout = QVBoxLayout(self)
        top_layout = QHBoxLayout()
        
        # --- Controles Superiores (Seleção e Ações) ---
        self.theme_selector = QComboBox()
        self.theme_selector.setStyleSheet("background-color: #3c3c3c; padding: 5px;")
        self.theme_selector.addItems(self.theme_manager.get_available_themes())
        self.theme_selector.currentTextChanged.connect(self._load_theme_for_editing)

        self.save_button = QPushButton("Salvar")
        self.save_as_button = QPushButton("Salvar Como...")
        
        top_layout.addWidget(QLabel("Editar Tema:"))
        top_layout.addWidget(self.theme_selector)
        top_layout.addStretch()
        top_layout.addWidget(self.save_button)
        top_layout.addWidget(self.save_as_button)
        
        main_layout.addLayout(top_layout)

        # --- Área de Conteúdo (Seletores e Preview) ---
        content_layout = QHBoxLayout()
        
        # --- Painel de Seletores de Cor (Esquerda) ---
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: 1px solid #454545; }")
        
        self.color_pickers_widget = QWidget()
        self.form_layout = QFormLayout(self.color_pickers_widget)
        self.form_layout.setSpacing(10)
        self.form_layout.setContentsMargins(10, 10, 10, 10)
        
        scroll_area.setWidget(self.color_pickers_widget)
        
        # --- Painel de Preview (Direita) ---
        self.preview_widget = QTextEdit()
        self.preview_widget.setReadOnly(True)
        self.preview_widget.setText(
            '# Exemplo de código Python\n'
            'class MyClass(object):\n'
            '    def __init__(self, name: str):\n'
            '        self.name = name  # Comentário\n'
            '        self.value = "Hello World!"\n\n'
            '    def greet(self):\n'
            '        if self.name:\n'
            '            return f"Greetings, {self.name}"\n'
            '        return None'
        )

        content_layout.addWidget(scroll_area, 1) # Ocupa 1/3
        content_layout.addWidget(self.preview_widget, 2) # Ocupa 2/3
        
        main_layout.addLayout(content_layout)

        # --- Conexões ---
        self.save_button.clicked.connect(self._save_current)
        self.save_as_button.clicked.connect(self._save_as)

        # --- Inicialização ---
        self.color_buttons = {}
        self._populate_color_pickers()
        self._load_theme_for_editing(self.theme_selector.currentText())

    def _populate_color_pickers(self):
        """Cria os botões de seleção de cor com base nas chaves do tema."""
        for key in self.logic.get_editable_keys():
            btn = QPushButton()
            btn.setFixedSize(100, 25)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda k=key: self._handle_color_button_clicked(k))
            
            self.color_buttons[key] = btn
            self.form_layout.addRow(f"{key}:", btn)

    def _load_theme_for_editing(self, theme_name):
        """Carrega os dados de um tema e atualiza a UI."""
        if not theme_name: return
        self.logic.load_theme_data(theme_name)
        self._update_ui_from_draft()

    def _update_ui_from_draft(self):
        """Atualiza os botões e o preview com as cores do rascunho."""
        draft = self.logic.draft_theme
        for key, btn in self.color_buttons.items():
            color = draft.get(key, "#ff00ff")
            btn.setStyleSheet(f"background-color: {color}; border: 1px solid #555;")
        
        # Atualiza o preview e a aplicação inteira
        self.theme_updated.emit(draft)
        self._update_preview_widget(draft)

    def _handle_color_button_clicked(self, key):
        """Abre o QColorDialog e atualiza a cor."""
        current_color = QColor(self.logic.draft_theme.get(key))
        new_color = QColorDialog.getColor(current_color, self, f"Selecione a cor para '{key}'")
        
        if new_color.isValid():
            self.logic.update_color(key, new_color.name())
            self._update_ui_from_draft()

    def _update_preview_widget(self, theme_data):
        """Aplica um estilo QSS simples ao widget de preview."""
        style = f"""
        QTextEdit {{
            background-color: {theme_data.get('background', '#fff')};
            color: {theme_data.get('foreground', '#000')};
            font-family: Consolas, Monospace;
            font-size: 14px;
            border: 1px solid {theme_data.get('selection', '#ccc')};
        }}
        """
        self.preview_widget.setStyleSheet(style)

    def _save_current(self):
        """Salva as alterações no tema atualmente selecionado."""
        theme_name = self.theme_selector.currentText()
        reply = QMessageBox.question(self, "Salvar Tema", 
                                     f"Isso irá sobrescrever o tema '{theme_name}'.\nDeseja continuar?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            if self.logic.save_theme(theme_name):
                QMessageBox.information(self, "Sucesso", f"Tema '{theme_name}' salvo com sucesso.")
            else:
                QMessageBox.critical(self, "Erro", "Não foi possível salvar o tema.")

    def _save_as(self):
        """Salva o tema atual com um novo nome."""
        new_name, ok = QInputDialog.getText(self, "Salvar Como...", "Nome do novo tema (ex: meu-tema-custom):")
        if ok and new_name:
            # Sanitização básica do nome
            new_name = new_name.lower().replace(" ", "-")
            if self.logic.save_theme(new_name):
                QMessageBox.information(self, "Sucesso", f"Tema '{new_name}' criado com sucesso.")
                # Atualiza a lista de temas
                self.theme_selector.blockSignals(True)
                self.theme_selector.addItems([new_name])
                self.theme_selector.setCurrentText(new_name)
                self.theme_selector.blockSignals(False)
            else:
                QMessageBox.critical(self, "Erro", "Não foi possível salvar o novo tema.")