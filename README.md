# batalha-naval-compiladores
**Trabalho de Compliladores**

Compilador desenvolvido em **Python** utilizando **SLY (Sly Lex Yacc)** para interpretar uma linguagem específica de domínio (DSL) que descreve partidas de Batalha Naval.

## Objetivo

A linguagem permite definir:

- Posicionamento de navios dos jogadores;
- Início da partida;
- Disparos durante a batalha;
- Verificação de acertos e condição de vitória.

O compilador realiza análise léxica, sintática e semântica, executando a partida no terminal.

## Como Executar

### Requisitos
- Python 3.8+
- Biblioteca SLY: `pip install sly`

### Execução do Exemplo
```bash
python batalha_naval.py
```