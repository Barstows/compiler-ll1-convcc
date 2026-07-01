// Programa 2: Funções, parâmetros e escopos
// Demonstra def, return com expressão, chamadas de função

int global;
global = 1000;

// Função de soma
def soma(int x, int y) {
    int resultado;
    resultado = x + y;
    return resultado;
}

// Função de multiplicação
def mult(int x, int y) {
    int resultado;
    resultado = x * y;
    return resultado;
}

// Função de máximo
def maximo(int x, int y) {
    if (x > y)
        return x;
    else
        return y;
}

// Função de fatorial iterativo
def fatorial(int n) {
    int fat;
    int i;
    fat = 1;
    i = 1;
    for (i = i; i < n; i = i + 1) {
        fat = fat * i;
    }
    return fat;
}

// Função com múltiplos parâmetros
def media(int a, int b, int c) {
    int soma;
    int media_valor;
    soma = a + b + c;
    media_valor = soma / 3;
    return media_valor;
}

// Teste das funções
int a;
int b;
int c;
int r;

a = 10;
b = 20;
c = 30;

r = soma(a, b);
print r;

r = mult(a, b);
print r;

r = maximo(a, b);
print r;

r = fatorial(5);
print r;

r = media(a, b, c);
print r;

// Funções aninhadas com variáveis locais
def externa(int x) {
    int y;
    y = x * 2;
    return y;
}

int z;
z = externa(7);
print z;

// Teste de escopo
int escopo_teste;
escopo_teste = 42;
print escopo_teste;

// Mais chamadas
int v1;
int v2;
int v3;
v1 = soma(1, 2);
v2 = mult(3, 4);
v3 = soma(v1, v2);
print v3;

// Função sem retorno (return vazio)
def imprime_global() {
    print global;
    return;
}

imprime_global();

// Última verificação
int ok;
ok = 1;
print ok;