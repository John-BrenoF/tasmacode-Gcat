from typing import Callable, Dict, Any
import logging

logger = logging.getLogger("CommandRegistry")

class CommandRegistry:
    """Registro central de comandos do editor.
    
    Armazena funções (callbacks) associadas a IDs de string (ex: 'file.save').
    """
    
    def __init__(self):
        self._commands: Dict[str, Callable] = {}

    def register(self, command_id: str, callback: Callable) -> None:
        """Registra um novo comando."""
        self._commands[command_id] = callback
        logger.debug(f"Comando registrado: {command_id}")

    def execute(self, command_id: str, *args, **kwargs) -> bool:
        """Executa um comando pelo ID."""
        if command_id in self._commands:
            self._commands[command_id](*args, **kwargs)
            return True
        else:
            logger.warning(f"Comando não encontrado: {command_id}")
            return False