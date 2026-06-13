# ============================================================================
# COMPILADOR DE BATALHA NAVAL
# Disciplina: Compiladores - 2026/1
# Gerador de Analisador: SLY (Sly Lex Yacc) - Python
# ============================================================================
# Este compilador interpreta uma linguagem de dominio especifico (DSL) para
# o jogo de Batalha Naval. A entrada eh um programa que descreve a fase de
# configuracao (posicionamento de navios) e a fase de batalha (disparos).
# A saida eh a execucao do jogo com visualizacao do tabuleiro no terminal.
# ============================================================================

import time
import sys
from sly import Lexer, Parser
from visual import (
    Cor, limpar_tela, flush, mostrar_cursor,
    animar_titulo, animar_texto, animar_vitoria, animar_posicionamento,
    animar_disparo_completo,
    renderizar_tabuleiro, renderizar_lado_a_lado,
    tela_setup_completo, tela_resultado_disparo
)

# ============================================================================
# 1. ANALISADOR LEXICO (LEXER)
# Gerador: SLY (classe Lexer)
# Define os tokens da linguagem atraves de expressoes regulares.
# ============================================================================

class BatalhaNavalLexer(Lexer):
    """
    Analisador Lexico para a linguagem de Batalha Naval.
    
    Tokens reconhecidos:
    - Palavras reservadas: SHIP, AT, FIRE, START, VERTICAL, HORIZONTAL
    - Identificadores de jogador: PLAYER (A ou B)
    - Coordenadas: COORD (letra seguida de numero, ex: A1, B5, J10)
    - Numeros: NUM (inteiros positivos para tamanho de navios)
    - Delimitadores: COLON (:), SEMICOLON (;), COMMA (,)
    """

    def __init__(self):
        self.erro_lexico = False

    # Conjunto de tokens da linguagem
    tokens = {
        SHIP, AT, FIRE, START,
        VERTICAL, HORIZONTAL,
        PLAYER, COORD, NUM,
        COLON, SEMICOLON, COMMA
    }

    # Caracteres ignorados (espacos e tabulacoes)
    ignore = ' \t'

    # --- Expressoes Regulares para Palavras Reservadas ---
    # MODIFICACAO: Definicao dos tokens de palavras reservadas da linguagem
    START      = r'start'
    SHIP       = r'ship'
    AT         = r'at'
    FIRE       = r'fire'

    # --- Expressoes Regulares para Direcao ---
    # MODIFICACAO: Tokens para direcao do navio (vertical/horizontal)
    VERTICAL   = r'vertical|v(?![a-zA-Z0-9])'
    HORIZONTAL = r'horizontal|h(?![a-zA-Z0-9])'

    # --- Expressao Regular para Coordenada ---
    # MODIFICACAO: Reconhece coordenadas do tabuleiro (A1 a J10)
    COORD      = r'[A-Ja-j](10|[1-9])'

    # --- Expressao Regular para Jogador ---
    # MODIFICACAO: Reconhece identificadores de jogador (A ou B)
    PLAYER     = r'[AB](?=\s*:)'

    # --- Expressao Regular para Numero (com acao semantica) ---
    # MODIFICACAO: Reconhece numeros inteiros e converte para int
    @_(r'[1-9][0-9]*')
    def NUM(self, t):
        t.value = int(t.value)
        return t

    # --- Expressoes Regulares para Delimitadores ---
    COLON     = r':'
    SEMICOLON = r';'
    COMMA     = r','

    # --- Tratamento de Nova Linha ---
    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += len(t.value)

    # --- Tratamento de Erros Lexicos ---
    def error(self, t):
        self.erro_lexico = True
        print(f"{Cor.VERMELHO}[ERRO LEXICO] Caractere ilegal '{t.value[0]}' na linha {self.lineno}{Cor.RESET}")
        self.index += 1


# ============================================================================
# 2. ANALISADOR SINTATICO E SEMANTICO (PARSER)
# Gerador: SLY (classe Parser)
# Define as regras gramaticais (producoes) e as acoes semanticas associadas.
# Implementa Traducao Dirigida pela Sintaxe (TDS).
# ============================================================================
#
# GRAMATICA LIVRE DE CONTEXTO (resumo):
#
#   Game         -> SetupPhase SEMICOLON StartCmd SEMICOLON BattlePhase
#   SetupPhase   -> SetupPhase SEMICOLON SetupTurn 
#                | SetupTurn 
#   BattlePhase  -> BattlePhase SEMICOLON BattleAction 
#                | BattleAction    
#   SetupTurn    -> PLAYER COLON ShipList
#   ShipList     -> ShipList COMMA Ship
#                | Ship
#   Ship         -> SHIP NUM AT COORD Direction
#   Direction    -> VERTICAL | HORIZONTAL
#   StartCmd     -> START 
#   BattleAction -> PLAYER COLON FIRE COORD
#
# ============================================================================

class BatalhaNavalParser(Parser):
    """
    Analisador Sintatico para a linguagem de Batalha Naval.
    Utiliza analise bottom-up (LALR) gerada automaticamente pelo SLY.
    """

    tokens = BatalhaNavalLexer.tokens

    # Desabilitar log de debug do SLY
    debuglevel = 0

    def __init__(self, animado=True):
        """Inicializa o estado do jogo (acoes semanticas de inicializacao)."""
        self.animado = animado
        
        # Estado do jogo
        self.jogo_terminado = False
        self.erro_semantico = False

        # Tabuleiros: dicionario com coordenadas ocupadas por navios
        self.tabuleiros = {
            'A': {},  # {coord: 'N'} - posicoes com navios do jogador A
            'B': {}   # {coord: 'N'} - posicoes com navios do jogador B
        }

        # Registro de disparos realizados
        self.disparos = {
            'A': {'acertos': set(), 'erros': set()},
            'B': {'acertos': set(), 'erros': set()}
        }

        # Tamanho do tabuleiro (10x10)
        self.TAM_TABULEIRO = 10

        # Contadores para estatisticas
        self.total_navios = {'A': 0, 'B': 0}
        self.total_disparos = {'A': 0, 'B': 0}

    # ========================================================================
    # PRODUCOES E ACOES SEMANTICAS
    # ========================================================================

    # --- Producao: Game -> SetupPhase SEMICOLON StartCmd SEMICOLON BattlePhase ---
    @_('SetupPhase SEMICOLON StartCmd SEMICOLON BattlePhase')
    def Game(self, p):
        """Regra inicial: o jogo eh uma sequencia de comandos."""
        if self.erro_semantico:
                print(f"\n{Cor.VERMELHO}Execucao abortada devido a erro(s) semantico(s).{Cor.RESET}")
        else:
                if not self.jogo_terminado:
                    print(f"\n{Cor.AMARELO}{'=' * 50}")
                    print(f"     FIM DO JOGO - SEM VENCEDOR DEFINIDO")
                    print(f"{'=' * 50}{Cor.RESET}")
                self._imprimir_tabuleiros_finais()
        return True

    # --- Producao: SetupPhase -> SetupPhase SEMICOLON SetupTurn ---
    @_('SetupPhase SEMICOLON SetupTurn')
    def SetupPhase(self, p):
        return True
 
    # --- Producao: SetupPhase -> SetupTurn ---
    @_('SetupTurn')
    def SetupPhase(self, p):
        return True

    # --- Producao: BattlePhase -> BattlePhase SEMICOLON BattleAction ---
    @_('BattlePhase SEMICOLON BattleAction')
    def BattlePhase(self, p):
        return True

    # --- Producao: BattlePhase -> BattleAction ---
    @_('BattleAction')
    def BattlePhase(self, p):
        return True

    # --- Producao: SetupTurn -> PLAYER COLON ShipList ---
    # Acao Semantica: Posiciona navios do jogador no tabuleiro
    @_('PLAYER COLON ShipList')
    def SetupTurn(self, p):
        """
        Turno de configuracao de um jogador.
        Acao Semantica: Insere coordenadas dos navios no tabuleiro.
        """
        jogador = p.PLAYER
        navios = p.ShipList

        # Inserir cada coordenada no tabuleiro do jogador
        for coords_navio in navios:
            for coord in coords_navio:
                if coord in self.tabuleiros[jogador]:
                    print(f"{Cor.VERMELHO}[ERRO SEMANTICO] Sobreposicao! Jogador {jogador}: "
                          f"coordenada {coord} ja esta ocupada.{Cor.RESET}")
                    self.erro_semantico = True
                else:
                    self.tabuleiros[jogador][coord] = 'N'

        self.total_navios[jogador] = len(self.tabuleiros[jogador])
        
        if self.animado:
            for coords_navio in navios:
                animar_posicionamento(jogador, coords_navio)
        else:
            print(f"[SETUP] Jogador {jogador} posicionou navios. "
                  f"Total de celulas ocupadas: {self.total_navios[jogador]}")
        return True

    # --- Producao: ShipList -> ShipList COMMA Ship ---
    @_('ShipList COMMA Ship')
    def ShipList(self, p):
        """Lista de navios separados por virgula."""
        return p.ShipList + [p.Ship]

    # --- Producao: ShipList -> Ship ---
    @_('Ship')
    def ShipList(self, p):
        """Lista com um unico navio."""
        return [p.Ship]

    # --- Producao: Ship -> SHIP NUM AT COORD Direction ---
    # Acao Semantica: Calcula coordenadas ocupadas pelo navio
    @_('SHIP NUM AT COORD Direction')
    def Ship(self, p):
        """
        Definicao de um navio.
        Acao Semantica: Calcula todas as coordenadas ocupadas pelo navio.
        Exemplo: ship 3 at B2 vertical -> ['B2', 'C2', 'D2']
        """
        tamanho = p.NUM
        coord_str = p.COORD.upper()
        direcao = p.Direction

        letra_inicial = coord_str[0]
        numero_inicial = int(coord_str[1:])

        # Validacao semantica: tamanho do navio (1 a 5)
        if tamanho < 1 or tamanho > 5:
            print(f"{Cor.VERMELHO}[ERRO SEMANTICO] Tamanho de navio invalido: {tamanho}. "
                  f"Deve ser entre 1 e 5.{Cor.RESET}")
            self.erro_semantico = True
            return []

        # Calcular coordenadas ocupadas pelo navio
        coordenadas = []
        for i in range(tamanho):
            if direcao == 'v':
                nova_letra = chr(ord(letra_inicial) + i)
                if ord(nova_letra) > ord('J'):
                    print(f"{Cor.VERMELHO}[ERRO SEMANTICO] Navio ultrapassa limite vertical "
                          f"do tabuleiro em {nova_letra}{numero_inicial}.{Cor.RESET}")
                    self.erro_semantico = True
                    return []
                coordenadas.append(f"{nova_letra}{numero_inicial}")
            else:
                novo_numero = numero_inicial + i
                if novo_numero > self.TAM_TABULEIRO:
                    print(f"{Cor.VERMELHO}[ERRO SEMANTICO] Navio ultrapassa limite horizontal "
                          f"do tabuleiro em {letra_inicial}{novo_numero}.{Cor.RESET}")
                    self.erro_semantico = True
                    return []
                coordenadas.append(f"{letra_inicial}{novo_numero}")

        return coordenadas

    # --- Producao: Direction -> VERTICAL ---
    @_('VERTICAL')
    def Direction(self, p):
        return 'v'

    # --- Producao: Direction -> HORIZONTAL ---
    @_('HORIZONTAL')
    def Direction(self, p):
        return 'h'

    # --- Producao: StartCmd -> START ---
    # Acao Semantica: Transicao de fase SETUP -> BATALHA
    @_('START')
    def StartCmd(self, p):
        """
        Comando de inicio da batalha.
        Acao Semantica: Transiciona para fase de batalha.
        """
        if self.animado:
            tela_setup_completo(self.tabuleiros, self.disparos)
        else:
            print("\n" + "=" * 50)
            print("       BATALHA NAVAL - FASE DE BATALHA")
            print("=" * 50)
        return True

    # --- Producao: BattleAction -> PLAYER COLON FIRE COORD ---
    # Acao Semantica: Executa disparo e verifica acerto/erro
    @_('PLAYER COLON FIRE COORD')
    def BattleAction(self, p):
        """
        Acao de disparo de um jogador.
        Acoes Semanticas:
        - Verifica se o jogo ja terminou
        - Identifica o oponente
        - Verifica se a coordenada ja foi atacada
        - Determina acerto ou erro
        - Atualiza estado do jogo
        - Verifica condicao de vitoria
        """
        if self.jogo_terminado:
            print(f"{Cor.DIM}[INFO] O jogo ja terminou. Disparos ignorados.{Cor.RESET}")
            return None

        jogador = p.PLAYER
        alvo = p.COORD.upper()
        oponente = 'B' if jogador == 'A' else 'A'

        self.total_disparos[jogador] += 1

        # Validacao semantica: coordenada ja atacada
        if alvo in self.disparos[jogador]['acertos'] or alvo in self.disparos[jogador]['erros']:
            print(f"{Cor.AMARELO}[AVISO] Jogador {jogador} ja disparou em {alvo} anteriormente.{Cor.RESET}")
            return None

        # Verificar acerto ou erro no tabuleiro do oponente
        acertou = alvo in self.tabuleiros[oponente]
        
        if acertou:
            self.disparos[jogador]['acertos'].add(alvo)
            del self.tabuleiros[oponente][alvo]
        else:
            self.disparos[jogador]['erros'].add(alvo)

        # Animacao completa do disparo
        if self.animado:
            animar_disparo_completo(jogador, alvo, self.tabuleiros, self.disparos, acertou)
        else:
            if acertou:
                print(f"  Jogador {jogador} dispara em {alvo}... ACERTOU!")
            else:
                print(f"  Jogador {jogador} dispara em {alvo}... AGUA!")

        # Verificar condicao de vitoria
        if acertou and len(self.tabuleiros[oponente]) == 0:
            self.jogo_terminado = True
            if self.animado:
                time.sleep(0.5)
                animar_vitoria(jogador)
            else:
                print(f"\n  VITORIA! Jogador {jogador} destruiu toda a frota inimiga!")

        return True

    # ========================================================================
    # CODIGO DO USUARIO - FUNCOES AUXILIARES
    # ========================================================================

    def _imprimir_tabuleiros_finais(self):
        """Imprime os tabuleiros finais com todos os navios visiveis."""
        print(f"\n{Cor.BOLD}{'=' * 50}")
        print(f"         ESTADO FINAL DOS TABULEIROS")
        print(f"{'=' * 50}{Cor.RESET}")
        renderizar_tabuleiro('A', self.tabuleiros, self.disparos, ocultar=False)
        renderizar_tabuleiro('B', self.tabuleiros, self.disparos, ocultar=False)

        # Estatisticas finais
        print(f"\n{Cor.BOLD}--- ESTATISTICAS ---{Cor.RESET}")
        for j in ['A', 'B']:
            acertos = len(self.disparos[j]['acertos'])
            erros = len(self.disparos[j]['erros'])
            total = acertos + erros
            taxa = (acertos / total * 100) if total > 0 else 0
            cor = Cor.CIANO if j == 'A' else Cor.MAGENTA
            print(f"  {cor}Jogador {j}{Cor.RESET}: {total} disparos, "
                  f"{Cor.VERDE}{acertos} acertos{Cor.RESET}, "
                  f"{Cor.AZUL}{erros} erros{Cor.RESET} "
                  f"({taxa:.1f}% precisao)")

    def error(self, p):
        """Tratamento de erros sintaticos."""
        if p:
            print(f"{Cor.VERMELHO}[ERRO SINTATICO] Token inesperado '{p.value}' "
                  f"(tipo: {p.type}) na linha {p.lineno}{Cor.RESET}")
        else:
            print(f"{Cor.VERMELHO}[ERRO SINTATICO] Fim inesperado da entrada. "
                  f"Verifique se o programa esta completo.{Cor.RESET}")

        raise SyntaxError("Erro sintatico encontrado")


# ============================================================================
# 3. EXECUCAO PRINCIPAL
# ============================================================================

def executar_programa(codigo, animado=True):
    """
    Executa um programa completo de Batalha Naval.
    """
    lexer = BatalhaNavalLexer()
    parser = BatalhaNavalParser(animado=animado)

    if animado:
        animar_titulo()
        time.sleep(0.5)
        animar_texto(f"  {Cor.DIM}Programa de entrada:{Cor.RESET}", delay=0.01)
        # Mostra o codigo com highlight
        print(f"  {Cor.CIANO}{codigo}{Cor.RESET}")
        print()
        time.sleep(1)
        
        animar_texto(f"  {Cor.AMARELO}--- ANALISE LEXICA ---{Cor.RESET}", delay=0.02)
        tokens_list = list(lexer.tokenize(codigo))
        for tok in tokens_list[:10]:
            print(f"    {Cor.DIM}Token({Cor.VERDE}{tok.type}{Cor.DIM}, '{Cor.BRANCO}{tok.value}{Cor.DIM}'){Cor.RESET}")
            time.sleep(0.05)
        if len(tokens_list) > 10:
            print(f"    {Cor.DIM}... (+{len(tokens_list)-10} tokens){Cor.RESET}")
        print(f"    {Cor.VERDE}Total: {len(tokens_list)} tokens reconhecidos{Cor.RESET}")
        print()
        time.sleep(1)
        
        animar_texto(f"  {Cor.AMARELO}--- ANALISE SINTATICA E SEMANTICA ---{Cor.RESET}", delay=0.02)
        time.sleep(0.5)
    else:
        print("=" * 50)
        print("     COMPILADOR DE BATALHA NAVAL")
        print("=" * 50)
        print(f"\nPrograma de entrada:")
        print(f"  {codigo}")
        print()
        
        print("--- ANALISE LEXICA (Tokens) ---")
        tokens_list = list(lexer.tokenize(codigo))
        for tok in tokens_list:
            print(f"  Token({tok.type}, '{tok.value}', linha={tok.lineno})")
        print(f"  Total: {len(tokens_list)} tokens reconhecidos")
        print()
        print("--- ANALISE SINTATICA E SEMANTICA ---")

    if lexer.erro_lexico:
        print(
            f"{Cor.VERMELHO}"
            "Execucao abortada devido a erro lexico."
            f"{Cor.RESET}"
        )
        return False

    try:
        resultado = parser.parse(lexer.tokenize(codigo))
    except SyntaxError:
        print(
            f"{Cor.VERMELHO}"
            "Execucao abortada devido a erro sintatico."
            f"{Cor.RESET}"
        )
        return False

    return resultado


# ============================================================================
# 4. PROGRAMA PRINCIPAL
# ============================================================================

if __name__ == '__main__':
    import sys as _sys
    
    # Habilitar ANSI no Windows
    if _sys.platform == 'win32':
        import os
        os.system('')  # Habilita ANSI escape sequences no cmd.exe
    
    if len(_sys.argv) > 1 and _sys.argv[1] == '--simples':
        # Modo sem animacao
        programa_exemplo = (
            "A: ship 3 at A1 h, ship 2 at C3 v; "
            "B: ship 3 at D4 v, ship 2 at A8 h;"
            "start; "
            "A: fire D4; B: fire A1; "
            "A: fire E4; B: fire A2; "
            "A: fire J4; B: fire J2; "
            "A: fire F4; B: fire A3; "
            "A: fire A8; B: fire C3; "
            "A: fire A9"
        )
        executar_programa(programa_exemplo, animado=False)
    else:
        # Modo padrao: executa programa completo com animacao
        programa_exemplo = (
            "A: ship 3 at A1 h, ship 2 at C3 v; "
            "B: ship 3 at D4 v, ship 2 at A8 h; "
            "start; "
            "A: fire D4; B: fire A1; "
            "A: fire E4; B: fire A2; "
            "A: fire J4; B: fire J2; "
            "A: fire F4; B: fire A3; "
            "A: fire A8; B: fire C3; "
            "A: fire A9"
        )
        executar_programa(programa_exemplo, animado=True)
