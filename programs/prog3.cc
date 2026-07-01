// Programa 3: Strings, leitura e alocação
// Demonstra string, read, new

string nome;
int idade;
float altura;
int ativo;

// Simulação de leitura (valores hard-coded para teste)
nome = "Joao";
idade = 25;
altura = 1.75;
ativo = 1;

print nome;
print idade;
print altura;

// Verificação com if
if (idade > 18)
    print nome;

if (altura > 1.5)
    print idade;

// Alocação com new
int vetor;
vetor = new int(5);

// Preenchendo "vetor" (simulado)
int i;
i = 0;
for (i = 0; i < 5; i = i + 1) {
    vetor = i;
}
print vetor;

// Trabalhando com strings
string saudacao;
saudacao = "Ola";
print saudacao;

string espaco;
espaco = " ";
print espaco;

// Concatenação simulada via print
print saudacao;
print espaco;
print nome;

// Verificações finais
int resultado;
resultado = 0;

if (ativo == 1)
    resultado = 1;

if (idade > 20)
    resultado = resultado + 1;

if (altura > 1.7)
    resultado = resultado + 1;

print resultado;

// Mais declarações
string cidade;
cidade = "Florianopolis";
print cidade;

int ano;
ano = 2026;
print ano;

// Verificação de tipo string
string teste;
teste = "teste";
print teste;

// Loop com condição e break
int contador;
contador = 0;
for (i = 0; i < 5; i = i + 1) {
    contador = contador + 1;
    if (contador == 3)
        break;
}
print contador;

// Teste adicional com múltiplas strings
string s1;
string s2;
string s3;
s1 = "UM";
s2 = "DOIS";
s3 = "TRES";
print s1;
print s2;
print s3;

// Condicional aninhado com strings
if (idade > 20) {
    if (altura > 1.6) {
        print nome;
        print cidade;
    }
}

// Loop adicional
int j;
int acum;
acum = 0;
j = 0;
for (j = 1; j < 10; j = j + 1) {
    acum = acum + j;
}
print acum;

// Verificação final
int sucesso;
sucesso = 1;
print sucesso;