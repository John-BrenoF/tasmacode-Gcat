import requests
import json
import os
import logging
from PySide6.QtCore import QObject, Signal

logger = logging.getLogger("GithubAuth")

class GithubAuth(QObject):
    """Gerencia a autenticação e sessão do usuário no GitHub."""

    auth_changed = Signal()

    def __init__(self, config_dir: str):
        super().__init__()
        self.config_file = os.path.join(config_dir, "auth_session.json")
        self._user_data = None
        self._token = None
        self._load_session()

    def _load_session(self):
        """Carrega a sessão salva do disco."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    self._token = data.get("token")
                    self._user_data = data.get("user_data")
            except Exception as e:
                logger.error(f"Falha ao carregar sessão de autenticação: {e}")

    def login(self, token: str) -> tuple[bool, str]:
        """Valida o token na API do GitHub e salva a sessão."""
        headers = {"Authorization": f"token {token}"}
        try:
            response = requests.get("https://api.github.com/user", headers=headers, timeout=10)
            if response.status_code == 200:
                self._user_data = response.json()
                self._token = token
                self._save_session()
                self.auth_changed.emit()
                return True, "Login realizado com sucesso!"
            elif response.status_code == 401:
                return False, "Token inválido."
            else:
                return False, f"Erro na API do GitHub: {response.status_code}"
        except Exception as e:
            return False, f"Erro de conexão: {str(e)}"

    def logout(self):
        """Limpa a sessão atual e remove o arquivo."""
        self._token = None
        self._user_data = None
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
        self.auth_changed.emit()

    def _save_session(self):
        data = {
            "token": self._token,
            "user_data": self._user_data
        }
        try:
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            logger.error(f"Falha ao salvar sessão de autenticação: {e}")

    def get_token(self) -> str | None:
        return self._token

    def get_user_data(self) -> dict | None:
        return self._user_data

    def is_logged_in(self) -> bool:
        return self._token is not None

    def get_avatar_bytes(self) -> bytes | None:
        if not self._user_data: return None
        url = self._user_data.get("avatar_url")
        if not url: return None
        try:
            return requests.get(url, timeout=5).content
        except:
            return None