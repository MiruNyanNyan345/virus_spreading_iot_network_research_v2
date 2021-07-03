import pandas as pd
import argparse
import os
import copy

import plotGraph


def main():
    args = argparse.ArgumentParser(description="Average Results Calculation")
    args.add_argument("task_name", type=str)
    args.add_argument("target_folder_path", type=str)
    args.add_argument("number_of_auth", type=str)
    args.add_argument("plot_results", type=bool)
    args = args.parse_args()

    # the name of this task
    task_name = args.task_name
    # path of target folder
    target_folder_path = args.target_folder_path
    # number of authenticated nodes
    num_of_auth_nodes = args.number_of_auth
    # do u wanna plot the result as graphs
    plot_results = args.plot_results

    target_folder = target_folder_path

    results_folder = task_name
    if not os.path.exists(results_folder):
        os.makedirs(results_folder)

    degree_l = []
    betweenness_l = []
    closeness_l = []

    for file in os.listdir(target_folder):
        file_split = file.split("_")
        if "Betweenness" in file_split and num_of_auth_nodes + "auth" in file_split:
            betweenness_l.append(file)
        elif "Closeness" in file_split and num_of_auth_nodes + "auth" in file_split:
            closeness_l.append(file)
        elif "Degree" in file_split and num_of_auth_nodes + "auth" in file_split:
            degree_l.append(file)

    for centrality in ["degree", "betweenness", "closeness"]:
        avg_dict = {}
        if centrality == "degree":
            lst = degree_l
        elif centrality == "betweenness":
            lst = betweenness_l
        else:
            lst = closeness_l

        cen_largest_case = 0
        for centrality_l in lst:
            df = pd.read_csv(target_folder + "/" + centrality_l)
            tmp_largest_case = df.caseID.iloc[-1]
            if tmp_largest_case > cen_largest_case:
                cen_largest_case = tmp_largest_case

        for centrality_l in lst:
            df = pd.read_csv(target_folder + "/" + centrality_l)

            last_case = df.iloc[-1].caseID
            for index, row in df.iterrows():
                if row["caseID"] not in avg_dict.keys():
                    avg_dict[row["caseID"]] = {"fractional_size": row["fractional_size"],
                                               "fraction_of_remove": row["fraction_of_remove"]}
                else:
                    avg_dict[row["caseID"]]["fractional_size"] += row["fractional_size"]
                    avg_dict[row["caseID"]]["fraction_of_remove"] += row["fraction_of_remove"]

            if last_case < cen_largest_case:
                last_case_fractional_size = df.loc[df["caseID"] == last_case].fractional_size.item()
                last_case_fraction_of_remove = df.loc[df["caseID"] == last_case].fraction_of_remove.item()
                for i in range(last_case + 1, cen_largest_case + 1):
                    if i not in avg_dict.keys():
                        avg_dict[i] = {"fractional_size": last_case_fractional_size,
                                       "fraction_of_remove": last_case_fraction_of_remove}
                    else:
                        avg_dict[i]["fractional_size"] += last_case_fractional_size
                        avg_dict[i]["fraction_of_remove"] += last_case_fraction_of_remove

        for caseID in avg_dict.keys():
            avg_dict[caseID]['fractional_size'] /= len(lst)
            avg_dict[caseID]['fraction_of_remove'] /= len(lst)
        # for centrality_l in lst:
        #     df = pd.read_csv(target_folder + "/" + centrality_l)
        #     for index, row in df.iterrows():
        #         if row["caseID"] not in avg_dict.keys():
        #             avg_dict[row["caseID"]] = {"fractional_size": row["fractional_size"],
        #                                        "fraction_of_remove": row["fraction_of_remove"],
        #                                        "times": 1}
        #         else:
        #             avg_dict[row["caseID"]]["fractional_size"] += row["fractional_size"]
        #             avg_dict[row["caseID"]]["fraction_of_remove"] += row["fraction_of_remove"]
        #             avg_dict[row["caseID"]]["times"] += 1
        #
        # for caseID in avg_dict.keys():
        #     avg_dict[caseID]['fractional_size'] /= avg_dict[caseID]["times"]
        #     avg_dict[caseID]['fraction_of_remove'] /= avg_dict[caseID]["times"]

        # Convert the centrality dictionary to dataframe
        avg_dict_lst = []
        for caseID in avg_dict.keys():
            avg_dict_lst.append({
                "caseID": int(caseID),
                "fractional_size": float(avg_dict[caseID]["fractional_size"]),
                "fraction_of_remove": float(avg_dict[caseID]["fraction_of_remove"])
            })

        # Initialize the dataframe
        avg_degree_df = pd.DataFrame(data=avg_dict_lst,
                                     columns={'caseID': pd.Series([], dtype='int'),
                                              'fractional_size': pd.Series([], dtype='float'),
                                              'fraction_of_remove': pd.Series([], dtype='float')})
        avg_betweenness_df = pd.DataFrame(data=avg_dict_lst,
                                          columns={'caseID': pd.Series([], dtype='int'),
                                                   'fractional_size': pd.Series([], dtype='float'),
                                                   'fraction_of_remove': pd.Series([], dtype='float')})
        avg_closeness_df = pd.DataFrame(data=avg_dict_lst,
                                        columns={'caseID': pd.Series([], dtype='int'),
                                                 'fractional_size': pd.Series([], dtype='float'),
                                                 'fraction_of_remove': pd.Series([], dtype='float')})
        if centrality == "degree":
            df = avg_degree_df
        elif centrality == "betweenness":
            df = avg_betweenness_df
        else:
            df = avg_closeness_df

        df = df.set_index(['caseID'])
        if centrality == "degree":
            df.to_csv('{}_degree.csv'.format(results_folder + '/' + task_name))
        elif centrality == "betweenness":
            df.to_csv('{}_betweenness.csv'.format(results_folder + '/' + task_name))
        else:
            df.to_csv('{}_closeness.csv'.format(results_folder + '/' + task_name))

    if plot_results:
        avg_graphs(results_folder, task_name, num_of_auth_nodes)
    else:
        pass


def avg_graphs(results_folder, task_name, num_of_auth_nodes):
    plot_data_l = ["{}_degree.csv".format(results_folder + '/' + task_name),
                   "{}_betweenness.csv".format(results_folder + '/' + task_name),
                   "{}_closeness.csv".format(results_folder + '/' + task_name)]
    plot_label_l = ['BA-degree', 'BA-betweenness', 'BA-closeness']

    plot_data_frac_remove = copy.deepcopy(plot_data_l)
    plot_data_frac_size = copy.deepcopy(plot_data_l)

    plotGraph.fraction_size(plot_data_frac_size, plot_label_l,
                            "avg_{}_auth_nodes_fractional_size".format(num_of_auth_nodes),
                            results_folder)
    plotGraph.fraction_remove(plot_data_frac_remove, plot_label_l,
                              "avg_{}_auth_nodes_fraction_remove".format(num_of_auth_nodes),
                              results_folder)


if __name__ == '__main__':
    main()
