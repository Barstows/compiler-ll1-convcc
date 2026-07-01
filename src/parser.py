"""
ConvCC-2026-1 Syntax Analyzer
=============================
Analisador sintático LL(1) para a linguagem ConvCC-2026-1.
Usa tabela de parsing explícita construída uma única vez para validação,
e parser recursivo para construção da AST.

Grupo: [Arthur Leite Bastos]
Data: 2026-06-30
"""

# Modificações da linguagem ConvCC-2026-1:
# 1. PROGRAM → (STATEMENT | FUNCDEF)* — Permite sequência mista de
#    declarações globais e definições de funções em qualquer ordem.
# 2. RETURNSTAT → return [EXPRESSION] — Permite retorno de valores
#    em funções (expressão opcional após return).
# 3. PARAM_LIST_CALL → EXPRESSION {, EXPRESSION} — Permite passar
#    expressões arbitrárias como argumentos em chamadas de função,
#    não apenas identificadores.
# 4. STATEMENT permite FUNCCALL como comando (ex: imprime_global();)
#    — Chamadas de função podem ser usadas como statements.

from typing import List, Optional, Dict, Tuple
from tokens import Token, TokenType


class ParseError(Exception):
    """Exceção para erros sintáticos."""
    
    def __init__(self, message: str, token: Token = None):
        self.message = message
        self.token = token
        super().__init__(f"{message} (line {token.line}, col {token.column})" if token else message)


class ASTNode:
    """Nó da Árvore de Sintaxe Abstrata."""
    
    def __init__(self, node_type: str, value: str = None):
        self.type = node_type
        self.value = value
        self.children: List['ASTNode'] = []
    
    def add_child(self, child: 'ASTNode'):
        """Adiciona um nó filho."""
        self.children.append(child)
    
    def __str__(self) -> str:
        return f"ASTNode({self.type}, value={self.value})"


# Mapeamento de símbolos terminais para TokenType
TERMINAL_MAP = {
    "DEF": TokenType.DEF,
    "INT": TokenType.INT,
    "FLOAT": TokenType.FLOAT,
    "STRING": TokenType.STRING,
    "PRINT": TokenType.PRINT,
    "READ": TokenType.READ,
    "RETURN": TokenType.RETURN,
    "IF": TokenType.IF,
    "ELSE": TokenType.ELSE,
    "FOR": TokenType.FOR,
    "BREAK": TokenType.BREAK,
    "NEW": TokenType.NEW,
    "NULL": TokenType.NULL,
    "IDENT": TokenType.IDENT,
    "INTCONSTANT": TokenType.INTCONSTANT,
    "FLOATCONSTANT": TokenType.FLOATCONSTANT,
    "STRINGCONSTANT": TokenType.STRINGCONSTANT,
    "SEMICOLON": TokenType.SEMICOLON,
    "COMMA": TokenType.COMMA,
    "LPAREN": TokenType.LPAREN,
    "RPAREN": TokenType.RPAREN,
    "LBRACE": TokenType.LBRACE,
    "RBRACE": TokenType.RBRACE,
    "LBRACKET": TokenType.LBRACKET,
    "RBRACKET": TokenType.RBRACKET,
    "ASSIGN": TokenType.ASSIGN,
    "PLUS": TokenType.PLUS,
    "MINUS": TokenType.MINUS,
    "MULT": TokenType.MULT,
    "DIV": TokenType.DIV,
    "MOD": TokenType.MOD,
    "LT": TokenType.LT,
    "GT": TokenType.GT,
    "LE": TokenType.LE,
    "GE": TokenType.GE,
    "EQ": TokenType.EQ,
    "NE": TokenType.NE,
}


class ParsingTable:
    """Tabela de parsing LL(1) explícita."""
    
    def __init__(self):
        self.table: Dict[str, Dict[TokenType, List[str]]] = {}
        self._build_table()
    
    def _build_table(self):
        """Constrói a tabela de parsing LL(1) com base na gramática transformada."""
        
        # PROGRAM → (STATEMENT | FUNCDEF)*
        self.table["PROGRAM"] = {
            TokenType.DEF: ["FUNCDEF", "PROGRAM"],
            TokenType.INT: ["STATEMENT", "PROGRAM"],
            TokenType.FLOAT: ["STATEMENT", "PROGRAM"],
            TokenType.STRING: ["STATEMENT", "PROGRAM"],
            TokenType.IDENT: ["STATEMENT", "PROGRAM"],
            TokenType.PRINT: ["STATEMENT", "PROGRAM"],
            TokenType.READ: ["STATEMENT", "PROGRAM"],
            TokenType.RETURN: ["STATEMENT", "PROGRAM"],
            TokenType.IF: ["STATEMENT", "PROGRAM"],
            TokenType.FOR: ["STATEMENT", "PROGRAM"],
            TokenType.LBRACE: ["STATEMENT", "PROGRAM"],
            TokenType.BREAK: ["STATEMENT", "PROGRAM"],
            TokenType.SEMICOLON: ["STATEMENT", "PROGRAM"],
            TokenType.EOF: [],
        }
        
        # FUNCDEF → def ident ( PARAM_LIST ) { STATELIST }
        self.table["FUNCDEF"] = {
            TokenType.DEF: ["DEF", "IDENT", "LPAREN", "PARAM_LIST", "RPAREN", "LBRACE", "STATELIST", "RBRACE"],
        }
        
        # PARAM_LIST → (int|float|string) ident PARAM_LIST_PRIME | ε
        self.table["PARAM_LIST"] = {
            TokenType.INT: ["INT", "IDENT", "PARAM_LIST_PRIME"],
            TokenType.FLOAT: ["FLOAT", "IDENT", "PARAM_LIST_PRIME"],
            TokenType.STRING: ["STRING", "IDENT", "PARAM_LIST_PRIME"],
            TokenType.RPAREN: [],
        }
        
        # PARAM_LIST_PRIME → , PARAM_LIST | ε
        self.table["PARAM_LIST_PRIME"] = {
            TokenType.COMMA: ["COMMA", "PARAM_LIST"],
            TokenType.RPAREN: [],
        }
        
        # STATELIST → STATEMENT STATELIST_PRIME
        self.table["STATELIST"] = {
            TokenType.INT: ["STATEMENT", "STATELIST_PRIME"],
            TokenType.FLOAT: ["STATEMENT", "STATELIST_PRIME"],
            TokenType.STRING: ["STATEMENT", "STATELIST_PRIME"],
            TokenType.IDENT: ["STATEMENT", "STATELIST_PRIME"],
            TokenType.PRINT: ["STATEMENT", "STATELIST_PRIME"],
            TokenType.READ: ["STATEMENT", "STATELIST_PRIME"],
            TokenType.RETURN: ["STATEMENT", "STATELIST_PRIME"],
            TokenType.IF: ["STATEMENT", "STATELIST_PRIME"],
            TokenType.FOR: ["STATEMENT", "STATELIST_PRIME"],
            TokenType.LBRACE: ["STATEMENT", "STATELIST_PRIME"],
            TokenType.BREAK: ["STATEMENT", "STATELIST_PRIME"],
            TokenType.SEMICOLON: ["STATEMENT", "STATELIST_PRIME"],
        }
        
        # STATELIST_PRIME → STATEMENT STATELIST_PRIME | ε
        self.table["STATELIST_PRIME"] = {
            TokenType.INT: ["STATEMENT", "STATELIST_PRIME"],
            TokenType.FLOAT: ["STATEMENT", "STATELIST_PRIME"],
            TokenType.STRING: ["STATEMENT", "STATELIST_PRIME"],
            TokenType.IDENT: ["STATEMENT", "STATELIST_PRIME"],
            TokenType.PRINT: ["STATEMENT", "STATELIST_PRIME"],
            TokenType.READ: ["STATEMENT", "STATELIST_PRIME"],
            TokenType.RETURN: ["STATEMENT", "STATELIST_PRIME"],
            TokenType.IF: ["STATEMENT", "STATELIST_PRIME"],
            TokenType.FOR: ["STATEMENT", "STATELIST_PRIME"],
            TokenType.LBRACE: ["STATEMENT", "STATELIST_PRIME"],
            TokenType.BREAK: ["STATEMENT", "STATELIST_PRIME"],
            TokenType.SEMICOLON: ["STATEMENT", "STATELIST_PRIME"],
            TokenType.RBRACE: [],
            TokenType.DEF: [],
            TokenType.EOF: [],
        }
        
        # STATEMENT → VARDECL; | ATTRIBSTAT; | FUNCCALL; | PRINTSTAT; | READSTAT; | RETURNSTAT; | IFSTAT | FORSTAT | {STATELIST} | break; | ;
        self.table["STATEMENT"] = {
            TokenType.INT: ["VARDECL", "SEMICOLON"],
            TokenType.FLOAT: ["VARDECL", "SEMICOLON"],
            TokenType.STRING: ["VARDECL", "SEMICOLON"],
            TokenType.IDENT: ["IDENT_STMT", "SEMICOLON"],
            TokenType.PRINT: ["PRINTSTAT", "SEMICOLON"],
            TokenType.READ: ["READSTAT", "SEMICOLON"],
            TokenType.RETURN: ["RETURNSTAT", "SEMICOLON"],
            TokenType.IF: ["IFSTAT"],
            TokenType.FOR: ["FORSTAT"],
            TokenType.LBRACE: ["LBRACE", "STATELIST", "RBRACE"],
            TokenType.BREAK: ["BREAK_STAT"],
            TokenType.SEMICOLON: ["SEMICOLON_STAT"],
        }
        
        # IDENT_STMT → ATTRIBSTAT | FUNCCALL
        self.table["IDENT_STMT"] = {
            TokenType.ASSIGN: ["ATTRIBSTAT"],
            TokenType.LPAREN: ["FUNCCALL"],
        }
        
        # VARDECL → (int|float|string) ident LVALUE_PRIME_DECL
        self.table["VARDECL"] = {
            TokenType.INT: ["INT", "IDENT", "LVALUE_PRIME_DECL"],
            TokenType.FLOAT: ["FLOAT", "IDENT", "LVALUE_PRIME_DECL"],
            TokenType.STRING: ["STRING", "IDENT", "LVALUE_PRIME_DECL"],
        }
        
        # LVALUE_PRIME_DECL → [INTCONSTANT] | ε
        self.table["LVALUE_PRIME_DECL"] = {
            TokenType.LBRACKET: ["LBRACKET", "INTCONSTANT", "RBRACKET"],
            TokenType.SEMICOLON: [],
        }
        
        # ATTRIBSTAT → LVALUE = RHS
        self.table["ATTRIBSTAT"] = {
            TokenType.IDENT: ["LVALUE", "ASSIGN", "RHS"],
        }
        
        # RHS → EXPRESSION | ALLOCEXPRESSION | FUNCCALL
        self.table["RHS"] = {
            TokenType.NEW: ["ALLOCEXPRESSION"],
            TokenType.IDENT: ["RHS_FACTOR"],
            TokenType.INTCONSTANT: ["EXPRESSION"],
            TokenType.FLOATCONSTANT: ["EXPRESSION"],
            TokenType.STRINGCONSTANT: ["EXPRESSION"],
            TokenType.NULL: ["EXPRESSION"],
            TokenType.LPAREN: ["EXPRESSION"],
            TokenType.PLUS: ["EXPRESSION"],
            TokenType.MINUS: ["EXPRESSION"],
        }
        
        # RHS_FACTOR → FUNCCALL | EXPRESSION
        self.table["RHS_FACTOR"] = {
            TokenType.LPAREN: ["FUNCCALL"],
            TokenType.LBRACKET: ["EXPRESSION"],
            TokenType.ASSIGN: ["EXPRESSION"],
            TokenType.SEMICOLON: ["EXPRESSION"],
            TokenType.COMMA: ["EXPRESSION"],
            TokenType.MULT: ["EXPRESSION"],
            TokenType.DIV: ["EXPRESSION"],
            TokenType.MOD: ["EXPRESSION"],
            TokenType.PLUS: ["EXPRESSION"],
            TokenType.MINUS: ["EXPRESSION"],
            TokenType.LT: ["EXPRESSION"],
            TokenType.GT: ["EXPRESSION"],
            TokenType.LE: ["EXPRESSION"],
            TokenType.GE: ["EXPRESSION"],
            TokenType.EQ: ["EXPRESSION"],
            TokenType.NE: ["EXPRESSION"],
            TokenType.RPAREN: ["EXPRESSION"],
        }
        
        # LVALUE → ident LVALUE_PRIME
        self.table["LVALUE"] = {
            TokenType.IDENT: ["IDENT", "LVALUE_PRIME"],
        }
        
        # LVALUE_PRIME → [NUMEXPRESSION] | ε
        self.table["LVALUE_PRIME"] = {
            TokenType.LBRACKET: ["LBRACKET", "NUMEXPRESSION", "RBRACKET"],
            TokenType.ASSIGN: [],
            TokenType.SEMICOLON: [],
            TokenType.COMMA: [],
            TokenType.RPAREN: [],
            TokenType.PLUS: [],
            TokenType.MINUS: [],
            TokenType.MULT: [],
            TokenType.DIV: [],
            TokenType.MOD: [],
            TokenType.LT: [],
            TokenType.GT: [],
            TokenType.LE: [],
            TokenType.GE: [],
            TokenType.EQ: [],
            TokenType.NE: [],
        }
        
        # FUNCCALL → ident ( PARAM_LIST_CALL )
        self.table["FUNCCALL"] = {
            TokenType.IDENT: ["IDENT", "LPAREN", "PARAM_LIST_CALL", "RPAREN"],
        }
        
        # PARAM_LIST_CALL → EXPRESSION PARAM_LIST_CALL_PRIME | ε
        self.table["PARAM_LIST_CALL"] = {
            TokenType.INTCONSTANT: ["EXPRESSION", "PARAM_LIST_CALL_PRIME"],
            TokenType.FLOATCONSTANT: ["EXPRESSION", "PARAM_LIST_CALL_PRIME"],
            TokenType.STRINGCONSTANT: ["EXPRESSION", "PARAM_LIST_CALL_PRIME"],
            TokenType.NULL: ["EXPRESSION", "PARAM_LIST_CALL_PRIME"],
            TokenType.IDENT: ["EXPRESSION", "PARAM_LIST_CALL_PRIME"],
            TokenType.LPAREN: ["EXPRESSION", "PARAM_LIST_CALL_PRIME"],
            TokenType.PLUS: ["EXPRESSION", "PARAM_LIST_CALL_PRIME"],
            TokenType.MINUS: ["EXPRESSION", "PARAM_LIST_CALL_PRIME"],
            TokenType.RPAREN: [],
        }
        
        # PARAM_LIST_CALL_PRIME → , PARAM_LIST_CALL | ε
        self.table["PARAM_LIST_CALL_PRIME"] = {
            TokenType.COMMA: ["COMMA", "PARAM_LIST_CALL"],
            TokenType.RPAREN: [],
        }
        
        # PRINTSTAT → print EXPRESSION
        self.table["PRINTSTAT"] = {
            TokenType.PRINT: ["PRINT", "EXPRESSION"],
        }
        
        # READSTAT → read LVALUE
        self.table["READSTAT"] = {
            TokenType.READ: ["READ", "LVALUE"],
        }
        
        # RETURNSTAT → return RETURN_PRIME
        self.table["RETURNSTAT"] = {
            TokenType.RETURN: ["RETURN", "RETURN_PRIME"],
        }
        
        # RETURN_PRIME → EXPRESSION | ε
        self.table["RETURN_PRIME"] = {
            TokenType.INTCONSTANT: ["EXPRESSION"],
            TokenType.FLOATCONSTANT: ["EXPRESSION"],
            TokenType.STRINGCONSTANT: ["EXPRESSION"],
            TokenType.NULL: ["EXPRESSION"],
            TokenType.IDENT: ["EXPRESSION"],
            TokenType.LPAREN: ["EXPRESSION"],
            TokenType.PLUS: ["EXPRESSION"],
            TokenType.MINUS: ["EXPRESSION"],
            TokenType.SEMICOLON: [],
        }
        
        # BREAK_STAT → break ;
        self.table["BREAK_STAT"] = {
            TokenType.BREAK: ["BREAK", "SEMICOLON"],
        }
        
        # SEMICOLON_STAT → ;
        self.table["SEMICOLON_STAT"] = {
            TokenType.SEMICOLON: ["SEMICOLON"],
        }
        
        # IFSTAT → if ( EXPRESSION ) STATEMENT IFSTAT_PRIME
        self.table["IFSTAT"] = {
            TokenType.IF: ["IF", "LPAREN", "EXPRESSION", "RPAREN", "STATEMENT", "IFSTAT_PRIME"],
        }
        
        # IFSTAT_PRIME → else STATEMENT | ε
        self.table["IFSTAT_PRIME"] = {
            TokenType.ELSE: ["ELSE", "STATEMENT"],
            TokenType.INT: [],
            TokenType.FLOAT: [],
            TokenType.STRING: [],
            TokenType.IDENT: [],
            TokenType.PRINT: [],
            TokenType.READ: [],
            TokenType.RETURN: [],
            TokenType.IF: [],
            TokenType.FOR: [],
            TokenType.LBRACE: [],
            TokenType.BREAK: [],
            TokenType.SEMICOLON: [],
            TokenType.RBRACE: [],
        }
        
        # FORSTAT → for ( ATTRIBSTAT ; EXPRESSION ; ATTRIBSTAT ) STATEMENT
        self.table["FORSTAT"] = {
            TokenType.FOR: ["FOR", "LPAREN", "ATTRIBSTAT", "SEMICOLON", "EXPRESSION", "SEMICOLON", "ATTRIBSTAT", "RPAREN", "STATEMENT"],
        }
        
        # ALLOCEXPRESSION → new ALLOC_TYPE ( NUMEXPRESSION )
        self.table["ALLOCEXPRESSION"] = {
            TokenType.NEW: ["NEW", "ALLOC_TYPE", "LPAREN", "NUMEXPRESSION", "RPAREN"],
        }
        
        # ALLOC_TYPE → int | float | string
        self.table["ALLOC_TYPE"] = {
            TokenType.INT: ["INT"],
            TokenType.FLOAT: ["FLOAT"],
            TokenType.STRING: ["STRING"],
        }
        
        # EXPRESSION → NUMEXPRESSION EXPRESSION_PRIME
        self.table["EXPRESSION"] = {
            TokenType.INTCONSTANT: ["NUMEXPRESSION", "EXPRESSION_PRIME"],
            TokenType.FLOATCONSTANT: ["NUMEXPRESSION", "EXPRESSION_PRIME"],
            TokenType.STRINGCONSTANT: ["NUMEXPRESSION", "EXPRESSION_PRIME"],
            TokenType.NULL: ["NUMEXPRESSION", "EXPRESSION_PRIME"],
            TokenType.IDENT: ["NUMEXPRESSION", "EXPRESSION_PRIME"],
            TokenType.LPAREN: ["NUMEXPRESSION", "EXPRESSION_PRIME"],
            TokenType.PLUS: ["NUMEXPRESSION", "EXPRESSION_PRIME"],
            TokenType.MINUS: ["NUMEXPRESSION", "EXPRESSION_PRIME"],
        }
        
        # EXPRESSION_PRIME → relop NUMEXPRESSION | ε
        self.table["EXPRESSION_PRIME"] = {
            TokenType.LT: ["LT", "NUMEXPRESSION"],
            TokenType.GT: ["GT", "NUMEXPRESSION"],
            TokenType.LE: ["LE", "NUMEXPRESSION"],
            TokenType.GE: ["GE", "NUMEXPRESSION"],
            TokenType.EQ: ["EQ", "NUMEXPRESSION"],
            TokenType.NE: ["NE", "NUMEXPRESSION"],
            TokenType.RPAREN: [],
            TokenType.SEMICOLON: [],
            TokenType.COMMA: [],
        }
        
        # NUMEXPRESSION → TERM NUMEXPRESSION_PRIME
        self.table["NUMEXPRESSION"] = {
            TokenType.INTCONSTANT: ["TERM", "NUMEXPRESSION_PRIME"],
            TokenType.FLOATCONSTANT: ["TERM", "NUMEXPRESSION_PRIME"],
            TokenType.STRINGCONSTANT: ["TERM", "NUMEXPRESSION_PRIME"],
            TokenType.NULL: ["TERM", "NUMEXPRESSION_PRIME"],
            TokenType.IDENT: ["TERM", "NUMEXPRESSION_PRIME"],
            TokenType.LPAREN: ["TERM", "NUMEXPRESSION_PRIME"],
            TokenType.PLUS: ["TERM", "NUMEXPRESSION_PRIME"],
            TokenType.MINUS: ["TERM", "NUMEXPRESSION_PRIME"],
        }
        
        # NUMEXPRESSION_PRIME → (+|-) TERM NUMEXPRESSION_PRIME | ε
        self.table["NUMEXPRESSION_PRIME"] = {
            TokenType.PLUS: ["PLUS", "TERM", "NUMEXPRESSION_PRIME"],
            TokenType.MINUS: ["MINUS", "TERM", "NUMEXPRESSION_PRIME"],
            TokenType.LT: [],
            TokenType.GT: [],
            TokenType.LE: [],
            TokenType.GE: [],
            TokenType.EQ: [],
            TokenType.NE: [],
            TokenType.RPAREN: [],
            TokenType.SEMICOLON: [],
            TokenType.COMMA: [],
        }
        
        # TERM → UNARYEXPR TERM_PRIME
        self.table["TERM"] = {
            TokenType.INTCONSTANT: ["UNARYEXPR", "TERM_PRIME"],
            TokenType.FLOATCONSTANT: ["UNARYEXPR", "TERM_PRIME"],
            TokenType.STRINGCONSTANT: ["UNARYEXPR", "TERM_PRIME"],
            TokenType.NULL: ["UNARYEXPR", "TERM_PRIME"],
            TokenType.IDENT: ["UNARYEXPR", "TERM_PRIME"],
            TokenType.LPAREN: ["UNARYEXPR", "TERM_PRIME"],
            TokenType.PLUS: ["UNARYEXPR", "TERM_PRIME"],
            TokenType.MINUS: ["UNARYEXPR", "TERM_PRIME"],
        }
        
        # TERM_PRIME → (*|/|%) UNARYEXPR TERM_PRIME | ε
        self.table["TERM_PRIME"] = {
            TokenType.MULT: ["MULT", "UNARYEXPR", "TERM_PRIME"],
            TokenType.DIV: ["DIV", "UNARYEXPR", "TERM_PRIME"],
            TokenType.MOD: ["MOD", "UNARYEXPR", "TERM_PRIME"],
            TokenType.PLUS: [],
            TokenType.MINUS: [],
            TokenType.LT: [],
            TokenType.GT: [],
            TokenType.LE: [],
            TokenType.GE: [],
            TokenType.EQ: [],
            TokenType.NE: [],
            TokenType.RPAREN: [],
            TokenType.SEMICOLON: [],
            TokenType.COMMA: [],
        }
        
        # UNARYEXPR → (+|-) FACTOR | FACTOR
        self.table["UNARYEXPR"] = {
            TokenType.PLUS: ["PLUS", "FACTOR"],
            TokenType.MINUS: ["MINUS", "FACTOR"],
            TokenType.INTCONSTANT: ["FACTOR"],
            TokenType.FLOATCONSTANT: ["FACTOR"],
            TokenType.STRINGCONSTANT: ["FACTOR"],
            TokenType.NULL: ["FACTOR"],
            TokenType.IDENT: ["FACTOR"],
            TokenType.LPAREN: ["FACTOR"],
        }
        
        # FACTOR → INTCONSTANT | FLOATCONSTANT | STRINGCONSTANT | null | LVALUE | FUNCCALL | ( NUMEXPRESSION )
        self.table["FACTOR"] = {
            TokenType.INTCONSTANT: ["INTCONSTANT"],
            TokenType.FLOATCONSTANT: ["FLOATCONSTANT"],
            TokenType.STRINGCONSTANT: ["STRINGCONSTANT"],
            TokenType.NULL: ["NULL"],
            TokenType.IDENT: ["FACTOR_IDENT"],
            TokenType.LPAREN: ["LPAREN", "NUMEXPRESSION", "RPAREN"],
        }
        
        # FACTOR_IDENT → FUNCCALL | LVALUE
        self.table["FACTOR_IDENT"] = {
            TokenType.LPAREN: ["FUNCCALL"],
            TokenType.LBRACKET: ["LVALUE"],
            TokenType.ASSIGN: ["LVALUE"],
            TokenType.SEMICOLON: ["LVALUE"],
            TokenType.COMMA: ["LVALUE"],
            TokenType.MULT: ["LVALUE"],
            TokenType.DIV: ["LVALUE"],
            TokenType.MOD: ["LVALUE"],
            TokenType.PLUS: ["LVALUE"],
            TokenType.MINUS: ["LVALUE"],
            TokenType.LT: ["LVALUE"],
            TokenType.GT: ["LVALUE"],
            TokenType.LE: ["LVALUE"],
            TokenType.GE: ["LVALUE"],
            TokenType.EQ: ["LVALUE"],
            TokenType.NE: ["LVALUE"],
            TokenType.RPAREN: ["LVALUE"],
        }
    
    def get_production(self, non_terminal: str, token_type: TokenType) -> Optional[List[str]]:
        """Obtém a produção para um não-terminal dado um token."""
        if non_terminal in self.table:
            if token_type in self.table[non_terminal]:
                return self.table[non_terminal][token_type]
        return None


class Parser:
    """
    Analisador sintático LL(1) para ConvCC-2026-1.
    Usa tabela de parsing explícita para validação sintática,
    e parser recursivo para construção da AST.
    """
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.errors: List[str] = []
        self.parsing_table = ParsingTable()
    
    # ============================================================
    # Métodos auxiliares
    # ============================================================
    
    def current_token(self) -> Token:
        """Retorna o token atual."""
        if self.pos >= len(self.tokens):
            return self.tokens[-1] if self.tokens else Token(TokenType.EOF)
        return self.tokens[self.pos]
    
    def lookahead(self, k: int = 1) -> Token:
        """Retorna o token k posições à frente."""
        if self.pos + k >= len(self.tokens):
            return self.tokens[-1] if self.tokens else Token(TokenType.EOF)
        return self.tokens[self.pos + k]
    
    def match(self, expected_type: TokenType) -> Token:
        """Consome o token se corresponder ao tipo esperado."""
        token = self.current_token()
        if token.type == expected_type:
            self.pos += 1
            return token
        raise ParseError(f"Esperado {expected_type.name}, encontrado {token.type.name}", token)
    
    def reset(self):
        """Reseta a posição do parser para o início."""
        self.pos = 0
        self.errors = []
    
    # ============================================================
    # Validação sintática (tabular LL(1))
    # ============================================================
    
    def validate(self) -> bool:
        """
        Valida a sintaxe do programa usando a tabela LL(1).
        Retorna True se o programa é sintaticamente correto.
        """
        self.reset()
        try:
            stack: List = [TokenType.EOF, "PROGRAM"]
            
            while stack:
                top = stack[-1]
                
                if isinstance(top, str):
                    current = self.current_token()
                    
                    # Lookahead para não-terminais que precisam
                    if top in ["FACTOR_IDENT", "RHS_FACTOR", "IDENT_STMT"]:
                        current = self.lookahead()
                    
                    production = self.parsing_table.get_production(top, current.type)
                    
                    if production is None:
                        if current.type == TokenType.EOF and top == "PROGRAM":
                            break
                        self.errors.append(f"Produção não encontrada para {top} com token {current.type.name} (linha {current.line}, col {current.column})")
                        return False
                    
                    stack.pop()
                    
                    for symbol in reversed(production):
                        if symbol:
                            if symbol in TERMINAL_MAP:
                                stack.append(TERMINAL_MAP[symbol])
                            else:
                                stack.append(symbol)
                
                else:
                    if top == self.current_token().type:
                        self.pos += 1
                        stack.pop()
                    else:
                        token = self.current_token()
                        self.errors.append(f"Terminal inesperado: esperado {top}, encontrado {token.type.name} (linha {token.line}, col {token.column})")
                        return False
            
            return True
            
        except ParseError as e:
            self.errors.append(str(e))
            return False
    
    # ============================================================
    # Construção da AST (parser recursivo)
    # ============================================================
    
    def parse(self) -> Optional[ASTNode]:
        """
        Primeiro valida a sintaxe, depois constrói a AST.
        Retorna a AST se o programa for válido, None caso contrário.
        """
        if not self.validate():
            return None
        
        self.reset()
        return self.build_ast()
    
    def build_ast(self) -> Optional[ASTNode]:
        """Constrói a AST usando parser recursivo."""
        try:
            return self.program()
        except ParseError as e:
            self.errors.append(str(e))
            return None
    
    # ============================================================
    # Regras da gramática (parser recursivo)
    # ============================================================
    
    def program(self) -> ASTNode:
        """PROGRAM → (STATEMENT | FUNCDEF)*"""
        node = ASTNode("PROGRAM")
        
        while self.current_token().type != TokenType.EOF:
            if self.current_token().type == TokenType.DEF:
                func_def = self.func_def()
                node.add_child(func_def)
            else:
                stmt = self.statement()
                node.add_child(stmt)
        
        return node
    
    def func_def(self) -> ASTNode:
        """FUNCDEF → def ident ( PARAM_LIST ) { STATELIST }"""
        node = ASTNode("FUNCDEF")
        
        self.match(TokenType.DEF)
        ident = self.match(TokenType.IDENT)
        node.add_child(ASTNode("IDENT", ident.value))
        
        self.match(TokenType.LPAREN)
        if self.current_token().type in [TokenType.INT, TokenType.FLOAT, TokenType.STRING]:
            param_list = self.param_list()
            node.add_child(param_list)
        self.match(TokenType.RPAREN)
        
        self.match(TokenType.LBRACE)
        state_list = self.state_list()
        node.add_child(state_list)
        self.match(TokenType.RBRACE)
        
        return node
    
    def param_list(self) -> ASTNode:
        """PARAM_LIST → type ident PARAM_LIST_PRIME"""
        node = ASTNode("PARAM_LIST")
        
        while self.current_token().type in [TokenType.INT, TokenType.FLOAT, TokenType.STRING]:
            type_token = self.current_token()
            self.match(type_token.type)
            type_node = ASTNode(type_token.type.name, type_token.value)
            
            ident = self.match(TokenType.IDENT)
            ident_node = ASTNode("IDENT", ident.value)
            
            param = ASTNode("PARAM")
            param.add_child(type_node)
            param.add_child(ident_node)
            node.add_child(param)
            
            if self.current_token().type == TokenType.COMMA:
                self.match(TokenType.COMMA)
            else:
                break
        
        return node
    
    def state_list(self) -> ASTNode:
        """STATELIST → STATEMENT STATELIST_PRIME"""
        node = ASTNode("STATELIST")
        
        while self.current_token().type not in [TokenType.RBRACE, TokenType.EOF]:
            stmt = self.statement()
            node.add_child(stmt)
        
        return node
    
    def statement(self) -> ASTNode:
        """STATEMENT → VARDECL; | ATTRIBSTAT; | FUNCCALL; | PRINTSTAT; | READSTAT; | RETURNSTAT; | IFSTAT | FORSTAT | {STATELIST} | break; | ;"""
        node = ASTNode("STATEMENT")
        
        token_type = self.current_token().type
        
        if token_type in [TokenType.INT, TokenType.FLOAT, TokenType.STRING]:
            var_decl = self.var_decl()
            node.add_child(var_decl)
            self.match(TokenType.SEMICOLON)
        elif token_type == TokenType.IDENT:
            if self.lookahead().type == TokenType.LPAREN:
                # Chamada de função como statement (ex: imprime_global();)
                func_call = self.func_call()
                node.add_child(func_call)
                self.match(TokenType.SEMICOLON)
            else:
                attrib = self.attrib_stat()
                node.add_child(attrib)
                self.match(TokenType.SEMICOLON)
        elif token_type == TokenType.PRINT:
            print_stat = self.print_stat()
            node.add_child(print_stat)
            self.match(TokenType.SEMICOLON)
        elif token_type == TokenType.READ:
            read_stat = self.read_stat()
            node.add_child(read_stat)
            self.match(TokenType.SEMICOLON)
        elif token_type == TokenType.RETURN:
            return_stat = self.return_stat()
            node.add_child(return_stat)
            self.match(TokenType.SEMICOLON)
        elif token_type == TokenType.IF:
            if_stat = self.if_stat()
            node.add_child(if_stat)
        elif token_type == TokenType.FOR:
            for_stat = self.for_stat()
            node.add_child(for_stat)
        elif token_type == TokenType.LBRACE:
            self.match(TokenType.LBRACE)
            state_list = self.state_list()
            node.add_child(state_list)
            self.match(TokenType.RBRACE)
        elif token_type == TokenType.BREAK:
            self.match(TokenType.BREAK)
            self.match(TokenType.SEMICOLON)
            node.add_child(ASTNode("BREAK"))
        elif token_type == TokenType.SEMICOLON:
            self.match(TokenType.SEMICOLON)
        else:
            raise ParseError(f"Token inesperado no statement: {token_type.name}", self.current_token())
        
        return node
    
    def var_decl(self) -> ASTNode:
        """VARDECL → type ident [ [INTCONSTANT] ]"""
        node = ASTNode("VARDECL")
        
        type_token = self.current_token()
        self.match(type_token.type)
        type_node = ASTNode(type_token.type.name, type_token.value)
        node.add_child(type_node)
        
        ident = self.match(TokenType.IDENT)
        ident_node = ASTNode("IDENT", ident.value)
        node.add_child(ident_node)
        
        if self.current_token().type == TokenType.LBRACKET:
            self.match(TokenType.LBRACKET)
            size = self.match(TokenType.INTCONSTANT)
            node.add_child(ASTNode("SIZE", size.value))
            self.match(TokenType.RBRACKET)
        
        return node
    
    def attrib_stat(self) -> ASTNode:
        """ATTRIBSTAT → LVALUE = (EXPRESSION | ALLOCEXPRESSION | FUNCCALL)"""
        node = ASTNode("ATTRIBSTAT")
        
        lvalue = self.lvalue()
        node.add_child(lvalue)
        
        self.match(TokenType.ASSIGN)
        
        if self.current_token().type == TokenType.NEW:
            alloc = self.alloc_expression()
            node.add_child(alloc)
        elif self.current_token().type == TokenType.IDENT and self.lookahead().type == TokenType.LPAREN:
            func_call = self.func_call()
            node.add_child(func_call)
        else:
            expr = self.expression()
            node.add_child(expr)
        
        return node
    
    def lvalue(self) -> ASTNode:
        """LVALUE → ident [ [NUMEXPRESSION] ]"""
        node = ASTNode("LVALUE")
        
        ident = self.match(TokenType.IDENT)
        node.add_child(ASTNode("IDENT", ident.value))
        
        if self.current_token().type == TokenType.LBRACKET:
            self.match(TokenType.LBRACKET)
            num_expr = self.num_expression()
            node.add_child(num_expr)
            self.match(TokenType.RBRACKET)
        
        return node
    
    def func_call(self) -> ASTNode:
        """FUNCCALL → ident ( PARAM_LIST_CALL )"""
        node = ASTNode("FUNCCALL")
        
        ident = self.match(TokenType.IDENT)
        node.add_child(ASTNode("IDENT", ident.value))
        
        self.match(TokenType.LPAREN)
        if self.current_token().type != TokenType.RPAREN:
            param_list = self.param_list_call()
            node.add_child(param_list)
        self.match(TokenType.RPAREN)
        
        return node
    
    def param_list_call(self) -> ASTNode:
        """PARAM_LIST_CALL → EXPRESSION PARAM_LIST_CALL_PRIME | ε"""
        node = ASTNode("PARAM_LIST_CALL")
        
        if self.current_token().type != TokenType.RPAREN:
            expr = self.expression()
            node.add_child(expr)
            
            while self.current_token().type == TokenType.COMMA:
                self.match(TokenType.COMMA)
                expr = self.expression()
                node.add_child(expr)
        
        return node
    
    def print_stat(self) -> ASTNode:
        """PRINTSTAT → print EXPRESSION"""
        node = ASTNode("PRINTSTAT")
        
        self.match(TokenType.PRINT)
        expr = self.expression()
        node.add_child(expr)
        
        return node
    
    def read_stat(self) -> ASTNode:
        """READSTAT → read LVALUE"""
        node = ASTNode("READSTAT")
        
        self.match(TokenType.READ)
        lvalue = self.lvalue()
        node.add_child(lvalue)
        
        return node
    
    def return_stat(self) -> ASTNode:
        """RETURNSTAT → return [ EXPRESSION ]"""
        node = ASTNode("RETURNSTAT")
        self.match(TokenType.RETURN)
        if self.current_token().type != TokenType.SEMICOLON:
            expr = self.expression()
            node.add_child(expr)
        return node
    
    def if_stat(self) -> ASTNode:
        """IFSTAT → if ( EXPRESSION ) STATEMENT [ else STATEMENT ]"""
        node = ASTNode("IFSTAT")
        
        self.match(TokenType.IF)
        self.match(TokenType.LPAREN)
        expr = self.expression()
        node.add_child(expr)
        self.match(TokenType.RPAREN)
        
        then_stmt = self.statement()
        node.add_child(then_stmt)
        
        if self.current_token().type == TokenType.ELSE:
            self.match(TokenType.ELSE)
            else_stmt = self.statement()
            node.add_child(else_stmt)
        
        return node
    
    def for_stat(self) -> ASTNode:
        """FORSTAT → for ( ATTRIBSTAT ; EXPRESSION ; ATTRIBSTAT ) STATEMENT"""
        node = ASTNode("FORSTAT")
        
        self.match(TokenType.FOR)
        self.match(TokenType.LPAREN)
        
        init = self.attrib_stat()
        node.add_child(init)
        self.match(TokenType.SEMICOLON)
        
        cond = self.expression()
        node.add_child(cond)
        self.match(TokenType.SEMICOLON)
        
        update = self.attrib_stat()
        node.add_child(update)
        self.match(TokenType.RPAREN)
        
        body = self.statement()
        node.add_child(body)
        
        return node
    
    def alloc_expression(self) -> ASTNode:
        """ALLOCEXPRESSION → new type ( NUMEXPRESSION )"""
        node = ASTNode("ALLOCEXPRESSION")
        
        self.match(TokenType.NEW)
        
        type_token = self.current_token()
        self.match(type_token.type)
        node.add_child(ASTNode(type_token.type.name, type_token.value))
        
        self.match(TokenType.LPAREN)
        num_expr = self.num_expression()
        node.add_child(num_expr)
        self.match(TokenType.RPAREN)
        
        return node
    
    def expression(self) -> ASTNode:
        """EXPRESSION → NUMEXPRESSION [ relop NUMEXPRESSION ]"""
        node = ASTNode("EXPRESSION")
        
        left = self.num_expression()
        node.add_child(left)
        
        if self.current_token().type in [TokenType.LT, TokenType.GT, TokenType.LE, TokenType.GE, TokenType.EQ, TokenType.NE]:
            op = self.current_token()
            self.match(op.type)
            node.add_child(ASTNode("RELOP", op.value))
            
            right = self.num_expression()
            node.add_child(right)
        
        return node
    
    def num_expression(self) -> ASTNode:
        """NUMEXPRESSION → TERM { (+|-) TERM }"""
        node = ASTNode("NUMEXPRESSION")
        
        term = self.term()
        node.add_child(term)
        
        while self.current_token().type in [TokenType.PLUS, TokenType.MINUS]:
            op = self.current_token()
            self.match(op.type)
            node.add_child(ASTNode("ADDOP", op.value))
            
            term = self.term()
            node.add_child(term)
        
        return node
    
    def term(self) -> ASTNode:
        """TERM → UNARYEXPR { (*|/|%) UNARYEXPR }"""
        node = ASTNode("TERM")
        
        unary = self.unary_expr()
        node.add_child(unary)
        
        while self.current_token().type in [TokenType.MULT, TokenType.DIV, TokenType.MOD]:
            op = self.current_token()
            self.match(op.type)
            node.add_child(ASTNode("MULOP", op.value))
            
            unary = self.unary_expr()
            node.add_child(unary)
        
        return node
    
    def unary_expr(self) -> ASTNode:
        """UNARYEXPR → [ + | - ] FACTOR"""
        node = ASTNode("UNARYEXPR")
        
        if self.current_token().type in [TokenType.PLUS, TokenType.MINUS]:
            op = self.current_token()
            self.match(op.type)
            node.add_child(ASTNode("UNARYOP", op.value))
        
        factor = self.factor()
        node.add_child(factor)
        
        return node
    
    def factor(self) -> ASTNode:
        """FACTOR → INTCONSTANT | FLOATCONSTANT | STRINGCONSTANT | null | LVALUE | FUNCCALL | ( NUMEXPRESSION )"""
        node = ASTNode("FACTOR")
        
        token_type = self.current_token().type
        
        if token_type == TokenType.INTCONSTANT:
            const = self.match(TokenType.INTCONSTANT)
            node.add_child(ASTNode("INTCONSTANT", const.value))
        elif token_type == TokenType.FLOATCONSTANT:
            const = self.match(TokenType.FLOATCONSTANT)
            node.add_child(ASTNode("FLOATCONSTANT", const.value))
        elif token_type == TokenType.STRINGCONSTANT:
            const = self.match(TokenType.STRINGCONSTANT)
            node.add_child(ASTNode("STRINGCONSTANT", const.value))
        elif token_type == TokenType.NULL:
            self.match(TokenType.NULL)
            node.add_child(ASTNode("NULL"))
        elif token_type == TokenType.IDENT:
            if self.lookahead().type == TokenType.LPAREN:
                func_call = self.func_call()
                node.add_child(func_call)
            else:
                lvalue = self.lvalue()
                node.add_child(lvalue)
        elif token_type == TokenType.LPAREN:
            self.match(TokenType.LPAREN)
            num_expr = self.num_expression()
            node.add_child(num_expr)
            self.match(TokenType.RPAREN)
        else:
            raise ParseError(f"Token inesperado no factor: {token_type.name}", self.current_token())
        
        return node
    
    # ============================================================
    # Impressão de erros e debug
    # ============================================================
    
    def print_errors(self):
        """Imprime os erros de análise sintática."""
        for error in self.errors:
            print(f"Erro sintático: {error}")
    
    def print_parsing_table(self):
        """Imprime a tabela de parsing (para debug)."""
        print("Tabela de Parsing LL(1):")
        for non_terminal, productions in self.parsing_table.table.items():
            print(f"\n{non_terminal}:")
            for token_type, production in productions.items():
                if production:
                    print(f"  {token_type.name}: {production}")
                else:
                    print(f"  {token_type.name}: ε")