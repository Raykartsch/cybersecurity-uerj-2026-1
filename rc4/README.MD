# Relatório de Implementação do Algoritmo Criptográfico RC4

## 1. Visão Geral do Algoritmo RC4

O RC4 é uma cifra de fluxo (*stream cipher*) de chave simétrica. Diferente das cifras de bloco (que criptografam pedaços fixos de dados por vez), o RC4 gera um fluxo contínuo de bytes pseudoaleatórios (chamado de *keystream*). A criptografia e a descriptografia são realizadas aplicando a operação lógica XOR (OU Exclusivo) bit a bit entre os dados e o *keystream*.

O algoritmo é dividido em duas fases principais:
1. **KSA (Key Scheduling Algorithm):** Responsável por inicializar e permutar o vetor de estado com base na chave fornecida.
2. **PRGA (Pseudo-Random Generation Algorithm):** Responsável por gerar o fluxo contínuo de bytes pseudoaleatórios a partir do vetor de estado.

---

## 2. Estrutura da Classe `RC4`

Abaixo está o detalhamento de cada um dos componentes e métodos da classe principal.

### 2.1. O Construtor (`__init__`)
O método de inicialização é responsável por preparar o terreno antes de qualquer criptografia acontecer.
* **Tratamento da Chave:** O código utiliza a função `isinstance(key, str)` para verificar se a chave fornecida é uma string. Se for, ele converte cada caractere em seu valor numérico ASCII correspondente (usando `ord()`). Caso contrário, assume que a chave já é uma sequência de bytes e a converte para uma lista.
* **Inicialização do Estado:** Cria o array de estado interno `self.S` contendo uma sequência de 0 a 255 (`list(range(256))`).
* **Execução do KSA:** Chama automaticamente o método `self.KSA()` para embaralhar o vetor de estado recém-criado.
* **Preparação do Gerador:** Inicializa a variável `self.keystream` recebendo o gerador produzido pelo `self.PRGA()`. Isso é crucial para manter o estado contínuo do fluxo pseudoaleatório ao longo de várias chamadas de processamento.

### 2.2. Key Scheduling Algorithm (`KSA`)
O método `KSA` realiza a permutação inicial do vetor de estado (*S-Box*).
* Ele itera 256 vezes (de `i = 0` até `255`).
* Em cada iteração, recalcula um índice `j` misturando seu valor anterior, o valor atual de `self.S[i]` e um byte da chave (usando módulo matemático para repetir a chave caso ela seja menor que 256 bytes).
* Por fim, realiza o *swap* (troca) entre os valores das posições `i` e `j` dentro do array `S`.

### 2.3. Pseudo-Random Generation Algorithm (`PRGA`)
O método `PRGA` é o coração gerador do RC4. Ele foi implementado como um *Generator* no Python (usando a palavra-chave `yield` em vez de `return`).
* Possui um loop infinito (`while True:`), o que significa que ele pode fornecer quantos bytes forem necessários, um por vez.
* A cada chamada, ele atualiza os ponteiros `i` e `j`, promove um novo *swap* no array de estado `S` e calcula um índice `t`.
* O byte gerado `K` é o valor armazenado na posição `t` do array de estado. Ao usar `yield K`, a função pausa e entrega o byte, aguardando a próxima solicitação pelo comando `next()`.

### 2.4. Processamento dos Dados (`process`)
O método `process` é a interface final que o usuário utiliza para criptografar ou descriptografar uma mensagem.
* **Tratamento de Entrada:** Assim como na chave, verifica se os dados de entrada (`data`) são do tipo string e os converte para bytes (UTF-8).
* **Operação XOR:** O laço `for byte in data:` itera sobre cada byte da mensagem. Para cada byte da mensagem, ele extrai o próximo byte do fluxo pseudoaleatório (usando `next(self.keystream)`) e aplica a operação XOR (símbolo `^` no Python).
* Como a operação XOR é perfeitamente simétrica, este mesmo método processa tanto a criptografia quanto a descriptografia sem precisar de nenhuma alteração lógica.


## 3. Fluxo de Execução e Testes

### 3.1. Criptografia
Instancia-se a classe com a chave secreta (`rc4_encrypt = RC4(key)`). Em seguida, chama-se o método `process(msg)` passando a mensagem em claro. O resultado é a mensagem cifrada exibida em formato Hexadecimal.

### 3.2. Descriptografia
Cria-se uma **nova instância** da classe com a mesma chave (`rc4_decrypt = RC4(key)`). Isso é fundamental: como o RC4 é uma cifra de fluxo que altera seu estado interno a cada byte processado, é necessário reiniciar a máquina de estado (re-executando o KSA) para descriptografar desde o início.

### 3.3. Validação
A asserção `assert msg == decrypted_msg` garante programaticamente que a mensagem original foi perfeitamente recuperada após o processo duplo de XOR, comprovando que o algoritmo foi implementado sem falhas de estado.