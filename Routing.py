##----------------------------------------------------------------
## Routing routines
##----------------------------------------------------------------

import random
import time, sys
import sets
import networkx as nx
from math import sqrt

def eucl(a, b):
    return sqrt(sum((x-y)**2 for x,y in zip(a, b)))

COLORS = list('rbgmyc')

# lookup for the node number of LatLng
def LatLngtoNode(latlngpoint, nodes):
    for node, LatLng in nodes.items():
        if LatLng==latlngpoint or isinstance(LatLng, list) and latlngpoint in LatLng:
            return node

# Path(s) as arguments
def route (PP, source=None, destination=None, view=False, debug=False):

    nPaths = len(PP)
    MainGraph = nx.DiGraph()
    tmp = []
    j=0
    epsilon = 0.0000000001
    nodes = dict()
    all_edges = dict()
    G = [None] * nPaths
    for c, ip in zip(COLORS, xrange(nPaths)):
        Path = PP[ip]
        G[ip] = nx.DiGraph()

        k = j
        for x in Path:            
            nodes[j] = x
            tmp.append([x,j])
            j+=1 

        G[ip].add_nodes_from(nodes.keys())        
        the_edges = [ (i,i+1) for i in xrange(k, j-1) ]
        all_edges[ip] = the_edges
        G[ip].add_edges_from(the_edges)
 
        # Add to Unified Graph
        MainGraph.add_nodes_from(nodes.keys())
        MainGraph.add_edges_from([ (i,i+1) for i in xrange(k, j-1) ])
     
    # Connecting the graph(s)
    for u in tmp:
        for v in tmp:
            if u != v:
                if u[0] == v[0]:
                    e = (u[1], v[1])     
                    if e in MainGraph.edges():          # TODO add capacity here?
                        if debug: print ' %s already there.' % list(e)
                    else:
                        if debug: print ' Adding %s to graph.' % list(e)
                        MainGraph.add_edge(e[0], e[1])
 
    n = len(MainGraph.nodes())

    source_node = LatLngtoNode(source, nodes)
    destination_node = LatLngtoNode(destination, nodes)

    # Optimization Graph
    
    OG = nx.DiGraph()

    m = 3 # max capacity  TODO randomly?
    w = 1

    for e in MainGraph.edges():
        OG.add_edge(e[0], e[1], weight=w, capacity=m)
    
    OG.add_node(source_node, demand = -1)
    OG.add_node(destination_node, demand = 1)

    try:
        
        flowCost, flowDict = nx.network_simplex(OG)
        print 'shortest_path_length? ', flowCost == nx.shortest_path_length(OG, source_node, destination_node, weight = 'weight')
    
    except Exception as e:
        print ('Pick another option (%s)' % e)
        print ("(Keep it, not congested)"  )

        return -1
    
    E = []
    print 'flowDict : '
    for u in flowDict:
        for v in flowDict[u]:
            if flowDict[u][v]!=0:
                print '\t', u, ' -> ', v, ' : ', flowDict[u][v]
                E.append((u,v))
    
    
    print ("Optimum = %s" % flowCost)
    
    for e in E:
        print e
    
    print '----- leaving route() ---------------------------------'
    
    return E, flowCost





'''
if __name__== "__main__":

    
    Path0   = [ (35.16973, 136.88105000000002),(35.16949, 136.88118),(35.16946, 136.88123000000002),(35.16924, 136.88059),(35.16868, 136.88087000000002),(35.168380000000006, 136.88097000000002),(35.16774, 136.88096000000002),(35.167480000000005, 136.88085),(35.167440000000006, 136.88264),(35.167730000000006, 136.88513),(35.1677, 136.88538),(35.167860000000005, 136.88639),(35.168000000000006, 136.88735),(35.16816, 136.88846),(35.168200000000006, 136.88876000000002),(35.16816, 136.88959),(35.16812, 136.89021000000002),(35.16799, 136.89122),(35.1679, 136.89235000000002),(35.168060000000004, 136.89491),(35.168220000000005, 136.8974),(35.169200000000004, 136.8973), (35.16928, 136.89742) ]
    Path1   = [ (35.169740000000004, 136.88559),(35.16964, 136.88558),(35.16949, 136.88572000000002),(35.16912, 136.88608000000002),(35.168710000000004, 136.88617000000002),(35.168890000000005, 136.88708),(35.16911, 136.88809),(35.16944, 136.8896),(35.169340000000005, 136.88992000000002),(35.16904, 136.88991000000001),(35.16814, 136.8899),(35.168060000000004, 136.89063000000002),(35.16794, 136.89165),(35.1679, 136.89235000000002),(35.167970000000004, 136.89348),(35.168150000000004, 136.89631),(35.167440000000006, 136.89639000000003),(35.167170000000006, 136.89642) ]
    Path2   = [ (35.166900000000005, 136.88430000000002),(35.166970000000006, 136.88468),(35.16702, 136.88525),(35.16758, 136.88517000000002),(35.1677, 136.88538),(35.1679, 136.88675),(35.16809, 136.88798),(35.168200000000006, 136.88876000000002),(35.16814, 136.8899),(35.16794, 136.89165),(35.1679, 136.89235000000002),(35.167970000000004, 136.89348),(35.168150000000004, 136.89631),(35.167170000000006, 136.89642) ]
    Path3   = [ (35.165850000000006, 136.88819),(35.166850000000004, 136.88823000000002),(35.16809, 136.88798),(35.168200000000006, 136.88876000000002),(35.16814, 136.8899),(35.16794, 136.89165),(35.1679, 136.89235000000002),(35.168490000000006, 136.89251000000002),(35.1691, 136.89261000000002) ]
    Path4   = [ (35.165850000000006, 136.88819),(35.166380000000004, 136.88821000000002),(35.166410000000006, 136.88914),(35.165850000000006, 136.88925),(35.16588, 136.88996),(35.16592, 136.89106),(35.16597, 136.89235000000002),(35.16601, 136.894) ]
    Path5   = [ (35.17152, 136.89462),(35.171850000000006, 136.89460000000003),(35.171760000000006, 136.89299),(35.17078, 136.89279000000002),(35.16989, 136.89269000000002),(35.16962, 136.89267),(35.16877, 136.89257),(35.1679, 136.89235000000002),(35.167590000000004, 136.89229),(35.16736, 136.89227000000002),(35.16597, 136.89235000000002),(35.16601, 136.89369000000002),(35.16601, 136.894) ]
    
    Paths = Path0 + Path1 + Path2 + Path3 + Path4 + Path5
    PP = [Path0,Path1,Path2,Path3,Path4,Path5]
 
    source = Path3[3]
    destination = Path5[9]
    
    main(PP, source, destination, view=True)
'''

