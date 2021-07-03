import networkx as nx
import measurement as measure
import copy
import random


class Node():
    def __init__(self, node_name, buffer, buffer_limit, status):
        self.node_name = node_name
        self.buffer = buffer
        self.buffer_limit = buffer_limit
        self.status = status

    def update_buffer(self):
        self.buffer += 1
        if self.buffer == self.buffer_limit:
            self.status = "FULL"

    def print_node_detail(self):
        return "Node Name: " + str(self.node_name) + ", Node Buffer: " + str(
            self.buffer) + ", Node Buffer Limit: " + str(self.buffer_limit) \
               + ", Node Status: " + str(self.status)


# Initialize the network nodes
def init_network_nodes(network, buffer_limit):
    nodes_dict = dict.fromkeys(range(len(network.nodes)), 0)
    for i in range(len(network.nodes)):
        nodes_dict[i] = Node(node_name=i, buffer=0, buffer_limit=buffer_limit, status="FREE")
    return nodes_dict


# Remove node from network
def remove_network_node(network, node):
    network.remove_node(node)
    return network


# Remove the isolation nodes from network
def clear_isolated_node(network, auth_nodes):
    # isolated_nodes = []
    # for node in network.nodes:
    #     if len(list(nx.edges(network, node))) == 0:
    #         if node in auth_nodes:
    #             continue
    #         isolated_nodes.append(node)

    isolated_nodes = list(nx.isolates(network))
    for auth_node in auth_nodes:
        if auth_node in isolated_nodes:
            isolated_nodes.remove(auth_node)
    return isolated_nodes


# Remove a highest selected centrality node from the network
def remove_highest_node(network, measure_type, auth_nodes):
    remove_node = None
    if measure_type == "Degree":
        # highest_degree_nodes = measure.network_degree(network=network, val_type="highest", auth_nodes=auth_nodes)
        # remove_node = random.choice(highest_degree_nodes)
        highest_degree_node = measure.network_degree(network=network, val_type="highest", auth_nodes=auth_nodes)
        remove_node = highest_degree_node
    elif measure_type == "Betweenness":
        # highest_betweenness_nodes = measure.network_betweenness(network=network, val_type="highest", auth_nodes=auth_nodes)
        # remove_node = random.choice(highest_betweenness_nodes)
        highest_betweenness_nodes = measure.network_betweenness(network=network, val_type="highest",
                                                                auth_nodes=auth_nodes)
        remove_node = highest_betweenness_nodes
    elif measure_type == "Closeness":
        # highest_closeness_nodes = measure.network_closeness(network=network, val_type="highest", auth_nodes=auth_nodes)
        # remove_node = random.choice(highest_closeness_nodes)
        highest_closeness_node = measure.network_closeness(network=network, val_type="highest",
                                                           auth_nodes=auth_nodes)
        remove_node = highest_closeness_node
    # if remove_node in auth_nodes:
    #     return None
    # else:
    #     pass
    return remove_node


# Remove node from network
def remove_nodes(network, removal_type, auth_nodes):
    if removal_type == "Degree":
        return remove_highest_node(network=network,
                                   measure_type="Degree",
                                   auth_nodes=auth_nodes)
    elif removal_type == "Betweenness":
        return remove_highest_node(network=network,
                                   measure_type="Betweenness",
                                   auth_nodes=auth_nodes)
    elif removal_type == "Closeness":
        return remove_highest_node(network=network,
                                   measure_type="Closeness",
                                   auth_nodes=auth_nodes)
    elif removal_type == "Isolation":
        return clear_isolated_node(network=network,
                                   auth_nodes=auth_nodes)
