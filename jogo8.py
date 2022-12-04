from enum import Enum
from tqdm import tqdm
from collections import deque
from time import sleep
from threading import Thread
from multiprocessing import Process,Lock,Queue

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

VAZIO = 0
TEMP = 9

#estados_conhecidos = set()
objetivo = Queue()
sync_q = Queue()
threads = []
procs = []
lock = Lock()

def state_string_to_int(estado_string):
    estado_string = estado_string.replace("_",f"{VAZIO}")
    estado_int = [int(i) for i in estado_string]
    return estado_int


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
        estado = [i for i in estado_atual]

        peca_mover = estado[(jogada[PECA_MOVER])]

        estado[(jogada[PECA_MOVER])] = VAZIO
        estado[pos_vazio] = peca_mover
        sucessores.append((jogada[ACAO_FAZER],estado) )



    return sucessores

def expande(nodo):
    jogadas = sucessor(nodo.estado)

    nodos_filhos = []
    for jogada in jogadas:
        nodos_filhos.append(Nodo(jogada[ESTADO_ACAO],jogada[ACAO_FAZER],custo =1, pai = nodo))


    return nodos_filhos

nodo_alvo = None
explorados = set()

fronteira = deque([Nodo(state_string_to_int("2_3541687"))])

#fronteira = deque([Nodo(state_string_to_int("672418_53"))])

def dfs(sync_q,plock,fronteira,explorados, alvo, profundidade = 56):
    global estados_conhecidos
    global lock
    global sync_queue

    lock = plock
    sync_queue = sync_q
    estados_conhecidos = explorados

    if profundidade == 0:
        return

    if(objetivo.empty() == False or sync_queue.empty() == False):
        return


    profundidade -= 1

    try:
        nodo = fronteira.pop()

        if(nodo.estado == alvo and objetivo.empty() == True):
            lock.acquire()


            if(objetivo.empty() == True and sync_queue.empty()):
                objetivo.put(nodo)
                sync_queue.put("done")
                estados_conhecidos.add(str(nodo.estado))
                print(len(estados_conhecidos))
                sleep(1)


            lock.release()
            return 1

        if str(nodo.estado) not in estados_conhecidos : #and str(nodo.estado) not in estados_conhecidos
            lock.acquire()
            estados_conhecidos.add(str(nodo.estado))
            lock.release()

            filhos = expande(nodo)
            for filho in filhos:
                if str(filho.estado) not in estados_conhecidos: #filho not in explorados and
                    fronteira.append(filho)
                    dfs(sync_queue,lock,fronteira,explorados,alvo,profundidade)






        return
    except IndexError:
        return




for i in range(10):
    proc = Process(target = dfs, args = (sync_q,lock,fronteira,explorados,state_string_to_int("12345678_")))
    procs.append(proc)
    proc.start()

for t in procs:
    proc.join()




nodo_alvo = objetivo.get()
print(nodo_alvo)

exit(0)





