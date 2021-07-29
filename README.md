# virus_spreading_iot_network_research_v2

## Usage 
* Simulation
  * main.py
* Plotting average graph of simulation results 
  * averagePlot.py
    
### Simulation
+     python3 main.py --experiment_name @experiment_name
                      --graph_config @network parameters (depends on the type of network)
                      --experiment_times @experiment_times
                      --authenticated_nodes_percentage @authenticated_nodes_percentage 
                      --simulation_limit @simulation_limit
#### Simulation Example 
+     python3 main.py --experiment_name TEST_BA 
                      --graph_config barabasi_albert 100 1 
                      --experiment_times 10
                      --authenticated_nodes_percentage 10 
                      --simulation_limit 10
  * Experiment Name is **TEST_BA**
  * Network Type is **barabasi_albert**
  * **100** initial nodes (parameter **N**)
  * **1** edges to attach from a new node to existing nodes nodes (parameter **M**)
  * **10** of experiments
  * **10%** of authenticated nodes
  * When the nodes of the largest cluster in the network is less than **10%** of initial nodes in the initial network, the simulation is stopped. 

### Plotting average graph of simulation results 
+     python3 averagePlot.py --task_name @task_name (String)
                             --target_folder_path @folder path of the target simulation results (String) 
                             --number_of_auth @number of authenticated node in the target simulation (int)
                             --plot_results @do u want to plot the result? (bool)
#### Plotting Example
+     python3 averagePlot.py --task_name TEST_BA 
                             --target_folder_path TEST_BA_result_datasets_20210706  
                             --number_of_auth 10 
                             --plot_results True
  * Task Name is **TEST_BA**
  * Results storing folder is **TEST_BA_result_datasets_20210706**
  * Experiments pre-defined authenticated nodes is **10%**
  * Plotting the average graph? **True == Yes**

**@xxx <-- Change it to the value that you would like to use**

## Prerequisite
* Python 3.6
* NetworkX
* numpy
* pandas
* matplotlib


## Currently Supported Network
* Barabási–Albert model
* Power Law Cluster
* Dual Barabási–Albert model

### Adding new network
1. Go to "network.py" and adding a new method to initialize the network for simulation
2. Go to "utils.py" and adding a new condition about the new network configuration in the function of "check_args_graph_config"
3. Go to "main.py" and adding a new condition about the new network in the function of "main"