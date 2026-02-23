from PySide6.QtCore import QObject, QEvent, Qt, Signal
from PySide6.QtGui import QKeyEvent
import logging

from src.core.editor_logic.buffer import DocumentBuffer

logger = logging.getLogger("EventHandler")

class EventHandler(QObject):
    """Mediador de eventos de entrada (Teclado/Mouse).
    
    Intercepta eventos da UI, traduz em comandos para o DocumentBuffer,
    e notifica a UI para se redesenhar.
    """
    
    buffer_modified = Signal()

    def __init__(self, extension_bridge, buffer: DocumentBuffer):
        super().__init__()
        self.extension_bridge = extension_bridge
        self.buffer = buffer

    def install_on(self, widget):
        """Instala este filtro de eventos no widget alvo."""
        widget.installEventFilter(self)

    def eventFilter(self, obj, event: QEvent) -> bool:
        """Filtra eventos. Retorna True se o evento foi consumido."""
        # A lógica de KeyPress foi movida para InputMapper e CodeEditor.keyPressEvent
        # Mantemos o eventFilter apenas se precisarmos interceptar outros eventos
        # ou atalhos globais que não dependem do foco no editor.
        
        if event.type() == QEvent.Type.KeyPress:
            # Retorna False para permitir que o evento chegue ao keyPressEvent do widget
            return False

        # Retorna False para permitir que o widget processe eventos não tratados (ex: scroll do mouse)
        return super().eventFilter(obj, event)