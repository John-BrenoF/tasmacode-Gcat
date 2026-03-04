from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class Marker:
    line: int
    label: str = ""
    color: str = "#007acc"  # Azul padrão

class MarkerManager:
    """Gerencia marcadores visuais em linhas específicas."""
    def __init__(self):
        self._markers: Dict[int, Marker] = {}

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