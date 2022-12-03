from enum import Enum

class Acao(Enum):
    ESQUERDA = 1
    ACIMA = 2
    DIREITA = 3
    ABAIXO = 4

PECA_MOVER = 0
ACAO_FAZER = 1
VAZIO = "_"
TEMP = 'X'


#0 1 2
#3 4 5
#6 7 8

#1 2 3
#4 5 6
#7 8 9


vizinhos = {
    0: [(3,Acao.ABAIXO),(1,Acao.DIREITA)],
    1: [(0,Acao.ESQUERDA),(2,Acao.DIREITA),(4,Acao.ABAIXO)],
    2: [(1,Acao.ESQUERDA),(5, Acao.ABAIXO)],
    3: [(6,Acao.ABAIXO),(0,Acao.ACIMA),(4,Acao.DIREITA)],
    4: [(1,Acao.ACIMA),(5,Acao.DIREITA),(7,Acao.ABAIXO),(3,Acao.ESQUERDA)],
    5: [(4,Acao.ESQUERDA),(2,Acao.ACIMA),(8,Acao.ABAIXO)],
    6: [(7,Acao.DIREITA),(3,Acao.ACIMA)],
    7: [(8,Acao.DIREITA),(6,Acao.ESQUERDA),(4,Acao.ACIMA)],
    8: [(5,Acao.ACIMA),(7,Acao.ESQUERDA)]

}

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

#print(sucessor('2_3541687'))
inicial = '41372586_'
next = inicial
for i in range(180000):
    next = sucessor(next)[0][1]

    if(next == "12345678_"):
        print("sucess")
        print(i)
        break


print(next)




