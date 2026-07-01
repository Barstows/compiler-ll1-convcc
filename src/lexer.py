"""
ConvCC-2026-1 Lexical Analyzer
=============================
Analisador léxico baseado em diagramas de transição.
Lê o código fonte caracter por caracter e produz tokens.

Grupo: [Arthur Leite Bastos]
Data: 2026-06-30
"""

from typing import List, Optional, Tuple
from tokens import Token, TokenType, KEYWORDS


class Symbol:
    """Representa um símbolo na tabela de símbolos."""
    
    def __init__(self, name: str, symbol_type: str = None):
        self.name = name
        self.type = symbol_type  # 'int', 'float', 'string'
        self.occurrences: List[Tuple[int, int]] = []  # (linha, coluna)
    
    def add_occurrence(self, line: int, column: int):
        """Adiciona uma ocorrência do identificador."""
        self.occurrences.append((line, column))
    
    def __str__(self) -> str:
        return f"Symbol({self.name}, type={self.type}, occurrences={self.occurrences})"


class SymbolTable:
    """Tabela de símbolos do compilador."""
    
    def __init__(self):
        self.symbols: dict[str, Symbol] = {}
    
    def insert(self, name: str, line: int, column: int) -> Symbol:
        """Insere um identificador na tabela ou retorna existente."""
        if name not in self.symbols:
            self.symbols[name] = Symbol(name)
        self.symbols[name].add_occurrence(line, column)
        return self.symbols[name]
    
    def lookup(self, name: str) -> Optional[Symbol]:
        """Busca um identificador na tabela."""
        return self.symbols.get(name)
    
    def set_type(self, name: str, symbol_type: str):
        """Define o tipo de um identificador."""
        if name in self.symbols:
            self.symbols[name].type = symbol_type
    
    def get_type(self, name: str) -> Optional[str]:
        """Obtém o tipo de um identificador."""
        symbol = self.lookup(name)
        return symbol.type if symbol else None
    
    def __str__(self) -> str:
        return "\n".join(str(s) for s in self.symbols.values())


class Lexer:
    """
    Analisador léxico para a linguagem ConvCC-2026-1.
    Implementado com diagramas de transição (state machine).
    """
    
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.symbol_table = SymbolTable()
        self.tokens: List[Token] = []
        self.errors: List[str] = []
    
    # ============================================================
    # Métodos auxiliares de leitura
    # ============================================================
    
    def current_char(self) -> Optional[str]:
        """Retorna o caractere atual sem avançar."""
        if self.pos >= len(self.source):
            return None
        return self.source[self.pos]
    
    def peek_char(self, offset: int = 1) -> Optional[str]:
        """Olha um caractere à frente sem avançar."""
        if self.pos + offset >= len(self.source):
            return None
        return self.source[self.pos + offset]
    
    def advance(self) -> Optional[str]:
        """Avança para o próximo caractere e retorna o atual."""
        if self.pos >= len(self.source):
            return None
        
        char = self.source[self.pos]
        self.pos += 1
        
        if char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        
        return char
    
    # ============================================================
    # Tratamento de espaços em branco e comentários
    # ============================================================
    
    def skip_whitespace_and_comments(self):
        """
        Pula caracteres de espaço em branco e comentários.
        Comentários de linha: // até o fim da linha
        Comentários de bloco: /* ... */ (podem atravessar múltiplas linhas)
        """
        while self.current_char() is not None:
            # Espaços em branco
            if self.current_char() in [' ', '\t', '\n', '\r']:
                self.advance()
            
            # Comentário de linha //
            elif self.current_char() == '/' and self.peek_char() == '/':
                # Pula até o fim da linha
                while self.current_char() is not None and self.current_char() != '\n':
                    self.advance()
            
            # Comentário de bloco /* ... */
            elif self.current_char() == '/' and self.peek_char() == '*':
                # Pula /*
                self.advance()
                self.advance()
                
                # Continua até encontrar */
                while self.current_char() is not None:
                    if self.current_char() == '*' and self.peek_char() == '/':
                        self.advance()  # pula *
                        self.advance()  # pula /
                        break
                    self.advance()
                else:
                    # Chegou ao fim do arquivo sem fechar o comentário
                    self.errors.append(f"Erro Léxico [{self.line}:{self.column}]: Comentário de bloco não fechado")
            
            else:
                # Não é espaço nem comentário
                break
    
    # ============================================================
    # Leitores de tokens (diagramas de transição)
    # ============================================================
    
    def read_identifier(self) -> str:
        """Lê um identificador ou palavra reservada."""
        start = self.pos
        while self.current_char() and (self.current_char().isalnum() or self.current_char() == '_'):
            self.advance()
        return self.source[start:self.pos]
    
    def read_number(self) -> Tuple[str, TokenType]:
        """
        Lê uma constante numérica (inteira ou float).
        Retorna (valor, tipo_do_token).
        Lê dígitos, depois verifica se tem '.' seguido de mais dígitos.
        """
        start = self.pos
        start_line = self.line
        start_col = self.column
        
        # Lê a parte inteira
        while self.current_char() and self.current_char().isdigit():
            self.advance()
        
        # Verifica se é float (tem '.' seguido de dígitos)
        if self.current_char() == '.' and self.peek_char() and self.peek_char().isdigit():
            self.advance()  # pula o '.'
            while self.current_char() and self.current_char().isdigit():
                self.advance()
            return self.source[start:self.pos], TokenType.FLOATCONSTANT
        
        return self.source[start:self.pos], TokenType.INTCONSTANT
    
    def read_string(self) -> str:
        """
        Lê uma constante string.
        Retorna o conteúdo da string (sem as aspas).
        Trata caracteres de escape: \\n, \\t, \\\", \\\\
        """
        # Pula a aspa inicial
        self.advance()
        
        result = []
        start_line = self.line
        start_col = self.column
        
        while self.current_char() is not None and self.current_char() != '"':
            if self.current_char() == '\\':
                self.advance()  # pula a barra invertida
                escaped = self.current_char()
                if escaped == 'n':
                    result.append('\n')
                elif escaped == 't':
                    result.append('\t')
                elif escaped == '"':
                    result.append('"')
                elif escaped == '\\':
                    result.append('\\')
                elif escaped is not None:
                    # Sequência de escape desconhecida - mantém a barra e o char
                    result.append('\\')
                    result.append(escaped)
                self.advance()
            elif self.current_char() == '\n':
                # String não pode ter quebra de linha sem escape
                self.errors.append(f"Erro Léxico [{self.line}:{self.column}]: String não fechada (quebra de linha)")
                self.advance()
                return ''.join(result)
            else:
                result.append(self.current_char())
                self.advance()
        
        # Verifica se a string foi fechada
        if self.current_char() == '"':
            self.advance()  # pula a aspa final
        else:
            self.errors.append(f"Erro Léxico [{start_line}:{start_col}]: String não fechada")
        
        return ''.join(result)
    
    # ============================================================
    # Tokenizador principal
    # ============================================================
    
    def next_token(self) -> Token:
        """Retorna o próximo token da entrada."""
        self.skip_whitespace_and_comments()
        
        char = self.current_char()
        
        if char is None:
            return Token(TokenType.EOF, line=self.line, column=self.column)
        
        # Guarda posição atual para o token
        token_line = self.line
        token_col = self.column
        
        # Identificadores e palavras reservadas
        if char.isalpha() or char == '_':
            value = self.read_identifier()
            token_type = KEYWORDS.get(value, TokenType.IDENT)
            if token_type == TokenType.IDENT:
                self.symbol_table.insert(value, token_line, token_col)
            return Token(token_type, value, token_line, token_col)
        
        # Constantes numéricas (inteiras ou float)
        if char.isdigit():
            value, token_type = self.read_number()
            return Token(token_type, value, token_line, token_col)
        
        # Strings
        if char == '"':
            value = self.read_string()
            return Token(TokenType.STRINGCONSTANT, value, token_line, token_col)
        
        # Operadores de dois caracteres
        if char == '=' and self.peek_char() == '=':
            self.advance()
            self.advance()
            return Token(TokenType.EQ, '==', token_line, token_col)
        
        if char == '!' and self.peek_char() == '=':
            self.advance()
            self.advance()
            return Token(TokenType.NE, '!=', token_line, token_col)
        
        if char == '<' and self.peek_char() == '=':
            self.advance()
            self.advance()
            return Token(TokenType.LE, '<=', token_line, token_col)
        
        if char == '>' and self.peek_char() == '=':
            self.advance()
            self.advance()
            return Token(TokenType.GE, '>=', token_line, token_col)
        
        # Operadores e símbolos de um caractere
        single_char_tokens = {
            '+': TokenType.PLUS,
            '-': TokenType.MINUS,
            '*': TokenType.MULT,
            '/': TokenType.DIV,
            '%': TokenType.MOD,
            '<': TokenType.LT,
            '>': TokenType.GT,
            '=': TokenType.ASSIGN,
            ';': TokenType.SEMICOLON,
            ',': TokenType.COMMA,
            '(': TokenType.LPAREN,
            ')': TokenType.RPAREN,
            '{': TokenType.LBRACE,
            '}': TokenType.RBRACE,
            '[': TokenType.LBRACKET,
            ']': TokenType.RBRACKET,
        }
        
        if char in single_char_tokens:
            self.advance()
            return Token(single_char_tokens[char], char, token_line, token_col)
        
        # Caractere inválido
        self.errors.append(f"Erro Léxico [{token_line}:{token_col}]: Caractere inesperado '{char}'")
        self.advance()
        return Token(TokenType.INVALID, char, token_line, token_col)
    
    # ============================================================
    # Tokenização completa e utilitários
    # ============================================================
    
    def tokenize(self) -> List[Token]:
        """Tokeniza todo o código fonte."""
        while True:
            token = self.next_token()
            self.tokens.append(token)
            if token.type == TokenType.EOF:
                break
        return self.tokens
    
    def has_errors(self) -> bool:
        """Verifica se houve erros léxicos."""
        return len(self.errors) > 0
    
    def print_errors(self):
        """Imprime os erros léxicos."""
        for error in self.errors:
            print(error)
    
    def print_symbol_table(self):
        """Imprime a tabela de símbolos."""
        print("Tabela de Símbolos:")
        for name, symbol in self.symbol_table.symbols.items():
            print(f"  {symbol}")