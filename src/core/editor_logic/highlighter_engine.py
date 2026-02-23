from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class Token:
    start: int
    length: int
    token_type: str # ex: 'keyword', 'string', 'comment'

class HighlighterEngine:
    """Motor de análise léxica independente da UI.
    
    Recebe texto puro e retorna metadados de coloração.
    """

    def process_block(self, text: str) -> List[Token]:
        """Analisa um bloco de texto e retorna tokens.
        
        Esta é uma implementação dummy. Futuramente integrará com Pygments ou TreeSitter.
        """
        tokens = []
        
        # Exemplo simples: encontrar a palavra "def" ou "class"
        keywords = ["def", "class", "import", "return"]
        
        for keyword in keywords:
            start = 0
            while True:
                idx = text.find(keyword, start)
                if idx == -1:
                    break
                tokens.append(Token(idx, len(keyword), "keyword"))
                start = idx + len(keyword)
                
        return tokens