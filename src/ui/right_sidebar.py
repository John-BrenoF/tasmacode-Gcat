from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
                               QFileDialog, QMessageBox, QFrame, QStackedWidget, QScrollArea, QMenu, 
                               QInputDialog, QApplication, QStyle, QComboBox, QDialog, QListWidget, QTextEdit)
from PySide6.QtCore import Qt, QRect, QPointF, Signal, QPoint
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QPainterPath, QFontMetrics, QCursor
from src.core.git_logic import GitLogic

class CommitTooltip(QLabel):
    """Tooltip customizado flutuante para commits."""
    def __init__(self):
        super().__init__(None, Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet("""
            background-color: #1e1e1e;
            color: #cccccc;
            border: 1px solid #454545;
            border-radius: 4px;
            padding: 8px;
        """)
        self.setWordWrap(True)
        self.setMaximumWidth(300)

    def show_data(self, commit, pos):
        content = (f"<b style='color: #ffffff'>Hash:</b> {commit['hash'][:8]}<br>"
                   f"<b style='color: #ffffff'>Autor:</b> {commit['author']}<br>"
                   f"<b style='color: #ffffff'>Data:</b> {commit['date']}<br>"
                   f"<hr style='background-color: #454545; height: 1px; border: none;'>"
                   f"{commit['message'].replace(chr(10), '<br>')}")
        self.setText(content)
        self.adjustSize()
        self.move(pos)
        self.show()

class DiffViewer(QDialog):
    """Janela para visualizar o diff de um arquivo."""
    def __init__(self, diff_text, title, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Diff: {title}")
        self.resize(800, 600)
        self.setStyleSheet("background-color: #1e1e1e; color: #cccccc;")
        
        layout = QVBoxLayout(self)
        text_edit = QTextEdit()
        text_edit.setPlainText(diff_text)
        text_edit.setReadOnly(True)
        text_edit.setFont(QFont("Monospace", 10))
        text_edit.setStyleSheet("border: none; background-color: #1e1e1e; color: #cccccc;")
        layout.addWidget(text_edit)

class CommitDetailsDialog(QDialog):
    """Janela com detalhes do commit e lista de arquivos modificados."""
    def __init__(self, repo_path, commit_data, git_logic, parent=None):
        super().__init__(parent)
        self.repo_path = repo_path
        self.commit_data = commit_data
        self.git_logic = git_logic
        self.setWindowTitle(f"Commit {commit_data['hash'][:8]}")
        self.resize(500, 400)
        self.setStyleSheet("background-color: #252526; color: #cccccc;")
        
        layout = QVBoxLayout(self)
        
        # Metadata
        meta = QLabel(f"<b>Autor:</b> {commit_data['author']}<br><b>Data:</b> {commit_data['date']}<br><br>{commit_data['message']}")
        meta.setWordWrap(True)
        layout.addWidget(meta)
        
        layout.addWidget(QLabel("<b>Arquivos Modificados (Clique para ver Diff):</b>"))
        
        self.files_list = QListWidget()
        self.files_list.setStyleSheet("background-color: #3c3c3c; border: none;")
        files = self.git_logic.get_commit_files(self.repo_path, self.commit_data['hash'])
        self.files_list.addItems(files)
        self.files_list.itemClicked.connect(self._show_diff)
        layout.addWidget(self.files_list)
        
    def _show_diff(self, item):
        file_path = item.text()
        diff = self.git_logic.get_diff(self.repo_path, self.commit_data['hash'], file_path)
        DiffViewer(diff, file_path, self).exec()

class CredentialsDialog(QDialog):
    """Diálogo para solicitar credenciais do Git."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Autenticação Git")
        self.resize(350, 180)
        self.setStyleSheet("background-color: #252526; color: #cccccc;")
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        layout.addWidget(QLabel("Falha na autenticação. Por favor, insira suas credenciais:"))
        
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Username")
        self.user_input.setStyleSheet("background-color: #3c3c3c; border: 1px solid #454545; padding: 6px; color: white;")
        
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Password / Personal Access Token")
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_input.setStyleSheet("background-color: #3c3c3c; border: 1px solid #454545; padding: 6px; color: white;")
        
        btn_box = QHBoxLayout()
        btn_ok = QPushButton("OK")
        btn_ok.setStyleSheet("background-color: #007acc; color: white; padding: 6px 12px; border: none; border-radius: 4px;")
        btn_ok.clicked.connect(self.accept)
        
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setStyleSheet("background-color: #3c3c3c; color: white; padding: 6px 12px; border: 1px solid #454545; border-radius: 4px;")
        btn_cancel.clicked.connect(self.reject)
        
        btn_box.addWidget(btn_cancel)
        btn_box.addWidget(btn_ok)
        
        layout.addWidget(self.user_input)
        layout.addWidget(self.pass_input)
        layout.addLayout(btn_box)

    def get_credentials(self):
        return self.user_input.text().strip(), self.pass_input.text().strip()

class GitGraphWidget(QWidget):
    """Widget customizado para desenhar o grafo de commits."""
    
    commit_clicked = Signal(dict)
    copy_hash_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.commits = []
        self.row_height = 36 # Altura aumentada para melhor espaçamento
        self.node_radius = 6
        self.lane_width = 24 # Largura aumentada para evitar aglomeração
        self.setMinimumHeight(400)
        self.hit_areas = [] # Armazena áreas clicáveis: (QRect, commit_data)
        self.setMouseTracking(True) # Habilita rastreamento do mouse para hover
        self.hovered_commit = None
        self.hover_pos = QPoint(0, 0)
        # Cores para os branches
        self.colors = [
            QColor("#40c463"), QColor("#f38ba8"), QColor("#89b4fa"), 
            QColor("#fab387"), QColor("#cba6f7"), QColor("#f9e2af"), 
            QColor("#94e2d5")
        ]
        self.tooltip_widget = CommitTooltip()

    def set_data(self, commits):
        self.commits = commits
        self.setMinimumHeight(len(commits) * self.row_height + 20)
        self.update()

    def mousePressEvent(self, event):
        pos = event.position().toPoint()
        for rect, commit in self.hit_areas:
            if rect.adjusted(-5, -5, 5, 5).contains(pos):
                self.commit_clicked.emit(commit)
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Detecta hover sobre os commits."""
        pos = event.position().toPoint()
        self.hover_pos = pos
        found = None
        for rect, commit in self.hit_areas:
            if rect.adjusted(-5, -5, 5, 5).contains(pos):
                found = commit
                break
        
        if found:
            global_pos = self.mapToGlobal(pos) + QPoint(15, 15)
            self.tooltip_widget.show_data(found, global_pos)
            self.hovered_commit = found
        else:
            self.tooltip_widget.hide()
            self.hovered_commit = None
        
        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        self.hovered_commit = None
        self.tooltip_widget.hide()
        super().leaveEvent(event)

    def contextMenuEvent(self, event):
        """Menu de contexto ao clicar com botão direito."""
        if self.hovered_commit:
            menu = QMenu(self)
            menu.setStyleSheet("QMenu { background-color: #252526; color: #cccccc; } QMenu::item:selected { background-color: #007acc; }")
            menu.addAction("Copiar Hash", lambda: self.copy_hash_requested.emit(self.hovered_commit['hash']))
            menu.addAction("Copiar Mensagem", lambda: QApplication.clipboard().setText(self.hovered_commit['message']))
            menu.exec(event.globalPos())

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        self.hit_areas = [] # Reinicia áreas de clique

        # Fontes
        font_refs = self.font()
        font_refs.setPointSize(9)
        font_refs.setBold(True)
        
        font_msg = self.font()
        font_msg.setPointSize(9)

        # Estado para o desenho do grafo
        # lanes: lista de hashes de commit esperados na próxima linha
        # O índice na lista representa a 'trilha' visual (coluna)
        lanes = [] 
        
        # Posições Y
        y = self.row_height // 2

        for commit in self.commits:
            commit_hash = commit['hash']
            
            # Determina a lane deste commit
            if commit_hash in lanes:
                node_lane_idx = lanes.index(commit_hash)
            else:
                # Nova ponta de branch, encontra uma lane livre (None) ou adiciona nova
                try:
                    node_lane_idx = lanes.index(None)
                except ValueError:
                    node_lane_idx = len(lanes)
                    lanes.append(None)
            
            # Prepara next_lanes (estado da próxima linha)
            next_lanes = list(lanes)
            
            # O commit atual consome sua posição na lane (será substituído pelos pais)
            if node_lane_idx < len(next_lanes):
                next_lanes[node_lane_idx] = None

            # Atribui pais às lanes na próxima linha
            parent_positions = []
            for i, parent_hash in enumerate(commit['parents']):
                if parent_hash in next_lanes:
                    # Pai já esperado (merge), reutiliza a lane existente
                    idx = next_lanes.index(parent_hash)
                    parent_positions.append(idx)
                else:
                    # Atribui a uma lane
                    if i == 0:
                        # Primeiro pai tenta herdar a lane do nó atual
                        if node_lane_idx < len(next_lanes) and next_lanes[node_lane_idx] is None:
                            next_lanes[node_lane_idx] = parent_hash
                            parent_positions.append(node_lane_idx)
                        else:
                            # Lane ocupada, busca livre
                            try:
                                idx = next_lanes.index(None)
                                next_lanes[idx] = parent_hash
                                parent_positions.append(idx)
                            except ValueError:
                                idx = len(next_lanes)
                                next_lanes.append(parent_hash)
                                parent_positions.append(idx)
                    else:
                        # Outros pais (bifurcação) buscam slots livres
                        try:
                            idx = next_lanes.index(None)
                            next_lanes[idx] = parent_hash
                            parent_positions.append(idx)
                        except ValueError:
                            idx = len(next_lanes)
                            next_lanes.append(parent_hash)
                            parent_positions.append(idx)

            # --- DESENHO ---
            
            # 1. Desenha linhas verticais para branches que apenas passam por aqui (Pass-through)
            for i in range(len(lanes)):
                if lanes[i] is not None and lanes[i] != commit_hash:
                    # Verifica se continua na próxima linha (deve continuar se não foi modificado)
                    if i < len(next_lanes) and next_lanes[i] == lanes[i]:
                        line_x = 20 + (i * self.lane_width)
                        color = self.colors[i % len(self.colors)]
                        painter.setPen(QPen(color, 2))
                        painter.drawLine(line_x, y, line_x, y + self.row_height)

            # 2. Desenha conexões do Nó atual para os Pais
            node_x = 20 + (node_lane_idx * self.lane_width)
            node_color = self.colors[node_lane_idx % len(self.colors)]
            
            for p_idx in parent_positions:
                target_x = 20 + (p_idx * self.lane_width)
                target_y = y + self.row_height
                
                painter.setPen(QPen(node_color, 2))
                painter.setBrush(Qt.NoBrush)
                
                path = QPainterPath()
                path.moveTo(node_x, y)
                
                if p_idx == node_lane_idx:
                    path.lineTo(target_x, target_y)
                else:
                    ctrl1 = QPointF(node_x, y + self.row_height * 0.5)
                    ctrl2 = QPointF(target_x, target_y - self.row_height * 0.5)
                    path.cubicTo(ctrl1, ctrl2, QPointF(target_x, target_y))
                
                painter.drawPath(path)

            # 3. Desenha o Nó do commit
            painter.setPen(QPen(node_color, 2))
            painter.setBrush(QBrush(QColor("#252526")))
            node_rect = QRect(node_x - self.node_radius, y - self.node_radius, self.node_radius*2, self.node_radius*2)
            painter.drawEllipse(node_rect)
            
            # Ponto central preenchido
            painter.setBrush(QBrush(node_color))
            painter.drawEllipse(node_x - 2, y - 2, 4, 4)
            
            self.hit_areas.append((node_rect, commit))

            # 4. Desenha Texto (Mensagem e Refs)
            # Posiciona o texto à direita de todas as lanes ativas (usando len(next_lanes) ou len(lanes))
            max_lane_idx = max(len(lanes), len(next_lanes))
            text_x = 20 + (max_lane_idx * self.lane_width) + 10
            
            # Refs (Branches/Tags)
            if commit['refs']:
                painter.setFont(font_refs)
                painter.setPen(QColor("#ffcc00"))
                painter.drawText(text_x, y + 4, commit['refs'])
                fm = QFontMetrics(font_refs)
                text_x += fm.horizontalAdvance(commit['refs']) + 8

            # Mensagem
            painter.setFont(font_msg)
            painter.setPen(QColor("#cccccc"))
            # Elide text se for muito longo
            msg = commit['message']
            fm = QFontMetrics(font_msg)
            elided_msg = fm.elidedText(msg, Qt.TextElideMode.ElideRight, self.width() - text_x - 10)
            painter.drawText(text_x, y + 4, elided_msg)

            # Atualiza estado para a próxima iteração
            lanes = next_lanes
            y += self.row_height

class RightSidebar(QWidget):
    """Barra lateral direita focada em ferramentas Git."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.git_logic = GitLogic()
        self.auth_logic = None
        self.setObjectName("RightSidebar")
        self.setMinimumWidth(200)
        self.setStyleSheet("background-color: #252526; border-left: 1px solid #3e3e42;")
        
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.stack = QStackedWidget()
        
        # --- Página 1: Clone (Default) ---
        self.page_clone = QWidget()
        clone_layout = QVBoxLayout(self.page_clone)
        clone_layout.setContentsMargins(10, 10, 10, 10)
        clone_layout.setSpacing(10)

        # Título
        lbl_title = QLabel("Git Clone")
        lbl_title.setStyleSheet("font-weight: bold; color: #cccccc; font-size: 14px;")
        clone_layout.addWidget(lbl_title)

        # Separador
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("background-color: #3e3e42;")
        clone_layout.addWidget(line)

        # Input URL
        lbl_url = QLabel("URL do Repositório:")
        lbl_url.setStyleSheet("color: #cccccc;")
        self.input_url = QLineEdit()
        self.input_url.setPlaceholderText("https://github.com/user/repo.git")
        self.input_url.setStyleSheet("background-color: #3c3c3c; color: white; border: 1px solid #454545; padding: 5px;")
        
        clone_layout.addWidget(lbl_url)
        clone_layout.addWidget(self.input_url)

        # Botão Clonar
        self.btn_clone = QPushButton("Clonar Repositório")
        self.btn_clone.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_clone.setStyleSheet("""
            QPushButton { background-color: #007acc; color: white; padding: 8px; border: none; border-radius: 4px; }
            QPushButton:hover { background-color: #0098ff; }
        """)
        self.btn_clone.clicked.connect(self._handle_clone_click)
        
        clone_layout.addWidget(self.btn_clone)
        clone_layout.addStretch()

        # --- Página 2: Controle Git (Visual) ---
        self.page_git = QWidget()
        git_layout = QVBoxLayout(self.page_git)
        git_layout.setContentsMargins(0, 0, 0, 0)
        
        # Header Git
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: #2d2d30; padding: 5px;")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        self.branch_selector = QComboBox()
        self.branch_selector.setStyleSheet("background-color: #3c3c3c; color: white; border: none; padding: 2px;")
        self.branch_selector.currentIndexChanged.connect(self._switch_branch)

        btn_new_branch = QPushButton()
        btn_new_branch.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogNewFolder))
        btn_new_branch.setToolTip("Criar Nova Branch")
        btn_new_branch.setFixedSize(24, 24)
        btn_new_branch.setStyleSheet("background-color: transparent; border: none; border-radius: 4px;")
        btn_new_branch.clicked.connect(self._create_branch)
        
        btn_commit = QPushButton()
        btn_commit.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogApplyButton))
        btn_commit.setToolTip("Commit")
        btn_commit.setFixedSize(26, 26)
        btn_commit.setStyleSheet("background-color: transparent; border: none; border-radius: 4px; margin-left: 5px;")
        btn_commit.clicked.connect(self._perform_commit)

        btn_pull = QPushButton()
        btn_pull.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowDown))
        btn_pull.setToolTip("Pull")
        btn_pull.setFixedSize(26, 26)
        btn_pull.setStyleSheet("background-color: transparent; border: none; border-radius: 4px;")
        btn_pull.clicked.connect(self._perform_pull)

        btn_push = QPushButton()
        btn_push.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowUp))
        btn_push.setToolTip("Push")
        btn_push.setFixedSize(26, 26)
        btn_push.setStyleSheet("background-color: transparent; border: none; border-radius: 4px;")
        btn_push.clicked.connect(self._perform_push)

        btn_refresh = QPushButton()
        btn_refresh.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload))
        btn_refresh.setToolTip("Atualizar")
        btn_refresh.setFixedSize(26, 26)
        btn_refresh.setStyleSheet("background-color: transparent; border: none; border-radius: 4px; margin-left: 5px;")
        btn_refresh.clicked.connect(self._refresh_graph)
        
        header_layout.addWidget(self.branch_selector, 1)
        header_layout.addWidget(btn_new_branch)
        header_layout.addWidget(btn_commit)
        header_layout.addWidget(btn_pull)
        header_layout.addWidget(btn_push)
        header_layout.addWidget(btn_refresh)
        
        git_layout.addWidget(header_frame)
        
        # Área do Gráfico (Scrollável)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background-color: #1e1e1e; border: none;")
        
        self.graph_widget = GitGraphWidget()
        self.graph_widget.copy_hash_requested.connect(self._copy_hash)
        self.graph_widget.commit_clicked.connect(self._open_commit_details)
        scroll.setWidget(self.graph_widget)
        
        git_layout.addWidget(scroll)
        
        # Adiciona páginas ao stack
        self.stack.addWidget(self.page_clone)
        self.stack.addWidget(self.page_git)
        
        layout.addWidget(self.stack)
        
        self.current_repo = None

    def set_auth_logic(self, auth_logic):
        self.auth_logic = auth_logic

    def load_repo(self, path):
        """Chamado quando um projeto é aberto."""
        if self.git_logic.is_repo(path):
            self.current_repo = path
            self.stack.setCurrentWidget(self.page_git)
            self._refresh_graph()
        else:
            self.current_repo = None
            self.stack.setCurrentWidget(self.page_clone)

    def _refresh_graph(self):
        if not self.current_repo: return
        
        branch = self.git_logic.get_current_branch(self.current_repo)
        branches = self.git_logic.get_branches(self.current_repo)
        
        self.branch_selector.blockSignals(True)
        self.branch_selector.clear()
        self.branch_selector.addItems(branches)
        self.branch_selector.setCurrentText(branch)
        self.branch_selector.blockSignals(False)

        commits = self.git_logic.get_graph_data(self.current_repo)
        self.graph_widget.set_data(commits)

    def _perform_commit(self):
        if not self.current_repo: return
        msg, ok = QInputDialog.getMultiLineText(self, "Commit", "Mensagem do Commit:")
        if ok and msg.strip():
            success, info = self.git_logic.commit(self.current_repo, msg.strip())
            if success:
                self._refresh_graph()
                QMessageBox.information(self, "Git", info)
            else:
                QMessageBox.warning(self, "Erro no Commit", info)

    def _perform_push(self):
        if not self.current_repo: return
        success, info = self.git_logic.push(self.current_repo)
        
        # Tenta usar credenciais salvas se falhar
        if not success and self.auth_logic and self.auth_logic.is_logged_in():
            user_data = self.auth_logic.get_user_data()
            token = self.auth_logic.get_token()
            success, info = self.git_logic.push(self.current_repo, user_data['login'], token)
        
        # Verifica falha de autenticação
        if not success and ("Authentication failed" in info or "could not read" in info):
            dlg = CredentialsDialog(self)
            if dlg.exec():
                user, token = dlg.get_credentials()
                if user and token:
                    success, info = self.git_logic.push(self.current_repo, user, token)

        if success:
            QMessageBox.information(self, "Git Push", info)
        else:
            QMessageBox.warning(self, "Git Push", info)

    def _perform_pull(self):
        if not self.current_repo: return
        success, info = self.git_logic.pull(self.current_repo)
        
        # Tenta usar credenciais salvas se falhar
        if not success and self.auth_logic and self.auth_logic.is_logged_in():
            user_data = self.auth_logic.get_user_data()
            token = self.auth_logic.get_token()
            success, info = self.git_logic.pull(self.current_repo, user_data['login'], token)
        
        # Verifica falha de autenticação
        if not success and ("Authentication failed" in info or "could not read" in info):
            dlg = CredentialsDialog(self)
            if dlg.exec():
                user, token = dlg.get_credentials()
                if user and token:
                    success, info = self.git_logic.pull(self.current_repo, user, token)

        if success:
            self._refresh_graph()
            QMessageBox.information(self, "Git Pull", info)
        else:
            QMessageBox.warning(self, "Git Pull", info)

    def _switch_branch(self):
        branch = self.branch_selector.currentText()
        if branch:
            success, info = self.git_logic.checkout(self.current_repo, branch)
            if success:
                self._refresh_graph()
            else:
                QMessageBox.warning(self, "Checkout", info)
                # Reverte seleção visual
                self._refresh_graph()

    def _create_branch(self):
        if not self.current_repo: return
        name, ok = QInputDialog.getText(self, "Nova Branch", "Nome da Branch:")
        if ok and name:
            # Sanitiza o nome: Git não aceita espaços em nomes de branch
            sanitized_name = name.strip().replace(" ", "-")
            success, info = self.git_logic.create_branch(self.current_repo, sanitized_name)
            if success: self._refresh_graph()
            QMessageBox.information(self, "Git", info)

    def _handle_clone_click(self):
        url = self.input_url.text().strip()
        if not url:
            QMessageBox.warning(self, "Aviso", "Por favor, insira uma URL válida.")
            return

        # Pergunta onde salvar
        dest_folder = QFileDialog.getExistingDirectory(self, "Escolha onde salvar o repositório")
        if not dest_folder:
            return

        # Feedback visual
        self.btn_clone.setText("Clonando...")
        self.btn_clone.setEnabled(False)
        self.repaint() # Força atualização da UI

        # Executa lógica
        success, msg = self.git_logic.clone_repository(url, dest_folder)

        # Restaura UI e mostra resultado
        self.btn_clone.setText("Clonar Repositório")
        self.btn_clone.setEnabled(True)
        
        if success:
            QMessageBox.information(self, "Sucesso", msg)
            self.input_url.clear()
        else:
            QMessageBox.critical(self, "Erro", msg)

    def _copy_hash(self, commit_hash):
        QApplication.clipboard().setText(commit_hash)
        # Opcional: Mostrar feedback na statusbar se tivesse acesso

    def _open_commit_details(self, commit_data):
        CommitDetailsDialog(self.current_repo, commit_data, self.git_logic, self).exec()