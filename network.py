import networkx as nx
import matplotlib.pyplot as plt

import random


def draw_network(network, title, folder_path):
    plt.figure(figsize=(10, 7))
    plt.title(title)
    nx.draw_networkx(network, node_color='grey', node_size=700, font_color="white", edge_color='grey')
    plt.savefig("{}/{}.png".format(folder_path, title))
    plt.show()


def init_ba_network(n, m, nauth, experiments, folder_path):
    network = nx.barabasi_albert_graph(n, m)
    # draw_network(network, title="Initial-BA-Network-{}".format(experiments))
    # "{}_n{}_{}auth_{}edges_FracRemove"

    num_auth_nodes = int(round(n * (nauth / 100), 0))
    auth_nodes = []
    for n in random.sample(network.nodes, num_auth_nodes):
        auth_nodes.append(n)
    draw_network(network=network,
                 title="BA_N{}_{}auth_{}edges_initial_{}".format(len(network.nodes), len(auth_nodes), m, experiments),
                 folder_path=folder_path)
    return network, auth_nodes


def init_power_law_cluster_graph(n, m, p, nauth, experiments, folder_path):
    # n (int) – the number of nodes
    # m (int) – the number of random edges to add for each new node
    # p (float,) – Probability of adding a triangle after adding a random edge
    network = nx.powerlaw_cluster_graph(n=n, m=m, p=p)
    num_auth_nodes = int(round(n * (nauth / 100), 0))
    auth_nodes = []
    for n in random.sample(network.nodes, num_auth_nodes):
        auth_nodes.append(n)
    draw_network(network=network,
                 title="PowerLaw_N{}_{}auth_{}edges_initial_{}".format(len(network.nodes),
                                                                       len(auth_nodes), m, experiments),
                 folder_path=folder_path)

    return network, auth_nodes


def init_dual_barabasi_albert_graph(n, m1, m2, p, nauth, experiments, folder_path):
    network = nx.dual_barabasi_albert_graph(n=n, m1=m1, m2=m2, p=p)
    num_auth_nodes = int(round(n * (nauth / 100), 0))
    auth_nodes = []
    for n in random.sample(network.nodes, num_auth_nodes):
        auth_nodes.append(n)
    draw_network(network=network,
                 title="PowerLaw_N{}_{}auth_{}edges1_{}edges2_initial_{}".format(len(network.nodes),
                                                                                 len(auth_nodes), m1, m2, experiments),
                 folder_path=folder_path)

    return network, auth_nodes
