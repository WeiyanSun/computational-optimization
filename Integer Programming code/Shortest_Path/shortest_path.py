
# coding: utf-8



import pyomo
import pandas
import pyomo.opt
import pyomo.environ as pe


node=pandas.read_csv("nodes.csv")
node.set_index(['Node'],inplace=True)
node


arc=pandas.read_csv("arcs.csv")
arc.set_index(["Start","End"],inplace=True)
arc


m=pe.ConcreteModel()

# Create set
m.node_set=pe.Set(initialize=node.index)
m.arc_set=pe.Set(initialize=arc.index,dimen=2)


# Create variable # don't use dimen parameter here, only use it when creating set
m.Y=pe.Var(m.arc_set,domain=pe.NonNegativeReals) # pe.Binary
# Create obj
def obj_rule(m):
    return sum(arc.loc[e,"ArcData"]*m.Y[e] for e in m.arc_set)
m.OBJ=pe.Objective(rule=obj_rule,sense=pe.minimize)

# take care the sequence of parameter, if here is m, r, n, 
# when we call this function, we must use res_set*ndoe*set
# in the sum, we don't need to add [] to make the inner part a list first. 
def flow_bal_rule(m,n):
    temp_arc=arc.reset_index()
    succs=temp_arc[temp_arc['Start']==n]['End'].values
    preds=temp_arc[temp_arc['End']==n]['Start'].values
    return sum(m.Y[p,n] for p in preds)-sum([m.Y[(n,s)] for s in succs])==node.loc[n,"Imbalance"]

m.FlowBal=pe.Constraint(m.node_set,rule=flow_bal_rule)

# if this is only one constraint instead of loop over all set
def loc_rule(m):
	return sum(m.Y[i] for i in m.loc_set)==2
m.LocRul=pe.Constraint(rule=loc_rule)




solver=pyomo.opt.SolverFactory("cplex")
results = solver.solve(m, tee=True, keepfiles=False, options_string="mip_tolerances_integrality=1e-9 mip_tolerances_mipgap=0")

if (results.solver.status != pyomo.opt.SolverStatus.ok):
    logging.warning('Check solver not ok?')
if (results.solver.termination_condition != pyomo.opt.TerminationCondition.optimal):  
    logging.warning('Check solver optimality?') 

# Use this to get the final objective function results
m.OBJ()

