import networkx as nx
import matplotlib.pyplot as plt
from copy import deepcopy
from collections import defaultdict
import math
import pylab

twitter_network = [ line.strip().split('\t') for line in file('twitter_network.csv') ]

DiG = nx.DiGraph()
hfollowers = defaultdict(lambda: 0)
for (twitter_user, followed_by, followers) in twitter_network:
    DiG.add_edge(twitter_user, followed_by, followers=int(followers))
    hfollowers[twitter_user] = int(followers)

#SEED = 'UnboxTherapy'
SEED = 'TEDxSingapore'

# centre around the SEED node and set radius of graph
#g=nx.DiGraph(nx.ego_graph(DiG, SEED, radius=2))
# g = nx.DiGraph(nx.ego_graph(o, SEED, radius=4))
g = nx.DiGraph(nx.ego_graph(DiG, SEED, radius=4))

def trim_degrees_ted(g, degree=1, ted_degree=1):
    g2 = deepcopy(g)
    d = nx.degree(g2)
    for n in g.nodes():
        if n == SEED: continue # don't prune the SEED node
        if d[n] <= degree and not n.lower().startswith('ted'):
            g2.remove_node(n)
        elif n.lower().startswith('ted') and d[n] <= ted_degree:
            g2.remove_node(n)
    return g2

def trim_edges_ted(g, weight=1, ted_weight=10):
    g2 = nx.DiGraph()
    for f, to, edata in (g.edges(data=True)):
        if((f == SEED) or (to == SEED)): # keep edges that link to the SEED node
            g2.add_edge(f, to, edata)
        elif f.lower().startswith('ted') or to.lower().startswith('ted'):
            if edata['followers'] >= ted_weight:
                g2.add_edge(f, to, edata)
        elif edata['followers'] >= weight:
            g2.add_edge(f, to, edata)
    return g2

print('g: ', len(g))
core = trim_degrees_ted(g, degree=235, ted_degree=1)
print('core after node pruning: ', len(core))
core = trim_edges_ted(core, weight=250000, ted_weight=35000)
print('core after edge pruning: ', len(core))

nodeset_types = { 'TED': lambda s: s.lower().startswith('ted'), 'Not TED': lambda s: not s.lower().startswith('ted') }

nodesets = defaultdict(list)

for nodeset_typename, nodeset_test in nodeset_types.iteritems():
    nodesets[nodeset_typename] = [ n for n in core.nodes() if nodeset_test(n) ]

pos = nx.spring_layout(core) # compute layout

colours = ['red','green']
colourmap = {}

plt.figure(figsize=(18,18))
plt.axis('off')

# draw nodes
i = 0
alphas = {'TED': 0.6, 'Not TED': 0.4}
for k in nodesets.keys():
    ns = [ math.log10(hfollowers[n]+1) * 80 for n in nodesets[k] ]
    print(k, len(ns))
    nx.draw_networkx_nodes(core, pos, nodelist=nodesets[k], node_size=ns, node_color=colours[i], alpha=alphas[k])
    colourmap[k] = colours[i]
    i += 1
print('colourmap: ', colourmap)

# draw edges
nx.draw_networkx_edges(core, pos, width=0.5, alpha=0.5)

# draw labels
alphas = { 'TED': 1.0, 'Not TED': 0.5}
for k in nodesets.keys():
    for n in nodesets[k]:
        x, y = pos[n]
        plt.text(x, y+0.02, s=n, alpha=alphas[k], horizontalalignment='center', fontsize=9)

