int global;
global = 100;

def soma(int a, int b) {
    int resultado;
    resultado = a + b;
    return resultado;
}

def fatorial(int n) {
    int fat;
    fat = 1;
    for (n = n; n > 1; n = n - 1) {
        fat = fat * n;
    }
    return fat;
}

int x;
int y;
int z;
x = 5;
y = 3;
z = soma(x, y);
print z;
print fatorial(5);
print global;
