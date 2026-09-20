Instruções
Trabalho Prático – Comunicação e Middleware em Multiplicação de Matrizes

Objetivo
Explorar os conceitos de comunicação síncrona e assíncrona e de middleware para chamadas remotas, aplicando-os em um cenário prático: a implementação de uma versão distribuída da multiplicação de matrizes.

Atividade: Multiplicação de Matrizes
O trabalho será dividido em duas partes complementares:

Parte 1 – Comunicação entre Processos
Implementar um programa em que um processo coordenador distribui tarefas para outros processos trabalhadores.

Cada processo trabalhador deve receber:

Uma linha da primeira matriz,

Uma coluna da segunda matriz.

O processo trabalhador calcula o produto escalar entre a linha e a coluna recebidas e devolve o resultado ao processo coordenador.

O processo coordenador deve reconstruir a matriz resultante com base nas respostas dos trabalhadores.

O trabalho deve contemplar duas implementações distintas:

Comunicação síncrona: coordenador aguarda cada resposta antes de prosseguir.

Comunicação assíncrona: coordenador distribui tarefas a múltiplos trabalhadores e coleta respostas conforme chegam.

Parte 2 – Middleware Simples
Expandir a implementação para usar chamada remota de procedimento (RPC) ou equivalente (ex.: RMI, Pyro).

Cada processo trabalhador deve disponibilizar um método remoto que recebe:

Uma linha da matriz A,

Uma coluna da matriz B.

Retorna o resultado do produto escalar.

O processo coordenador passa a invocar esse método remoto para calcular cada posição da matriz resultante.

Demonstrar a diferença entre o uso de comunicação direta (Parte 1) e via middleware (Parte 2).

Entrega
Códigos-fonte:

Implementação das comunicações síncrona e assíncrona (Parte 1).

Implementação da chamada remota com middleware (Parte 2).

Comentários explicativos no código.

Relatório técnico (máx. 4 páginas), contendo:

Descrição da arquitetura implementada (mestre/escravo).

Como foi feita a comunicação síncrona e assíncrona.

Como foi feito o middleware e as chamadas remotas.

Exemplos de execução com matrizes pequenas (prints das saídas).

Comparação crítica entre as abordagens da Parte 1 e da Parte 2.

Critérios de Avaliação
Comunicação síncrona funcional	15%
Comunicação assíncrona funcional	15%
Middleware / RPC implementado corretamente	25%
Clareza, completude e organização do relatório	25%
Organização, modularidade e legibilidade do código	20%
Recomendações
Testar inicialmente com matrizes pequenas (ex.: 2x2, 3x3) antes de escalar.

Modularizar bem o código para poder reutilizar funções entre as partes.

Comentar o código para facilitar a correção e entendimento.

No relatório, destacar diferenças de esforço de implementação entre comunicação direta e middleware.