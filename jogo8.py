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

#1 2 3
#4 5 6
#7 8 0

#2 0 3
#4 5 1
#6 8 7
#23541687
#12345678



vizinhos = {
    0: [(3,Acao.ABAIXO),(1,Acao.DIREITA)],
    1: [(0,Acao.ESQUERDA),(2,Acao.DIREITA),(4,Acao.ABAIXO)],
    2: [(5, Acao.ABAIXO),(1,Acao.ESQUERDA)],
    3: [(6,Acao.ABAIXO),(4,Acao.DIREITA),(0,Acao.ACIMA)],
    4: [(1,Acao.ACIMA),(5,Acao.DIREITA),(3,Acao.ESQUERDA),(7,Acao.ABAIXO)],
    5: [(8,Acao.ABAIXO),(4,Acao.ESQUERDA),(2,Acao.ACIMA)],
    6: [(7,Acao.DIREITA),(3,Acao.ACIMA)],
    7: [(4,Acao.ACIMA),(6,Acao.ESQUERDA),(8,Acao.DIREITA)],
    8: [(7,Acao.ESQUERDA),(5,Acao.ACIMA)]

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
    #print(f"{estado_atual.index(VAZIO)}")
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



print(invCount('123456_87'))
print(invCount('2_3541687'))

#print(sucessor('2_3541687'))
inicial = sucessor('123456_87')
next = inicial


for x in range(200000):
    try:
        current = next.pop()
        if(current[1] == "12345678_"):
            print("sucess")
            print(i*x)
            break
        else:
            for resultado in sucessor(current[1]):
                next.append(resultado)
    except IndexError:
        next = current
        break

    if(next == "12345678_"):
        print("sucess")
        print(i*x)
        break

print(next)
