from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication

class ClipboardManager(QObject):
    """
    Gerencia um histórico de textos da área de transferência.
    Esta classe é destinada a ser uma instância única na aplicação.
    """
    history_changed = Signal()
    MAX_HISTORY_SIZE = 15

    def __init__(self, parent=None):
        super().__init__(parent)
        self._history = []
        self._clipboard = QApplication.clipboard()
        self._clipboard.dataChanged.connect(self._on_clipboard_changed)
        # Popula com o conteúdo inicial
        initial_text = self._clipboard.text()
        if initial_text:
            self._history.append(initial_text)

    def _on_clipboard_changed(self):
        new_text = self._clipboard.text()
        if not new_text:
            return

        # Evita adicionar duplicatas no topo da pilha
        if self._history and self._history[0] == new_text:
            return

        # Remove a instância existente do texto para movê-la para o topo
        if new_text in self._history:
            self._history.remove(new_text)

        self._history.insert(0, new_text)

        # Limita o tamanho do histórico
        if len(self._history) > self.MAX_HISTORY_SIZE:
            self._history = self._history[:self.MAX_HISTORY_SIZE]
        
        self.history_changed.emit()

    def get_history(self) -> list[str]:
        """Retorna o histórico da área de transferência, com o mais recente primeiro."""
        return self._history