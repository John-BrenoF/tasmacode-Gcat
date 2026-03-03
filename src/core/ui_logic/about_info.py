from dataclasses import dataclass

@dataclass
class AboutInfo:
    """Armazena dados estáticos sobre a aplicação."""
    app_name: str = "tasmacode Gcat"
    version: str = "10.0 Beta"
    description: str = "Um editor de código modular e leve, focado em performance e extensibilidade."
    creator_name: str = "John-BrenoF"
    creator_url: str = "https://github.com/John-BrenoF"
    icon_relative_path: str = "icon/JCODE.svg"