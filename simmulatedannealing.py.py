import networkx as nx
import os
from networkx.algorithms import approximation
import math
import random
from copy import deepcopy

###########################################
# Change this variable to the path to 
# the folder containing all three input
# size category folders
###########################################
path_to_inputs = "./all_inputs"

###########################################
# Change this variable if you want
# your outputs to be put in a 
# different folder
###########################################
path_to_outputs = "./outputs"

def parse_input(folder_name):
    '''
        Parses an input and returns the corresponding graph and parameters

        Inputs:
            folder_name - a string representing the path to the input folder

        Outputs:
            (graph, num_groups, size_group, constraints)
            graph - the graph as a NetworkX object
            num_groups - an integer representing the number of groups you can allocate to
            size_groups - an integer representing the number of nodes that can fit on a group
            constraints - a list where each element is a list vertices which represents a constraint
                set where if the set is a subset of one subgraph in the solution, the nodes are ignored.
    '''
    graph = nx.read_gml(folder_name + "/graph.gml")
    parameters = open(folder_name + "/parameters.txt")
    num_groups = int(parameters.readline())
    size_group = int(parameters.readline())
    constraints = []
    
    for line in parameters:
        line = line[1: -2]
        curr_constraint = [num.replace("'", "") for num in line.split(", ")]
        constraints.append(curr_constraint)

    return graph, num_groups, size_group, constraints

def acc_prob(old_cost, new_cost, temp):
    if new_cost < old_cost:
        return 1.0
    else:
        return math.exp((old_cost-new_cost)/temp)

def move(state, num_groups, size_groups):
    # Choose two groups, either switch two nodes, or pick one to move to the other.
    copy_state = deepcopy(state)
    swap_or_move = random.randint(0, 1)

    group1 = random.randint(0, num_groups - 1)
    group2 = random.randint(0, num_groups - 1)
    node1 = random.randint(0, len(copy_state[group1])-1)
    node2 = random.randint(0, len(copy_state[group2])-1)

    if swap_or_move == 0:
        copy_state[group1][node1], copy_state[group2][node2] = copy_state[group2][node2], copy_state[group1][node1]
    else:
        
        if len(copy_state[group1]) == size_groups or len(copy_state[group2]) <= 1:
           copy_state[group1][node1], copy_state[group2][node2] = copy_state[group2][node2], copy_state[group1][node1]
        else:
            move_node = copy_state[group2][node2]
            copy_state[group2].remove(move_node)
            copy_state[group1].append(move_node)
    return copy_state

def anneal(sol, num_groups, size_groups, graph, constraints):
    old_cost = cost(sol, graph, constraints)
    temp = 1.0
    temp_min = 0.00001
    alpha = 0.90
    while temp > temp_min:
        for i in range(100):
            new_sol =  move(sol, num_groups, size_groups)
            new_cost = cost(new_sol, graph, constraints)
            ap = acc_prob(old_cost, new_cost, temp)
            if ap > random.random():
                sol = new_sol
                old_cost = new_cost
        temp = temp * alpha 
        # print(old_cost, temp)
    return sol, old_cost

def cost(state, graph, constraints):
    graph_dup = graph.copy()
    group_assignments = {}
    for group in range(len(state)):
        for node in state[group]:
            group_assignments[node] = group
    total_edges = graph_dup.number_of_edges()

    for i in range(len(constraints)):
        groups = set()
        for node in constraints[i]:
            groups.add(group_assignments[node])
        if len(groups) <= 1:
            for node in constraints[i]:
                if node in graph_dup:
                    graph_dup.remove_node(node)
    
    score = 0
    for edge in graph_dup.edges():
        if group_assignments[edge[0]] == group_assignments[edge[1]]:
            score += 1
    final_score = 1 - (score / total_edges)
    return final_score



def initial(graph, num_groups, size_group):
    groups = []
    group_nums = [x for x in range(num_groups)]
    for i in range(num_groups):
        groups.append([])
    nodes = list(graph.nodes)
    first_nodes = random.sample(nodes, num_groups)
    for i in range(len(first_nodes)):
        nodes.remove(first_nodes[i])
        groups[i].append(first_nodes[i])

    for s in nodes:
        group = random.choice(group_nums)
        groups[group].append(s)
        if len(groups[group]) == size_group:
            group_nums.remove(group)
    return groups

def main():
    '''
        Main method which iterates over all inputs and calls `solve` on each.
        
    '''
    folder_names = ["medium"] 
    if not os.path.isdir(path_to_outputs):
        os.mkdir(path_to_outputs)

    for folder in folder_names:
        category_path = path_to_inputs + "/" + folder
        output_category_path = path_to_outputs + "/" + folder
        category_dir = os.fsencode(category_path)
        
        if not os.path.isdir(output_category_path):
            os.mkdir(output_category_path)

        tracker = open(folder + "tracker.txt", 'w')
        tracker.close()

        for input_folder in os.listdir(category_dir):
            input_name = os.fsdecode(input_folder) 
            print(input_name)
            graph, num_groups, size_group, constraints = parse_input(category_path + "/" + input_name)

            
            min_state = initial(graph, num_groups, size_group)
            min_cost = cost(min_state, graph, constraints)

            for i in range(3): #Runs multiple times, can reduce to 1 for a single iteration 
                temp_state = initial(graph, num_groups, size_group)
                result, fin_cost = anneal(temp_state, num_groups, size_group, graph, constraints)
                if fin_cost < min_cost:
                    min_cost = fin_cost
                    min_state = result
                
                print("Got: " + str(1-fin_cost), "Current Best: " + str(1-min_cost))

            print("Final score for " + input_name + ": " + str(1-min_cost))
            output_file = open(output_category_path + "/" + input_name + ".out", "w")
            tracker = open(folder + "tracker.txt", 'a+')
            for i in min_state:
                output_file.write(str(list(i)) + '\n')

            tracker.write(input_name + " " + str(1-min_cost) + '\n')

            output_file.close()
            tracker.close()

if __name__ == '__main__':
    main()




