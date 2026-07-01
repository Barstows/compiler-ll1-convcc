# ConvCC-2026-1 Compiler

Compilador modular para a linguagem ConvCC-2026-1, desenvolvido como parte do Exercício-Programa da disciplina INE5426 - Construção de Compiladores.

## Estrutura do Projeto

```
exercicio_programa/
├── src/                    # Arquivos fonte do compilador
│   ├── __init__.py        # Módulo do compilador
│   ├── tokens.py          # Definição dos tokens (terminais)
│   ├── lexer.py           # Analisador léxico
│   ├── parser.py          # Analisador sintático LL(1)
│   ├── semantic.py        # Analisador semântico
│   ├── codegen.py         # Gerador de código intermediário
│   └── main.py            # Arquivo principal
├── programs/              # Programas de exemplo em ConvCC-2026-1
├── docs/                  # Documentação
├── Makefile               # Automatização de compilação e execução
└── README.md              # Este arquivo
```

## Requisitos

- Python 3.11.2
- Sistema Linux/Unix

## Instalação

Não é necessária instalação. O compilador é executado diretamente via Python.

## Uso

### Compilar o compilador

```bash
make build
# ou
python3 -m py_compile src/*.py
```

### Executar o compilador

```bash
# Usando make
make run FILE=programs/exemplo.cc

# Ou diretamente
python3 src/main.py programs/exemplo.cc
```

### Testar todos os programas

```bash
make test
# ou
python3 src/main.py --test
```

## Fases da Compilação

O compilador executa as seguintes fases:

1. **Análise Léxica** (`lexer.py`): Lê o código fonte caracter por caracter e gera tokens. Mantém uma tabela de símbolos com ocorrências de identificadores.

2. **Análise Sintática** (`parser.py`): Usa uma tabela de reconhecimento sintático LL(1) para validar a estrutura do programa e construir a Árvore de Sintaxe Abstrata (AST).

3. **Análise Semântica** (`semantic.py`): Realiza:
   - Construção de árvore de expressão
   - Verificação de tipos em expressões aritméticas
   - Verificação de identificadores por escopo
   - Verificação de `break` em escopo de `for`

4. **Geração de Código Intermediário** (`codegen.py`): Gera código intermediário em notação tríplice (quadruplas).

## Tokens da Linguagem

A linguagem ConvCC-2026-1 possui os seguintes tokens:

### Palavras Reservadas
- `def`, `int`, `float`, `string`, `print`, `read`, `return`, `if`, `else`, `for`, `break`, `null`

### Operadores
- Aritméticos: `+`, `-`, `*`, `/`, `%`
- Relacionais: `<`, `>`, `<=`, `>=`, `==`, `!=`
- Atribuição: `=`

### Símbolos
- `;`, `,`, `(`, `)`, `{`, `}`, `[`, `]`

### Constantes
- `intconstant`, `floatconstant`, `stringconstant`

### Identificadores
- `ident`

## Exemplo de Programa

```cc
def main() {
    int a;
    float b;
    a = 10;
    b = 5.5;
    print a + b;
}
```

## Saída do Compilador

Em caso de sucesso, o compilador produz:
1. Tabela de símbolos com tipos
2. Mensagem de verificação de tipos
3. Mensagem de verificação de escopos
4. Mensagem de verificação de break
5. Código intermediário gerado

Em caso de erro, produz uma mensagem indicando:
- Tipo do erro (léxico, sintático ou semântico)
- Linha e coluna do erro
- Descrição do problema

## Desenvolvimento

### Integrantes do Grupo
- [Nome dos integrantes]

### Licença
Este projeto é acadêmico e segue as normas de integridade acadêmica da UFRGS.