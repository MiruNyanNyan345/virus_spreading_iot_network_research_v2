import networkx as nx
import random


def replace_path(network, source, target):
    try:
        new_path = nx.shortest_path(G=network, source=source, target=target)
    except Exception as e:
        return False,  e
    return True, new_path


def count_time_step(path):
    return len(path) - 1


def largest_separation(network):
    component = list(nx.connected_components(network))
    return list(max(component, key=lambda x: len(x)))


def generate_packet(network, case_id):
    # get the source node and target node from the largest cluster of the network
    biggest_cluster = largest_separation(network=network)
    random_case = random.sample(biggest_cluster, 2)
    source = random_case[0]
    target = random_case[1]
    path = nx.shortest_path(G=network, source=source, target=target)
    packet = {"caseID": case_id,
              "source": source, "target": target, "path": path, "time_steps": count_time_step(path),
              "status": None, "reason": None,
              "replacement_history": None,
              "network_nodes": None, "remove_nodes": None,
              "achieved_packet": None,
              "fractional_size": None, "fraction_of_remove": None,
              "degree": None, "betweenness": None, "closeness": None}
    return packet
