"""
Created on Sun Nov 06 16:08:25 2016

@author: Weiyan Sun 
"""

import pyomo
import pandas
import pyomo.opt
import pyomo.environ as pe
import networkx



class mst:
	"""A class to find Minimum Spanning Tree using a row-generation algorithm."""
	def __init__(self,df_name="mst.csv"):
		self.df=pandas.read_csv(df_name)
		
		# one way to get unique nodes
		# do this before we set_index
		self.node=list(set(self.df['startNode']).union(set(self.df['destNode'])))
		# another way, seems to be easilier 
		#m.node = set( list( node_arc.startNode ) + list(node_arc.destNode) )

		self.df.set_index(['startNode' ,'destNode'],inplace=True)
		self.createModel()

	def createModel(self):
		self.m=pe.ConcreteModel()
		# Create set
		self.m.arc_set=pe.Set(initialize=self.df.index,dimen=2)

		# Create variable # don't use dimen parameter here, only use it when creating set
		self.m.Y=pe.Var(self.m.arc_set,domain=pe.Binary) # pe.Binary

		# Create obj. In the function, only m doesn't need self since this is what we pass in
		def obj_rule(m):
		    return sum(self.df.loc[e,"dist"]*m.Y[e] for e in self.m.arc_set)
		self.m.OBJ=pe.Objective(rule=obj_rule,sense=pe.minimize)

		# Create constraint rules		
		def tot_edge_rule(m):
		    return sum(m.Y[e] for e in m.arc_set)==len(self.node)-1

		self.m.TotEdge=pe.Constraint(rule=tot_edge_rule)

		def convertYsToNetworkx(m):
			ans=networkx.Graph()
			# get the edges that have value 1
			pick_edges=[e for e in m.arc_set if m.Y[e].value==1.0]
			ans.add_edges_from(pick_edges)
			return ans

		def createConstForCC(m,cc):
			return sum(m.Y[e] for e in m.arc_set if (e[0] in cc.nodes()) and (e[1] in cc.nodes()))<=len(cc.nodes())-1

		self.m.ccConstraints=pe.ConstraintList()

		done=False

		while done==False:
			solver=pyomo.opt.SolverFactory("cplex")
			results = solver.solve(self.m, tee=True, keepfiles=False, options_string="mip_tolerances_integrality=1e-9 mip_tolerances_mipgap=0")
			graph=convertYsToNetworkx(self.m)
			# in graph theory, connected component can be thinked as closed communication class in DTMC
			# so ccs contains all the connected components (subgraphs) objects.
			ccs=list(networkx.connected_component_subgraphs(graph))
			for cc in ccs:
				# this cc is one connected component, which is a graph object. 
				print createConstForCC(self.m,cc)
				# Now we want to add this constraint to our model, however, using traditional way is very complex for several reasons:
				# add a expression 
				self.m.ccConstraints.add(createConstForCC(self.m,cc))
			
			# stop rule: when the connected component is itself the whole graph
			if (ccs[0].number_of_nodes()==len(self.node)):
				done=True


if __name__ == '__main__':
	mst = mst()

