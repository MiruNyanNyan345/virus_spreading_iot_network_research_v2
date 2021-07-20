import networkx as nx

import pandas as pd
import numpy as np
import time
import copy
import logging
import os
import argparse
import datetime

import utils
import node
import network
import measurement as measure
import plotGraph
import modification as modify


def simulation_largest_separation(nk, nodes, simulation_limit,
                                  auth_nodes, removal_method, nk_type, experiments,
                                  num_init_edges, result_folder_path):
    print("Largest Separation Simulation")
    print("Network Type: {}, Removal Method: {}".format(nk_type, removal_method))
    print("Authenticated Nodes: {}".format(auth_nodes))

    # number of initial nodes in the largest isolation of the network
    # it is equal to the number of initial network nodes
    num_init_nodes = len(modify.largest_separation(nk))

    # Initialize the case id of the packet
    case_id = 0

    # Initialize the list for storing the packets
    packets = []

    # Number of total removed nodes
    total_remove_nodes = []

    while len(modify.largest_separation(nk)) > num_init_nodes / 100 * simulation_limit:
        print("Entire Network Remaining Nodes: {} : Largest Isolation Nodes: {}".format(
            (len(nk.nodes) / num_init_nodes) * 100, len(modify.largest_separation(nk))))

        # Removing nodes according to the centrality measurement of current task
        centrality_remove_node = node.remove_nodes(network=nk, removal_type=removal_method, auth_nodes=auth_nodes)
        nk = node.remove_network_node(network=nk, node=centrality_remove_node)
        total_remove_nodes.append(centrality_remove_node)

        # Removing isolated nodes from network
        isolated_nodes = node.remove_nodes(network=nk, removal_type="Isolation", auth_nodes=auth_nodes)
        for n in isolated_nodes:
            nk = node.remove_network_node(network=nk, node=n)
            total_remove_nodes.append(n)

        # require the number of nodes in largest separation of network >= 2
        if len(modify.largest_separation(network=nk)) >= 2:
            # Generate a packet for current iteration
            packet = modify.generate_packet(network=nk, case_id=case_id)
        else:
            break

        # Update "network nodes" column of current packet
        packet["network_nodes"] = len(nk.nodes)
        # Update "remove nodes" column of current packet
        packet["remove_nodes"] = {"Highest_{}".format(removal_method): centrality_remove_node,
                                  "Isolated_Nodes": isolated_nodes}

        # Calculate three centrality of the network in the current task
        degree_mean = measure.network_degree(network=nk, val_type="mean", auth_nodes=auth_nodes)
        betweenness_mean = measure.network_degree(network=nk, val_type="mean", auth_nodes=auth_nodes)
        closeness_mean = measure.network_degree(network=nk, val_type="mean", auth_nodes=auth_nodes)

        achieved_packets = []
        # Packet's path simulation
        for idx, pkt in enumerate(packets):
            if pkt["status"]:
                continue
            else:
                remaining_ts = (pkt["time_steps"] + pkt["caseID"]) - packet["caseID"]

                if remaining_ts > 0:
                    checking_node_idx = len(pkt["path"]) - remaining_ts - 1
                    checking_node = pkt["path"][checking_node_idx]

                    if checking_node == pkt["target"]:
                        # target node of the packet has been removed from network,
                        if checking_node not in nk.nodes:
                            pkt["status"] = "Failed"
                            pkt["reason"] = "Target node has been removed"
                            continue
                        elif nodes[checking_node].status == "FULL":
                            pkt["status"] = "Failed"
                            pkt["reason"] = "Target node has been filled"
                            continue
                        else:
                            pass
                    else:
                        pass

                    if checking_node not in nk.nodes or nodes[checking_node].status == "FULL":
                        if pkt["source"] not in nk.nodes or nodes[pkt["source"]].status == "FULL":
                            replace_source = 1
                            while pkt["source"] not in nk.nodes and nodes[pkt["source"]].status == "FULL":
                                # if target replace node is the target node of the packet's path, the packet is failed
                                if replace_source == len(pkt["path"]) - 1:
                                    pkt["status"] = "Failed"
                                    pkt["reason"] = "Cannot find source node replacement"
                                else:
                                    # move source node to next node of the packet's path
                                    pkt["source"] = pkt["path"][replace_source]
                                    pkt["path"] = modify.replace_path(network=nk, source=pkt["source"],
                                                                      target=pkt["target"])
                                    pkt["time_steps"] = modify.count_time_step(path=pkt["path"])
                                    replace_source += 1
                        elif pkt["target"] not in nk.nodes:
                            pkt["status"] = "Failed"
                            pkt["reason"] = "Target node has been removed"
                        elif nodes[pkt["target"]].status == "FULL":
                            pkt["status"] = "Failed"
                            pkt["reason"] = "Target node has been filled"
                        else:
                            replace_path_success, replace_path_result = modify.replace_path(network=nk,
                                                                                            source=pkt["source"],
                                                                                            target=pkt["target"])
                            if replace_path_success:
                                if checking_node not in nk.nodes:
                                    pkt["replacement_history"] = {"current_packet": packet["caseID"],
                                                                  "caseID": pkt["caseID"],
                                                                  "original": pkt["path"],
                                                                  "replacement": replace_path_result,
                                                                  "replace_reason": "{} does not exist in network"
                                                                      .format(checking_node)}
                                elif nodes[checking_node].status == "FULL":
                                    pkt["replacement_history"] = {"current_packet": packet["caseID"],
                                                                  "caseID": pkt["caseID"],
                                                                  "original": pkt["path"],
                                                                  "replacement": replace_path_result,
                                                                  "replace_reason": "{}'s buffer is filled".format(
                                                                      checking_node)}

                                pkt["path"] = replace_path_result
                                pkt["time_steps"] = modify.count_time_step(path=pkt["path"])
                            else:
                                pkt["status"] = "Failed"
                                pkt["reason"] = replace_path_result
                    else:
                        pass
                else:
                    achieved_packets.append(pkt["caseID"])
                    pkt["status"] = "Successful"
            packet["achieved_packet"] = achieved_packets

        # Update the dictionary
        packet["fractional_size"] = len(modify.largest_separation(nk)) / num_init_nodes
        # packet["fraction_of_remove"] = (num_init_nodes - len(modify.largest_separation(nk))) / num_init_nodes
        packet["fraction_of_remove"] = ((len(nk.nodes) - len(modify.largest_separation(network=nk))) +
                                        len(total_remove_nodes)) / num_init_nodes
        packet["degree"] = degree_mean
        packet["betweenness"] = betweenness_mean
        packet["closeness"] = closeness_mean

        # Appending the packet into the list of packets
        packets.append(packet)
        case_id += 1

    df = pd.DataFrame(data=packets, columns=["caseID",
                                             "source", "target", "path", "time_steps",
                                             "status", "reason",
                                             "replacement_history",
                                             "network_nodes", "remove_nodes",
                                             "achieved_packet",
                                             "fractional_size", "fraction_of_remove",
                                             "degree", "betweenness", "closeness"])
    print(result_folder_path)
    df.to_csv('{}/{}_n{}_{}auth_{}edges_{}_{}.csv'.format(result_folder_path, nk_type, num_init_nodes, len(auth_nodes),
                                                          num_init_edges,
                                                          removal_method,
                                                          experiments))


def simulation(nk, nodes, simulation_limit, auth_nodes, removal_method, nk_type, experiments,
               num_init_edges, result_folder_path):
    print("Network Type: {}, Removal Method: {}".format(nk_type, removal_method))
    print("Authenticated Nodes: {}".format(auth_nodes))

    # number of initial network nodes
    num_init_nodes = len(nk.nodes)

    # Initialize the case id of the packet
    case_id = 0

    # Initialize the list for storing the packets
    packets = []

    # Number of total removed nodes
    total_remove_nodes = []

    while len(nk.nodes) > num_init_nodes / 100 * simulation_limit:
        print("Remaining Nodes: {}%".format((len(nk.nodes) / num_init_nodes) * 100))

        iter_remove_nodes = []

        # Removing nodes according to the centrality measurement of current task
        centrality_remove_node = node.remove_nodes(network=nk, removal_type=removal_method, auth_nodes=auth_nodes)
        nk = node.remove_network_node(network=nk, node=centrality_remove_node)
        total_remove_nodes.append(centrality_remove_node)

        # Removing isolated nodes from network
        isolated_nodes = node.remove_nodes(network=nk, removal_type="Isolation", auth_nodes=auth_nodes)
        for n in isolated_nodes:
            nk = node.remove_network_node(network=nk, node=n)
            total_remove_nodes.append(n)

        # require the number of nodes in largest separation of network >= 2
        if len(modify.largest_separation(network=nk)) >= 2:
            # Generate a packet for current iteration
            packet = modify.generate_packet(network=nk, case_id=case_id)
        else:
            break

        # Update "network nodes" column of current packet
        packet["network_nodes"] = len(nk.nodes)
        # Update "remove nodes" column of current packet
        packet["remove_nodes"] = {"Highest_{}".format(removal_method): centrality_remove_node,
                                  "Isolated_Nodes": isolated_nodes}

        # Calculate three centrality of the network in the current task
        degree_mean = measure.network_degree(network=nk, val_type="mean", auth_nodes=auth_nodes)
        betweenness_mean = measure.network_degree(network=nk, val_type="mean", auth_nodes=auth_nodes)
        closeness_mean = measure.network_degree(network=nk, val_type="mean", auth_nodes=auth_nodes)

        achieved_packets = []
        # Packet's path simulation
        for idx, pkt in enumerate(packets):
            if pkt["status"]:
                continue
            else:
                remaining_ts = (pkt["time_steps"] + pkt["caseID"]) - packet["caseID"]

                if remaining_ts > 0:
                    checking_node_idx = len(pkt["path"]) - remaining_ts - 1
                    checking_node = pkt["path"][checking_node_idx]

                    if checking_node == pkt["target"]:
                        # target node of the packet has been removed from network,
                        if checking_node not in nk.nodes:
                            pkt["status"] = "Failed"
                            pkt["reason"] = "Target node has been removed"
                            continue
                        elif nodes[checking_node].status == "FULL":
                            pkt["status"] = "Failed"
                            pkt["reason"] = "Target node has been filled"
                            continue
                        else:
                            pass
                    else:
                        pass

                    if checking_node not in nk.nodes or nodes[checking_node].status == "FULL":
                        if pkt["source"] not in nk.nodes or nodes[pkt["source"]].status == "FULL":
                            replace_source = 1
                            while pkt["source"] not in nk.nodes and nodes[pkt["source"]].status == "FULL":
                                # if target replace node is the target node of the packet's path, the packet is failed
                                if replace_source == len(pkt["path"]) - 1:
                                    pkt["status"] = "Failed"
                                    pkt["reason"] = "Cannot find source node replacement"
                                else:
                                    # move source node to next node of the packet's path
                                    pkt["source"] = pkt["path"][replace_source]
                                    pkt["path"] = modify.replace_path(network=nk, source=pkt["source"],
                                                                      target=pkt["target"])
                                    pkt["time_steps"] = modify.count_time_step(path=pkt["path"])
                                    replace_source += 1
                        elif pkt["target"] not in nk.nodes:
                            pkt["status"] = "Failed"
                            pkt["reason"] = "Target node has been removed"
                        elif nodes[pkt["target"]].status == "FULL":
                            pkt["status"] = "Failed"
                            pkt["reason"] = "Target node has been filled"
                        else:
                            replace_path_success, replace_path_result = modify.replace_path(network=nk,
                                                                                            source=pkt["source"],
                                                                                            target=pkt["target"])
                            if replace_path_success:
                                if checking_node not in nk.nodes:
                                    pkt["replacement_history"] = {"current_packet": packet["caseID"],
                                                                  "caseID": pkt["caseID"],
                                                                  "original": pkt["path"],
                                                                  "replacement": replace_path_result,
                                                                  "replace_reason": "{} does not exist in network"
                                                                      .format(checking_node)}
                                elif nodes[checking_node].status == "FULL":
                                    pkt["replacement_history"] = {"current_packet": packet["caseID"],
                                                                  "caseID": pkt["caseID"],
                                                                  "original": pkt["path"],
                                                                  "replacement": replace_path_result,
                                                                  "replace_reason": "{}'s buffer is filled".format(
                                                                      checking_node)}

                                pkt["path"] = replace_path_result
                                pkt["time_steps"] = modify.count_time_step(path=pkt["path"])
                            else:
                                pkt["status"] = "Failed"
                                pkt["reason"] = replace_path_result
                    else:
                        pass
                else:
                    achieved_packets.append(pkt["caseID"])
                    pkt["status"] = "Successful"
            packet["achieved_packet"] = achieved_packets

        # Update the dictionary
        packet["fractional_size"] = len(modify.largest_separation(nk)) / num_init_nodes
        # packet["fraction_of_remove"] = (num_init_nodes - len(modify.largest_separation(nk))) / num_init_nodes
        packet["fraction_of_remove"] = ((len(nk.nodes) - len(modify.largest_separation(network=nk))) +
                                        len(total_remove_nodes)) / num_init_nodes
        packet["degree"] = degree_mean
        packet["betweenness"] = betweenness_mean
        packet["closeness"] = closeness_mean

        # Appending the packet into the list of packets
        packets.append(packet)
        case_id += 1

    df = pd.DataFrame(data=packets, columns=["caseID",
                                             "source", "target", "path", "time_steps",
                                             "status", "reason",
                                             "replacement_history",
                                             "network_nodes", "remove_nodes",
                                             "achieved_packet",
                                             "fractional_size", "fraction_of_remove",
                                             "degree", "betweenness", "closeness"])
    # df.to_csv('result_datasets/{}_{}_{}.csv'.format(nk_type, removal_method, experiments), index=False)
    print(result_folder_path)
    df.to_csv('{}/{}_n{}_{}auth_{}edges_{}_{}.csv'.format(result_folder_path, nk_type, num_init_nodes, len(auth_nodes),
                                                          num_init_edges,
                                                          removal_method,
                                                          experiments))


def demo(nk, simulation_limit, buffer_limit, auth_nodes, network_type, experiments, num_of_nodes, edges,
         result_folder_path, plots_folder_path):
    # num_init_nodes = len(nk.nodes)

    # saving initial network's nodes as object
    # given each node a buffer
    nodes = node.init_network_nodes(network=nk, buffer_limit=buffer_limit)

    # copy thr initial network, as well as the nodes, for the 3 type of measurement simulation
    nodes_copies = []
    network_copies = []
    for i in range(3):
        nodes_copies.append(copy.deepcopy(nodes))
        network_copies.append(copy.deepcopy(nk))

    # each simulation consists of "Degree", "Betweenness", and "Closeness".
    removal_methods = ["Degree", "Betweenness", "Closeness"]

    plot_df_lst = [
        '{}/{}_n{}_{}auth_{}edges_Degree_{}.csv'.format(result_folder_path,
                                                        network_type, num_of_nodes, len(auth_nodes), edges,
                                                        experiments),
        '{}/{}_n{}_{}auth_{}edges_Betweenness_{}.csv'.format(result_folder_path,
                                                             network_type, num_of_nodes, len(auth_nodes),
                                                             edges,
                                                             experiments),
        '{}/{}_n{}_{}auth_{}edges_Closeness_{}.csv'.format(result_folder_path,
                                                           network_type, num_of_nodes, len(auth_nodes),
                                                           edges,
                                                           experiments), ]
    plot_label_lst = [
        '{}-degree'.format(network_type),
        '{}-betweenness'.format(network_type),
        '{}-closeness'.format(network_type)
    ]

    for removal_method in removal_methods:
        sim_start = time.time()
        nodes = nodes_copies.pop()
        nk = network_copies.pop()

        # simulation(nk=nk, nodes=nodes,
        #            simulation_limit=simulation_limit, auth_nodes=auth_nodes,
        #            removal_method=removal_method, nk_type=network_type, experiments=experiments, num_init_edges=edges,
        #            result_folder_path=result_folder_path)

        simulation_largest_separation(nk=nk, nodes=nodes,
                                      simulation_limit=simulation_limit, auth_nodes=auth_nodes,
                                      removal_method=removal_method, nk_type=network_type, experiments=experiments,
                                      num_init_edges=edges,
                                      result_folder_path=result_folder_path)

        sim_end = time.time()
        logging.info("{} simulation running time is {}. \n".format(removal_method, sim_end - sim_start))
        print("{} simulation running time is {}. \n".format(removal_method, sim_end - sim_start))

    plot_df_lst_frac_size = copy.deepcopy(plot_df_lst)
    plot_df_lst_frac_remove = copy.deepcopy(plot_df_lst)
    plotGraph.fraction_remove(plot_df_lst_frac_remove, plot_label_lst,
                              "{}_n{}_{}auth_{}edges_FracRemove_{}"
                              .format(network_type, num_of_nodes, len(auth_nodes), edges, experiments),
                              folder_path=plots_folder_path)
    plotGraph.fraction_size(plot_df_lst_frac_size, plot_label_lst,
                            "{}_n{}_{}auth_{}edges_FracSize_{}"
                            .format(network_type, num_of_nodes, len(auth_nodes), edges, experiments),
                            folder_path=plots_folder_path)


def main():
    parser = argparse.ArgumentParser(description="Simulation Program")
    parser.add_argument("--experiment_name", required=True, type=str)
    parser.add_argument("--graph_config", required=True, nargs='+')
    parser.add_argument("--experiment_times", required=True, type=int)
    parser.add_argument("--authenticated_nodes_percentage", required=True, type=float)
    parser.add_argument("--simulation_limit", required=True, type=float)
    # args.add_argument("graph_type", required=True)
    args = parser.parse_args()

    # set the experiment name and it will be the folder name of the results' and plots' folder
    # experiment_name = "LI_BA_15_auth_nodes_{}".format(current_time)
    experiment_name = args.experiment_name

    graph_config = args.graph_config
    # Checking whether the configuration of the target simulation graph is correct
    correct_g_config, g_config_result = utils.check_args_graph_config(graph_config)
    graph_config_dict = None
    if not correct_g_config:
        parser.error(g_config_result)
    else:
        graph_config_dict = g_config_result

    # Experiment Times
    experiments = args.experiment_times

    # get the experiment starting time
    # current_time = int(time.time())
    current_time = datetime.date.today().strftime("%Y%m%d")

    # percentage of how many nodes are authenticated
    n_auth = args.authenticated_nodes_percentage

    # the threshold of remaining nodes to stop the simulation
    simulation_limit = args.simulation_limit

    plots_folder = f"{experiment_name}_plots_{current_time}"
    result_datasets_folder = f"{experiment_name}_result_datasets_{current_time}"
    if not os.path.exists(plots_folder):
        os.makedirs(plots_folder)
    if not os.path.exists(result_datasets_folder):
        os.makedirs(result_datasets_folder)

    # initial the log file
    # logging.basicConfig(filename="experiments_{}.log".format(experiment_name), level=logging.INFO)
    logging.basicConfig(filename=f"{experiment_name}_experiments_{current_time}.log", level=logging.INFO)

    for i in range(experiments):
        logging.info(f"Experiment {i} started.")
        # Graph Type
        g = graph_config_dict["g"]
        # Initialized Network
        experiment_nk = None
        # Authenticated selected from Initialized Network
        experiment_auth_nodes = None

        if g == "barabasi_albert":
            # Number of network nodes
            n = graph_config_dict["n"]
            # Number of network edges
            m = graph_config_dict["m"]
            experiment_nk, experiment_auth_nodes = network.init_ba_network(n=n, m=m, nauth=n_auth, experiments=i,
                                                                           folder_path=plots_folder)
        elif g == "powerlaw_cluster":
            # Number of network nodes
            n = graph_config_dict["n"]
            # Number of network edges
            m = graph_config_dict["m"]
            # Probability of adding a triangle after adding a random edge
            p = graph_config_dict["p"]
            experiment_nk, experiment_auth_nodes = network.init_power_law_cluster_graph(n=n, m=m, p=p,
                                                                                        nauth=n_auth, experiments=i,
                                                                                        folder_path=plots_folder)
        elif g == "dual_barabasi_albert":
            # Number of nodes
            n = graph_config_dict["n"]
            # Number of edges to attach from a new node to existing nodes with probability 𝑝
            m1 = graph_config_dict["m1"]
            #  Number of edges to attach from a new node to existing nodes with probability 1−𝑝
            m2 = graph_config_dict["m2"]
            # The probability of attaching 𝑚1 edges (as opposed to 𝑚2 edges)
            p = graph_config_dict["p"]
            experiment_nk, experiment_auth_nodes = network.init_dual_barabasi_albert_graph(n=n, m1=m1, m2=m2, p=p,
                                                                                           nauth=n_auth, experiments=i,
                                                                                           folder_path=plots_folder)

        nk_type = graph_config_dict["g"]
        sim_start_time = time.time()
        demo(nk=experiment_nk, simulation_limit=simulation_limit, buffer_limit=5, auth_nodes=experiment_auth_nodes,
             network_type=nk_type, experiments=i,
             num_of_nodes=n, edges=m,
             result_folder_path=result_datasets_folder, plots_folder_path=plots_folder)
        sim_end_time = time.time()
        logging.info(f"Experiment {i} Running Time: {sim_end_time - sim_start_time}")
        logging.info(f"Experiment {i} ended. \n")

    # experiment times
    # experiments = 10
    # a list of percentage of how many nodes are authenticated
    # list(reversed(range(11)))
    # n_auth = [15]

    # the simulation limit to stop the simulation
    # simulation_limit = 20

    # for a in n_auth:
    #     for i in range(experiments):
    #         logging.info("Experiment {} started.".format(i))
    #         # ba network - number of nodes
    #         ba_n = 1000
    #         # ba network - number of edges to attach from a new node to existing nodes
    #         ba_m = 3
    #
    #         # power law cluster -  the number of nodes
    #         power_law_cluster_n = 100
    #         # power law cluster - the number of random edges to add for each new node
    #         power_law_cluster_m = 2
    #         # power law cluster - Probability of adding a triangle after adding a random edge
    #         power_law_cluster_p = 0.5
    #
    #         # network_type = ["BA", "PowerLaw"]
    #         network_type = ["BA"]
    #
    #         network_list = [
    #             network.init_ba_network(n=ba_n,
    #                                     m=ba_m,
    #                                     nauth=a,
    #                                     experiments=i,
    #                                     folder_path=plots_folder),
    #
    #             # network.init_power_law_cluster_graph(n=power_law_cluster_n,
    #             #                                      m=power_law_cluster_m,
    #             #                                      p=power_law_cluster_p,
    #             #                                      nauth=a,
    #             #                                      experiments=i,
    #             #                                      folder_path=plots_folder)
    #         ]
    #
    #         for nk, auth_nodes in network_list:
    #             nk_type = network_type.pop(0)
    #             start = time.time()
    #             demo(nk=nk, simulation_limit=simulation_limit, buffer_limit=5, auth_nodes=auth_nodes,
    #                  network_type=nk_type, experiments=i,
    #                  num_of_nodes=ba_n, edges=ba_m,
    #                  result_folder_path=result_datasets_folder, plots_folder_path=plots_folder)
    #             end = time.time()
    #             logging.info("The running time is {} .".format(end - start))
    #             print("The running time is {} .".format(end - start))
    #             print("")
    #
    #         logging.info("{} experiment ended.\n".format(i))


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
