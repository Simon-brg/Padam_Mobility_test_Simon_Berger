from collections import defaultdict
from input import parse_cmd_line, parse_file
from graph import Graph
from pulp import *
import time

'''

Méthodologie de résolution
Nous allons utiliser le fait que pour avoir un chemin pseudo eulérien il faut et suffit d'avoir:
-Chaque sommet doit avoir autant d'arêtes rentrantes que d'arêtes sortantes (similaire problème de flot)
-Uniquement deux sommets qui sont la source et le puit doivent avoir un nombre impair d'arête

N.B : Un graphe est eulérien ssi il est connexe et tous ses sommets sont de degré pair

'''

def cycle_eulerien_minimal(edges, vertices):
    '''PLNE pour trouver le cycle eulérien minimal'''

    prob = LpProblem("chemin_pseudo_eulerien", LpMinimize)

    # Variables de décision : +1 si l'arête est parcourue, 0 sinon
    edge_vars = {}
    for u, v, _, _, _ in edges:
        edge_vars[(u, v)] = LpVariable("Edge_{}_{}".format(u, v), lowBound=0, cat='Integer')
        edge_vars[(v, u)] = LpVariable("Edge_{}_{}".format(v, u), lowBound=0, cat='Integer')

    nombre_sommets = len(vertices)

    # Compter le nombre d'arêtes incidentes à chaque sommet
    degree = defaultdict(int)
    for u, v, _, _, _ in edges:
        degree[u] += 1
        degree[v] += 1

    # Identifier les sommets avec un degré impair
    odd_degree_vertices = [v for v, d in degree.items() if d % 2 == 1]

    # indice entier k dépendant de chaque sommet
    k = {}
    for n in range(nombre_sommets + 2):
        k[n] = LpVariable(f'k_{n}', lowBound=0, cat='Integer')

    # Contrainte 1: Tous les sommets doivent avoir exactement un nombre pair d'arêtes incidentes
    for idx in range(nombre_sommets):
        incident_edges_count = lpSum(edge_vars[(idx, idx2)] + edge_vars[(idx2, idx)]
                                     for idx2 in range(nombre_sommets)
                                     if (idx, idx2) in edge_vars or (idx2, idx) in edge_vars)
        if idx in odd_degree_vertices:
            prob += incident_edges_count == 2 * (k[idx] + 1)


    # Contrainte 2 : chaque arête est parcourue au moins une fois
    for u, v, _, _, _ in edges:
        prob += edge_vars[(u, v)] + edge_vars[(v, u)] >= 1

    # fonction objective : minimiser le poids total des arêtes
    prob += lpSum(weight * (edge_vars[(u, v)] + edge_vars[(v, u)]) for u, v, weight, _, _ in edges)

    # Résoudre le problème pour obtenir le chemin parcouru
    prob.solve()

    # retrouver quelles arêtes ont été sélectionnées lors de la résolution PLNE
    chemin_parcouru = []
    for u, v, w, c1, c2 in edges:
        if edge_vars[(u, v)].varValue > 0:
            for _ in range(int(edge_vars[(u, v)].varValue)):
                chemin_parcouru.append((u, v,w,c1,c2))
        if edge_vars[(v, u)].varValue > 0:
            for _ in range(int(edge_vars[(v, u)].varValue)):
                chemin_parcouru.append((v, u,w,c2,c1))


    # Retourner le chemin parcouru dans et la distance totale minimale
    return chemin_parcouru, value(prob.objective)



def get_edge_weight(edge, edges):
    '''récupère le poids d'une certaine arête'''
    for u, v, w, _, _ in edges:
        if (u, v) == (edge[0], edge[1]) or (v, u) == (edge[0], edge[1]):
            return w
    return None


def convertir_en_chemin(pseudo_cycle_eulerien,edges):
    '''Convertit un cycle en chemin'''
    chemin_eulerien = pseudo_cycle_eulerien[:]
    
    # Trouver les arêtes en double dans le chemin
    aretes_en_double = [edge for edge in chemin_eulerien if chemin_eulerien.count(edge) > 1]
    
    # Trier les arêtes en double par poids décroissant
    aretes_en_double.sort(key=lambda edge: (get_edge_weight(edge, edges), edge), reverse=True)

    # Retirer l'arête en double de poids maximal afin de créer un chemin (un sommet de départ et d'arrivée)
    if aretes_en_double:
        arete_enlevee = aretes_en_double[0]
        poids = get_edge_weight(arete_enlevee, edges)
        chemin_eulerien.remove(arete_enlevee)
        print('on enlève arête :', arete_enlevee)
    else:
        arete_enlevee = None
        poids = None
    return chemin_eulerien,poids
   

# On appelle nos méthodes que l'on teste avec les instances
temps_debut=time.time()
in_file = "C:/Users/HP/OneDrive/Documents/Documents_importants/professionnel/Test_Padam_Mobility/islands.txt"
vertices, edges = parse_file(in_file)
pseudo_cycle, distance= cycle_eulerien_minimal(edges, vertices)
#print("pseudo cycle :", [(u,v) for u,v,_,_,_ in pseudo_cycle])
chemin_pseudo_eulerien,distance_enlevee = convertir_en_chemin(pseudo_cycle,edges)
print("Chemin eulérien:", [(u,v) for u,v,_,_,_ in chemin_pseudo_eulerien])
if distance_enlevee is not None:
    print("Distance totale parcourue:", distance - distance_enlevee)
else:
    print("Aucune arête retirée, c'est un cycle eulérien, distance totale parcourue:", distance)

graph = Graph(vertices, chemin_pseudo_eulerien)
graph.plot()

temps_fin=time.time()
print(f"temps de calcul : {round(temps_fin-temps_debut,2)} secondes")



