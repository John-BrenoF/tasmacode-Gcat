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