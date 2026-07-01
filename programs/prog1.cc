// Programa 1: Cálculos matemáticos e controle de fluxo
// Demonstra declarações, atribuições, if/else, for, break

int a;
int b;
int c;
int i;
int soma;
int produto;
int max;
int min;
int contador;

a = 10;
b = 20;
c = 30;

// Cálculo de soma
soma = a + b + c;
print soma;

// Cálculo de produto
produto = a * b * c;
print produto;

// Encontrar o máximo
max = a;
if (b > max)
    max = b;
if (c > max)
    max = c;
print max;

// Encontrar o mínimo
min = a;
if (b < min)
    min = b;
if (c < min)
    min = c;
print min;

// Contagem com for
contador = 0;
for (i = 1; i < 10; i = i + 1) {
    contador = contador + 1;
    if (i == 5)
        break;
}
print contador;

// Loop aninhado
soma = 0;
for (i = 1; i < 5; i = i + 1) {
    int j;
    for (j = 1; j < 4; j = j + 1) {
        soma = soma + 1;
        if (soma > 8)
            break;
    }
    if (soma > 8)
        break;
}
print soma;

// Cálculo com float
float x;
float y;
float z;
x = 3.14;
y = 2.71;
z = x * y + 1.5;
print z;

// Comparações
if (a == b)
    print a;
else
    print b;

if (a != b)
    print c;

if (a < b)
    if (b < c)
        print a;

// Múltiplas declarações
int d;
int e;
int f;
d = 100;
e = 200;
f = d + e;
print f;

// Expressão complexa
int resultado;
resultado = (a + b) * (c - d) + e / 2;
print resultado;

// Mais atribuições
int g;
int h;
g = 42;
h = g * 2;
print h;

// Verificação final
int tudo_certo;
tudo_certo = 1;
print tudo_certo;