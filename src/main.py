#!/usr/bin/env python3
"""
ConvCC-2026-1 Compiler
======================
Compilador modular para a linguagem ConvCC-2026-1.
Orquestra as fases: léxica -> sintática -> semântica -> geração de código.

Grupo: [Arthur Leite Bastos]
Data: 2026-06-30
"""

import sys
import os
from typing import Optional

# Adiciona o diretório src ao path para imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lexer import Lexer
from parser import Parser
from semantic import SemanticAnalyzer
from codegen import IntermediateCodeGenerator


def compile_file(filepath: str) -> bool:
    """
    Compila um arquivo ConvCC-2026-1.
    
    Args:
        filepath: Caminho para o arquivo fonte
        
    Returns:
        True se compilação bem-sucedida, False caso contrário
    """
    # Lê o arquivo fonte
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
    except FileNotFoundError:
        print(f"Erro: Arquivo '{filepath}' não encontrado.")
        return False
    except Exception as e:
        print(f"Erro ao ler arquivo: {e}")
        return False
    
    print(f"Compilando: {filepath}")
    print("=" * 50)
    
    # Fase 1: Análise Léxica
    print("\n[1/4] Análise Léxica...")
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    
    # Verifica erros léxicos
    has_lexical_errors = any(t.type.name == "INVALID" for t in tokens)
    if has_lexical_errors:
        for token in tokens:
            if token.type.name == "INVALID":
                print(f"Erro léxico: Caractere inválido '{token.value}' na linha {token.line}, coluna {token.column}")
        return False
    
    print(f"  Tokens gerados: {len(tokens)}")
    
    # Fase 2: Análise Sintática
    print("\n[2/4] Análise Sintática...")
    parser = Parser(tokens)
    ast = parser.parse()
    
    if parser.errors:
        parser.print_errors()
        return False
    
    print("  Árvore sintática gerada com sucesso")
    
    # Fase 3: Análise Semântica
    print("\n[3/4] Análise Semântica...")
    semantic = SemanticAnalyzer(ast)
    success = semantic.analyze()
    
    if not success:
        semantic.print_errors()
        return False
    
    # Imprime resultados da análise semântica
    semantic.print_symbol_table()
    print("\n  Verificação de tipos: SUCESSO")
    print("  Verificação de escopos: SUCESSO")
    print("  Verificação de break: SUCESSO")
    
    # Fase 4: Geração de Código Intermediário
    print("\n[4/4] Geração de Código Intermediário...")
    codegen = IntermediateCodeGenerator(ast)
    quadruples = codegen.generate()
    
    print(f"  Quadruplas geradas: {len(quadruples)}")
    
    # Imprime resultados
    print("\n" + "=" * 50)
    print("RESULTADO DA COMPILAÇÃO: SUCESSO")
    print("=" * 50)
    
    # Imprime árvores de expressão
    print("\nÁrvores de Expressão (percurso raiz-esquerda-direita):")
    semantic.print_expression_trees()
    
    # Imprime código intermediário
    print("\nCódigo Intermediário:")
    codegen.print_code()
    
    return True


def main():
    """Função principal do compilador."""
    if len(sys.argv) < 2:
        print("Uso: python main.py <arquivo_fonte>")
        print("     python main.py --test (para testar todos os programas em /programs)")
        sys.exit(1)
    
    if sys.argv[1] == "--test":
        # Modo teste: compila todos os arquivos em /programs
        programs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "programs")
        
        if not os.path.exists(programs_dir):
            print(f"Erro: Diretório '{programs_dir}' não encontrado.")
            sys.exit(1)
        
        program_files = [f for f in os.listdir(programs_dir) if f.endswith('.cc') or f.endswith('.txt')]
        
        if not program_files:
            print(f"Nenhum programa de teste encontrado em '{programs_dir}'")
            sys.exit(0)
        
        print(f"Testando {len(program_files)} programa(s)...\n")
        
        for program_file in sorted(program_files):
            filepath = os.path.join(programs_dir, program_file)
            compile_file(filepath)
            print("\n")
    else:
        # Compila o arquivo especificado
        filepath = sys.argv[1]
        success = compile_file(filepath)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()