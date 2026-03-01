import subprocess
import os
import logging

logger = logging.getLogger("GitLogic")

class GitLogic:
    """Gerencia operações do Git, isolando a lógica de sistema da UI."""

    def clone_repository(self, repo_url: str, destination_folder: str) -> tuple[bool, str]:
        """
        Executa o comando git clone.
        Retorna: (sucesso: bool, mensagem: str)
        """
        if not repo_url or not destination_folder:
            return False, "URL e pasta de destino são obrigatórios."

        try:
            # Executa o git clone no diretório escolhido
            # check=True levanta exceção se o comando falhar
            env = os.environ.copy()
            env["GIT_TERMINAL_PROMPT"] = "0"
            subprocess.run(["git", "clone", repo_url], cwd=destination_folder, check=True, capture_output=True, env=env)
            return True, f"Repositório clonado com sucesso em: {destination_folder}"
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode().strip() if e.stderr else "Erro desconhecido"
            return False, f"Erro ao clonar: {error_msg}"
        except Exception as e:
            return False, f"Erro de sistema: {str(e)}"

    def is_repo(self, path: str) -> bool:
        """Verifica se o caminho é um repositório git."""
        try:
            # Usa git rev-parse para verificar se estamos dentro de uma árvore de trabalho git
            # Isso funciona mesmo se abrirmos uma subpasta do repositório
            subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"], 
                cwd=path, 
                check=True, 
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def get_current_branch(self, repo_path: str) -> str:
        try:
            res = subprocess.run(["git", "branch", "--show-current"], cwd=repo_path, capture_output=True, text=True)
            return res.stdout.strip()
        except:
            return "HEAD"

    def get_graph_data(self, repo_path: str) -> list:
        """Retorna lista de commits formatada para o gráfico."""
        # Separador único para evitar conflito com mensagens de commit
        sep = "^@^"
        cmd = ["git", "log", "--all", "--date=short", f"--pretty=format:%h{sep}%p{sep}%s{sep}%cd{sep}%an{sep}%d", "-n", "100"]
        
        try:
            result = subprocess.run(cmd, cwd=repo_path, capture_output=True, text=True, encoding='utf-8', errors='replace')
            if result.returncode != 0:
                return []
                
            commits = []
            for line in result.stdout.splitlines():
                parts = line.split(sep)
                if len(parts) < 6: continue
                
                commits.append({
                    "hash": parts[0],
                    "parents": parts[1].split(),
                    "message": parts[2],
                    "date": parts[3],
                    "author": parts[4],
                    "refs": parts[5].strip()
                })
            return commits
        except Exception as e:
            logger.error(f"Git graph error: {e}")
            return []

    def stage_all(self, repo_path: str):
        """Adiciona todos os arquivos modificados ao stage."""
        subprocess.run(["git", "add", "."], cwd=repo_path, check=False)

    def commit(self, repo_path: str, message: str) -> tuple[bool, str]:
        """Realiza um commit com todos os arquivos modificados."""
        if not message: return False, "Mensagem de commit vazia."
        try:
            self.stage_all(repo_path)
            subprocess.run(["git", "commit", "-m", message], cwd=repo_path, check=True, capture_output=True)
            return True, "Commit realizado com sucesso."
        except subprocess.CalledProcessError as e:
            return False, f"Erro no commit: {e.stderr.decode() if e.stderr else str(e)}"

    def create_branch(self, repo_path: str, branch_name: str) -> tuple[bool, str]:
        try:
            subprocess.run(["git", "checkout", "-b", branch_name], cwd=repo_path, check=True, capture_output=True)
            return True, f"Branch '{branch_name}' criado e ativo."
        except subprocess.CalledProcessError as e:
            return False, f"Erro ao criar branch: {e.stderr.decode() if e.stderr else str(e)}"

    def get_remote_url(self, repo_path: str, remote: str = "origin") -> str:
        try:
            res = subprocess.run(["git", "remote", "get-url", remote], cwd=repo_path, capture_output=True, text=True)
            return res.stdout.strip()
        except:
            return ""

    def _inject_credentials(self, url: str, username: str, token: str) -> str:
        if "://" not in url: return url
        protocol, rest = url.split("://", 1)
        if "@" in rest:
            rest = rest.split("@", 1)[1]
        return f"{protocol}://{username}:{token}@{rest}"

    def push(self, repo_path: str, username: str = None, token: str = None) -> tuple[bool, str]:
        try:
            cmd = ["git", "push"]
            if username and token:
                url = self.get_remote_url(repo_path)
                if url.startswith("http"):
                    auth_url = self._inject_credentials(url, username, token)
                    cmd = ["git", "push", auth_url]
            
            env = os.environ.copy()
            env["GIT_TERMINAL_PROMPT"] = "0"
            subprocess.run(cmd, cwd=repo_path, check=True, capture_output=True, env=env)
            return True, "Push realizado com sucesso."
        except subprocess.CalledProcessError as e:
            return False, f"Erro no Push: {e.stderr.decode() if e.stderr else str(e)}"

    def pull(self, repo_path: str, username: str = None, token: str = None) -> tuple[bool, str]:
        try:
            cmd = ["git", "pull"]
            if username and token:
                url = self.get_remote_url(repo_path)
                if url.startswith("http"):
                    auth_url = self._inject_credentials(url, username, token)
                    cmd = ["git", "pull", auth_url]

            env = os.environ.copy()
            env["GIT_TERMINAL_PROMPT"] = "0"
            subprocess.run(cmd, cwd=repo_path, check=True, capture_output=True, env=env)
            return True, "Pull realizado com sucesso."
        except subprocess.CalledProcessError as e:
            return False, f"Erro no Pull: {e.stderr.decode() if e.stderr else str(e)}"

    def get_branches(self, repo_path: str) -> list[str]:
        try:
            res = subprocess.run(["git", "branch", "--format=%(refname:short)"], cwd=repo_path, capture_output=True, text=True)
            return [b.strip() for b in res.stdout.split('\n') if b.strip()]
        except:
            return []

    def checkout(self, repo_path: str, branch_name: str) -> tuple[bool, str]:
        try:
            subprocess.run(["git", "checkout", branch_name], cwd=repo_path, check=True, capture_output=True)
            return True, f"Checkout para '{branch_name}' realizado."
        except subprocess.CalledProcessError as e:
            return False, f"Erro no Checkout: {e.stderr.decode() if e.stderr else str(e)}"

    def get_commit_files(self, repo_path: str, commit_hash: str) -> list[str]:
        try:
            res = subprocess.run(["git", "show", "--pretty=", "--name-only", commit_hash], cwd=repo_path, capture_output=True, text=True)
            return [f for f in res.stdout.split('\n') if f.strip()]
        except:
            return []

    def get_diff(self, repo_path: str, commit_hash: str, file_path: str) -> str:
        try:
            res = subprocess.run(["git", "show", commit_hash, "--", file_path], cwd=repo_path, capture_output=True, text=True)
            return res.stdout
        except:
            return "Não foi possível obter o diff."