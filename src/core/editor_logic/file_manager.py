import asyncio
import os
import logging


logger = logging.getLogger("FileManager")

class FileManager:
    """Gerencia leitura e escrita de arquivos de forma assíncrona."""

    @staticmethod
    async def load_file(path: str) -> str:
        """Lê um arquivo do disco sem bloquear a thread principal.
        
        Args:
            path: Caminho absoluto do arquivo.
        Returns:
            Conteúdo do arquivo como string.
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"Arquivo não encontrado: {path}")

        # Simulação de detecção de encoding (pode usar chardet no futuro)
        encoding = 'utf-8'
        
        try:
            # Executa a leitura em uma thread separada para garantir não-bloqueio
            # mesmo sem aiofiles
            return await asyncio.to_thread(FileManager._read_sync, path, encoding)
        except Exception as e:
            logger.error(f"Erro ao ler arquivo: {e}")
            raise

    @staticmethod
    def _read_sync(path: str, encoding: str) -> str:
        with open(path, 'r', encoding=encoding) as f:
            return f.read()

    @staticmethod
    async def save_file(path: str, content: str) -> bool:
        """Salva o conteúdo no disco."""
        try:
            await asyncio.to_thread(FileManager._write_sync, path, content)
            logger.info(f"Arquivo salvo: {path}")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar arquivo: {e}")
            return False

    @staticmethod
    def _write_sync(path: str, content: str):
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

    @staticmethod
    def create_file(base_path: str, relative_path: str) -> str:
        """Cria um arquivo e diretórios intermediários se necessário."""
        full_path = os.path.join(base_path, relative_path)
        
        if os.path.exists(full_path):
            raise FileExistsError(f"O arquivo '{relative_path}' já existe.")
            
        parent_dir = os.path.dirname(full_path)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir)
            
        with open(full_path, 'w', encoding='utf-8') as f:
            pass
        return full_path

    @staticmethod
    def create_directory(base_path: str, relative_path: str) -> str:
        """Cria um diretório e pais se necessário."""
        full_path = os.path.join(base_path, relative_path)
        if os.path.exists(full_path):
            raise FileExistsError(f"A pasta '{relative_path}' já existe.")
        os.makedirs(full_path)
        return full_path