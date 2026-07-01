"""
ConvCC-2026-1 Intermediate Code Generator
========================================
Gerador de código intermediário para a linguagem ConvCC-2026-1.
Gera código intermediário usando notação tríplice (quadruplas).

Grupo: [Arthur Leite Bastos]
Data: 2026-06-30
"""

# Modificações da linguagem ConvCC-2026-1:
# 1. Geração de código intermediário para definição e chamada de funções
#    (label func_nome, call, param, return).
# 2. Geração de código intermediário para alocação dinâmica (alloc).
# 3. Geração de código intermediário para operadores unários (neg).

from typing import List, Optional, Dict
from parser import ASTNode


class Quadruple:
    """Representa uma quadrupla de código intermediário."""
    
    def __init__(self, op: str, arg1: str = None, arg2: str = None, result: str = None):
        self.op = op
        self.arg1 = arg1
        self.arg2 = arg2
        self.result = result
    
    def __str__(self) -> str:
        return f"({self.op}, {self.arg1}, {self.arg2}, {self.result})"
    
    def __repr__(self) -> str:
        return self.__str__()


class IntermediateCodeGenerator:
    """
    Gerador de código intermediário para ConvCC-2026-1.
    Implementa SDT (Syntax Directed Translation) para geração de código.
    """
    
    def __init__(self, ast: ASTNode):
        self.ast = ast
        self.quadruples: List[Quadruple] = []
        self.temp_counter = 0
        self.label_counter = 0
        self.symbol_table: Dict[str, str] = {}  # nome -> endereço/temp
        self.current_function: Optional[str] = None  # Nome da função atual
        self.function_labels: Dict[str, str] = {}  # nome_da_funcao -> label de entrada
    
    def generate(self) -> List[Quadruple]:
        """Gera o código intermediário a partir da AST."""
        if self.ast is None:
            return []
        
        self.visit(self.ast)
        return self.quadruples
    
    def new_temp(self) -> str:
        """Gera um novo temporário."""
        self.temp_counter += 1
        return f"t{self.temp_counter}"
    
    def new_label(self) -> str:
        """Gera um novo rótulo."""
        self.label_counter += 1
        return f"L{self.label_counter}"
    
    # ============================================================
    # Visitantes
    # ============================================================
    
    def visit(self, node: ASTNode) -> Optional[str]:
        """Visita um nó da AST e gera código."""
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
        """Visita o nó PROGRAM - sequência de declarações e funções."""
        # Gera um salto inicial para pular as funções (entry point)
        main_label = self.new_label()
        self.quadruples.append(Quadruple("goto", None, None, main_label))
        
        # Processa todas as funções primeiro (para gerar seus corpos)
        for child in node.children:
            if child.type == "FUNCDEF":
                self.visit(child)
        
        # Label do entry point (início do programa principal)
        self.quadruples.append(Quadruple("label", main_label, None, None))
        
        # Processa os statements globais
        for child in node.children:
            if child.type != "FUNCDEF":
                self.visit(child)
        
        # Halt no final do programa
        self.quadruples.append(Quadruple("halt", None, None, None))
    
    # ============================================================
    # Funções
    # ============================================================
    
    def visit_funcdef(self, node: ASTNode) -> Optional[str]:
        """Visita o nó FUNCDEF - gera código de função."""
        # Estrutura: IDENT, [PARAM_LIST], STATELIST
        func_name = None
        
        for child in node.children:
            if child.type == "IDENT":
                func_name = child.value
        
        if func_name:
            # Cria label de entrada para a função
            func_label = f"func_{func_name}"
            self.function_labels[func_name] = func_label
            
            # Label de início da função
            self.quadruples.append(Quadruple("label", func_label, None, None))
            
            # Registra a função atual
            old_function = self.current_function
            self.current_function = func_name
            
            # Processa o corpo da função
            for child in node.children:
                if child.type == "STATELIST":
                    self.visit(child)
            
            # Se a função não tem return explícito, adiciona return implícito
            # (verifica se a última quadrupla é um return)
            if self.quadruples and self.quadruples[-1].op != "return":
                self.quadruples.append(Quadruple("return", None, None, None))
            
            # Restaura função anterior
            self.current_function = old_function
        
        return func_name
    
    def visit_returnstat(self, node: ASTNode) -> Optional[str]:
        """Visita o nó RETURNSTAT - gera código de retorno."""
        # Pode ter EXPRESSION opcional
        return_value = None
        
        for child in node.children:
            if child.type == "EXPRESSION":
                return_value = self.visit(child)
        
        if return_value:
            self.quadruples.append(Quadruple("return", return_value, None, None))
        else:
            self.quadruples.append(Quadruple("return", None, None, None))
        
        return return_value
    
    # ============================================================
    # Chamadas de função
    # ============================================================
    
    def visit_funccall(self, node: ASTNode) -> Optional[str]:
        """Visita o nó FUNCCALL - gera código de chamada de função."""
        # Estrutura: IDENT, [PARAM_LIST_CALL]
        func_name = None
        param_list = None
        
        for child in node.children:
            if child.type == "IDENT":
                func_name = child.value
            elif child.type == "PARAM_LIST_CALL":
                param_list = child
        
        if func_name:
            # Gera código para os parâmetros (ordem de avaliação)
            params = []
            if param_list:
                params = self.visit(param_list)
                if params is None:
                    params = []
                elif not isinstance(params, list):
                    params = [params]
            
            # Emite instruções param para cada argumento
            for param in params:
                if param:
                    self.quadruples.append(Quadruple("param", param, None, None))
            
            # Emite a chamada
            temp = self.new_temp()
            self.quadruples.append(Quadruple("call", func_name, str(len(params)), temp))
            
            return temp
        
        return None
    
    def visit_param_list_call(self, node: ASTNode) -> List[str]:
        """Visita PARAM_LIST_CALL - retorna lista de temporários/valores."""
        params = []
        
        for child in node.children:
            if child.type == "EXPRESSION":
                result = self.visit(child)
                if result:
                    params.append(result)
        
        return params
    
    # ============================================================
    # Declarações e atribuições
    # ============================================================
    
    def visit_vardecl(self, node: ASTNode):
        """Visita o nó VARDECL - aloca variável."""
        var_name = None
        
        for child in node.children:
            if child.type == "IDENT":
                var_name = child.value
        
        if var_name:
            self.symbol_table[var_name] = var_name
    
    def visit_attribstat(self, node: ASTNode):
        """Visita o nó ATTRIBSTAT - gera código de atribuição."""
        lvalue = None
        expr_result = None
        
        for child in node.children:
            if child.type == "LVALUE":
                lvalue = self.visit(child)
            elif child.type == "EXPRESSION":
                expr_result = self.visit(child)
            elif child.type == "ALLOCEXPRESSION":
                expr_result = self.visit(child)
            elif child.type == "FUNCCALL":
                expr_result = self.visit(child)
        
        if lvalue and expr_result:
            self.quadruples.append(Quadruple("=", expr_result, None, lvalue))
    
    def visit_lvalue(self, node: ASTNode) -> Optional[str]:
        """Visita o nó LVALUE - retorna endereço da variável."""
        for child in node.children:
            if child.type == "IDENT":
                return child.value
        return None
    
    # ============================================================
    # Expressões
    # ============================================================
    
    def visit_expression(self, node: ASTNode) -> Optional[str]:
        """Visita o nó EXPRESSION - gera código de expressão."""
        left = None
        op = None
        right = None
        
        for child in node.children:
            if child.type == "NUMEXPRESSION":
                if left is None:
                    left = self.visit(child)
                else:
                    right = self.visit(child)
            elif child.type == "RELOP":
                op = child.value
        
        if op and left and right:
            temp = self.new_temp()
            self.quadruples.append(Quadruple(op, left, right, temp))
            return temp
        
        return left
    
    def visit_numexpression(self, node: ASTNode) -> Optional[str]:
        """Visita o nó NUMEXPRESSION - gera código de expressão numérica."""
        left = None
        op = None
        right = None
        
        for child in node.children:
            if child.type == "TERM":
                if left is None:
                    left = self.visit(child)
                else:
                    right = self.visit(child)
            elif child.type == "ADDOP":
                op = child.value
        
        if op and left and right:
            temp = self.new_temp()
            self.quadruples.append(Quadruple(op, left, right, temp))
            return temp
        
        return left
    
    def visit_term(self, node: ASTNode) -> Optional[str]:
        """Visita o nó TERM - gera código de termo."""
        left = None
        op = None
        right = None
        
        for child in node.children:
            if child.type == "UNARYEXPR":
                if left is None:
                    left = self.visit(child)
                else:
                    right = self.visit(child)
            elif child.type == "MULOP":
                op = child.value
        
        if op and left and right:
            temp = self.new_temp()
            self.quadruples.append(Quadruple(op, left, right, temp))
            return temp
        
        return left
    
    def visit_unaryexpr(self, node: ASTNode) -> Optional[str]:
        """Visita o nó UNARYEXPR - gera código de expressão unária."""
        op = None
        operand = None
        
        for child in node.children:
            if child.type == "UNARYOP":
                op = child.value
            elif child.type == "FACTOR":
                operand = self.visit(child)
        
        if op and operand:
            temp = self.new_temp()
            if op == '-':
                self.quadruples.append(Quadruple("neg", operand, None, temp))
            else:
                temp = operand  # + não faz nada
            return temp
        
        return operand
    
    def visit_factor(self, node: ASTNode) -> Optional[str]:
        """Visita o nó FACTOR - retorna valor/operando."""
        for child in node.children:
            if child.type in ["INTCONSTANT", "FLOATCONSTANT", "STRINGCONSTANT"]:
                return child.value
            elif child.type == "NULL":
                return "null"
            elif child.type == "LVALUE":
                return self.visit(child)
            elif child.type == "FUNCCALL":
                return self.visit(child)
            elif child.type == "NUMEXPRESSION":
                return self.visit(child)
        return None
    
    # ============================================================
    # Comandos de E/S
    # ============================================================
    
    def visit_printstat(self, node: ASTNode):
        """Visita o nó PRINTSTAT - gera código de impressão."""
        for child in node.children:
            if child.type == "EXPRESSION":
                value = self.visit(child)
                self.quadruples.append(Quadruple("print", value, None, None))
    
    def visit_readstat(self, node: ASTNode):
        """Visita o nó READSTAT - gera código de leitura."""
        for child in node.children:
            if child.type == "LVALUE":
                lvalue = self.visit(child)
                self.quadruples.append(Quadruple("read", lvalue, None, None))
    
    # ============================================================
    # Controle de fluxo
    # ============================================================
    
    def visit_ifstat(self, node: ASTNode):
        """Visita o nó IFSTAT - gera código de if/else."""
        expr_result = None
        has_else = len(node.children) > 2
        
        for i, child in enumerate(node.children):
            if child.type == "EXPRESSION":
                expr_result = self.visit(child)
            elif child.type == "STATEMENT":
                if i == 1:  # then
                    label_else = self.new_label()
                    label_end = self.new_label()
                    
                    if has_else:
                        self.quadruples.append(Quadruple("ifFalse", expr_result, None, label_else))
                    else:
                        self.quadruples.append(Quadruple("ifFalse", expr_result, None, label_end))
                    
                    self.visit(child)
                    
                    if has_else:
                        self.quadruples.append(Quadruple("goto", None, None, label_end))
                        self.quadruples.append(Quadruple("label", label_else, None, None))
                        # else statement é o terceiro filho
                        self.visit(node.children[2])
                    
                    self.quadruples.append(Quadruple("label", label_end, None, None))
    
    def visit_forstat(self, node: ASTNode):
        """Visita o nó FORSTAT - gera código de for."""
        start_label = self.new_label()
        end_label = self.new_label()
        
        # Inicialização (primeiro ATTRIBSTAT)
        if node.children and node.children[0].type == "ATTRIBSTAT":
            self.visit(node.children[0])
        
        # Label de início
        self.quadruples.append(Quadruple("label", start_label, None, None))
        
        # Condição (EXPRESSION)
        if len(node.children) > 1 and node.children[1].type == "EXPRESSION":
            cond = self.visit(node.children[1])
            self.quadruples.append(Quadruple("ifFalse", cond, None, end_label))
        
        # Corpo (STATEMENT)
        if len(node.children) > 3 and node.children[3].type == "STATEMENT":
            self.visit(node.children[3])
        
        # Atualização (segundo ATTRIBSTAT)
        if len(node.children) > 2 and node.children[2].type == "ATTRIBSTAT":
            self.visit(node.children[2])
        
        # Goto início
        self.quadruples.append(Quadruple("goto", None, None, start_label))
        
        # Label de fim
        self.quadruples.append(Quadruple("label", end_label, None, None))
    
    def visit_break(self, node: ASTNode):
        """Visita o nó BREAK - não gera código diretamente (tratado no FORSTAT)."""
        pass
    
    # ============================================================
    # Alocação
    # ============================================================
    
    def visit_allocexpression(self, node: ASTNode) -> Optional[str]:
        """Visita o nó ALLOCEXPRESSION - aloca memória."""
        for child in node.children:
            if child.type == "NUMEXPRESSION":
                size = self.visit(child)
                temp = self.new_temp()
                self.quadruples.append(Quadruple("alloc", size, None, temp))
                return temp
        return None
    
    # ============================================================
    # Impressão
    # ============================================================
    
    def print_code(self):
        """Imprime o código intermediário gerado."""
        print("Código Intermediário:")
        for i, quad in enumerate(self.quadruples):
            print(f"  {i+1}: {quad}")