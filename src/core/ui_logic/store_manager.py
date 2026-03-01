import logging
import os
import requests
import zipfile
import io
import shutil

logger = logging.getLogger("StoreManager")

class StoreManager:
    """
    Gerencia a lógica da loja de plugins, como instalação a partir de uma URL.
    """
    def __init__(self, root_dir: str):
        self.root_dir = root_dir
        self.tmp_dir = os.path.join(root_dir, "tmp")
        self.plugins_dir = os.path.join(root_dir, "plugins")

    def install_from_url(self, url: str) -> bool:
        """
        Orquestra o processo de download, extração e instalação de um plugin do GitHub.
        """
        if not url or "github.com" not in url:
            logger.warning(f"URL inválida ou não é do GitHub: {url}")
            return False
        
        logger.info(f"Iniciando instalação a partir de: {url}")
        
        try:
            # 1. Obter URL do ZIP
            zip_url = self._get_zip_url(url)
            if not zip_url:
                return False

            # 2. Baixar e extrair
            extracted_path = self._download_and_extract(zip_url)
            if not extracted_path:
                return False

            # 3. Mover arquivos do plugin
            self._move_plugin_files(extracted_path)
            
            logger.info(f"Plugin de {url} instalado com sucesso.")
            return True

        except Exception as e:
            logger.error(f"Falha na instalação do plugin: {e}")
            return False
        finally:
            # 4. Limpeza
            self._cleanup()

    def _get_zip_url(self, github_url: str) -> str | None:
        """Converte uma URL de repositório GitHub para uma URL de download de ZIP."""
        repo_path = github_url.replace("https://github.com/", "").replace(".git", "")
        
        for branch in ["main", "master"]:
            zip_url = f"https://github.com/{repo_path}/archive/refs/heads/{branch}.zip"
            try:
                response = requests.head(zip_url, allow_redirects=True, timeout=5)
                if response.status_code == 200:
                    logger.debug(f"URL do ZIP encontrada: {zip_url}")
                    return zip_url
            except requests.RequestException as e:
                logger.warning(f"Erro ao verificar URL do ZIP ({branch}): {e}")
                continue
        
        logger.error(f"Não foi possível encontrar um branch 'main' ou 'master' para {github_url}")
        return None

    def _download_and_extract(self, zip_url: str) -> str | None:
        """Baixa o ZIP, extrai para a pasta tmp e retorna o caminho da pasta extraída."""
        logger.info(f"Baixando de {zip_url}...")
        response = requests.get(zip_url, timeout=30)
        response.raise_for_status()

        zip_file = zipfile.ZipFile(io.BytesIO(response.content))
        
        if os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)
        os.makedirs(self.tmp_dir)

        zip_file.extractall(self.tmp_dir)
        logger.info(f"Extraído para {self.tmp_dir}")
        
        extracted_folders = [d for d in os.listdir(self.tmp_dir) if os.path.isdir(os.path.join(self.tmp_dir, d))]
        if not extracted_folders:
            raise IOError("O arquivo ZIP não continha um diretório raiz.")
            
        return os.path.join(self.tmp_dir, extracted_folders[0])

    def _move_plugin_files(self, extracted_path: str):
        """Move os arquivos de dentro da pasta extraída para a pasta de plugins."""
        if not os.path.exists(self.plugins_dir):
            os.makedirs(self.plugins_dir)

        for item_name in os.listdir(extracted_path):
            source_item = os.path.join(extracted_path, item_name)
            dest_item = os.path.join(self.plugins_dir, item_name)
            
            if os.path.exists(dest_item):
                if os.path.isdir(dest_item):
                    shutil.rmtree(dest_item)
                else:
                    os.remove(dest_item)
            
            shutil.move(source_item, self.plugins_dir)
            logger.debug(f"Movido '{item_name}' para a pasta de plugins.")

    def _cleanup(self):
        """Remove a pasta temporária."""
        if os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)
            logger.info(f"Pasta temporária '{self.tmp_dir}' removida.")

    def get_installed_plugins(self) -> list[str]:
        """Retorna uma lista com os nomes dos plugins instalados."""
        if not os.path.exists(self.plugins_dir):
            return []
        
        plugins = []
        for name in os.listdir(self.plugins_dir):
            if os.path.isdir(os.path.join(self.plugins_dir, name)) and not name.startswith("__"):
                plugins.append(name)
        return sorted(plugins)

    def remove_plugin(self, plugin_name: str) -> bool:
        """Remove (deleta) a pasta de um plugin."""
        plugin_path = os.path.join(self.plugins_dir, plugin_name)
        if not os.path.isdir(plugin_path):
            logger.warning(f"Tentativa de remover plugin não existente: {plugin_name}")
            return False
        
        try:
            shutil.rmtree(plugin_path)
            logger.info(f"Plugin '{plugin_name}' removido com sucesso.")
            return True
        except Exception as e:
            logger.error(f"Erro ao remover plugin '{plugin_name}': {e}")
            return False