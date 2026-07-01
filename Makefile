# ConvCC-2026-1 Compiler Makefile
# Grupo: [Arthur Leite Bastos]
# Data: 2026-06-30

# Configurações
PYTHON = python3
PYTHON_VERSION = $(shell $(PYTHON) --version 2>&1 | head -1)
SRC_DIR = src
PROGRAMS_DIR = programs

# Arquivos fonte
MAIN = $(SRC_DIR)/main.py
LEXER = $(SRC_DIR)/lexer.py
PARSER = $(SRC_DIR)/parser.py
SEMANTIC = $(SRC_DIR)/semantic.py
CODEGEN = $(SRC_DIR)/codegen.py
TOKENS = $(SRC_DIR)/tokens.py

# Programas de teste
PROGRAMS = $(wildcard $(PROGRAMS_DIR)/*.cc) $(wildcard $(PROGRAMS_DIR)/*.txt)

# Regra padrão
.PHONY: all
all: build

# Regra build (compilação)
.PHONY: build
build:
	@echo "Construindo compilador ConvCC-2026-1..."
	@echo "Python: $(PYTHON_VERSION)"
	@$(PYTHON) -m py_compile $(SRC_DIR)/*.py
	@echo "Compilação concluída com sucesso!"

# Regra run (executar o compilador com um arquivo de entrada)
.PHONY: run
run: build
	@if [ -z "$(FILE)" ]; then \
		echo "Uso: make run FILE=<arquivo_fonte>"; \
		exit 1; \
	fi
	@echo "Executando compilador no arquivo: $(FILE)"
	@$(PYTHON) $(MAIN) $(FILE)

# Regra test (executar o compilador para cada programa em /programs)
.PHONY: test
test: build
	@echo "Testando compilador com programas de exemplo..."
	@if [ -d "$(PROGRAMS_DIR)" ]; then \
		for program in $(PROGRAMS); do \
			echo ""; \
			echo "========================================"; \
			$(PYTHON) $(MAIN) "$$program"; \
		done; \
	else \
		echo "Diretório $(PROGRAMS_DIR) não encontrado."; \
	fi

# Regra clean (limpar arquivos gerados)
.PHONY: clean
clean:
	@echo "Limpando arquivos gerados..."
	@find . -name "*.pyc" -delete
	@find . -name "__pycache__" -type d -delete
	@echo "Limpeza concluída!"

# Regra help (ajuda)
.PHONY: help
help:
	@echo "ConvCC-2026-1 Compiler - Makefile"
	@echo ""
	@echo "Comandos disponíveis:"
	@echo "  make build       - Compila o compilador (verifica sintaxe Python)"
	@echo "  make run FILE=X  - Executa o compilador no arquivo X"
	@echo "  make test        - Testa o compilador com todos os programas em /programs"
	@echo "  make clean       - Remove arquivos gerados"
	@echo "  make help        - Mostra esta ajuda"
	@echo ""
	@echo "Exemplo:"
	@echo "  make run FILE=programs/exemplo1.cc"