from enum import Enum
from queue import Empty as qEmpty
from collections import deque
from time import sleep,time
from threading import Thread
from multiprocessing import Process,Lock,Queue,cpu_count
import random
from scipy.spatial.distance import hamming
from queue import PriorityQueue

global total_explorados

ACAO_ESQUERDA = "esquerda"
ACAO_DIREITA = "direita"
ACAO_ABAIXO = "abaixo"
ACAO_ACIMA = "acima"



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

def state_string_to_int(estado_string):
    estado_string = estado_string.replace("_",f"{VAZIO}")
    estado_int = [int(i) for i in estado_string]
    return estado_int


class Nodo():
    def __init__(self,estado, acao = None, custo = 0,pai = None, heuristica = None):
        self.estado = estado
        self.acao = acao
        self.custo = custo
        self.pai = pai
        self.estado_objetivo = [1,2,3,4,5,6,7,8,0]

        if heuristica is not None:
          self.heuristica = heuristica

        self.total = self.custo+self.heuristica(self.estado,self.estado_objetivo)
        

    def __str__(self):
        return f"\n______{self=}_______\n  {self.estado=}\n  {self.acao=}\n  {self.pai=}\n  {self.custo=}\n  {self.total=}\n"

    def __gt__(self, nodo2):
      return self.total > nodo2.total

    def __lt__(self, nodo2):
      return self.total < nodo2.total

    def __eq__(self, nodo2):
      return self.total == nodo2.total      

    def heuristica(self, estado, estado_objetivo):
      return 0






vizinhos = {
    0: [(ACAO_ABAIXO,3),(ACAO_DIREITA,1)],
    1: [(ACAO_DIREITA,2),(ACAO_ABAIXO,4),(ACAO_ESQUERDA,0)],
    2: [(ACAO_ESQUERDA,1),(ACAO_ABAIXO,5)],
    3: [(ACAO_ABAIXO,6),(ACAO_DIREITA,4),(ACAO_ACIMA,0)],
    4: [(ACAO_ACIMA,1),(ACAO_DIREITA,5),(ACAO_ESQUERDA,3),(ACAO_ABAIXO,7)],
    5: [(ACAO_ABAIXO,8),(ACAO_ESQUERDA,4),(ACAO_ACIMA,2)],
    6: [(ACAO_DIREITA,7),(ACAO_ACIMA,3)],
    7: [(ACAO_ACIMA,4),(ACAO_ESQUERDA,6),(ACAO_DIREITA,8)],
    8: [(ACAO_ESQUERDA,7),(ACAO_ACIMA,5)]

}

def invCount(tabuleiro):
    arr = tabuleiro.replace(VAZIO,'0')
    inv_count = 0
    for i in range(9):
        for j in range(i+1,9):
            if ( (int(arr[j]) and (int(arr[i]))) and (int(arr[i]) > int(arr[j])) ):
                inv_count+=1

    return inv_count

def manhattan_distance(estado1,estado2):
  distancia = 0
  estado1 = [e for e in estado1 if e>0]
  estado2 = [e for e in estado2 if e>0]

  for peca in zip(sorted(estado1),sorted(estado2)):
      x1,y1 = int((estado1.index(peca[0])/3)),int((estado1.index(peca[0])+1) % 3)
      x2,y2 = int((estado2.index(peca[1])/3)),int((estado2.index(peca[1])+1) % 3)
      distancia += (abs(x2-x1) + abs(y2-y1))

  return distancia

def hamming_distance(estado1,estado2):
    estado1 = [e for e in estado1 if e>0]
    estado2 = [e for e in estado2 if e>0]

    return hamming(estado1,estado2)*8


def sucessor_int(estado_atual,teste = False):

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

def sucessor(estado_atual):
  if(type(estado_atual) is str):
      estado_atual = state_string_to_int(estado_atual)

  sucessores_int = sucessor_int(estado_atual)
  sucessores = []

  for sucs in sucessores_int:
    estado = "".join(str(sucs[ESTADO_ACAO]).strip(']').strip('[').replace(" ","").replace(",","").replace("0","_"))
    sucessores.append( (sucs[ACAO_FAZER]),estado)

  return sucessores


def expande(nodo,heuristica = None):
    jogadas = sucessor_int(nodo.estado)
    nodos_filhos = []
    for jogada in jogadas:
        nodos_filhos.append(Nodo(jogada[ESTADO_ACAO],jogada[ACAO_FAZER],nodo.custo+1, pai = nodo, heuristica = heuristica))


    return nodos_filhos

def expande_shuffle(nodo,heuristica = None):
    nodos = expande(nodo,heuristica)
    random.shuffle(nodos)
    return nodos


def caminho_sv(nodo):
  caminho = []


  while(nodo.pai is not None):
      caminho.append(nodo.acao)
      nodo = nodo.pai

  caminho.reverse()

  return caminho





def astar(heuristica,objetivo,fronteira,explorados, alvo, profundidade = 56):

    estados_conhecidos = explorados
    print(heuristica)
    nodo = fronteira.get(block = False)[1]
    while(nodo.custo <= 56):
        try:
            if(nodo.custo > 56):
                return

            if(nodo.estado == alvo and objetivo.empty() == True):


                if(objetivo.empty() == True):
                    caminho_solucao = caminho_sv(nodo)
                    print(caminho_solucao)
                    objetivo.put(caminho_solucao)
                    estados_conhecidos.add(str(nodo.estado)+f".{nodo.custo}")
                    print(nodo)
                    print(len(estados_conhecidos))


                return 1


            while((str(nodo.estado) + f".{nodo.custo}") in estados_conhecidos):
               nodo = fronteira.get(block = False)[1]

            if str(nodo.estado) not in estados_conhecidos : #and str(nodo.estado) not in estados_conhecidos
                estados_conhecidos.add(str(nodo.estado)+f".{nodo.custo}")
                filhos = expande(nodo, heuristica)

                for filho in filhos:
                    if (str(filho.estado)+f".{filho.custo}") not in estados_conhecidos: #filho not in explorados and
                        fronteira.put( (filho.total,filho))
                    else:
                        continue

            nodo = fronteira.get(block = False)[1]
        except qEmpty:
            print("excp")
            return
          
    print("aaaa")
    return


def astar_hamming(objetivo,fronteira,explorados, alvo, profundidade = 56):
  heuristica = hamming_distance
  resultado = astar(heuristica,objetivo,fronteira,explorados, alvo, profundidade = 56)
  return resultado

def astar_manhattan(objetivo,fronteira,explorados, alvo, profundidade = 56):
  heuristica = manhattan_distance
  resultado = astar(heuristica,objetivo,fronteira,explorados, alvo, profundidade = 56)
  return resultado 

def bfs(objetivo,fronteira,explorados, alvo, profundidade = 56):
    global estados_conhecidos
    estados_conhecidos = explorados

    nodo = fronteira.popleft()
    while(nodo.custo <= 56):
        try:
            if(nodo.custo > 56):
                return

            while str(nodo.estado) in estados_conhecidos:
                nodo = fronteira.popleft()

            if(nodo.estado == alvo and objetivo.empty() == True):
                caminho_solucao = caminho_sv(nodo)
                print(caminho_solucao)
                objetivo.put(caminho_solucao)
                estados_conhecidos.add(str(nodo.estado))
                print(nodo)
                return caminho_solucao


            if str(nodo.estado) not in estados_conhecidos : #and str(nodo.estado) not in estados_conhecidos
                estados_conhecidos.add(str(nodo.estado))

                filhos = expande_shuffle(nodo)
                for filho in filhos:
                    if str(filho.estado) not in estados_conhecidos: #filho not in explorados and
                        fronteira.append(filho)
                    else:
                        continue

            nodo = fronteira.popleft()


        except IndexError:
            return




def dfs(fronteira,explorados, alvo, profundidade = 100):
    global estados_conhecidos 
    global sucesso
    global total_explorados

    estados_conhecidos = explorados

    if(sucesso):
      return None


    profundidade -= 1

    caminho = None

    try:
        nodo = fronteira.pop()
        total_explorados = len(estados_conhecidos)

        while str(nodo.estado) in estados_conhecidos:
          nodo = fronteira.pop()
       
        if(nodo.estado == alvo and objetivo.empty() == True):
            caminho_solucao = caminho_sv(nodo)
            print(caminho_solucao)
            sucesso = True 
            estados_conhecidos.add(str(nodo.estado))
            print(nodo)
            caminho = caminho_solucao


            return caminho_solucao

        
        if str(nodo.estado) not in estados_conhecidos : #and str(nodo.estado) not in estados_conhecidos
            estados_conhecidos.add(str(nodo.estado))

            filhos = expande_shuffle(nodo)
            for filho in filhos:
                if str(filho.estado) not in estados_conhecidos and profundidade > 0: #filho not in explorados and
                    fronteira.append(filho)
                    resultado = dfs(fronteira,explorados,alvo,profundidade)

                    if(resultado):
                      caminho = resultado



    except IndexError:
        print("a\n")
        return caminho

    return caminho  

fronteira = Queue()
#fronteira = deque([Nodo(state_string_to_int("2_3541687"))])

#fronteira = deque([Nodo(state_string_to_int("672418_53"))])

print("\n ______ASTAR MANHTANN_______\n")

t1 = time()

nodo_alvo = None
explorados = set()
lock = Lock()
xlock = Lock()
objetivo = Queue()

fronteira = PriorityQueue()
fronteira.put((0,Nodo(state_string_to_int("2_3541687"))) )
astar_manhattan(objetivo,fronteira,explorados,state_string_to_int("12345678_"))


print("\n ______ASTAR HAMMING_______\n")
t2 = time()

objetivo = Queue()
explorados = set()
sync_q = Queue()
fronteira = PriorityQueue()
fronteira.put((0,Nodo(state_string_to_int("2_3541687"))) )
astar_hamming(objetivo,fronteira,explorados,state_string_to_int("12345678_"))


print("\n ______BFS_______\n")

t3  = time()

fronteira = deque([Nodo(state_string_to_int("2_3541687"))])
objetivo = Queue()
explorados = set()
resultado = bfs(objetivo,fronteira,explorados,state_string_to_int("12345678_"))
print(f"{resultado=}")

print("\n ______DFS_______\n")
t4  = time()

fronteira = deque([Nodo(state_string_to_int("2_5341687"))])
sync_q = Queue()
explorados = set()
resultado = dfs(fronteira,explorados,state_string_to_int("12345678_"))
print(f"{resultado=} \n{total_explorados=}")

t5 = time()

print(f"astar manhattan time {t2-t1}")
print(f"astar hamming time {t3-t2}")
print(f"bfs time {t4-t3}")
print(f"dfs time {t5-t4}")





