## SDD e SDT para as Fases de Análise e Síntese

### SDD L-atribuída para EXPA (Expressões Aritméticas)

A gramática EXPA contém as produções que derivam expressões aritméticas:
EXPRESSION, NUMEXPRESSION, TERM, UNARYEXPR, FACTOR, LVALUE.

#### Regras Semânticas (SDD L-atribuída)

| Produção | Regra Semântica |
|----------|-----------------|
| EXPRESSION → NUMEXPRESSION EXPRESSION_PRIME | EXPRESSION.node = EXPRESSION_PRIME.node (se houver relop) ou NUMEXPRESSION.node |
| EXPRESSION → NUMEXPRESSION relop NUMEXPRESSION | EXPRESSION.node = new Node(relop.lexeme, NUMEXPRESSION₁.node, NUMEXPRESSION₂.node) |
| NUMEXPRESSION → TERM NUMEXPRESSION_PRIME | NUMEXPRESSION.node = NUMEXPRESSION_PRIME.syn |
| NUMEXPRESSION_PRIME → + TERM NUMEXPRESSION_PRIME₁ | NUMEXPRESSION_PRIME₁.inh = new Node('+', NUMEXPRESSION_PRIME.inh, TERM.node); NUMEXPRESSION_PRIME.syn = NUMEXPRESSION_PRIME₁.syn |
| NUMEXPRESSION_PRIME → - TERM NUMEXPRESSION_PRIME₁ | NUMEXPRESSION_PRIME₁.inh = new Node('-', NUMEXPRESSION_PRIME.inh, TERM.node); NUMEXPRESSION_PRIME.syn = NUMEXPRESSION_PRIME₁.syn |
| NUMEXPRESSION_PRIME → ε | NUMEXPRESSION_PRIME.syn = NUMEXPRESSION_PRIME.inh |
| TERM → UNARYEXPR TERM_PRIME | TERM_PRIME.inh = UNARYEXPR.node |
| TERM_PRIME → * UNARYEXPR TERM_PRIME₁ | TERM_PRIME₁.inh = new Node('*', TERM_PRIME.inh, UNARYEXPR.node); TERM_PRIME.syn = TERM_PRIME₁.syn |
| TERM_PRIME → / UNARYEXPR TERM_PRIME₁ | TERM_PRIME₁.inh = new Node('/', TERM_PRIME.inh, UNARYEXPR.node); TERM_PRIME.syn = TERM_PRIME₁.syn |
| TERM_PRIME → % UNARYEXPR TERM_PRIME₁ | TERM_PRIME₁.inh = new Node('%', TERM_PRIME.inh, UNARYEXPR.node); TERM_PRIME.syn = TERM_PRIME₁.syn |
| TERM_PRIME → ε | TERM_PRIME.syn = TERM_PRIME.inh |
| UNARYEXPR → + FACTOR | UNARYEXPR.node = FACTOR.node |
| UNARYEXPR → - FACTOR | UNARYEXPR.node = new Node('neg', FACTOR.node, null) |
| UNARYEXPR → FACTOR | UNARYEXPR.node = FACTOR.node |
| FACTOR → INTCONSTANT | FACTOR.node = new Leaf(INTCONSTANT.value) |
| FACTOR → FLOATCONSTANT | FACTOR.node = new Leaf(FLOATCONSTANT.value) |
| FACTOR → LVALUE | FACTOR.node = LVALUE.node |
| FACTOR → ( NUMEXPRESSION ) | FACTOR.node = NUMEXPRESSION.node |
| LVALUE → ident | LVALUE.node = new Leaf(ident.lexeme) |

#### Prova de que a SDD é L-atribuída

Uma SDD é L-atribuída se todos os atributos herdados de um símbolo X dependem
apenas de:
- Atributos herdados do pai de X
- Atributos sintetizados de irmãos à esquerda de X
- Atributos herdados ou sintetizados do próprio X (mas sem formar ciclos)

Na SDD acima:
- `NUMEXPRESSION_PRIME.inh` recebe `TERM.node` (irmão à esquerda) — OK
- `TERM_PRIME.inh` recebe `UNARYEXPR.node` (irmão à esquerda) — OK
- Nenhum atributo herdado depende de irmãos à direita — OK

Portanto, a SDD é L-atribuída. ✅

#### SDT (Tradução Dirigida por Sintaxe) para EXPA

A SDT é implementada no `SemanticAnalyzer` (arquivo `src/semantic.py`) através
dos métodos `visit_expression`, `visit_numexpression`, `visit_term`,
`visit_unaryexpr`, `visit_factor` e `visit_lvalue`. Cada método retorna o tipo
da expressão (como atributo sintetizado) e constrói a árvore de expressão
armazenada em `self.expression_trees`.

---

### SDD L-atribuída para DEC (Declarações de Variáveis)

A gramática DEC contém as produções: VARDECL, LVALUE_PRIME_DECL.

#### Regras Semânticas (SDD L-atribuída)

| Produção | Regra Semântica |
|----------|-----------------|
| VARDECL → int ident LVALUE_PRIME_DECL | ident.type = 'int'; addToSymbolTable(ident.lexeme, 'int') |
| VARDECL → float ident LVALUE_PRIME_DECL | ident.type = 'float'; addToSymbolTable(ident.lexeme, 'float') |
| VARDECL → string ident LVALUE_PRIME_DECL | ident.type = 'string'; addToSymbolTable(ident.lexeme, 'string') |
| LVALUE_PRIME_DECL → [ INTCONSTANT ] | (declaração de array) |
| LVALUE_PRIME_DECL → ε | (declaração de variável simples) |

#### Prova de que a SDD é L-atribuída

A SDD não utiliza atributos herdados — apenas atributos sintetizados
(`ident.type`). Portanto, é trivialmente L-atribuída. ✅

#### SDT para DEC

A SDT é implementada no `SemanticAnalyzer.visit_vardecl()`, que extrai o tipo
da variável do nó `INT`, `FLOAT` ou `STRING` e o insere na tabela de símbolos
via `declare_variable()`.

---

### SDD L-atribuída para ConvCC-2026-1 (Geração de Código Intermediário)

A SDD completa para geração de código intermediário cobre todas as produções
da gramática.

#### Regras Semânticas Principais

| Produção | Regra Semântica (ação) |
|----------|------------------------|
| PROGRAM → (STATEMENT \| FUNCDEF)* | Gera `goto main`; processa funções; gera `label main`; processa statements; gera `halt` |
| FUNCDEF → def ident ( PARAM_LIST ) { STATELIST } | Gera `label func_nome`; processa corpo; gera `return` implícito |
| RETURNSTAT → return EXPRESSION | Gera `return EXPRESSION.val` |
| RETURNSTAT → return | Gera `return` |
| FUNCCALL → ident ( PARAM_LIST_CALL ) | Gera `param argᵢ` para cada argumento; gera `call nome, n, temp` |
| ATTRIBSTAT → LVALUE = EXPRESSION | Gera `= EXPRESSION.val, None, LVALUE.addr` |
| ATTRIBSTAT → LVALUE = FUNCCALL | Gera `= FUNCCALL.temp, None, LVALUE.addr` |
| IFSTAT → if ( EXPRESSION ) STATEMENT | Gera `ifFalse EXPRESSION.val goto L_else`; processa STATEMENT; gera `label L_else` |
| IFSTAT → if ( EXPRESSION ) STATEMENT else STATEMENT | Gera `ifFalse EXPRESSION.val goto L_else`; processa STATEMENT₁; gera `goto L_end`; gera `label L_else`; processa STATEMENT₂; gera `label L_end` |
| FORSTAT → for ( ATTRIBSTAT ; EXPRESSION ; ATTRIBSTAT ) STATEMENT | Gera `label L_start`; processa EXPRESSION; gera `ifFalse ... goto L_end`; processa STATEMENT; processa ATTRIBSTAT₂; gera `goto L_start`; gera `label L_end` |
| PRINTSTAT → print EXPRESSION | Gera `print EXPRESSION.val` |
| READSTAT → read LVALUE | Gera `read LVALUE.addr` |
| ALLOCEXPRESSION → new type ( NUMEXPRESSION ) | Gera `alloc NUMEXPRESSION.val, None, temp` |
| EXPRESSION → NUMEXPRESSION relop NUMEXPRESSION | Gera `relop NUMEXPRESSION₁.val, NUMEXPRESSION₂.val, temp` |
| NUMEXPRESSION → TERM + TERM | Gera `+ TERM₁.val, TERM₂.val, temp` |
| NUMEXPRESSION → TERM - TERM | Gera `- TERM₁.val, TERM₂.val, temp` |
| TERM → UNARYEXPR * UNARYEXPR | Gera `* UNARYEXPR₁.val, UNARYEXPR₂.val, temp` |
| TERM → UNARYEXPR / UNARYEXPR | Gera `/ UNARYEXPR₁.val, UNARYEXPR₂.val, temp` |
| UNARYEXPR → - FACTOR | Gera `neg FACTOR.val, None, temp` |

#### Prova de que a SDD é L-atribuída

A SDD para GCI usa principalmente atributos sintetizados:
- `EXPRESSION.val` (valor/temporário da expressão)
- `LVALUE.addr` (endereço da variável)
- `temp` (novos temporários gerados)

Os atributos herdados são usados apenas para passar o nome da função atual
(`self.current_function`), que vem do pai FUNCDEF. Nenhum atributo herdado
depende de irmãos à direita. Portanto, a SDD é L-atribuída. ✅

#### SDT para ConvCC-2026-1

A SDT completa está implementada no `IntermediateCodeGenerator`
(arquivo `src/codegen.py`). Os métodos `visit_*` correspondem às ações
semânticas de cada produção da gramática. As ações são executadas em
percurso pós-ordem (bottom-up) para expressões e em ordem mista para
comandos de controle de fluxo.

---

## Implementação das SDD/SDT no Código

### EXPA — Árvore de Expressão
- **Arquivo:** `src/semantic.py`
- **Métodos:** `visit_expression()`, `visit_numexpression()`, `visit_term()`, `visit_unaryexpr()`, `visit_factor()`
- **Estrutura:** `self.expression_trees` armazena a raiz de cada árvore
- **Impressão:** `print_expression_trees()` percorre em raiz-esquerda-direita

### DEC — Inserção de Tipos
- **Arquivo:** `src/semantic.py`
- **Métodos:** `visit_vardecl()`, `declare_variable()`
- **Estrutura:** `self.symbol_table` armazena símbolos com tipo e escopo

### GCI — Geração de Código Intermediário
- **Arquivo:** `src/codegen.py`
- **Métodos:** `visit_program()`, `visit_funcdef()`, `visit_returnstat()`, `visit_funccall()`, `visit_attribstat()`, `visit_ifstat()`, `visit_forstat()`, `visit_printstat()`, `visit_readstat()`, `visit_allocexpression()`, `visit_expression()`, `visit_numexpression()`, `visit_term()`, `visit_unaryexpr()`
- **Estrutura:** `self.quadruples` armazena a lista de quádruplas geradas
```