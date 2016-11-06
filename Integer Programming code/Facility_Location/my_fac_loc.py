# coding: utf-8
"""
Created on Sat Nov 05 16:40:25 2016

@author: Weiyan Sun 
"""


import pandas
import networkx
import scipy
import pyomo
import pyomo.opt
import pyomo.environ as pe

class FacLoc:
	def __init__(self,budget=2,disn_csv="distances.csv",loc_csv="nodeData.csv"):
		self.disn=pandas.read_csv(disn_csv)
		self.cus_set=list(set(self.disn.startNode.unique()).union(set(self.disn.destNode.unique())))
		self.loc=pandas.read_csv(loc_csv)
		self.loc_set=list(self.loc.location.unique())
		self.budget=budget

		self.create_network()
		self.Create_model()


	def create_network(self):
		self.g = networkx.Graph()
		for i,row in self.disn.iterrows():
			self.g.add_edge(row['startNode'],row['destNode'],disn=row['dist'])

		self.dist_dict=networkx.algorithms.all_pairs_dijkstra_path_length(self.g, weight='disn')

	def Create_model(self):
		# change the index for convenience
		self.loc.set_index("location",inplace=True)
		self.m=pe.ConcreteModel()
		
		# Create set
		self.m.loc_set=pe.Set(initialize=self.loc_set)
		self.m.cus_set=pe.Set(initialize=self.cus_set)

		# Create variable # don't use dimen parameter here, only use it when creating set
		self.m.Y=pe.Var(self.m.loc_set,domain=pe.Binary) # pe.Binary
		self.m.X=pe.Var(self.m.cus_set*self.m.cus_set,domain=pe.Binary)
		# Create obj
		def obj_rule(m):
			return sum(self.loc.ix[l,"cost"]*m.Y[l] for l in m.loc_set)+sum(m.X[(c,l)]*self.dist_dict[c][l]*self.loc.ix[c,'ncust'] for c in m.cus_set for l in m.loc_set)
		self.m.OBJ=pe.Objective(rule=obj_rule,sense=pe.minimize)

		# take care the sequence of parameter, if here is m, r, n, 
		# when we call this function, we must use res_set*ndoe*set
		
		def cus_rule(m,j):
			return sum(m.X[j,i] for i in m.loc_set)==1

		self.m.CusRule=pe.Constraint(self.m.cus_set,rule=cus_rule)


		# if this is only one constraint instead of loop over all set
		def loc_rule(m):
			return sum(m.Y[i] for i in m.loc_set)==self.budget
		self.m.LocRul=pe.Constraint(rule=loc_rule)


		def cus_loc_rule(m,j,i):
			return m.X[(j,i)]-m.Y[i]<=0
		self.m.CusLocRul=pe.Constraint(self.m.cus_set*self.m.loc_set,rule=cus_loc_rule)

		solver = pyomo.opt.SolverFactory('cplex')
		results = solver.solve(self.m, tee=True, keepfiles=False, options_string="mip_tolerances_integrality=1e-9 mip_tolerances_mipgap=0")

		if (results.solver.status != pyomo.opt.SolverStatus.ok):
			logging.warning('Check solver not ok?')
		if (results.solver.termination_condition != pyomo.opt.TerminationCondition.optimal):  
			logging.warning('Check solver optimality?') 
		
		return results


if __name__ == '__main__':
	fl = FacLoc(budget=1) 
	#fl.m.pprint()


