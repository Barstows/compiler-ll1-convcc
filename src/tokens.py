"""
ConvCC-2026-1 Language Tokens
============================
Definição de todos os tokens (terminais) da gramática CC-2026-1.

Grupo: [Arthur Leite Bastos]
Data: 2026-06-30
"""

from enum import Enum, auto


class TokenType(Enum):
    """Enumeração de todos os tipos de tokens da linguagem ConvCC-2026-1."""
    
    # Palavras reservadas (keywords)
    DEF = auto()           # 'def'
    INT = auto()           # 'int'
    FLOAT = auto()         # 'float'
    STRING = auto()        # 'string'
    PRINT = auto()         # 'print'
    READ = auto()          # 'read'
    RETURN = auto()        # 'return'
    IF = auto()            # 'if'
    ELSE = auto()          # 'else'
    FOR = auto()           # 'for'
    BREAK = auto()         # 'break'
    NEW = auto()           # 'new'
    
    # Constantes
    INTCONSTANT = auto()   # intconstant
    FLOATCONSTANT = auto()   # floatconstant
    STRINGCONSTANT = auto()  # stringconstant
    NULL = auto()          # 'null'
    
    # Identificadores
    IDENT = auto()         # ident
    
    # Operadores aritméticos
    PLUS = auto()          # '+'
    MINUS = auto()         # '-'
    MULT = auto()          # '*'
    DIV = auto()           # '/'
    MOD = auto()           # '%'
    
    # Operadores relacionais
    LT = auto()            # '<'
    GT = auto()            # '>'
    LE = auto()            # '<='
    GE = auto()            # '>='
    EQ = auto()            # '=='
    NE = auto()            # '!='
    
    # Operadores de atribuição
    ASSIGN = auto()        # '='
    
    # Símbolos especiais
    SEMICOLON = auto()     # ';'
    COMMA = auto()         # ','
    LPAREN = auto()        # '('
    RPAREN = auto()        # ')'
    LBRACE = auto()        # '{'
    RBRACE = auto()        # '}'
    LBRACKET = auto()       # '['
    RBRACKET = auto()       # ']'
    
    # Fim de arquivo
    EOF = auto()
    
    # Token inválido (para erros)
    INVALID = auto()


# Mapeamento de palavras reservadas para seus tipos de token
KEYWORDS = {
    'def': TokenType.DEF,
    'int': TokenType.INT,
    'float': TokenType.FLOAT,
    'string': TokenType.STRING,
    'print': TokenType.PRINT,
    'read': TokenType.READ,
    'return': TokenType.RETURN,
    'if': TokenType.IF,
    'else': TokenType.ELSE,
    'for': TokenType.FOR,
    'break': TokenType.BREAK,
    'null': TokenType.NULL,
    'new': TokenType.NEW,
}


class Token:
    """Representa um token com seu tipo, valor e posição na entrada."""
    
    def __init__(self, token_type: TokenType, value: str = None, 
                 line: int = 0, column: int = 0):
        self.type = token_type
        self.value = value
        self.line = line
        self.column = column
    
    def __str__(self) -> str:
        if self.value is not None:
            return f"Token({self.type.name}, '{self.value}', line={self.line}, col={self.column})"
        return f"Token({self.type.name}, line={self.line}, col={self.column})"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def __eq__(self, other) -> bool:
        if isinstance(other, TokenType):
            return self.type == other
        if isinstance(other, Token):
            return self.type == other.type and self.value == other.value
        return False
    
    def __hash__(self) -> int:
        return hash((self.type, self.value))