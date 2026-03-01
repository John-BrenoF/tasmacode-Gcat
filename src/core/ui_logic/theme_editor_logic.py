import os
import json
import logging
from typing import Dict, Any, List

logger = logging.getLogger("ThemeEditorLogic")

class ThemeEditorLogic:
    """Lida com a manipulação de dados de temas para o editor visual."""

    def __init__(self, theme_manager):
        self.theme_manager = theme_manager
        self.draft_theme: Dict[str, Any] = {}

    def get_editable_keys(self) -> List[str]:
        """Retorna as chaves de cor que podem ser editadas."""
        # Retorna todas as chaves do tema padrão, que serve como base
        return sorted(self.theme_manager._default_theme.keys())

    def load_theme_data(self, theme_name: str) -> Dict[str, Any]:
        """Carrega os dados de um tema para o estado de rascunho."""
        theme_path = os.path.join(self.theme_manager.themes_dir, f"{theme_name}.json")
        if os.path.exists(theme_path):
            try:
                with open(theme_path, 'r') as f:
                    loaded_data = json.load(f)
                    # Começa com o padrão e atualiza com o carregado para garantir consistência
                    self.draft_theme = self.theme_manager._default_theme.copy()
                    self.draft_theme.update(loaded_data)
            except Exception as e:
                logger.error(f"Erro ao carregar dados do tema '{theme_name}': {e}")
                self.draft_theme = self.theme_manager._default_theme.copy()
        else:
            self.draft_theme = self.theme_manager._default_theme.copy()
        
        return self.draft_theme

    def update_color(self, key: str, color_hex: str):
        """Atualiza uma cor no rascunho do tema."""
        self.draft_theme[key] = color_hex

    def save_theme(self, theme_name: str) -> bool:
        """Salva o rascunho atual em um arquivo JSON."""
        save_path = os.path.join(self.theme_manager.themes_dir, f"{theme_name}.json")
        try:
            with open(save_path, 'w') as f:
                json.dump(self.draft_theme, f, indent=4)
            logger.info(f"Tema '{theme_name}' salvo com sucesso em {save_path}")
            return True
        except Exception as e:
            logger.error(f"Falha ao salvar o tema '{theme_name}': {e}")
            return False