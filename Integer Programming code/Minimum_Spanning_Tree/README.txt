minimum spanning tree: a tree that has minimum weights whose edges touch all the nodes in the original graph. 


We will use an algorithm called row generation to implement the Integer programming by Pyomo.
The basic idea of row-generation algorithm in our content is: 

First solve the IP with only one single constraint. 
Second, construct current solution as a graph using networkx
Third, get all the connected components of this graphs.
Check if there is only one connected component which contains whole nodes, stop
Else, go to the fourth step
Fourth, for each subgraph (connected component), check our second constraint.
If it is not satisfied, create this new constraint. 

