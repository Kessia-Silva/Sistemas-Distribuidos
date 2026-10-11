# Monitoramento Distribuído de Eventos com Relógios Vetoriais

## 1. Descrição

Este projeto implementa um sistema distribuído utilizando Python e Pyro5, com quatro processos independentes (P1, P2, P3 e P4) que geram e compartilham eventos.

O sistema utiliza relógios vetoriais para registrar a ordem causal dos eventos e permitir a identificação de eventos concorrentes. A comunicação entre os processos possui atrasos aleatórios, simulando diferentes tempos de entrega das mensagens.

## 2. Requisitos

- Python 3 instalado.
- Biblioteca Pyro5.
- Cinco terminais disponíveis para executar o servidor e os quatro processos.

## 3. Instalação

Na pasta do projeto, execute:

```bash
python -m pip install Pyro5
```

## 4. Como executar

**Passo 1 — Iniciar o servidor de nomes**

No primeiro terminal, execute:

```bash
python NameServe.py
```

Mantenha esse terminal aberto durante a execução.

**Passo 2 — Iniciar os processos**

Abra quatro terminais adicionais. Em cada um, execute:

```bash
python processo.py
```

Quando solicitado, informe o nome correspondente ao processo:

- Terminal 2: `p1`
- Terminal 3: `p2`
- Terminal 4: `p3`
- Terminal 5: `p4`

Inicie os quatro processos em sequência, de preferência com pouca diferença de tempo entre eles.

**Passo 3 — Acompanhar a execução**

Os processos geram eventos durante aproximadamente 30 segundos. Os registros são exibidos nos terminais e armazenados em arquivos de log na pasta `logs`.

## 5. Estrutura do projeto

```text
projeto/
├── configuracao.py
├── NameServe.py
├── processo.py
├── relogioVetorial.py
├── evento.py
├── logger.py
└── logs/
    ├── p1.log
    ├── p2.log
    ├── p3.log
    └── p4.log
```

A pasta `logs` e os arquivos correspondentes são criados durante a execução.

## 6. Resultados esperados

Durante a execução, os logs registram eventos locais, envios e recebimentos de mensagens, incluindo o relógio vetorial associado a cada evento.

Os relógios são atualizados de acordo com as regras dos relógios vetoriais, permitindo analisar relações causais entre eventos e identificar eventos concorrentes por meio da comparação dos vetores registrados.

## 7. Encerramento

Após o término da execução, os processos encerram suas atividades. Os arquivos de log podem ser consultados para analisar a evolução dos relógios vetoriais e os eventos registrados durante o experimento.