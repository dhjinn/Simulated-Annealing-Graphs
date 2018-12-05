# Simulated-Annealing-Graphs
Script to run simulated annealing on finding optimal subgraphs

Takes in an input folder as given by attached folder. 
Currently configured to take in two variables: group number & size, a set of constraint sets, and a networkx graph. 
Outputs a .out file with the subgraphs of students.

Cost optimized on maximizing connectedness of subgraphs while minimizing number of occurrences where a constraint set is a subset of the subgraph.

Also outputs a single file that records percentage of edges maintained overall. 
