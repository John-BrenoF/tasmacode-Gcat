from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor
from PySide6.QtCore import Qt

class Minimap(QWidget):
    """Renderiza uma visão 'micro' do código para navegação rápida."""
    
    def __init__(self, editor):
        super().__init__()
        self.editor = editor # Referência ao editor principal para sincronia
        self.setFixedWidth(100)
        self.buffer = None
        self.theme = None

    def set_dependencies(self, buffer, theme):
        self.buffer = buffer
        self.theme = theme

    def paintEvent(self, event):
        if not self.buffer or not self.theme: return

        painter = QPainter(self)
        bg = QColor(self.theme.get_color("minimap_bg"))
        fg = QColor(self.theme.get_color("foreground"))
        painter.fillRect(event.rect(), bg)

        # Escala: 1 linha real = 2 pixels no minimap
        scale_y = 2
        
        # Desenha representação abstrata das linhas
        # Otimização: Desenhar apenas linhas que cabem no widget
        max_lines = self.height() // scale_y
        lines = self.buffer.get_lines(0, max_lines) # Simplificado: desenha do topo
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(fg)
        
        for i, line in enumerate(lines):
            if not line.strip(): continue
            y = i * scale_y
            # Desenha um retângulo representando o comprimento da linha
            width = min(len(line), 50) * 2 # 2px por char
            painter.drawRect(2, y, width, scale_y - 1)

        # Desenha o viewport overlay (área visível)
        if self.editor:
            scroll_pct = self.editor.verticalScrollBar().value() / max(1, self.editor.verticalScrollBar().maximum())
            overlay_y = scroll_pct * (len(self.buffer.lines) * scale_y)
            overlay_h = (self.editor.viewport().height() / self.editor.line_height) * scale_y
            
            painter.setBrush(QColor(self.theme.get_color("minimap_overlay")))
            painter.drawRect(0, overlay_y, self.width(), overlay_h)