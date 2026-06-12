"""
Modulo de visualizacao e animacao para o Compilador de Batalha Naval.
Usa ANSI escape codes e time.sleep para criar animacoes no terminal.
"""
import os
import sys
import time
import random

# ============================================================================
# CORES ANSI
# ============================================================================
class Cor:
    RESET     = "\033[0m"
    BOLD      = "\033[1m"
    DIM       = "\033[2m"
    
    PRETO     = "\033[30m"
    VERMELHO  = "\033[31m"
    VERDE     = "\033[32m"
    AMARELO   = "\033[33m"
    AZUL      = "\033[34m"
    MAGENTA   = "\033[35m"
    CIANO     = "\033[36m"
    BRANCO    = "\033[37m"
    
    BG_PRETO    = "\033[40m"
    BG_VERMELHO = "\033[41m"
    BG_VERDE    = "\033[42m"
    BG_AMARELO  = "\033[43m"
    BG_AZUL     = "\033[44m"
    BG_MAGENTA  = "\033[45m"
    BG_CIANO    = "\033[46m"
    BG_BRANCO   = "\033[47m"

# ============================================================================
# FUNCOES DE TERMINAL
# ============================================================================

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

def flush():
    sys.stdout.flush()

def mostrar_cursor():
    sys.stdout.write("\033[?25h")
    flush()

# ============================================================================
# ARTE ASCII
# ============================================================================

TITULO = f"""{Cor.CIANO}{Cor.BOLD}
  ____        __        ____            _   __                  __
 / __ )____ _/ /_____ _/ / /_  ____ _  / | / /___ __   ______ _/ /
/ __  / __ `/ __/ __ `/ / __ \\/ __ `/ /  |/ / __ `/ | / / __ `/ /
/ /_/ / /_/ / /_/ /_/ / / / / / /_/ / / /|  / /_/ /| |/ / /_/ / /
/_____/\\__,_/\\__/\\__,_/_/_/ /_/\\__,_/ /_/ |_/\\__,_/ |___/\\__,_/_/
{Cor.RESET}"""

VITORIA = f"""{Cor.AMARELO}{Cor.BOLD}
 **    ** ** ******** ******* ******* **    **
 **    ** **    **    **   ** **   ** **   ** **
 **    ** **    **    **   ** ******* ** *******
  **  **  **    **    **   ** **  **  ** **   **
   ****   **    **    ******* **   ** ** **   **
{Cor.RESET}"""

# ============================================================================
# FUNCOES DE ANIMACAO BASICAS
# ============================================================================

def animar_titulo():
    limpar_tela()
    for linha in TITULO.split('\n'):
        print(linha)
        time.sleep(0.06)
    print()
    time.sleep(0.5)

def animar_texto(texto, delay=0.03):
    for char in texto:
        sys.stdout.write(char)
        flush()
        time.sleep(delay)
    print()

def animar_posicionamento(jogador, coords):
    print(f"  {Cor.VERDE}+{Cor.RESET} Jogador {Cor.BOLD}{jogador}{Cor.RESET}: ", end="")
    for i, coord in enumerate(coords):
        sys.stdout.write(f"{Cor.VERDE}{coord}{Cor.RESET}")
        flush()
        time.sleep(0.15)
        if i < len(coords) - 1:
            sys.stdout.write("-")
    print(f" {Cor.DIM}(navio posicionado){Cor.RESET}")
    time.sleep(0.3)

def animar_vitoria(jogador):
    print()
    print(VITORIA)
    time.sleep(0.5)
    print(f"    {Cor.AMARELO}{Cor.BOLD}Jogador {jogador} VENCEU a batalha!{Cor.RESET}")
    print()
    for _ in range(5):
        fogos = ""
        for _ in range(50):
            c = random.choice([Cor.AMARELO, Cor.VERMELHO, Cor.VERDE, Cor.CIANO, Cor.MAGENTA])
            s = random.choice(['*', '.', '+', 'o', "'", "^"])
            fogos += f"{c}{s}{Cor.RESET}"
        print(f"    {fogos}")
        time.sleep(0.4)
    print()

# ============================================================================
# RENDERIZACAO DO TABULEIRO - LADO A LADO
# ============================================================================

# Largura fixa de cada tabuleiro (sem cores ANSI): "X|...|...|...|" = 1+10*4 = 41
# Usamos celulas de 3 chars: " X " com separador "|"

def _cel(coord, jogador, tabuleiros, disparos, ocultar, mira_coord=None, destaque_coord=None):
    """Retorna string formatada de 3 chars para uma celula."""
    oponente = 'B' if jogador == 'A' else 'A'
    
    # Mira piscando
    if coord == mira_coord:
        return f"{Cor.BG_AMARELO}{Cor.PRETO} ? {Cor.RESET}"
    
    # Destaque resultado
    if coord == destaque_coord:
        if coord in disparos[oponente]['acertos']:
            return f"{Cor.BG_VERMELHO}{Cor.BRANCO}{Cor.BOLD} X {Cor.RESET}"
        elif coord in disparos[oponente]['erros']:
            return f"{Cor.BG_AZUL}{Cor.BRANCO}{Cor.BOLD} ~ {Cor.RESET}"
    
    # Normal
    if coord in disparos[oponente]['acertos']:
        return f"{Cor.VERMELHO}{Cor.BOLD} X {Cor.RESET}"
    elif coord in disparos[oponente]['erros']:
        return f"{Cor.AZUL} ~ {Cor.RESET}"
    elif not ocultar and coord in tabuleiros[jogador]:
        return f"{Cor.VERDE}{Cor.BOLD} # {Cor.RESET}"
    else:
        return f"{Cor.DIM} . {Cor.RESET}"


def _construir_linha_tabuleiro(letra, jogador, tabuleiros, disparos, ocultar, mira_coord=None, destaque_coord=None):
    """Constroi uma linha do tabuleiro como string."""
    s = f"{Cor.BOLD}{letra}{Cor.RESET}{Cor.DIM}|{Cor.RESET}"
    for col in range(1, 11):
        coord = f"{letra}{col}"
        s += _cel(coord, jogador, tabuleiros, disparos, ocultar, mira_coord, destaque_coord)
        s += f"{Cor.DIM}|{Cor.RESET}"
    return s


def _len_visivel(s):
    """Retorna o comprimento visivel de uma string (sem contar codigos ANSI)."""
    import re
    return len(re.sub(r'\033\[[0-9;]*m', '', s))


def renderizar_lado_a_lado(tabuleiros, disparos, ocultar=True,
                           mira_jogador=None, mira_coord=None,
                           destaque_jogador=None, destaque_coord=None,
                           centro_linhas=None):
    """
    Renderiza os dois tabuleiros lado a lado com espaco central.
    centro_linhas: lista de ate 10 strings para mostrar entre os tabuleiros.
    """
    GAP = "    "  # espaco entre tabuleiro e centro
    CENTRO_W = 16  # largura do painel central
    
    # Se nao tem centro, usa espaco simples
    if centro_linhas is None:
        centro_linhas = []
    
    # Pad centro_linhas para 10 linhas
    while len(centro_linhas) < 10:
        centro_linhas.append("")
    
    # === HEADERS ===
    sep = f"{Cor.DIM}{'=' * 41}{Cor.RESET}"
    centro_pad = " " * (len(GAP) * 2 + CENTRO_W)
    
    print(f"  {sep}{centro_pad}{sep}")
    
    ha = f"{Cor.CIANO}{Cor.BOLD}{'JOGADOR A':^41}{Cor.RESET}"
    hb = f"{Cor.MAGENTA}{Cor.BOLD}{'JOGADOR B':^41}{Cor.RESET}"
    print(f"  {ha}{centro_pad}{hb}")
    
    print(f"  {sep}{centro_pad}{sep}")
    
    # === NUMEROS COLUNAS ===
    nums = f"{Cor.DIM}   1   2   3   4   5   6   7   8   9  10{Cor.RESET}"
    print(f"  {nums}{centro_pad}{nums}")
    
    # === BORDA SUPERIOR ===
    borda = f"{Cor.DIM}  +{'---+' * 10}{Cor.RESET}"
    centro_total = len(GAP) * 2 + CENTRO_W
    print(f"  {borda}{centro_pad}{borda}")
    
    # === LINHAS DO TABULEIRO ===
    for i in range(10):
        letra = chr(ord('A') + i)
        
        # Tabuleiro A
        mira_a = mira_coord if mira_jogador == 'A' else None
        dest_a = destaque_coord if destaque_jogador == 'A' else None
        linha_a = _construir_linha_tabuleiro(letra, 'A', tabuleiros, disparos, ocultar, mira_a, dest_a)
        
        # Tabuleiro B
        mira_b = mira_coord if mira_jogador == 'B' else None
        dest_b = destaque_coord if destaque_jogador == 'B' else None
        linha_b = _construir_linha_tabuleiro(letra, 'B', tabuleiros, disparos, ocultar, mira_b, dest_b)
        
        # Centro (texto da acao)
        ctxt = centro_linhas[i]
        # Padding fixo: GAP + conteudo + espacos ate completar + GAP
        # Nao usamos format porque ANSI codes bagunçam o alinhamento
        vis_len = _len_visivel(ctxt)
        pad_restante = max(0, CENTRO_W - vis_len)
        centro_formatado = f"{GAP}{ctxt}{' ' * pad_restante}{GAP}"
        
        print(f"  {linha_a}{centro_formatado}{linha_b}")
        print(f"  {borda}{centro_pad}{borda}")
    
    # === LEGENDA ===
    print(f"  {Cor.VERDE}#{Cor.RESET}=Navio  {Cor.VERMELHO}X{Cor.RESET}=Acerto  {Cor.AZUL}~{Cor.RESET}=Agua  {Cor.BG_AMARELO}{Cor.PRETO} ? {Cor.RESET}=Mira")
    print()


# ============================================================================
# RENDERIZACAO UNICA (para tabuleiros finais)
# ============================================================================

def renderizar_tabuleiro_unico(jogador, tabuleiros, disparos, ocultar=False, destaque_coord=None):
    """Renderiza um tabuleiro sozinho (para estado final)."""
    cor_j = Cor.CIANO if jogador == 'A' else Cor.MAGENTA
    print(f"  {cor_j}{Cor.BOLD}{'=' * 45}{Cor.RESET}")
    print(f"  {cor_j}{Cor.BOLD}{'TABULEIRO DO JOGADOR ' + jogador:^45}{Cor.RESET}")
    print(f"  {cor_j}{Cor.BOLD}{'=' * 45}{Cor.RESET}")
    print(f"  {Cor.DIM}     1   2   3   4   5   6   7   8   9  10{Cor.RESET}")
    print(f"  {Cor.DIM}  +{'---+' * 10}{Cor.RESET}")
    
    for i in range(10):
        letra = chr(ord('A') + i)
        linha = _construir_linha_tabuleiro(letra, jogador, tabuleiros, disparos, ocultar, destaque_coord=destaque_coord)
        print(f"  {linha}")
        print(f"  {Cor.DIM}  +{'---+' * 10}{Cor.RESET}")
    
    print(f"  {Cor.VERDE}#{Cor.RESET}=Navio  {Cor.VERMELHO}X{Cor.RESET}=Acerto  {Cor.AZUL}~{Cor.RESET}=Agua")
    print()


# Alias
def renderizar_tabuleiro(jogador, tabuleiros, disparos, ocultar=False, destaque_coord=None):
    renderizar_tabuleiro_unico(jogador, tabuleiros, disparos, ocultar, destaque_coord)


# ============================================================================
# ANIMACAO DE DISPARO COMPLETA
# ============================================================================

def animar_disparo_completo(jogador, alvo, tabuleiros, disparos, acertou):
    """
    Animacao completa de disparo com tabuleiros lado a lado:
    1. Mira piscando na celula alvo + caixa central "MIRANDO"
    2. Seta animada no centro indo para o tabuleiro atacado
    3. Impacto (explosao ou splash) no centro
    4. Tabuleiro atualizado com destaque no resultado
    """
    oponente = 'B' if jogador == 'A' else 'A'
    
    # === FASE 1: MIRA PISCANDO ===
    for frame in range(6):
        limpar_tela()
        print(TITULO)
        
        # Caixa central de acao
        centro = [""] * 10
        centro[3] = f"{Cor.AMARELO}+------------+"
        centro[4] = f"| Jogador {jogador}  |"
        centro[5] = f"|  MIRANDO.. |"
        centro[6] = f"| alvo: {alvo:<4} |"
        centro[7] = f"+------------+{Cor.RESET}"
        
        mira = alvo if (frame % 2 == 0) else None
        
        renderizar_lado_a_lado(
            tabuleiros, disparos, ocultar=True,
            mira_jogador=oponente, mira_coord=mira,
            centro_linhas=centro)
        
        flush()
        time.sleep(0.6)
    
    # === FASE 2: SETA ANIMADA ===
    if oponente == 'B':
        # Seta para direita (atacando B)
        setas = [
            f"{Cor.VERMELHO}  ->{Cor.RESET}",
            f"{Cor.VERMELHO}  --->{Cor.RESET}",
            f"{Cor.VERMELHO}  ----->{Cor.RESET}",
            f"{Cor.VERMELHO}  ------->{Cor.RESET}",
        ]
    else:
        # Seta para esquerda (atacando A)
        setas = [
            f"{Cor.VERMELHO}        <-{Cor.RESET}",
            f"{Cor.VERMELHO}      <---{Cor.RESET}",
            f"{Cor.VERMELHO}    <-----{Cor.RESET}",
            f"{Cor.VERMELHO}  <-------{Cor.RESET}",
        ]
    
    for seta in setas:
        limpar_tela()
        print(TITULO)
        
        centro = [""] * 10
        centro[3] = f"{Cor.VERMELHO}{Cor.BOLD}+------------+"
        centro[4] = f"|   FOGO!!   |"
        centro[5] = f"|{seta:^12}|"
        centro[6] = f"|  -> {alvo:<4}   |"
        centro[7] = f"+------------+{Cor.RESET}"
        
        renderizar_lado_a_lado(
            tabuleiros, disparos, ocultar=True,
            mira_jogador=oponente, mira_coord=alvo,
            centro_linhas=centro)
        
        flush()
        time.sleep(0.4)
    
    time.sleep(0.3)
    
    # === FASE 3: IMPACTO ===
    if acertou:
        impactos = [
            ["", "", "",
             f"{Cor.AMARELO}      *{Cor.RESET}", f"{Cor.AMARELO}     ***{Cor.RESET}",
             f"{Cor.AMARELO}      *{Cor.RESET}", "", "", "", ""],
            ["", "", "",
             f"{Cor.VERMELHO}    \\   /{Cor.RESET}", f"{Cor.VERMELHO}   -BUM!-{Cor.RESET}",
             f"{Cor.VERMELHO}    /   \\{Cor.RESET}", "", "", "", ""],
            ["", "", "",
             f"{Cor.VERMELHO}{Cor.BOLD}  \\ \\ | / /{Cor.RESET}", f"{Cor.VERMELHO}{Cor.BOLD}  = BOOM! ={Cor.RESET}",
             f"{Cor.VERMELHO}{Cor.BOLD}  / / | \\ \\{Cor.RESET}",
             f"{Cor.VERMELHO}{Cor.BOLD}   ACERTOU!{Cor.RESET}", "", "", ""],
            ["", "", "",
             f"{Cor.DIM}   . . .{Cor.RESET}", f"{Cor.VERMELHO}{Cor.BOLD}  ACERTOU!{Cor.RESET}",
             f"{Cor.DIM}   . . .{Cor.RESET}",
             f"{Cor.DIM}  Navio {oponente}!{Cor.RESET}", "", "", ""],
        ]
    else:
        impactos = [
            ["", "", "",
             f"{Cor.AZUL}      .{Cor.RESET}", f"{Cor.AZUL}     .:.{Cor.RESET}",
             f"{Cor.AZUL}      .{Cor.RESET}", "", "", "", ""],
            ["", "", "",
             f"{Cor.CIANO}   ~ . ~{Cor.RESET}", f"{Cor.CIANO}  ~ ::: ~{Cor.RESET}",
             f"{Cor.CIANO}   ~ . ~{Cor.RESET}", "", "", "", ""],
            ["", "", "",
             f"{Cor.CIANO}{Cor.BOLD} ~~ ... ~~{Cor.RESET}", f"{Cor.CIANO}{Cor.BOLD}  SPLASH!{Cor.RESET}",
             f"{Cor.CIANO}{Cor.BOLD} ~~ ... ~~{Cor.RESET}",
             f"{Cor.AZUL}    AGUA!{Cor.RESET}", "", "", ""],
            ["", "", "",
             f"{Cor.DIM}  ~~~~~~{Cor.RESET}", f"{Cor.AZUL}{Cor.BOLD}    AGUA!{Cor.RESET}",
             f"{Cor.DIM}  ~~~~~~{Cor.RESET}",
             f"{Cor.DIM} Nada ali.{Cor.RESET}", "", "", ""],
        ]
    
    for imp in impactos:
        limpar_tela()
        print(TITULO)
        renderizar_lado_a_lado(
            tabuleiros, disparos, ocultar=True,
            centro_linhas=imp)
        flush()
        time.sleep(0.6)
    
    time.sleep(1.0)
    
    # === FASE 4: RESULTADO FINAL ===
    limpar_tela()
    print(TITULO)
    if acertou:
        print(f"  {Cor.VERMELHO}{Cor.BOLD}  Jogador {jogador} -> {alvo} = ACERTOU!{Cor.RESET}")
    else:
        print(f"  {Cor.AZUL}  Jogador {jogador} -> {alvo} = AGUA{Cor.RESET}")
    print()
    renderizar_lado_a_lado(
        tabuleiros, disparos, ocultar=True,
        destaque_jogador=oponente, destaque_coord=alvo)
    time.sleep(2.0)


# ============================================================================
# TELAS ESPECIAIS
# ============================================================================

def tela_setup_completo(tabuleiros, disparos):
    """Tela apos setup completo, antes da batalha."""
    limpar_tela()
    print(TITULO)
    time.sleep(0.3)
    animar_texto(f"  {Cor.VERDE}{Cor.BOLD}FASE DE BATALHA INICIADA!{Cor.RESET}", delay=0.04)
    time.sleep(0.3)
    animar_texto(f"  {Cor.DIM}Os navios estao posicionados. Hora de atacar!{Cor.RESET}", delay=0.02)
    print()
    time.sleep(0.5)
    renderizar_lado_a_lado(tabuleiros, disparos, ocultar=True)
    time.sleep(1.5)


def tela_resultado_disparo(tabuleiros, disparos, jogador, coord, acertou):
    """Redesenha a tela apos um disparo (versao sem animacao)."""
    oponente = 'B' if jogador == 'A' else 'A'
    limpar_tela()
    print(TITULO)
    if acertou:
        print(f"  {Cor.VERMELHO}{Cor.BOLD}ULTIMO DISPARO: Jogador {jogador} -> {coord} = ACERTOU!{Cor.RESET}")
    else:
        print(f"  {Cor.AZUL}ULTIMO DISPARO: Jogador {jogador} -> {coord} = AGUA{Cor.RESET}")
    print()
    renderizar_lado_a_lado(tabuleiros, disparos, ocultar=True,
                           destaque_jogador=oponente, destaque_coord=coord)
