import re
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class Token:
    start: int
    length: int
    color_key: str

class SyntaxHighlighter:
    """Motor de realce de sintaxe baseado em Regex para Python."""

    def __init__(self):
        self.rules = []
        self._compile_rules()

    def _compile_rules(self):
        """Compila as regras de regex. A ordem define a prioridade."""
        self.rules = [
            # 1. Strings (Aspas duplas e simples) - Alta prioridade para evitar keywords dentro delas
            ('string_color', re.compile(r'"[^"\\]*(\\.[^"\\]*)*"')),
            ('string_color', re.compile(r"'[^'\\]*(\\.[^'\\]*)*'")),
            
            # 2. Comentários
            ('comment_color', re.compile(r'#.*')),
            
            # 3. Definições (Nomes de Classes e Funções)
            # Captura apenas o nome (grupo 1), ignorando a keyword 'class'/'def'
            ('class_color', re.compile(r'\bclass\s+([a-zA-Z_][a-zA-Z0-9_]*)')),
            ('function_color', re.compile(r'\bdef\s+([a-zA-Z_][a-zA-Z0-9_]*)')),
            
            # 4. Palavras-chave e Built-ins
            ('keyword_color', re.compile(r'\b(def|class|import|from|return|if|else|elif|for|while|try|except|finally|with|as|lambda|pass|break|continue)\b')),
            ('builtin_color', re.compile(r'\b(True|False|None|self)\b')),
            
            # 5. Operadores
            ('operator_color', re.compile(r'[\+\-\*\/=\&\|\!\<\>\%\^]+')),
        ]

    def highlight(self, text: str) -> List[Token]:
        """Processa uma linha de texto e retorna os tokens de cor."""
        tokens = []
        # Máscara para rastrear caracteres já coloridos (evita sobreposição)
        mask = [False] * len(text)

        for key, regex in self.rules:
            for match in regex.finditer(text):
                # Se a regra tem grupos de captura (ex: def nome), usa o grupo 1
                if key in ('class_color', 'function_color') and match.lastindex:
                    start, end = match.span(1)
                else:
                    start, end = match.span()

                # Verifica se já foi colorido (ex: keyword dentro de string)
                if any(mask[start:end]):
                    continue

                # Marca a região como colorida
                for i in range(start, end):
                    mask[i] = True

                tokens.append(Token(start, end - start, key))

        return tokens