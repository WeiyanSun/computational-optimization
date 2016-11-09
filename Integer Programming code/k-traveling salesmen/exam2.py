# coding: utf-8

import pyomo
import pandas
import pyomo.opt
import pyomo.environ as pe

"""A class to solve the k-traveling salesmen problem
By Weiyan Sun 
"""

class k_salesman():
    def __init__(self,node_csv="nodes.csv",arc_csv="arcs.csv",sale_csv="salespeople.csv"):
        # read in relevant files
        self.node=pandas.read_csv(node_csv)

        # We will need both dataframe using edges as index and not using edges as index
        self.ori_arc=pandas.read_csv(arc_csv)
        self.arc=self.ori_arc.set_index(["startNode","endNode"])

        self.sale=pandas.read_csv(sale_csv)
        #test case, add another saleman
        # self.sale.loc[3,'Name']='Deeter'

        self.CreateModel()
        self.print_result()

    def CreateModel(self):
        self.m=pe.ConcreteModel()

        # Create set
        self.m.node_set=pe.Set(initialize=self.node['nodeName'].values)
        self.m.arc_set=pe.Set(initialize=self.arc.index,dimen=2)
        self.m.sale_set=pe.Set(initialize=self.sale['Name'].values)

        # Create variable 
        self.m.Y=pe.Var(self.m.sale_set*self.m.arc_set,domain=pe.Binary) 

        # Create obj
        def obj_rule(m):
            return sum(self.arc.loc[e,"Cost"]*m.Y[s,e] for s in self.m.sale_set for e in self.m.arc_set)
        self.m.OBJ=pe.Objective(rule=obj_rule,sense=pe.minimize)

        # Create constraint.
        # every node, for each saleman, should have zero imbalance. (So we can get a circle for each man)
        def in_out_bal_rule(m,u,k):
            succs=self.ori_arc[self.ori_arc['startNode']==u]['endNode'].values
            preds=self.ori_arc[self.ori_arc['endNode']==u]['startNode'].values
            return sum(m.Y[(k,a,u)] for a in preds)-sum(m.Y[(k,u,b)] for b in succs)==0
            
        self.m.InOutBal=pe.Constraint(self.m.node_set*self.m.sale_set,rule=in_out_bal_rule)

        #for each saleman, exact one path return to start (everyone must return)
        def start_in_rule(m,k):
            return sum(m.Y[k,e] for e in m.arc_set if e[1]=='start')==1

        self.m.StartInConst=pe.Constraint(self.m.sale_set,rule=start_in_rule)

        #for each saleman, exact one path out from start (everyone must go out)
        def start_out_rule(m,k):
            return sum(m.Y[k,e] for e in m.arc_set if e[0]=='start')==1

        self.m.StartOutConst=pe.Constraint(self.m.sale_set,rule=start_out_rule)


        # for nodes other than start, exact one path will come in this node for all salesman. (no duplicate visit)
        NonStaNode_set=[n for n in self.m.node_set if n!='start']

        def NonStart_In_rule(m,u):
            preds=self.ori_arc[self.ori_arc['endNode']==u]['startNode'].values
            return sum(m.Y[k,a,u] for a in preds for k in m.sale_set)==1

        self.m.NonStartInConst=pe.Constraint(NonStaNode_set,rule=NonStart_In_rule)

        # for nodes other than start, exact one path will go out of this node for all salesman. (again no duplicate visit)
        def NonStart_Out_rule(m,u):
            succs=self.ori_arc[self.ori_arc['startNode']==u]['endNode'].values
            return sum(m.Y[k,u,a] for a in succs for k in m.sale_set)==1

        self.m.NonStartOutConst=pe.Constraint(NonStaNode_set,rule=NonStart_Out_rule)

        # apply cplex
        solver=pyomo.opt.SolverFactory("cplex")
        results = solver.solve(self.m, tee=True, keepfiles=False, options_string="mip_tolerances_integrality=1e-9 mip_tolerances_mipgap=0")

    def print_result(self):
        # find possible first step
        pos_fir_step=[e for e in self.m.arc_set if e[0]=='start']
        # print each saleman's path
        for man in self.m.sale_set:
            # reset path for each man
            cur_man_path=['start']
            cur_node=None
            # find first step
            for fir in pos_fir_step:
                if self.m.Y[(man,fir)].value==1:
                    cur_node=fir[1]
                    cur_man_path.append(fir[1])
                    break
                    
            while cur_node!='start':
                succs=self.ori_arc[self.ori_arc['startNode']==cur_node]['endNode'].values
                for succ in succs:
                    if self.m.Y[(man,cur_node,succ)].value==1:
                        cur_man_path.append(succ)
                        cur_node=succ
                        break
            print man+"'s path is " +str(cur_man_path)
        print 'Objective function value is '+str(self.m.OBJ()) 


if __name__ == '__main__':
       ksaleman = k_salesman('nodes.csv','arcs.csv',"salespeople.csv") 
