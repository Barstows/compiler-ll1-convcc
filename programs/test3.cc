int i;
int soma;
soma = 0;
i = 1;
for (i = 1; i < 5; i = i + 1) {
    soma = soma + i;
    if (i == 3)
        break;
}
print soma;
