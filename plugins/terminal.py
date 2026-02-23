import sys
import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit
from PySide6.QtCore import QProcess, Qt
from PySide6.QtGui import QFont, QColor

class Terminal(QWidget):
    """Emulador de terminal integrado usando QProcess."""

    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Área de Saída (Read-only)
        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        self.output_area.setStyleSheet("background-color: #1e1e1e; color: #cccccc; border: none;")
        
        # Configuração de Fonte Monoespaçada
        font = QFont("Consolas")
        font.setStyleHint(QFont.StyleHint.Monospace)
        font.setPointSize(10)
        self.output_area.setFont(font)

        # Área de Entrada
        self.input_line = QLineEdit()
        self.input_line.setStyleSheet("background-color: #252526; color: #cccccc; border-top: 1px solid #3e3e42; padding: 2px;")
        self.input_line.setFont(font)
        self.input_line.returnPressed.connect(self._send_command)
        self.input_line.setPlaceholderText("Digite um comando...")

        self.layout.addWidget(self.output_area)
        self.layout.addWidget(self.input_line)

        # Processo do Sistema
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self._handle_stdout)
        self.process.readyReadStandardError.connect(self._handle_stderr)
        self.process.finished.connect(self._handle_finished)

        self._start_shell()

    def _start_shell(self):
        """Inicia o shell apropriado para o SO."""
        if sys.platform == "win32":
            shell = "cmd.exe"
        else:
            shell = os.environ.get("SHELL", "/bin/bash")
        
        self.process.start(shell)

    def change_directory(self, path: str):
        """Muda o diretório de trabalho do terminal."""
        if os.path.exists(path):
            # No QProcess, setWorkingDirectory afeta o processo antes de iniciar.
            # Para um shell rodando, enviamos o comando cd.
            cmd = f"cd /d \"{path}\"" if sys.platform == "win32" else f"cd \"{path}\""
            self._write_to_process(cmd)
            # Limpa a tela visualmente para dar feedback de "novo contexto"
            self.output_area.append(f"--- Working Directory: {path} ---")

    def _send_command(self):
        cmd = self.input_line.text()
        self._write_to_process(cmd)
        self.input_line.clear()

    def _write_to_process(self, cmd):
        if self.process.state() != QProcess.ProcessState.Running:
            self._start_shell()
            
        # Adiciona quebra de linha para executar
        self.process.write((cmd + "\n").encode())

    def _handle_stdout(self):
        data = self.process.readAllStandardOutput().data().decode(errors='replace')
        self.output_area.insertPlainText(data)
        self.output_area.ensureCursorVisible()

    def _handle_stderr(self):
        data = self.process.readAllStandardError().data().decode(errors='replace')
        # Poderíamos usar cor vermelha aqui futuramente
        self.output_area.insertPlainText(data)
        self.output_area.ensureCursorVisible()

    def _handle_finished(self):
        self.output_area.append("\n[Processo finalizado]")