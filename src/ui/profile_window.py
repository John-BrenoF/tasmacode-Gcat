from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, 
                               QHBoxLayout, QMessageBox, QFrame, QApplication)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
import requests

class ProfileWindow(QDialog):
    """Janela para login e visualização de perfil do GitHub."""
    
    def __init__(self, auth_logic, parent=None):
        super().__init__(parent)
        self.auth_logic = auth_logic
        self.setWindowTitle("Perfil GitHub")
        self.resize(400, 350)
        self.setStyleSheet("background-color: #252526; color: #cccccc;")
        
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(15)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout.setContentsMargins(20, 20, 20, 20)

        if self.auth_logic.is_logged_in():
            self._setup_logged_in_ui()
        else:
            self._setup_login_ui()

    def _setup_login_ui(self):
        lbl_title = QLabel("Login com GitHub")
        lbl_title.setStyleSheet("font-size: 20px; font-weight: bold; color: white; margin-bottom: 10px;")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(lbl_title)

        lbl_info = QLabel("Insira seu Personal Access Token (PAT) para habilitar operações de Git (Push/Pull) sem senha.")
        lbl_info.setWordWrap(True)
        lbl_info.setStyleSheet("color: #8b949e; margin-bottom: 10px;")
        lbl_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(lbl_info)

        token_layout = QHBoxLayout()
        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText("ghp_...")
        self.token_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.token_input.setStyleSheet("background-color: #3c3c3c; border: 1px solid #454545; padding: 10px; color: white; border-radius: 4px;")
        
        btn_paste = QPushButton("Colar")
        btn_paste.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_paste.setStyleSheet("background-color: #3c3c3c; color: white; padding: 10px; border: 1px solid #454545; border-radius: 4px;")
        btn_paste.clicked.connect(lambda: self.token_input.setText(QApplication.clipboard().text()))
        
        token_layout.addWidget(self.token_input)
        token_layout.addWidget(btn_paste)
        self.layout.addLayout(token_layout)

        btn_login = QPushButton("Entrar")
        btn_login.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_login.setStyleSheet("background-color: #2ea043; color: white; padding: 10px; border: none; border-radius: 4px; font-weight: bold; font-size: 14px;")
        btn_login.clicked.connect(self._handle_login)
        self.layout.addWidget(btn_login)
        
        self.layout.addStretch()

    def _setup_logged_in_ui(self):
        user_data = self.auth_logic.get_user_data()
        
        # Avatar
        avatar_url = user_data.get("avatar_url")
        lbl_avatar = QLabel()
        lbl_avatar.setFixedSize(120, 120)
        lbl_avatar.setStyleSheet("border-radius: 60px; background-color: #3c3c3c; border: 2px solid #454545;")
        lbl_avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        if avatar_url:
            try:
                # Download simples da imagem para exibição
                data = requests.get(avatar_url, timeout=5).content
                pixmap = QPixmap()
                pixmap.loadFromData(data)
                lbl_avatar.setPixmap(pixmap.scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            except:
                lbl_avatar.setText("Sem Imagem")
        
        # Container centralizado para avatar
        h_avatar = QHBoxLayout()
        h_avatar.addStretch()
        h_avatar.addWidget(lbl_avatar)
        h_avatar.addStretch()
        self.layout.addLayout(h_avatar)

        # Info
        name = user_data.get("name") or user_data.get("login")
        lbl_name = QLabel(name)
        lbl_name.setStyleSheet("font-size: 22px; font-weight: bold; color: white; margin-top: 10px;")
        lbl_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(lbl_name)

        lbl_login = QLabel(f"@{user_data.get('login')}")
        lbl_login.setStyleSheet("color: #8b949e; font-size: 14px;")
        lbl_login.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(lbl_login)

        # Logout
        btn_logout = QPushButton("Sair")
        btn_logout.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_logout.setStyleSheet("background-color: #d73a49; color: white; padding: 8px 20px; border: none; border-radius: 4px; margin-top: 30px;")
        btn_logout.clicked.connect(self._handle_logout)
        
        h_btn = QHBoxLayout()
        h_btn.addStretch()
        h_btn.addWidget(btn_logout)
        h_btn.addStretch()
        self.layout.addLayout(h_btn)
        
        self.layout.addStretch()

    def _handle_login(self):
        token = self.token_input.text().strip()
        if not token:
            QMessageBox.warning(self, "Erro", "Por favor, insira um token.")
            return
            
        success, msg = self.auth_logic.login(token)
        if success:
            QMessageBox.information(self, "Sucesso", msg)
            self.close()
        else:
            QMessageBox.critical(self, "Erro", msg)

    def _handle_logout(self):
        self.auth_logic.logout()
        self.close()