import numpy as np
import networkx as nx
import plot_parallel_betweenness as p_between
import time


def network_degree(network, val_type, auth_nodes):
    if val_type == "mean":
        degree_cen = nx.degree_centrality(network)
        return np.array([degree_cen[key] for key in degree_cen]).mean()
    elif val_type == "lowest":
        degree_cen = nx.degree_centrality(network)
        min_val = min(degree_cen.values())
        min_nodes = [node for node in degree_cen if degree_cen[node] == min_val]
        return min_nodes
    elif val_type == "highest":
        degree_cen = nx.degree_centrality(network)
        # Sorted the degree centrality of nodes in the network
        sorted_degree_cen = sorted(degree_cen.items(), key=lambda x: x[1], reverse=True)
        max_idx = 0
        # remove node cannot be authenticated node
        while sorted_degree_cen[max_idx][0] in auth_nodes:
            max_idx += 1
        max_node = sorted_degree_cen[max_idx][0]
        return max_node


def network_betweenness(network, val_type, auth_nodes):
    if val_type == "mean":
        betweenness_cen = dict(nx.betweenness_centrality(network))
        return np.array([betweenness_cen[val] for val in betweenness_cen]).mean()
    elif val_type == "lowest":
        betweenness_cen = nx.betweenness_centrality(network)
        min_val = min(betweenness_cen.values())
        min_nodes = [node for node in betweenness_cen if betweenness_cen[node] == min_val]
        return min_nodes
    elif val_type == "highest":
        betweenness_cen = nx.betweenness_centrality(network)
        # using parallel computation to calculate the betweenness centrality
        # betweenness_cen = p_between.betweenness_centrality_parallel(G=network)
        # Sorted the betweenness centrality of nodes in the network
        sorted_betweenness_cen = sorted(betweenness_cen.items(), key=lambda x: x[1], reverse=True)
        max_idx = 0
        # remove node cannot be authenticated node
        while sorted_betweenness_cen[max_idx][0] in auth_nodes:
            max_idx += 1
        max_node = sorted_betweenness_cen[max_idx][0]
        return max_node


def network_closeness(network, val_type, auth_nodes):
    if val_type == "mean":
        closeness_cen = dict(nx.nx.closeness_centrality(network))
        return np.array([closeness_cen[val] for val in closeness_cen]).mean()
    elif val_type == "lowest":
        closeness_cen = nx.closeness_centrality(network)
        min_val = min(closeness_cen.values())
        min_nodes = [node for node in closeness_cen if closeness_cen[node] == min_val]
        return min_nodes
    elif val_type == "highest":
        closeness_cen = nx.closeness_centrality(network)
        # Sorted the closeness centrality of nodes in the network
        sorted_closeness_cen = sorted(closeness_cen.items(), key=lambda x: x[1], reverse=True)
        max_idx = 0
        # remove node cannot be authenticated node
        while sorted_closeness_cen[max_idx][0] in auth_nodes:
            max_idx += 1
        max_node = sorted_closeness_cen[max_idx][0]
        return max_node
