# Credit for this: Nicholas Swift
# as found at https://medium.com/@nicholas.w.swift/easy-a-star-pathfinding-7e6689c7f7b2
from warnings import warn
import heapq


class Node():
    """A node class for A* Pathfinding"""

    def __init__(self, pai=None, pos=None):
        self.pai = pai
        self.pos = pos

        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.pos == other.pos


def astar(matriz, inicial, final):
    """Returns a list of tuples as a path from the given inicial to the given final in the given matriz"""

    # Create inicial and final node
    node_inicial = Node(None, inicial)
    node_inicial.g = node_inicial.h = node_inicial.f = 0
    node_final = Node(None, final)
    node_final.g = node_final.h = node_final.f = 0

    # Initialize both open and closed list
    lista_aberta = []
    lista_fechada = []

    # Add the inicial node
    lista_aberta.append(node_inicial)

    # Loop until you find the final
    while len(lista_aberta) > 0:

        # Get the atual node
        node_atual = lista_aberta[0]
        index_atual = 0
        for index, item in enumerate(lista_aberta):
            if item.f < node_atual.f:
                node_atual = item
                index_atual = index

        # Pop atual off open list, add to closed list
        lista_aberta.pop(index_atual)
        lista_fechada.append(node_atual)

        # Found the goal
        if node_atual == node_final:
            path = []
            atual = node_atual
            while atual is not None:
                path.append(atual.pos)
                atual = atual.pai
            return path[::-1] # Return reversed path

        # Generate filhos
        filhos = []
        for new_pos in [(0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]: # Adjacent squares

            # Get node pos
            pos_node = (node_atual.pos[0] + new_pos[0], node_atual.pos[1] + new_pos[1])

            # Make sure within range
            if pos_node[0] > (len(matriz) - 1) or pos_node[0] < 0 or pos_node[1] > (len(matriz[len(matriz)-1]) -1) or pos_node[1] < 0:
                continue

            # Make sure walkable terrain
            if matriz[pos_node[0][0]][pos_node[1][0]]: continue #último [0] pq cor.

            # Create new node
            node_nova = Node(node_atual, pos_node)

            # Append
            filhos.append(node_nova)

        # Loop through filhos
        for filho in filhos:

            # filho is on the closed list
            for filho_fechado in lista_fechada:
                if filho == filho_fechado: continue

            # Create the f, g, and h values
            filho.g = node_atual.g + 1
            filho.h = ((filho.pos[0] - node_final.pos[0]) ** 2) + ((filho.pos[1] - node_final.pos[1]) ** 2)
            filho.f = filho.g + filho.h

            # filho is already in the open list
            for open_node in lista_aberta:
                if filho == open_node and filho.g > open_node.g: continue

            # Add the filho to the open list
            lista_aberta.append(filho)
        


def main():

    matriz=[[0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

    inicial = (0, 0)
    final = (7, 6)

    path = astar(matriz, inicial, final)
    print(path)


if __name__ == '__main__':
    main()

'''
def dist (posini, posfim):
    return (posini[0]-posfim[0])**2 + (posini[1]-posfim[1])**2  

def astar (matriz, posini, posfim):
    distancia = dist(posini, posfim)
    listaAberta = list()
    listaFechada = list()

    menorF = 10000
    menorP = posini
    xi, yi = posini

    for i in range((xi-1), (xi+1)):
        for j in range(yi-1, yi+1):
            if ((i == xi and j == yi) or ((i,j) in listaFechada)): continue

            f = dist(posini, (i,j)) + dist((i,j), posfim)
            if (f < menorF):
                menorP = (i,j); menorF = f
    
    listaFechada.append(menorP)

    ...

    return listaFechada
'''