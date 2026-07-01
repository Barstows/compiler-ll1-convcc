"""
ConvCC-2026-1 Semantic Analyzer
==============================
Analisador semântico para a linguagem ConvCC-2026-1.
Realiza verificação de tipos, escopos e construção de árvore de expressão.

Grupo: [Arthur Leite Bastos]
Data: 2026-06-30
"""

# Modificações da linguagem ConvCC-2026-1:
# 1. Suporte a declaração de funções com parâmetros e retorno de valores.
# 2. Verificação de nomes de funções vs. variáveis no mesmo escopo.
# 3. Suporte a chamadas de função como statements.

from typing import List, Optional, Dict, Set
from parser import ASTNode, Parser
from tokens import TokenType


class SemanticError(Exception):
    """Exceção para erros semânticos."""
    
    def __init__(self, message: str, line: int = 0, column: int = 0):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"{message} (line {line}, col {column})")


class Symbol:
    """Símbolo na tabela de símbolos com escopo."""
    
    def __init__(self, name: str, symbol_type: str = None, scope: int = 0, is_function: bool = False):
        self.name = name
        self.type = symbol_type  # 'int', 'float', 'string' ou 'function'
        self.scope = scope
        self.is_function = is_function
        self.occurrences: List[tuple] = []  # (linha, coluna)
    
    def add_occurrence(self, line: int, column: int):
        self.occurrences.append((line, column))
    
    def __str__(self) -> str:
        kind = "function" if self.is_function else "variable"
        return f"Symbol({self.name}, type={self.type}, scope={self.scope}, kind={kind})"


class SemanticAnalyzer:
    """
    Analisador semântico para ConvCC-2026-1.
    - Construção de árvore de expressão
    - Verificação de tipos
    - Verificação de escopos
    - Verificação de break em escopo de for
    - Verificação de nomes de funções vs variáveis no mesmo escopo
    """
    
    def __init__(self, ast: ASTNode):
        self.ast = ast
        self.symbol_table: Dict[str, List[Symbol]] = {}  # nome -> lista de símbolos por escopo
        self.current_scope = 0
        self.scope_counter = 0  # Contador global para gerar escopos únicos
        self.errors: List[str] = []
        self.expression_trees: List[ASTNode] = []
        self.for_scope_stack: List[int] = []  # Pilha de escopos de for para validação de break
        self.function_names: Dict[int, List[str]] = {}  # escopo -> lista de nomes de funções
    
    def analyze(self) -> bool:
        """Executa a análise semântica."""
        if self.ast is None:
            return False
        
        try:
            self.visit(self.ast)
            return len(self.errors) == 0
        except SemanticError as e:
            self.errors.append(str(e))
            return False
    
    def visit(self, node: ASTNode) -> Optional[str]:
        """Visita um nó da AST e aplica regras semânticas."""
        if node is None:
            return None
        
        method_name = f"visit_{node.type.lower()}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)
    
    def generic_visit(self, node: ASTNode) -> Optional[str]:
        """Visita genérica para nós sem método específico."""
        for child in node.children:
            self.visit(child)
        return None
    
    def visit_program(self, node: ASTNode):
        """Visita o nó PROGRAM."""
        for child in node.children:
            self.visit(child)
    
    def visit_funcdef(self, node: ASTNode):
        """Visita o nó FUNCDEF - novo escopo único para cada função."""
        old_scope = self.current_scope
        self.scope_counter += 1
        self.current_scope = self.scope_counter  # Escopo único e irrepetível
        
        # Extrai o nome da função e verifica conflitos
        func_name = None
        for child in node.children:
            if child.type == "IDENT":
                func_name = child.value
                break
        
        if func_name:
            # Verifica se o nome da função conflita com variáveis no mesmo escopo
            self.check_function_name_conflict(func_name, old_scope)
            # Registra a função na tabela de símbolos
            self.declare_function(func_name)
        
        # Visita parâmetros e corpo
        for child in node.children:
            if child.type == "PARAM_LIST":
                self.visit_param_list(child)
            elif child.type == "STATELIST":
                self.visit(child)
        
        self.current_scope = old_scope  # Restaura escopo anterior
    
    def check_function_name_conflict(self, name: str, scope: int):
        """Verifica se o nome da função conflita com variáveis já declaradas no escopo."""
        if name in self.symbol_table:
            for symbol in self.symbol_table[name]:
                if symbol.scope == scope and not symbol.is_function:
                    self.errors.append(
                        f"Nome '{name}' já usado como variável no escopo {scope} — "
                        f"não pode ser usado como função no mesmo escopo"
                    )
                    return
    
    def declare_function(self, name: str):
        """Declara uma função na tabela de símbolos."""
        if name not in self.symbol_table:
            self.symbol_table[name] = []
        
        # Verifica se já existe função com mesmo nome no mesmo escopo
        for symbol in self.symbol_table[name]:
            if symbol.scope == self.current_scope and symbol.is_function:
                self.errors.append(f"Função '{name}' já declarada no escopo {self.current_scope}")
                return
        
        symbol = Symbol(name, "function", self.current_scope, is_function=True)
        self.symbol_table[name].append(symbol)
        
        # Registra no mapa de funções
        if self.current_scope not in self.function_names:
            self.function_names[self.current_scope] = []
        self.function_names[self.current_scope].append(name)
    
    def visit_param_list(self, node: ASTNode):
        """Visita PARAM_LIST - declara parâmetros como variáveis no escopo atual."""
        for child in node.children:
            if child.type == "PARAM":
                param_type = None
                param_name = None
                for param_child in child.children:
                    if param_child.type in ["INT", "FLOAT", "STRING"]:
                        param_type = param_child.type.lower()
                    elif param_child.type == "IDENT":
                        param_name = param_child.value
                if param_name and param_type:
                    self.declare_variable(param_name, param_type)
    
    def visit_vardecl(self, node: ASTNode):
        """Visita o nó VARDECL - insere tipo na tabela de símbolos."""
        var_type = None
        var_name = None
        
        for child in node.children:
            if child.type in ["INT", "FLOAT", "STRING"]:
                var_type = child.type.lower()
            elif child.type == "IDENT":
                var_name = child.value
        
        if var_name:
            # Verifica se o nome da variável conflita com função no mesmo escopo
            self.check_variable_name_conflict(var_name)
            self.declare_variable(var_name, var_type)
    
    def check_variable_name_conflict(self, name: str):
        """Verifica se o nome da variável conflita com funções no mesmo escopo."""
        if name in self.symbol_table:
            for symbol in self.symbol_table[name]:
                if symbol.scope == self.current_scope and symbol.is_function:
                    self.errors.append(
                        f"Nome '{name}' já usado como função no escopo {self.current_scope} — "
                        f"não pode ser usado como variável no mesmo escopo"
                    )
                    return
    
    def visit_attribstat(self, node: ASTNode):
        """Visita o nó ATTRIBSTAT - verifica tipos."""
        lvalue_type = None
        expr_type = None
        
        for child in node.children:
            if child.type == "LVALUE":
                lvalue_type = self.visit(child)
            elif child.type in ["EXPRESSION", "ALLOCEXPRESSION", "FUNCCALL"]:
                expr_type = self.visit(child)
        
        if lvalue_type and expr_type and lvalue_type != expr_type:
            self.errors.append(f"Tipo incompatível na atribuição: {lvalue_type} vs {expr_type}")
    
    def visit_lvalue(self, node: ASTNode) -> Optional[str]:
        """Visita o nó LVALUE - retorna tipo da variável."""
        var_name = None
        
        for child in node.children:
            if child.type == "IDENT":
                var_name = child.value
        
        if var_name:
            return self.get_variable_type(var_name)
        return None
    
    def visit_expression(self, node: ASTNode) -> Optional[str]:
        """Visita o nó EXPRESSION - constrói árvore de expressão e verifica tipos."""
        expr_tree = self.build_expression_tree(node)
        self.expression_trees.append(expr_tree)
        return self.check_expression_type(node)
    
    def visit_numexpression(self, node: ASTNode) -> Optional[str]:
        """Visita o nó NUMEXPRESSION."""
        return self.check_expression_type(node)
    
    def visit_term(self, node: ASTNode) -> Optional[str]:
        """Visita o nó TERM."""
        return self.check_expression_type(node)
    
    def visit_unaryexpr(self, node: ASTNode) -> Optional[str]:
        """Visita o nó UNARYEXPR."""
        return self.check_expression_type(node)
    
    def visit_factor(self, node: ASTNode) -> Optional[str]:
        """Visita o nó FACTOR - retorna tipo do fator."""
        for child in node.children:
            if child.type in ["INTCONSTANT", "FLOATCONSTANT", "STRINGCONSTANT"]:
                return child.type.lower().replace("constant", "")
            elif child.type == "NULL":
                return "null"
            elif child.type == "LVALUE":
                return self.visit(child)
            elif child.type == "FUNCCALL":
                return self.visit(child)
            elif child.type == "NUMEXPRESSION":
                return self.visit(child)
        return None
    
    def visit_funccall(self, node: ASTNode) -> Optional[str]:
        """Visita o nó FUNCCALL - retorna tipo assumido da função."""
        return "int"
    
    def visit_forstat(self, node: ASTNode):
        """Visita o nó FORSTAT - empilha escopo de for."""
        self.for_scope_stack.append(self.current_scope)
        for child in node.children:
            self.visit(child)
        self.for_scope_stack.pop()
    
    def visit_break(self, node: ASTNode):
        """Visita o nó BREAK - verifica se está em escopo de for."""
        if not self.for_scope_stack:
            self.errors.append("Comando 'break' fora de escopo de 'for'")
    
    def visit_ifstat(self, node: ASTNode):
        """Visita o nó IFSTAT."""
        for child in node.children:
            self.visit(child)
    
    def visit_returnstat(self, node: ASTNode):
        """Visita o nó RETURNSTAT - pode ter expressão opcional."""
        for child in node.children:
            if child.type == "EXPRESSION":
                self.visit(child)
    
    def build_expression_tree(self, node: ASTNode) -> ASTNode:
        """Constrói árvore de expressão para percurso raiz-esquerda-direita."""
        return node
    
    def check_expression_type(self, node: ASTNode) -> Optional[str]:
        """Verifica se os tipos na expressão são compatíveis."""
        types = self.collect_types(node)
        if not types:
            return None
        if len(set(types)) > 1:
            return self.find_common_type(types)
        return types[0] if types else None
    
    def collect_types(self, node: ASTNode) -> List[str]:
        """Coleta todos os tipos de uma expressão."""
        types = []
        for child in node.children:
            if child.type in ["INTCONSTANT", "FLOATCONSTANT", "STRINGCONSTANT"]:
                types.append(child.type.lower().replace("constant", ""))
            elif child.type == "NULL":
                types.append("null")
            elif child.type in ["LVALUE", "FACTOR"]:
                t = self.collect_types(child)
                types.extend(t)
            else:
                t = self.collect_types(child)
                types.extend(t)
        return types
    
    def find_common_type(self, types: List[str]) -> Optional[str]:
        """Encontra o tipo comum entre operandos."""
        if "float" in types:
            return "float"
        if "int" in types:
            return "int"
        if "string" in types:
            return "string"
        return None
    
    def declare_variable(self, name: str, var_type: str):
        """Declara uma variável no escopo atual."""
        if name not in self.symbol_table:
            self.symbol_table[name] = []
        
        for symbol in self.symbol_table[name]:
            if symbol.scope == self.current_scope:
                self.errors.append(f"Variável '{name}' já declarada no escopo {self.current_scope}")
                return
        
        symbol = Symbol(name, var_type, self.current_scope, is_function=False)
        self.symbol_table[name].append(symbol)
    
    def get_variable_type(self, name: str) -> Optional[str]:
        """Obtém o tipo de uma variável pelo nome (busca em escopos)."""
        if name not in self.symbol_table:
            self.errors.append(f"Variável '{name}' não declarada")
            return None
        
        for scope in range(self.current_scope, -1, -1):
            for symbol in self.symbol_table[name]:
                if symbol.scope == scope:
                    return symbol.type
        
        return None
    
    def print_symbol_table(self):
        """Imprime a tabela de símbolos."""
        print("Tabela de Símbolos (com tipos):")
        for name, symbols in self.symbol_table.items():
            for symbol in symbols:
                print(f"  {symbol}")
    
    def print_expression_trees(self):
        """Imprime as árvores de expressão."""
        print("Árvores de Expressão:")
        for i, tree in enumerate(self.expression_trees):
            print(f"  Expressão {i+1}:")
            self.print_tree(tree, indent=2)
    
    def print_tree(self, node: ASTNode, indent: int = 0):
        """Imprime a árvore de expressão em percurso raiz-esquerda-direita."""
        if node is None:
            return
        print("  " * indent + f"{node.type}" + (f" ({node.value})" if node.value else ""))
        for child in node.children:
            self.print_tree(child, indent + 1)
    
    def print_errors(self):
        """Imprime os erros semânticos."""
        for error in self.errors:
            print(f"Erro semântico: {error}")