from enum import Enum
from tqdm import tqdm
from collections import deque
from time import sleep

class Acao(Enum):
    ESQUERDA = 1
    ACIMA = 2
    DIREITA = 3
    ABAIXO = 4

PECA_MOVER = 1
ACAO_FAZER = 0
ESTADO_ACAO = 1
leaf_count = 1
sucesso = 0

VAZIO = "_"
TEMP = 'X'

estados_conhecidos = set()


class Nodo():
    def __init__(self,estado, acao = None, custo = 1,pai = None):
        self.estado = estado
        self.acao = acao
        self.custo = custo
        self.pai = pai

    def __str__(self):
        return f"\n______{self=}_______\n  {self.estado=}\n  {self.acao=}\n  {self.pai=}"



#0 1 2
#3 4 5
#6 7 8

#1 2 3
#4 5 6
#7 8 9

#1 2 3
#4 5 6
#7 8 0

#2 0 3
#4 5 1
#6 8 7
#23541687
#12345678



vizinhos = {
    0: [(Acao.ABAIXO,3),(Acao.DIREITA,1)],
    1: [(Acao.DIREITA,2),(Acao.ABAIXO,4),(Acao.ESQUERDA,0)],
    2: [(Acao.ESQUERDA,1),(Acao.ABAIXO,5)],
    3: [(Acao.ABAIXO,6),(Acao.DIREITA,4),(Acao.ACIMA,0)],
    4: [(Acao.ACIMA,1),(Acao.DIREITA,5),(Acao.ESQUERDA,3),(Acao.ABAIXO,7)],
    5: [(Acao.ABAIXO,8),(Acao.ESQUERDA,4),(Acao.ACIMA,2)],
    6: [(Acao.DIREITA,7),(Acao.ACIMA,3)],
    7: [(Acao.ACIMA,4),(Acao.ESQUERDA,6),(Acao.DIREITA,8)],
    8: [(Acao.ESQUERDA,7),(Acao.ACIMA,5)]

}

def invCount(tabuleiro):
    arr = tabuleiro.replace(VAZIO,'0')
    inv_count = 0
    for i in range(9):
        for j in range(i+1,9):
            if ( (int(arr[j]) and (int(arr[i]))) and (int(arr[i]) > int(arr[j])) ):
                inv_count+=1

    return inv_count


def sucessor(estado_atual):
    sucessores = []

    pos_vazio = estado_atual.index(VAZIO)
    jogadas = vizinhos[pos_vazio]

    for jogada in jogadas:
        estado = estado_atual

        peca_mover = estado[(jogada[PECA_MOVER])]
        estado = estado.replace(VAZIO,TEMP)
        estado = estado.replace(peca_mover,VAZIO)
        estado = estado.replace(TEMP,peca_mover)
        sucessores.append((jogada[ACAO_FAZER],estado) )

    return sucessores

def expande(nodo):
    jogadas = sucessor(nodo.estado)

    nodos_filhos = []
    for jogada in jogadas:
        nodos_filhos.append(Nodo(jogada[ESTADO_ACAO],jogada[ACAO_FAZER],custo =1, pai = nodo))


    return nodos_filhos


explorados = []
fronteira = deque([Nodo("2_3541687")])

def dfs(fronteira,explorados, alvo, profundidade = 56):
    if profundidade == 0:
        return 0

    profundidade -= 1

    try:
        nodo = fronteira.pop()


        if(nodo.estado == alvo):
            estados_conhecidos.add(nodo.estado)
            print(f"{profundidade=}\n")
            print(f"{nodo}")
            print("sucess!")
            return 1

        if nodo not in explorados and nodo.estado not in estados_conhecidos:
            explorados.append(nodo)
            estados_conhecidos.add(nodo.estado)

            filhos = expande(nodo)
            for filho in filhos:
                if filho not in explorados and filho.estado not in estados_conhecidos:
                    fronteira.append(filho)
                    global sucesso
                    temp = dfs(fronteira,explorados,alvo,profundidade)
                    if (temp is not None):
                        sucesso = temp







        return sucesso
    except IndexError:
        return 0


print(dfs(fronteira,explorados, "12345678_"))
print("12345678_" in estados_conhecidos)
print(len(estados_conhecidos))
exit(0)




