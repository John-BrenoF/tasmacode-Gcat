from PySide6.QtWidgets import QApplication

class ContextMenuLogic:
    """
    Gerencia a lógica de negócios para o menu de contexto do editor.
    Respeita o SRP ao separar a execução das ações da interface visual.
    """
    def __init__(self, buffer, save_callback=None, close_callback=None, clipboard_manager=None):
        self.buffer = buffer
        self.save_callback = save_callback
        self.close_callback = close_callback
        self.clipboard_manager = clipboard_manager

    def select_all(self):
        """Seleciona todo o texto do buffer."""
        if self.buffer:
            self.buffer.select_all()

    def copy(self):
        """Copia o texto selecionado para a área de transferência."""
        if self.buffer:
            selected_texts = [self.buffer.get_selected_text(i) for i in range(len(self.buffer.cursors))]
            non_empty = [text for text in selected_texts if text]
            if non_empty:
                QApplication.clipboard().setText("\n".join(non_empty))
            # O ClipboardManager detectará a mudança automaticamente
            # através do sinal dataChanged.

    def cut(self):
        """Recorta o texto selecionado."""
        if self.buffer:
            self.copy()
            self.buffer.delete_selection()

    def paste(self):
        """Cola o texto da área de transferência."""
        if self.buffer:
            text = QApplication.clipboard().text()
            if text:
                self.buffer.insert_text(text)

    def clear_clipboard_history(self):
        """Limpa o histórico da área de transferência."""
        if self.clipboard_manager:
            self.clipboard_manager.clear_history()

    def paste_from_history(self, text: str):
        """Cola um item específico do histórico no editor."""
        if self.buffer and text:
            # Define o texto no clipboard principal para que ele se torne o mais recente
            QApplication.clipboard().setText(text)
            self.buffer.insert_text(text)

    def save(self):
        """Aciona o callback de salvamento."""
        if self.save_callback:
            self.save_callback()

    def close_tab(self):
        """Aciona o callback de fechar aba."""
        if self.close_callback:
            self.close_callback()