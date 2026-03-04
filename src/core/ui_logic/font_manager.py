import os
import logging
import zipfile
import shutil
from PySide6.QtGui import QFontDatabase, QFontInfo
from PySide6.QtCore import QDir

logger = logging.getLogger("FontManager")

class FontManager:
    """
    Gerencia o carregamento de fontes customizadas pelo usuário e lista fontes disponíveis.
    """
    def __init__(self, user_fonts_dir: str):
        self.db = QFontDatabase()
        self.user_fonts_dir = user_fonts_dir
        self.loaded_font_ids = []
        self._load_user_fonts()

    def _load_user_fonts(self):
        """Carrega todos os arquivos de fonte do diretório de fontes do usuário."""
        if not os.path.exists(self.user_fonts_dir):
            logger.info(f"Criando diretório de fontes do usuário: {self.user_fonts_dir}")
            os.makedirs(self.user_fonts_dir)
            return

        font_dir = QDir(self.user_fonts_dir)
        font_files = font_dir.entryList(["*.ttf", "*.otf", "*.woff", "*.woff2"], QDir.Filter.Files)

        for font_file in font_files:
            font_path = os.path.join(self.user_fonts_dir, font_file)
            font_id = self.db.addApplicationFont(font_path)
            if font_id != -1:
                self.loaded_font_ids.append(font_id)
                families = self.db.applicationFontFamilies(font_id)
                logger.info(f"Fonte customizada carregada '{font_file}' com famílias: {families}")
            else:
                logger.warning(f"Falha ao carregar fonte customizada: {font_path}")

    def get_monospace_fonts(self) -> list[str]:
        """Retorna uma lista de todas as famílias de fontes monoespaçadas disponíveis."""
        all_families = self.db.families()
        monospace_families = [f for f in all_families if self.db.isFixedPitch(f)]
        
        # Garante que fontes comuns estejam na lista, mesmo que o Qt não as detecte como fixed pitch
        common_monospace = [
            "JetBrains Mono", "Fira Code", "Consolas", "Courier New", "Menlo", "Monaco", 
            "Source Code Pro", "JetBrainsMono Nerd Font", "MesloLGS NF", "Droid Sans Mono", 
            "Inconsolata", "Hack", "Ubuntu Mono", "Cascadia Code", "Victor Mono"
        ]
        for font in common_monospace:
            if font in all_families and font not in monospace_families:
                monospace_families.append(font)
        
        # Adiciona explicitamente TODAS as fontes carregadas pelo usuário (via pasta fonts ou ZIP)
        for font_id in self.loaded_font_ids:
            user_families = self.db.applicationFontFamilies(font_id)
            for family in user_families:
                if family not in monospace_families:
                    monospace_families.append(family)
        
        return sorted(list(set(monospace_families)))

    def unload_user_fonts(self):
        """Descarrega todas as fontes de usuário carregadas anteriormente."""
        for font_id in self.loaded_font_ids:
            self.db.removeApplicationFont(font_id)
        self.loaded_font_ids = []

    def install_font_from_zip(self, zip_path: str) -> list[str]:
        """Instala fontes a partir de um arquivo ZIP e retorna os nomes das famílias instaladas."""
        if not os.path.exists(zip_path) or not zipfile.is_zipfile(zip_path):
            logger.error(f"Arquivo inválido: {zip_path}")
            return []
            
        try:
            installed_families = []
            with zipfile.ZipFile(zip_path, 'r') as z:
                for file_info in z.infolist():
                    if file_info.filename.lower().endswith(('.ttf', '.otf', '.woff', '.woff2')):
                        # Extrai apenas o arquivo (flatten) para a pasta de fontes
                        source = z.open(file_info)
                        target_filename = os.path.basename(file_info.filename)
                        if not target_filename: continue # Pula diretórios
                        
                        target_path = os.path.join(self.user_fonts_dir, target_filename)
                        with open(target_path, "wb") as target:
                            shutil.copyfileobj(source, target)
                        
                        font_id = self.db.addApplicationFont(target_path)
                        if font_id != -1:
                            if font_id not in self.loaded_font_ids:
                                self.loaded_font_ids.append(font_id)
                            families = self.db.applicationFontFamilies(font_id)
                            if families:
                                installed_families.extend(families)
                            logger.info(f"Fonte instalada: {target_filename} com famílias: {families}")
            return list(set(installed_families))
            
        except Exception as e:
            logger.error(f"Erro ao instalar fonte do zip: {e}")
            return []