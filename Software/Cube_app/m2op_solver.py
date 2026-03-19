import json
import concurrent.futures

def count_moves(solution_str):
    if not solution_str.strip():
        return 0
    return len(solution_str.strip().split())


def invert_moves(sequence: str) -> str:
    inverse = {
        "U": "U'", "U'": "U", "U2": "U2",
        "R": "R'", "R'": "R", "R2": "R2",
        "F": "F'", "F'": "F", "F2": "F2",
        "L": "L'", "L'": "L", "L2": "L2",
        "B": "B'", "B'": "B", "B2": "B2",
        "D": "D'", "D'": "D", "D2": "D2",
    }
    moves = sequence.split()
    inverted = [inverse[m] for m in reversed(moves)]
    return " ".join(inverted)

def converter_movimentos(seq):
    tabela = {
        "U": "A", "U'": "B", "U2": "C",
        "R": "D", "R'": "E", "R2": "F",
        "F": "G", "F'": "H", "F2": "I",
        "D": "J", "D'": "K", "D2": "L",
        "L": "M", "L'": "N", "L2": "O",
        "B": "P", "B'": "Q", "B2": "R"
    }
    return "".join(tabela[m] for m in seq.split() if m in tabela)


def solve_from_file_2(json_path="cube_state.json"):
    try:
        with open(json_path, "r") as f:
            data = json.load(f)

        state = data["cube_string"]

        # ==================================================
        # FUNÇÃO INTERNA QUE EXECUTA O SOLVER
        # ==================================================

        def solver_task():

            #####################
            #   LEITURA EDGES   #
            #####################

            def certas_flips_edges(edges_list, map_edges_list):
                """
                Detecta edges corretas (certas) e edges flipadas (flips).

                Parâmetros:
                - edges_list: lista das 24 letras representando o sticker atualmente presente
                            nas posições de edges extraídas do estado do cubo.
                - map_edges_list: tabela que mapeia cada notação de aresta (por ex. 'UB') para
                                os índices na lista de stickers (par de indices).

                Retorna:
                - certas: lista de strings representando edges "certas" (inclui a permutação
                        do par, p.ex. "UB" e "BU" para marcar ambos os orientações possíveis).
                - flips: lista de strings representando as edges detectadas como flipadas.
                - counter: contador de quantas peças ainda faltam.
                """
                counter = 11          # contador inicial
                flips = []            # lista de edges que precisam ser marcadas como flip
                certas = []           # lista de edges que estão corretas

                # Abaixo há uma longa sequência de testes, cada bloco testa uma aresta específica:
                # - concatena os dois stickers correspondentes (pela tabela map_edges_list)
                # - compara com a forma esperada (ex: "UB" ou "BU")
                # - atualiza counter, certas ou flips conforme o caso.

                # Testa posição UB / BU
                if edges_list[map_edges_list[0][1][0]] + edges_list[map_edges_list[0][1][1]] == "UB":
                    counter += -1
                    certas += ["UB"]
                    certas += ["BU"]
                if edges_list[map_edges_list[0][1][0]] + edges_list[map_edges_list[0][1][1]] == "BU":
                    counter += -1
                    flips += ["UB"]

                # Testa UR / RU
                if edges_list[map_edges_list[2][1][0]] + edges_list[map_edges_list[2][1][1]] == "UR":
                    counter += -1
                    certas += ["UR"]
                    certas += ["RU"]
                if edges_list[map_edges_list[2][1][0]] + edges_list[map_edges_list[2][1][1]] == "RU":
                    counter += -1
                    flips += ["UR"]

                # Testa UF / FU
                if edges_list[map_edges_list[4][1][0]] + edges_list[map_edges_list[4][1][1]] == "UF":
                    counter += -1
                    certas += ["UF"]
                    certas += ["FU"]
                if edges_list[map_edges_list[4][1][0]] + edges_list[map_edges_list[4][1][1]] == "FU":
                    counter += -1
                    flips += ["UF"]

                # Testa UL / LU
                if edges_list[map_edges_list[6][1][0]] + edges_list[map_edges_list[6][1][1]] == "UL":
                    counter += -1
                    certas += ["UL"]
                    certas += ["LU"]
                if edges_list[map_edges_list[6][1][0]] + edges_list[map_edges_list[6][1][1]] == "LU":
                    counter += -1
                    flips += ["UL"]

                # Testa LF / FL
                if edges_list[map_edges_list[8][1][0]] + edges_list[map_edges_list[8][1][1]] == "LF":
                    counter += -1
                    certas += ["LF"]
                    certas += ["FL"]
                if edges_list[map_edges_list[8][1][0]] + edges_list[map_edges_list[8][1][1]] == "FL":
                    counter += -1
                    flips += ["LF"]

                # Testa LD / DL
                if edges_list[map_edges_list[10][1][0]] + edges_list[map_edges_list[10][1][1]] == "LD":
                    counter += -1
                    certas += ["LD"]
                    certas += ["DL"]
                if edges_list[map_edges_list[10][1][0]] + edges_list[map_edges_list[10][1][1]] == "DL":
                    counter += -1
                    flips += ["LD"]

                # Testa LB / BL
                if edges_list[map_edges_list[12][1][0]] + edges_list[map_edges_list[12][1][1]] == "LB":
                    counter += -1
                    certas += ["LB"]
                    certas += ["BL"]
                if edges_list[map_edges_list[12][1][0]] + edges_list[map_edges_list[12][1][1]] == "BL":
                    counter += -1
                    flips += ["LB"]

                # Testa FR / RF
                if edges_list[map_edges_list[14][1][0]] + edges_list[map_edges_list[14][1][1]] == "FR":
                    counter += -1
                    certas += ["FR"]
                    certas += ["RF"]
                if edges_list[map_edges_list[14][1][0]] + edges_list[map_edges_list[14][1][1]] == "RF":
                    counter += -1
                    flips += ["FR"]

                # Testa DF / FD  (note que aqui faz counter +=1 em caso de "DF/FD")
                if edges_list[map_edges_list[16][1][0]] + edges_list[map_edges_list[16][1][1]] == "DF":
                    counter += 1
                    certas += ["DF"]
                    certas += ["FD"]
                if edges_list[map_edges_list[16][1][0]] + edges_list[map_edges_list[16][1][1]] == "FD":
                    counter += 1
                    flips += ["DF"]

                # Testa RB / BR
                if edges_list[map_edges_list[18][1][0]] + edges_list[map_edges_list[18][1][1]] == "RB":
                    counter += -1
                    certas += ["RB"]
                    certas += ["BR"]
                if edges_list[map_edges_list[18][1][0]] + edges_list[map_edges_list[18][1][1]] == "BR":
                    counter += -1
                    flips += ["RB"]

                # Testa RD / DR
                if edges_list[map_edges_list[20][1][0]] + edges_list[map_edges_list[20][1][1]] == "RD":
                    counter += -1
                    certas += ["RD"]
                    certas += ["DR"]
                if edges_list[map_edges_list[20][1][0]] + edges_list[map_edges_list[20][1][1]] == "DR":
                    counter += -1
                    flips += ["RD"]

                # Testa BD / DB
                if edges_list[map_edges_list[22][1][0]] + edges_list[map_edges_list[22][1][1]] == "BD":
                    counter += -1
                    certas += ["BD"]
                    certas += ["DB"]
                if edges_list[map_edges_list[22][1][0]] + edges_list[map_edges_list[22][1][1]] == "DB":
                    counter += -1
                    flips += ["BD"]

                return (certas, flips, counter)


            def test_buffer_1(piece, certas, flips, solved_edges_list):
                """
                Garante que o buffer escolhido represente uma peça errada (ou seja,
                que o buffer não esteja entre as 'certas' já detectadas).

                Parâmetros:
                - piece: string representando a peça proposta como buffer.
                - certas, flips: listas retornadas por certas_flips_edges.
                - solved_edges_list: lista de pares [nome_aresta, letra] que mapeia edges para letras.

                Retorna:
                - piece: string substituta caso a original esteja em 'certas' ou 'flips'.
                A função incrementa um índice internamente (inc) de 0,2,4,... e recupera a
                nova proposta de buffer a partir de solved_edges_list[inc][0].
                """
                ready = False
                inc = -2
                flips_true = [f for pair in flips for f in (pair, pair[::-1])]
                while ready == False:
                    inc += 2
                    # Se a peça atual for considerada "certa" ou "flipada", troca o buffer por outra peça
                    if (piece in certas) or (piece in flips_true):
                        piece = solved_edges_list[inc][0]
                    else:
                        ready = True
                return (piece)


            def adicionar_flips_1(flips, solved_edges_list, hist_edges):
                """
                Quando detectamos edges flipadas (flips), precisamos adicionar as letras
                correspondentes à história. Esta função percorre a lista 'flips' e, para cada
                peça flipada, localiza a letra correspondente em solved_edges_list e a concatena
                a hist_edges.

                Parâmetros:
                - flips: lista de edges flipadas.
                - solved_edges_list: tabela com mapeamento.
                - hist_edges: string/lista acumuladora de história.
                """
                for piece in flips:
                    for j in range(len(solved_edges_list)):
                        if solved_edges_list[j][0] == piece or solved_edges_list[j][0] == piece[::-1]:
                            hist_edges += solved_edges_list[j][1]
                return hist_edges


            # As posições dos stickers de edges no string `state` (indices onde estão os stickers)
            edges = [1, 3, 5, 7, 10, 12, 14, 16, 19, 21, 23, 25, 28, 30, 32, 34, 37, 39, 41, 43, 46, 48, 50, 52]
            edges_list = []
            for i in range(len(edges)):
                edges_list += [state[edges[i]]]

            # Tabela de edges resolvidas: cada par [nome_da_aresta, letra] mapeia a aresta à letra do diagrama.
            solved_edges_list = [
                ['UB', 'A'], ['UR', 'B'], ['UF', 'C'], ['UL', 'D'],
                ['LU', 'E'], ['LF', 'F'], ['LD', 'G'], ['LB', 'H'],
                ['FU', 'I'], ['FR', 'J'], ['FD', 'K'], ['FL', 'L'],
                ['RU', 'M'], ['RB', 'N'], ['RD', 'O'], ['RF', 'P'],
                ['BU', 'Q'], ['BL', 'R'], ['BD', 'S'], ['BR', 'T'],
                ['DF', 'U'], ['DR', 'V'], ['DB', 'W'], ['DL', 'X']
            ]

            # Mapeamento auxiliares: para cada notação de aresta, quais indices na edges_list correspondem
            map_edges_list = [
                ['UB', (0, 20)], ['BU', (20, 0)], ['UR', (2, 4)], ['RU', (4, 2)],
                ['UF', (3, 8)], ['FU', (8, 3)], ['UL', (1, 16)], ['LU', (16, 1)],
                ['LF', (18, 9)], ['FL', (9, 18)], ['LD', (19, 13)], ['DL', (13, 19)],
                ['LB', (17, 22)], ['BL', (22, 17)], ['FR', (10, 5)], ['RF', (5, 10)],
                ['DF', (12, 11)], ['FD', (11, 12)], ['RB', (6, 21)], ['BR', (21, 6)],
                ['RD', (7, 14)], ['DR', (14, 7)], ['BD', (23, 15)], ['DB', (15, 23)]
            ]

            # Executa a detecção de certas e flips nas edges
            certas, flips, counter = certas_flips_edges(edges_list, map_edges_list)  # Encontramos todas as peças certas e flipadas
            ciclos = 0
            continuar = True

            hist_edges = []         # inicialmente nossa historia está vazia
            buffer = "DF"           # buffer inicial escolhido
            buffer = test_buffer_1(buffer, certas, flips, solved_edges_list)  # garante que buffer seja uma peça errada
            certas.append("DF")    # marca DF/FD como tratadas para não serem alvo novamente
            certas.append("FD")
            target = ""             # target atual não determinado ainda

            # Loop principal para construir a história das edges até counter > 0
            while counter > 0:
                # Se o buffer não for a aresta DF/FD, adiciona a letra correspondente na história
                if buffer not in ("DF", "FD"):
                    for j in range(len(solved_edges_list)):  # procura a letra correspondente ao buffer
                        if (solved_edges_list[j][0] == buffer):
                            hist_edges += solved_edges_list[j][1]
                            counter = counter - 1               # decrementa o contador de peças pendentes
                            break

                # Encontra o próximo target dado o buffer (usa a tabela map_edges_list)
                for k in range(len(map_edges_list)):
                    if map_edges_list[k][0] == buffer:
                        target = edges_list[map_edges_list[k][1][0]] + edges_list[map_edges_list[k][1][1]]
                        continuar = True
                        break

                # Enquanto houver um ciclo em andamento (seguir links até retornar a 'certas')
                while continuar and (counter > 0):

                    # Adiciona letra do target à história
                    for j in range(len(solved_edges_list)):
                        if (solved_edges_list[j][0] == target):
                            hist_edges += solved_edges_list[j][1]
                            counter = counter - 1               # decrementa o contador
                            break

                    if counter != 0:
                        # Se ainda restam peças, segue para o próximo link (o próximo lugar onde a peça aponta)
                        for k in range(len(map_edges_list)):
                            if map_edges_list[k][0] == target:
                                certas.append(target)           # marca target como "certa"
                                certas.append(target[::-1])     # e também sua inversa
                                # calcula o próximo target consultando edges_list e map_edges_list
                                target = edges_list[map_edges_list[k][1][0]] + edges_list[map_edges_list[k][1][1]]
                                break

                        # Se o novo target já estava em 'certas', então fechamos o ciclo
                        if target not in certas:
                            continuar = True
                        elif target in certas:
                            continuar = False
                            ciclos = ciclos + 1  # contabiliza um ciclo completo
                            counter = counter + 1  # ajuste de contagem
                            # escolhe um novo buffer que não esteja em 'certas' nem 'flips'
                            buffer = test_buffer_1(target, certas, flips, map_edges_list)


            def remover_strings_especificas_edges(lista):
                strings_para_remover = {"FD", "DF"}
                return [item for item in lista if item not in strings_para_remover]

            flips = remover_strings_especificas_edges(flips)



            # Depois de construir a história, adicionamos os flips detectados
            hist_edges = adicionar_flips_1(flips, solved_edges_list, hist_edges)  # adiciona os flips

            #####################
            #  LEITURA PARIDADE #
            #####################

            # Se a história tiver comprimento ímpar, marca paridade
            if len(hist_edges) % 2 != 0:
                hist_edges.append("PARIDADE")
            else:
                hist_edges.append("NO PARIDADE")


            #####################
            #  LEITURA CORNERS  #
            #####################

            def certas_flips_corners(corners_list, map_corners_list):
                """
                Detecta corners 'certos' e corners rotacionados (em sentido horário ou anti-horário).

                Parâmetros:
                - corners_list: lista de stickers das posições de corners extraídas do state.
                - map_corners_list: tabelas de mapeamento para cada canto (3 indices por canto).

                Retorna:
                - certas: lista de corners já corretos (em qualquer rotação equivalente).
                - flips_ah: lista de corners rotacionados anti-horário.
                - flips_h: lista de corners rotacionados horário.
                - counter: contador inicial de corners a serem resolvidos.
                """
                counter = 7
                flips_h = []
                flips_ah = []
                certas = []

                # O padrão é o mesmo que para edges, mas com 3 letras por canto.
                # Cada bloco testa uma das 8 posições de canto e classifica como "certa",
                # "rotacionada horario" (flips_h) ou "rotacionada anti-horario" (flips_ah).

                # Canto ULB / LBU / BUL
                if corners_list[map_corners_list[0][1][0]] + corners_list[map_corners_list[0][1][1]] + corners_list[map_corners_list[0][1][2]] == "ULB":
                    counter += 1
                    certas += ["ULB"]
                    certas += ["BUL"]
                    certas += ["LBU"]
                if corners_list[map_corners_list[0][1][0]] + corners_list[map_corners_list[0][1][1]] + corners_list[map_corners_list[0][1][2]] == "BUL":
                    counter += 1
                    flips_ah += ["BUL"]
                if corners_list[map_corners_list[0][1][0]] + corners_list[map_corners_list[0][1][1]] + corners_list[map_corners_list[0][1][2]] == "LBU":
                    counter += 1
                    flips_h += ["LBU"]

                # Canto UBR / RUB / BRU
                if corners_list[map_corners_list[3][1][0]] + corners_list[map_corners_list[3][1][1]] + corners_list[map_corners_list[3][1][2]] == "UBR":
                    counter += -1
                    certas += ["UBR"]
                    certas += ["BRU"]
                    certas += ["RUB"]
                if corners_list[map_corners_list[3][1][0]] + corners_list[map_corners_list[3][1][1]] + corners_list[map_corners_list[3][1][2]] == "RUB":
                    counter += -1
                    flips_ah += ["RUB"]
                if corners_list[map_corners_list[3][1][0]] + corners_list[map_corners_list[3][1][1]] + corners_list[map_corners_list[3][1][2]] == "BRU":
                    counter += -1
                    flips_h += ["BRU"]

                # Canto URF / FUR / RFU
                if corners_list[map_corners_list[6][1][0]] + corners_list[map_corners_list[6][1][1]] + corners_list[map_corners_list[6][1][2]] == "URF":
                    counter += -1
                    certas += ["URF"]
                    certas += ["FUR"]
                    certas += ["RFU"]
                if corners_list[map_corners_list[6][1][0]] + corners_list[map_corners_list[6][1][1]] + corners_list[map_corners_list[6][1][2]] == "FUR":
                    counter += -1
                    flips_ah += ["FUR"]
                if corners_list[map_corners_list[6][1][0]] + corners_list[map_corners_list[6][1][1]] + corners_list[map_corners_list[6][1][2]] == "RFU":
                    counter += -1
                    flips_h += ["RFU"]

                # Canto UFL / LUF / FLU
                if corners_list[map_corners_list[9][1][0]] + corners_list[map_corners_list[9][1][1]] + corners_list[map_corners_list[9][1][2]] == "UFL":
                    counter += -1
                    certas += ["UFL"]
                    certas += ["FLU"]
                    certas += ["LUF"]
                if corners_list[map_corners_list[9][1][0]] + corners_list[map_corners_list[9][1][1]] + corners_list[map_corners_list[9][1][2]] == "LUF":
                    counter += -1
                    flips_ah += ["LUF"]
                if corners_list[map_corners_list[9][1][0]] + corners_list[map_corners_list[9][1][1]] + corners_list[map_corners_list[9][1][2]] == "FLU":
                    counter += -1
                    flips_h += ["FLU"]

                # Canto DLF / FDL / LFD
                if corners_list[map_corners_list[12][1][0]] + corners_list[map_corners_list[12][1][1]] + corners_list[map_corners_list[12][1][2]] == "DLF":
                    counter += -1
                    certas += ["DLF"]
                    certas += ["FDL"]
                    certas += ["LFD"]
                if corners_list[map_corners_list[12][1][0]] + corners_list[map_corners_list[12][1][1]] + corners_list[map_corners_list[12][1][2]] == "FDL":
                    counter += -1
                    flips_ah += ["FDL"]
                if corners_list[map_corners_list[12][1][0]] + corners_list[map_corners_list[12][1][1]] + corners_list[map_corners_list[12][1][2]] == "LFD":
                    counter += -1
                    flips_h += ["LFD"]

                # Canto DFR / RDF / FRD
                if corners_list[map_corners_list[15][1][0]] + corners_list[map_corners_list[15][1][1]] + corners_list[map_corners_list[15][1][2]] == "DFR":
                    counter += -1
                    certas += ["DFR"]
                    certas += ["FRD"]
                    certas += ["RDF"]
                if corners_list[map_corners_list[15][1][0]] + corners_list[map_corners_list[15][1][1]] + corners_list[map_corners_list[15][1][2]] == "RDF":
                    counter += -1
                    flips_ah += ["RDF"]
                if corners_list[map_corners_list[15][1][0]] + corners_list[map_corners_list[15][1][1]] + corners_list[map_corners_list[15][1][2]] == "FRD":
                    counter += -1
                    flips_h += ["FRD"]

                # Canto DRB / BDR / RBD
                if corners_list[map_corners_list[18][1][0]] + corners_list[map_corners_list[18][1][1]] + corners_list[map_corners_list[18][1][2]] == "DRB":
                    counter += -1
                    certas += ["DRB"]
                    certas += ["BDR"]
                    certas += ["RBD"]
                if corners_list[map_corners_list[18][1][0]] + corners_list[map_corners_list[18][1][1]] + corners_list[map_corners_list[18][1][2]] == "BDR":
                    counter += -1
                    flips_ah += ["BDR"]
                if corners_list[map_corners_list[18][1][0]] + corners_list[map_corners_list[18][1][1]] + corners_list[map_corners_list[18][1][2]] == "RBD":
                    counter += -1
                    flips_h += ["RBD"]

                # Canto DBL / BLD / LDB
                if corners_list[map_corners_list[21][1][0]] + corners_list[map_corners_list[21][1][1]] + corners_list[map_corners_list[21][1][2]] == "DBL":
                    counter += -1
                    certas += ["DBL"]
                    certas += ["BLD"]
                    certas += ["LDB"]
                if corners_list[map_corners_list[21][1][0]] + corners_list[map_corners_list[21][1][1]] + corners_list[map_corners_list[21][1][2]] == "LDB":
                    counter += -1
                    flips_ah += ["LDB"]
                if corners_list[map_corners_list[21][1][0]] + corners_list[map_corners_list[21][1][1]] + corners_list[map_corners_list[21][1][2]] == "BLD":
                    counter += -1
                    flips_h += ["BLD"]

                return (certas, flips_ah, flips_h, counter)

            def rotacoes_horarias(piece):
                return [piece[i:] + piece[:i] for i in range(len(piece))]

            def test_buffer_2(piece, certas, flips_ah, flips_h, solved_corners_list):
                """
                Equivalente a test_buffer_1, mas adaptado para corners.
                - Usa incrementos de 3 em 3 para iterar pelos pares de letras em solved_corners_list.
                - Garante que o buffer de corners inicial apontado seja realmente uma peça errada.
                """
                ready=False
                inc=-3
                rotacoes_ah  = [rot for p in flips_ah for rot in rotacoes_horarias(p)]
                rotacoes_h  = [rot for p in flips_h for rot in rotacoes_horarias(p)]
                while ready==False:
                    inc+=3
                    if piece in (certas + rotacoes_ah + rotacoes_h):
                        piece=solved_corners_list[inc][0]
                    else:
                        ready=True
                return(piece)


            def adicionar_flips_2(flips_ah, flips_h, solved_corners_list, hist_corners):
                """
                Adiciona as letras dos corners rotacionados (horário e anti-horário) à história.
                - Para rotações antihorárias, compara a peça com sua rotação e adiciona letra correspondente.
                - Para rotações horárias, faz o mesmo com a rotação horária.
                """
                def rotacionar_antihorario(piece):
                    # rotaciona a string de 3 caracteres para simular a rotação antihorária
                    return piece[2] + piece[0] + piece[1]

                def rotacionar_horario(piece):
                    # rotaciona a string de 3 caracteres para simular a rotação horária
                    return piece[1] + piece[2] + piece[0]

                # Para cada peça em flips_ah (anti-horário), procura a entrada e concatena a letra
                for piece in flips_ah:
                    for j in range(len(solved_corners_list)):
                        if solved_corners_list[j][0] == piece:
                            hist_corners += solved_corners_list[j][1]
                        if solved_corners_list[j][0] == rotacionar_antihorario(piece):
                            hist_corners += solved_corners_list[j][1]

                # Para cada peça em flips_h (horário), procura a entrada e concatena a letra
                for piece in flips_h:
                    # primeiro o próprio label da peça
                    for nome, alg in solved_corners_list:
                        if nome == piece:
                            hist_corners += alg
                    # depois o rotacionado horario dela
                    alvo = rotacionar_horario(piece)
                    for nome, alg in solved_corners_list:
                        if nome == alvo:
                            hist_corners += alg

                return hist_corners

            # Índices na string 'state' correspondentes aos stickers de corners
            corners = [0, 2, 6, 8, 9, 11, 15, 17, 18, 20, 24, 26, 27, 29, 33, 35, 36, 38, 42, 44, 45, 47, 51, 53]
            corners_list = []
            for i in range(len(corners)):
                corners_list += [state[corners[i]]]

            # Tabela de corners resolvidos: mapeia notação do canto para letra
            solved_corners_list = [
                ['ULB', 'A'], ['UBR', 'B'], ['URF', 'C'], ['UFL', 'D'],
                ['LBU', 'E'], ['LUF', 'F'], ['LFD', 'G'], ['LDB', 'H'],
                ['FLU', 'I'], ['FUR', 'J'], ['FRD', 'K'], ['FDL', 'L'],
                ['RFU', 'M'], ['RUB', 'N'], ['RBD', 'O'], ['RDF', 'P'],
                ['BRU', 'Q'], ['BUL', 'R'], ['BLD', 'S'], ['BDR', 'T'],
                ['DLF', 'U'], ['DFR', 'V'], ['DRB', 'W'], ['DBL', 'X']
            ]

            # Mapeamento auxiliar para corners: cada entrada fornece 3 índices na lista corners_list
            map_corners_list = [
                ['ULB', (0, 16, 21)], ['LBU', (16, 21, 0)], ['BUL', (21, 0, 16)],
                ['UBR', (1, 20, 5)], ['RUB', (5, 1, 20)], ['BRU', (20, 5, 1)],
                ['URF', (3, 4, 9)], ['FUR', (9, 3, 4)], ['RFU', (4, 9, 3)],
                ['UFL', (2, 8, 17)], ['FLU', (8, 17, 2)], ['LUF', (17, 2, 8)],
                ['DLF', (12, 19, 10)], ['FDL', (10, 12, 19)], ['LFD', (19, 10, 12)],
                ['DFR', (13, 11, 6)], ['FRD', (11, 6, 13)], ['RDF', (6, 13, 11)],
                ['DRB', (15, 7, 22)], ['BDR', (22, 15, 7)], ['RBD', (7, 22, 15)],
                ['DBL', (14, 23, 18)], ['BLD', (23, 18, 14)], ['LDB', (18, 14, 23)]
            ]

            # Executa a detecção inicial para corners
            certas, flips_ah, flips_h, counter = certas_flips_corners(corners_list, map_corners_list)  # Obtém listas e contador
            ciclos = 0
            continuar = True
            hist_corners = []        # acumulador de letras para história dos corners
            buffer = "ULB"           # buffer inicial para corners
            buffer = test_buffer_2(buffer, certas, flips_ah, flips_h, map_corners_list)  # garante buffer válido
            # marca as rotações equivalentes do buffer como já tratadas
            certas.append("ULB")
            certas.append("LBU")
            certas.append("BUL")
            target = ""              # target inicial desconhecido


            # Loop principal para construir a história dos corners
            while counter > 0:

                # Se o buffer não for uma das rotações de ULB, adiciona a letra correspondente
                if buffer not in ("ULB", "LBU", "BUL"):
                    for j in range(len(solved_corners_list)):
                        if (solved_corners_list[j][0] == buffer):
                            hist_corners += solved_corners_list[j][1]            
                            counter = counter - 1
                            break

                # Acha a próxima peça da sequência dado o buffer usando map_corners_list
                for k in range(len(map_corners_list)):
                    if map_corners_list[k][0] == buffer:
                        target = (
                            corners_list[map_corners_list[k][1][0]]
                            + corners_list[map_corners_list[k][1][1]]
                            + corners_list[map_corners_list[k][1][2]]
                        )
                        continuar = True
                        break

                # Segue a cadeia até encontrar uma peça já marcada como 'certa'
                while continuar and (counter > 0):

                    for j in range(len(solved_corners_list)):
                        if (solved_corners_list[j][0] == target):
                            hist_corners += solved_corners_list[j][1]
                            counter = counter - 1
                            break

                    if counter != 0:
                        for k in range(len(map_corners_list)):
                            if map_corners_list[k][0] == target:
                                # adiciona todas as rotações equivalentes à lista 'certas'
                                certas.append(target[0] + target[1] + target[2])
                                certas.append(target[2] + target[0] + target[1])
                                certas.append(target[1] + target[2] + target[0])
                                # define o próximo target consultando corners_list
                                target = (
                                    corners_list[map_corners_list[k][1][0]]
                                    + corners_list[map_corners_list[k][1][1]]
                                    + corners_list[map_corners_list[k][1][2]]
                                )
                                break

                        if target not in certas:
                            continuar = True
                        elif target in certas:
                            continuar = False
                            ciclos = ciclos + 1
                            counter = counter + 1
                            buffer = test_buffer_2(target, certas, flips_ah, flips_h, map_corners_list)

            def remover_strings_especificas(lista):
                strings_para_remover = {"ULB", "LBU", "BUL"}
                return [item for item in lista if item not in strings_para_remover]

            flips_h= remover_strings_especificas(flips_h)
            flips_ah = remover_strings_especificas(flips_ah)


            # Após construir a história, adicionamos as entradas relativas às rotações detectadas
            hist_corners = adicionar_flips_2(flips_ah, flips_h, solved_corners_list, hist_corners)

            ###############
            #  HISTORIA   #
            ###############

            # Concatena história de edges e corners e imprime o resultado final
            hist = hist_edges + hist_corners

            ##################################
            #   GERADOR DE SEQUÊNCIA M2/OP   #
            ##################################

            # Algoritmo Y (para corners)
            alg_Y = "R U' R' U' R U R' F' R U R' U' R' F R"

            # Paridade (M2 específico)
            alg_paridade = "U' L2 U L2 R2 D' L2 D"

            # Tabelas de movimentos M2 (odd / even)
            M2_odd = {
                'A': "L2 R2",
                'B': "R' U R U' L2 R2 D R' D' R",
                'C': "U2 L R' F2 L R'",
                'D': "L U' L' U L2 R2 D' L D L'",
                'E': "B L' B' L2 R2 F L F'",
                'F': "B L2 B' L2 R2 F L2 F'",
                'G': "B L B' L2 R2 F L' F'",
                'H': "L' B L B' L2 R2 F L' F' L",
                'I': "D L R' F R2 F' L' R U R2 U' D' L2 R2",
                'J': "U R U' L2 R2 D R' D'",
                'L': "U' L' U L2 R2 D' L D",
                'M': "B' R B L2 R2 F' R' F",
                'N': "R B' R' B L2 R2 F' R F R'",
                'O': "B' R' B L2 R2 F' R F",
                'P': "B' R2 B L2 R2 F' R2 F",
                'Q': "B' R B U R2 U' L2 R2 D R2 D' F' R' F",
                'R': "U' L U L2 R2 D' L' D",
                'S': "L2 R2 U D R2 D' L R' B R2 B' L' R U'",
                'T': "U R' U' L2 R2 D R D'",
                'V': "U R2 U' L2 R2 D R2 D'",
                'W': "L' R B2 L' R D2",
                'X': "U' L2 U L2 R2 D' L2 D"
            }

            M2_even = {
                'A': "L2 R2",
                'B': "R' D R D' L2 R2 U R' U' R",
                'C': "L' R F2 L' R U2",
                'D': "L D' L' D L2 R2 U' L U L'",
                'E': "F L' F' L2 R2 B L B'",
                'F': "F L2 F' L2 R2 B L2 B'",
                'G': "F L F' L2 R2 B L' B'",
                'H': "L' F L F' L2 R2 B L' B' L",
                'I': "L2 R2 D U R2 U' L R' F R2 F' L' R D'",
                'J': "D R D' L2 R2 U R' U'",
                'L': "D' L' D L2 R2 U' L U",
                'M': "F' R F L2 R2 B' R' B",
                'N': "R F' R' F L2 R2 B' R B R'",
                'O': "F' R' F L2 R2 B' R B",
                'P': "F' R2 F L2 R2 B' R2 B",
                'Q': "F' R F D R2 D' L2 R2 U R2 U' B' R' B",
                'R': "D' L D L2 R2 U' L' U",
                'S': "U L R' B R2 B' L' R D R2 D' U' L2 R2",
                'T': "D R' D' L2 R2 U R U'",
                'V': "D R2 D' L2 R2 U R2 U'",
                'W': "D2 L R' B2 L R'",
                'X': "D' L2 D L2 R2 U' L2 U"
            }

            # Tabela do método OP (corners)
            OP_table = {
                'B': "R D' Y D R'",
                'C': "F Y F'",
                'D': "F R' Y R F'",
                'F': "F2 Y F2",
                'G': "D2 R Y R' D2",
                'H': "D2 Y D2",
                'I': "F' D Y D' F",
                'J': "F2 D Y D' F2",
                'K': "F D Y D' F'",
                'L': "D Y D'",
                'M': "R' Y R",
                'N': "R2 Y R2",
                'O': "R Y R'",
                'P': "Y",
                'Q': "R' F Y F' R",
                'S': "D' R Y R' D",
                'T': "D' Y D",
                'U': "F' Y F",
                'V': "D' F' Y F D",
                'W': "D2 F' Y F D2",
                'X': "D F' Y F D'"
            }

            def gerar_solucao(hist_edges, hist_corners):
                seq_final = []
                # EDGES
                for i, letra in enumerate(hist_edges):
                    # se for “PARIDADE” ou “NO PARIDADE” já trata depois
                    if letra in ("PARIDADE", "NO PARIDADE"):
                        continue
                    # M2
                    if (i + 1) % 2 == 0:
                        seq_final.append(M2_even[letra])
                    else:
                        seq_final.append(M2_odd[letra])
                # PARIDADE
                # (olha só o último item da lista de edges)
                if len(hist_edges) > 0:
                    if hist_edges[-1] == "PARIDADE":
                        seq_final.append(alg_paridade)
                    # se for "NO PARIDADE" não faz nada
                # CORNERS
                for letra in hist_corners:
                    seq_final.append(OP_table[letra].replace("Y", alg_Y))

                return " ".join(seq_final)

            # Simplificador
            def simplificar_movimentos(seq_str):
                """
                Simplifica uma sequência de movimentos do cubo mágico.
                Regras aplicadas:
                X X   -> X2
                X X'  -> (cancela)
                X' X' -> X2
                X' X  -> (cancela)
                X2 X  -> X'
                X2 X' -> X
                X' X2 -> X
                X X2  -> X'
                """
                moves = seq_str.split()
                stack = []

                def combina(a, b):
                    # Extrai o eixo (L, R, U, D, F, B)
                    base_a = a[0]
                    base_b = b[0]
                    if base_a != base_b:
                        return None  # eixos diferentes não combina

                    suf_a = a[1:] if len(a) > 1 else ''
                    suf_b = b[1:] if len(b) > 1 else ''

                    # Todas as combinações possíveis
                    if suf_a == '' and suf_b == '':
                        return base_a + '2'
                    if suf_a == "'" and suf_b == "'":
                        return base_a + '2'
                    if (suf_a == '' and suf_b == "'") or (suf_a == "'" and suf_b == ''):
                        return ''  # cancelam
                    if suf_a == '2' and suf_b == '':
                        return base_a + "'"
                    if suf_a == '2' and suf_b == "'":
                        return base_a
                    if suf_a == '' and suf_b == '2':
                        return base_a + "'"
                    if suf_a == "'" and suf_b == '2':
                        return base_a
                    return None

                for move in moves:
                    if stack:
                        comb = combina(stack[-1], move)
                        if comb is not None:
                            stack.pop()
                            if comb != '':
                                stack.append(comb)
                        else:
                            stack.append(move)
                    else:
                        stack.append(move)

                # repete até não haver mais simplificações possíveis (casos tipo X X X)
                simplified = ' '.join(stack)
                if simplified != seq_str:
                    return simplificar_movimentos(simplified)
                return simplified

            # Execução
            solucao = gerar_solucao(hist_edges, hist_corners)

            solucao_final = simplificar_movimentos(solucao)
            move_count = count_moves(solucao_final)
            robot_sequence = converter_movimentos(solucao_final)
            inverse_sequence = invert_moves(solucao_final)
            inverted_sequence = converter_movimentos(inverse_sequence)

            return {
                "solution": solucao_final,
                "move_count": move_count,
                "robot_sequence": robot_sequence,
                "inverted_sequence": inverted_sequence
            }
    
        # ==================================================
        # TIMEOUT
        # ==================================================

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(solver_task)
            result = future.result(timeout=3)  

        return result

    except concurrent.futures.TimeoutError:
        return {
            "error": "Error. Probably cubestring is invalid."
        }

    except Exception as e:
        return {
            "error": str(e)
        }
