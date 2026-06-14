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
Executa o programa padrão animado embutido no compilador:
```bash
python batalha_naval.py
```

### Execução de um Programa Externo (--cod)
É possível carregar um programa da linguagem Batalha Naval a partir de um arquivo '.txt'.
```bash
python batalha_naval.py --cod arquivo.txt
```

### Execução sem Animações
Esse modo desativa as animações de terminal.

Para executar o exemplo em modo simplificado:
```bash
python batalha_naval.py --simples
```