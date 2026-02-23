import os
import sys
import importlib.util
import logging
from typing import Dict, List, Callable, Any
from PySide6.QtCore import QObject, Signal

# Configuração básica de log
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ExtensionBridge")

class ExtensionBridge(QObject):
    """Gerencia o carregamento de plugins e o sistema de Hooks.

    Atua como a ponte entre o Core e funcionalidades estendidas.
    Herda de QObject para permitir comunicação via Sinais se necessário.
    """

    # Sinais para notificar a UI sobre mudanças no estado dos plugins
    plugin_loaded = Signal(str)
    
    def __init__(self):
        super().__init__()
        self._hooks: Dict[str, List[Callable]] = {
            "on_text_changed": [],
            "on_file_open": [],
            "before_render": [],
            "on_app_start": []
        }
        self._plugins: Dict[str, Any] = {}

    def register_hook(self, hook_name: str, callback: Callable) -> None:
        """Registra uma função callback em um hook específico.

        Args:
            hook_name: O nome do evento (ex: 'on_text_changed').
            callback: A função a ser executada.
        """
        if hook_name in self._hooks:
            self._hooks[hook_name].append(callback)
            logger.debug(f"Hook registrado em '{hook_name}': {callback.__name__}")
        else:
            logger.warning(f"Tentativa de registro em hook inexistente: {hook_name}")

    def trigger_hook(self, hook_name: str, *args, **kwargs) -> None:
        """Dispara todos os callbacks registrados para um hook.

        Args:
            hook_name: O nome do evento a disparar.
            *args, **kwargs: Argumentos passados para os callbacks.
        """
        if hook_name in self._hooks:
            for callback in self._hooks[hook_name]:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Erro ao executar hook '{hook_name}': {e}")

    def load_plugins(self, plugins_dir: str) -> None:
        """Carrega dinamicamente todos os scripts Python no diretório de plugins.

        Args:
            plugins_dir: Caminho absoluto ou relativo para a pasta de plugins.
        """
        if not os.path.exists(plugins_dir):
            logger.warning(f"Diretório de plugins não encontrado: {plugins_dir}")
            return

        # Adiciona o diretório ao path para facilitar imports relativos nos plugins
        sys.path.append(plugins_dir)

        for filename in os.listdir(plugins_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                self._load_single_plugin(plugins_dir, filename)

    def _load_single_plugin(self, directory: str, filename: str) -> None:
        """Carrega um único arquivo de plugin.

        Espera que o plugin tenha uma função `register(bridge)`.
        """
        plugin_name = filename[:-3] # Remove .py
        path = os.path.join(directory, filename)

        try:
            spec = importlib.util.spec_from_file_location(plugin_name, path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Protocolo: O plugin deve ter uma função 'register'
                if hasattr(module, "register"):
                    module.register(self)
                    self._plugins[plugin_name] = module
                    self.plugin_loaded.emit(plugin_name)
                    logger.info(f"Plugin carregado com sucesso: {plugin_name}")
                else:
                    logger.warning(f"Plugin {plugin_name} ignorado: função 'register' não encontrada.")
        except Exception as e:
            logger.error(f"Falha ao carregar plugin {plugin_name}: {e}")

    def get_loaded_plugins(self) -> List[str]:
        """Retorna lista de nomes dos plugins carregados."""
        return list(self._plugins.keys())