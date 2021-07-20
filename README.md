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

### Plotting average graph of simulation results 
+     python3 averagePlot.py --task_name @task_name (String)
                             --target_folder_path @folder path of the target simulation results (String) 
                             --number_of_auth @number of authenticated node in the target simulation (int)
                             --plot_results @do u want to plot the result? (bool)

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