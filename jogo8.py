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



def state_string_to_int(estado_string):
    estado_string = estado_string.replace("_",f"{VAZIO}")
    estado_int = [int(i) for i in estado_string]
    return estado_int


class Nodo():
    def __init__(self,estado = None,pai = None, acao = None, custo = 0, heuristica = None):
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

'''
Função que calcula a distância manhattan entre dois estados, sendo o segundo estado considerado o alvo do solver
'''
def manhattan_distance(estado1,estado2):
  distancia = 0
  estado1 = [e for e in estado1 if e>0]
  estado2 = [e for e in estado2 if e>0]

  for peca in zip(sorted(estado1),sorted(estado2)):
      x1,y1 = int((estado1.index(peca[0])/3)),int((estado1.index(peca[0])+1) % 3)
      x2,y2 = int((estado2.index(peca[1])/3)),int((estado2.index(peca[1])+1) % 3)
      distancia += (abs(x2-x1) + abs(y2-y1))

  return distancia

'''
Função que calcula a distância de hamming entre dois estados, sendo o segundo estado considerado o alvo do solver
'''
def hamming_distance(estado1,estado2):
    estado1 = [e for e in estado1 if e>0]
    estado2 = [e for e in estado2 if e>0]

    return hamming(estado1,estado2)*8


'''Função geradora de sucessores usada pelo programa. Por questões de otimização, o estado do tabuleiro usado internamente
é um array de inteiros em vez de uma string. Sendo o 0 o espaço vazio

'''
def sucessor_int(estado_atual):

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

#Função sucessor exposta ao testador. Resultados em formato string
def sucessor(estado_atual):
  if(type(estado_atual) is str):
      estado_atual = state_string_to_int(estado_atual)

  sucessores_int = sucessor_int(estado_atual)
  sucessores = []

  for sucs in sucessores_int:
    estado = "".join(str(sucs[ESTADO_ACAO]).strip(']').strip('[').replace(" ","").replace(",","").replace("0","_"))
    sucessores.append( (sucs[ACAO_FAZER],estado))

  return sucessores


def expande(nodo,heuristica = None, teste = True):
    jogadas = []

    if (teste):
        jogadas = sucessor(nodo.estado)
    else:
        jogadas = sucessor_int(nodo.estado)
    nodos_filhos = []
    for jogada in jogadas:

        nodos_filhos.append(Nodo(estado = jogada[ESTADO_ACAO],acao = jogada[ACAO_FAZER],custo = nodo.custo+1, pai = nodo, heuristica = heuristica))


    return nodos_filhos

def expande_shuffle(nodo,heuristica = None):
    nodos = expande(nodo,heuristica, teste = False)
    random.shuffle(nodos)
    return nodos


'''
Função que percorre o caminho no grafo de um nodo até a raiz. Retorna a lista de ações que leva do nodo raiz até o nodo alvo
'''
def caminho_sv(nodo):
  caminho = []
  while(nodo.pai is not None):
      caminho.append(nodo.acao)
      nodo = nodo.pai

  caminho.reverse()

  return caminho




'''
Base do algoritmo de busca astar. A heuristica utilizada determina o seu tipo, e essa é passada como parâmetro pelos algoritmos astar
específicos (astar hamming e astar manhattan)
'''
def astar(heuristica,fronteira,explorados, alvo, profundidade = 56):

    estados_conhecidos = explorados
    nodo = fronteira.get(block = False)[1]
    while(nodo.custo <= 56):
        try:
            if(nodo.custo > 56):
                return

            if(nodo.estado == alvo):
                caminho_solucao = caminho_sv(nodo)
                estados_conhecidos.add(str(nodo.estado)+f".{nodo.custo % 2}")
                print(nodo)


                return caminho_solucao


            while((str(nodo.estado) + f".{nodo.custo}") in estados_conhecidos):
               nodo = fronteira.get(block = False)[1]

            if str(nodo.estado) not in estados_conhecidos : #and str(nodo.estado) not in estados_conhecidos
                estados_conhecidos.add(str(nodo.estado)+f".{nodo.custo % 2}")
                filhos = expande(nodo, heuristica, teste = False)

                for filho in filhos:
                    if (str(filho.estado)+f".{filho.custo % 2}") not in estados_conhecidos: #filho not in explorados and
                        fronteira.put( (filho.total,filho))
                    else:
                        continue

            nodo = fronteira.get(block = False)[1]
        except qEmpty:
            return

    return


'''
As duas funções a seguir são as interfaces expostas dos algoritmos de busca astar. Recebem o estado inicial para resolução do grafo
'''
def astar_hamming(estado):
  explorados = set()
  sync_q = Queue()
  fronteira = PriorityQueue()
  fronteira.put((0,Nodo(state_string_to_int(estado))) )

  resultado = astar_hamming_i(fronteira,explorados,state_string_to_int("12345678_"))
  return resultado

def astar_manhattan(estado):
  explorados = set()
  sync_q = Queue()
  fronteira = PriorityQueue()
  fronteira.put((0,Nodo(state_string_to_int(estado))) )

  resultado = astar_manhattan_i(fronteira,explorados,state_string_to_int("12345678_"))
  return resultado


#############################

'''
Funções internas para os algoritmos de busca astar
'''
def astar_hamming_i(fronteira,explorados, alvo, profundidade = 56):
  heuristica = hamming_distance
  resultado = astar(heuristica,fronteira,explorados, alvo, profundidade = 56)
  return resultado

def astar_manhattan_i(fronteira,explorados, alvo, profundidade = 56):
  heuristica = manhattan_distance
  resultado = astar(heuristica,fronteira,explorados, alvo, profundidade = 56)
  return resultado


'''Interface e função interna para o algoritmo bfs'''
def bfs(estado = "2_3541687"):
  fronteira = deque([Nodo(state_string_to_int(estado))])
  alvo = state_string_to_int("12345678_")
  explorados = set()

  return bfs_i(fronteira,explorados,alvo)

def bfs_i(fronteira,explorados, alvo, profundidade = 56):
    global estados_conhecidos
    global total_explorados
    estados_conhecidos = explorados

    nodo = fronteira.popleft()
    while(nodo.custo <= 56):
        total_explorados = len(estados_conhecidos)
        try:
            if(nodo.custo > 56):
                return

            while str(nodo.estado) in estados_conhecidos:
                nodo = fronteira.popleft()

            if(nodo.estado == alvo):
                caminho_solucao = caminho_sv(nodo)
                estados_conhecidos.add(str(nodo.estado))
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

'''Interface e função interna para o algoritmo dfs'''
def dfs(estado):
  fronteira = deque([Nodo(state_string_to_int(estado))])
  alvo = state_string_to_int("12345678_")
  explorados = set()

  resultado = dfs_i(fronteira,explorados,alvo)
  return resultado

def dfs_i(fronteira,explorados, alvo, profundidade = 80):
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

        if(nodo.estado == alvo):
            caminho_solucao = caminho_sv(nodo)
            print(caminho_solucao)
            sucesso = True
            estados_conhecidos.add(str(nodo.estado))
            caminho = caminho_solucao


            return caminho_solucao


        if str(nodo.estado) not in estados_conhecidos : #and str(nodo.estado) not in estados_conhecidos
            estados_conhecidos.add(str(nodo.estado))

            filhos = expande(nodo, teste = False)
            for filho in filhos:
                if str(filho.estado) not in estados_conhecidos and profundidade > 0: #filho not in explorados and
                    fronteira.append(filho)
                    resultado = dfs_i(fronteira,explorados,alvo,profundidade)

                    if(resultado):
                      caminho = resultado



    except IndexError:
        print("a\n")
        return caminho

    return caminho


if __name__ == '__main__':
    #fronteira = deque([Nodo(state_string_to_int("2_3541687"))])

    #fronteira = deque([Nodo(state_string_to_int("672418_53"))])
    estado_pai = "185432_67"
    pai = Nodo(estado_pai, None, "abaixo", 2)
    resposta = expande(pai)
    print(resposta)


    print("\n ______ASTAR MANHTANN_______\n")

    t1 = time()


    resultado = astar_manhattan("2_3541687")
    print(f"{resultado=} \n")


    print("\n ______ASTAR HAMMING_______\n")
    t2 = time()
    resultado = astar_hamming("2_3541687")
    print(f"{resultado=} \n")


    print("\n ______BFS_______\n")

    t3  = time()

    resultado = bfs("2_3541687")
    print(f"{resultado=} \n{total_explorados=}")

    print("\n ______DFS_______\n")
    t4  = time()



    resultado = dfs("2_3541687")
    print(f"{resultado=} \n{total_explorados=}")

    t5 = time()



    print(f"astar manhattan time {t2-t1}")
    print(f"astar hamming time {t3-t2}")
    print(f"bfs time {t4-t3}")
    print(f"dfs time {t5-t4}")





