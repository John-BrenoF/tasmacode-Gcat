from dataclasses import dataclass, asdict
from typing import Dict, Optional
import json
import os
import hashlib

@dataclass
class Marker:
    line: int
    label: str = ""
    color: str = "#007acc"  # Azul padrão

class MarkerManager:
    """Gerencia marcadores visuais em linhas específicas."""
    def __init__(self):
        self._markers: Dict[int, Marker] = {}
        self.file_path = ""

    def set_file_path(self, path: str):
        self.file_path = path

    def add_marker(self, line: int, label: str = "", color: str = "#007acc"):
        self._markers[line] = Marker(line, label, color)

    def remove_marker(self, line: int):
        if line in self._markers:
            del self._markers[line]

    def get_marker(self, line: int) -> Optional[Marker]:
        return self._markers.get(line)

    def has_marker(self, line: int) -> bool:
        return line in self._markers

    def toggle_marker(self, line: int):
        if self.has_marker(line):
            self.remove_marker(line)
        else:
            self.add_marker(line)
            
    def get_all_markers(self) -> Dict[int, Marker]:
        return self._markers

    def load_from_cache(self, cache_dir: str):
        if not self.file_path or not cache_dir: return
        
        marker_file = self._get_cache_file(cache_dir)
        if os.path.exists(marker_file):
            try:
                with open(marker_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Suporte para formato novo (com file_path) e antigo (apenas dict)
                    markers_data = data.get("markers", data) if "markers" in data else data
                    self._markers = {int(k): Marker(**v) for k, v in markers_data.items()}
            except Exception as e:
                print(f"Erro ao carregar marcadores: {e}")

    def save_to_cache(self, cache_dir: str):
        if not self.file_path or not cache_dir: return
        
        marker_file = self._get_cache_file(cache_dir)
        try:
            os.makedirs(os.path.dirname(marker_file), exist_ok=True)
            # Salva estrutura com metadados do arquivo
            data = {
                "file_path": self.file_path,
                "markers": {str(k): asdict(v) for k, v in self._markers.items()}
            }
            with open(marker_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Erro ao salvar marcadores: {e}")

    def _get_cache_file(self, cache_dir: str) -> str:
        # Cria um hash único para o caminho do arquivo
        hash_name = hashlib.md5(self.file_path.encode('utf-8')).hexdigest()
        return os.path.join(cache_dir, "markers", f"{hash_name}.json")

    @staticmethod
    def get_global_markers(cache_dir: str) -> list:
        """Retorna uma lista de tuplas (file_path, line, marker) de todo o projeto."""
        results = []
        markers_dir = os.path.join(cache_dir, "markers")
        if not os.path.exists(markers_dir):
            return results
            
        for filename in os.listdir(markers_dir):
            if not filename.endswith(".json"): continue
            filepath = os.path.join(markers_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Apenas processa se tiver o formato novo com file_path
                if "file_path" in data and "markers" in data:
                    f_path = data["file_path"]
                    # Verifica se o arquivo ainda existe
                    if os.path.exists(f_path):
                        for line_str, marker_dict in data["markers"].items():
                            marker = Marker(**marker_dict)
                            results.append((f_path, int(line_str), marker))
            except:
                continue
        return results