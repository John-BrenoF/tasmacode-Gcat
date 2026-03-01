from PySide6.QtWidgets import QListWidget, QListWidgetItem, QStyle, QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon, QColor

class SuggestionItemWidget(QWidget):
    """Widget customizado para um item da lista de autocomplete, com layout rico."""
    def __init__(self, suggestion: dict, parent=None):
        super().__init__(parent)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 5, 8, 5) # Aumenta o padding para deixar o item mais alto
        layout.setSpacing(10)

        # Ícone
        icon_label = QLabel()
        icon = self._get_icon_for_kind(suggestion.get('kind', 'variable'))
        icon_label.setPixmap(icon.pixmap(QSize(16, 16)))
        
        # Texto da Sugestão
        text_label = QLabel(suggestion['label'])
        text_label.setStyleSheet("color: #cccccc; background: transparent;")

        # Detalhe (tipo da sugestão, alinhado à direita)
        detail_label = QLabel(suggestion.get('detail', ''))
        detail_label.setStyleSheet("color: #888888; background: transparent;")
        
        layout.addWidget(icon_label)
        layout.addWidget(text_label)
        layout.addStretch()
        layout.addWidget(detail_label)

    def _get_icon_for_kind(self, kind: str) -> QIcon:
        """Retorna um ícone para o tipo de sugestão."""
        # Reutiliza a lógica de ícones que já estava no AutocompleteWidget
        return AutocompleteWidget.get_icon_for_kind(self, kind)

class AutocompleteWidget(QListWidget):
    """Widget popup para exibir sugestões de autocomplete."""
    suggestion_selected = Signal(dict) # Emite o dicionário completo da sugestão

    def __init__(self, parent_editor):
        super().__init__(parent_editor)
        self.editor = parent_editor
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setFocusPolicy(Qt.NoFocus)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.itemActivated.connect(self._on_item_activated)
        
        self.setStyleSheet("""
            QListWidget {
                background-color: #252526;
                color: #cccccc;
                border: 1px solid #454545;
                border-radius: 4px;
                outline: none;
            }
            QListWidget::item:selected {
                background-color: #04395e;
            }
            /* Scrollbar styling */
            QScrollBar:vertical {
                border: none;
                background: transparent; /* Fundo transparente */
                width: 8px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #44475a;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        self.hide()

    def show_suggestions(self, suggestions: list):
        """Preenche a lista com sugestões e a exibe."""
        self.clear()
        if not suggestions:
            self.hide()
            return
            
        for sugg in suggestions:
            item = QListWidgetItem(self)
            # Armazena o dicionário completo da sugestão
            item.setData(Qt.UserRole, sugg)
            
            # Cria e define o widget customizado para o item
            widget = SuggestionItemWidget(sugg)
            item.setSizeHint(widget.sizeHint())
            self.addItem(item) # Adiciona o item primeiro
            self.setItemWidget(item, widget) # Depois define o widget para ele

        self.setCurrentRow(0)
        
        # Ajusta tamanho dinamicamente
        item_height = self.sizeHintForRow(0) if self.count() > 0 else 32
        count = min(len(suggestions), 8) # Mostra no máximo 8 itens antes de scrollar
        self.resize(350, count * item_height)
        
        self.show()
        self.raise_() # Garante que fique no topo

    @staticmethod
    def get_icon_for_kind(widget, kind):
        """Retorna um ícone padrão do Qt baseado no tipo de sugestão."""
        style = widget.style()
        if kind == 'snippet':
            return style.standardIcon(QStyle.StandardPixmap.SP_ToolBarHorizontalExtensionButton)
        elif kind == 'keyword':
            return style.standardIcon(QStyle.StandardPixmap.SP_ArrowRight)
        elif kind == 'function':
            return style.standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView)
        elif kind == 'class':
            return style.standardIcon(QStyle.StandardPixmap.SP_DirIcon)
        elif kind == 'variable':
            return style.standardIcon(QStyle.StandardPixmap.SP_FileIcon)
        return style.standardIcon(QStyle.StandardPixmap.SP_FileIcon)

    def _on_item_activated(self, item: QListWidgetItem):
        suggestion_data = item.data(Qt.UserRole) # Pega o dicionário
        if suggestion_data:
            self.suggestion_selected.emit(suggestion_data)
        self.hide()

    def keyPressEvent(self, event):
        """Processa teclas para navegação e seleção."""
        if event.key() in (Qt.Key_Enter, Qt.Key_Return, Qt.Key_Tab):
            if self.currentItem():
                suggestion_data = self.currentItem().data(Qt.UserRole)
                if suggestion_data:
                    self.suggestion_selected.emit(suggestion_data)
            self.hide()
        elif event.key() in (Qt.Key_Up, Qt.Key_Down):
            super().keyPressEvent(event)
        elif event.key() == Qt.Key_Escape:
            self.hide()
        else:
            self.editor.keyPressEvent(event)
            self.hide()