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
            (graph, num_buses, size_bus, constraints)
            graph - the graph as a NetworkX object
            num_buses - an integer representing the number of buses you can allocate to
            size_buses - an integer representing the number of students that can fit on a bus
            constraints - a list where each element is a list vertices which represents a single rowdy group
    '''
    graph = nx.read_gml(folder_name + "/graph.gml")
    parameters = open(folder_name + "/parameters.txt")
    num_buses = int(parameters.readline())
    size_bus = int(parameters.readline())
    constraints = []
    
    for line in parameters:
        line = line[1: -2]
        curr_constraint = [num.replace("'", "") for num in line.split(", ")]
        constraints.append(curr_constraint)

    return graph, num_buses, size_bus, constraints

def acc_prob(old_cost, new_cost, temp):
    if new_cost < old_cost:
        return 1.0
    else:
        return math.exp((old_cost-new_cost)/temp)

def move(state, num_buses, size_buses):
    # Choose two buses, either switch two students, or pick one to move to the other.
    copy_state = deepcopy(state)
    swap_or_move = random.randint(0, 1)

    bus1 = random.randint(0, num_buses - 1)
    bus2 = random.randint(0, num_buses - 1)
    student1 = random.randint(0, len(copy_state[bus1])-1)
    student2 = random.randint(0, len(copy_state[bus2])-1)

    if swap_or_move == 0:
        copy_state[bus1][student1], copy_state[bus2][student2] = copy_state[bus2][student2], copy_state[bus1][student1]
    else:
        
        if len(copy_state[bus1]) == size_buses or len(copy_state[bus2]) <= 1:
           copy_state[bus1][student1], copy_state[bus2][student2] = copy_state[bus2][student2], copy_state[bus1][student1]
        else:
            move_student = copy_state[bus2][student2]
            copy_state[bus2].remove(move_student)
            copy_state[bus1].append(move_student)
    return copy_state

def anneal(sol, num_buses, size_buses, graph, constraints):
    old_cost = cost(sol, graph, constraints)
    temp = 1.0
    temp_min = 0.00001
    alpha = 0.90
    while temp > temp_min:
        for i in range(100):
            new_sol =  move(sol, num_buses, size_buses)
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
    bus_assignments = {}
    for bus in range(len(state)):
        for student in state[bus]:
            bus_assignments[student] = bus
    total_edges = graph_dup.number_of_edges()

    for i in range(len(constraints)):
        buses = set()
        for student in constraints[i]:
            buses.add(bus_assignments[student])
        if len(buses) <= 1:
            for student in constraints[i]:
                if student in graph_dup:
                    graph_dup.remove_node(student)
    
    score = 0
    for edge in graph_dup.edges():
        if bus_assignments[edge[0]] == bus_assignments[edge[1]]:
            score += 1
    final_score = 1 - (score / total_edges)
    return final_score



def initial(graph, num_buses, size_bus):
    buses = []
    bus_nums = [x for x in range(num_buses)]
    for i in range(num_buses):
        buses.append([])
    students = list(graph.nodes)
    first_students = random.sample(students, num_buses)
    for i in range(len(first_students)):
        students.remove(first_students[i])
        buses[i].append(first_students[i])

    for s in students:
        bus = random.choice(bus_nums)
        buses[bus].append(s)
        if len(buses[bus]) == size_bus:
            bus_nums.remove(bus)
    return buses

def main():
    '''
        Main method which iterates over all inputs and calls `solve` on each.
        The student should modify `solve` to return their solution and modify
        the portion which writes it to a file to make sure their output is
        formatted correctly.
    '''
    size_categories = ["medium"] #["small", "medium", "large"]
    if not os.path.isdir(path_to_outputs):
        os.mkdir(path_to_outputs)

    for size in size_categories:
        category_path = path_to_inputs + "/" + size
        output_category_path = path_to_outputs + "/" + size
        category_dir = os.fsencode(category_path)
        
        if not os.path.isdir(output_category_path):
            os.mkdir(output_category_path)

        tracker = open(size + "tracker.txt", 'w')
        tracker.close()

        for input_folder in os.listdir(category_dir):
            input_name = os.fsdecode(input_folder) 
            print(input_name)
            graph, num_buses, size_bus, constraints = parse_input(category_path + "/" + input_name)

            
            min_state = initial(graph, num_buses, size_bus)
            min_cost = cost(min_state, graph, constraints)

            for i in range(3):
                temp_state = initial(graph, num_buses, size_bus)
                result, fin_cost = anneal(temp_state, num_buses, size_bus, graph, constraints)
                if fin_cost < min_cost:
                    min_cost = fin_cost
                    min_state = result
                
                print("Got: " + str(1-fin_cost), "Current Best: " + str(1-min_cost))

            print("Final score for " + input_name + ": " + str(1-min_cost))
            output_file = open(output_category_path + "/" + input_name + ".out", "w")
            tracker = open(size + "tracker.txt", 'a+')
            #TODO: modify this to write your solution to your 
            #      file properly as it might not be correct to 
            #      just write the variable solution to a file
        
            for i in min_state:
                output_file.write(str(list(i)) + '\n')

            tracker.write(input_name + " " + str(1-min_cost) + '\n')

            output_file.close()
            tracker.close()

if __name__ == '__main__':
    main()




