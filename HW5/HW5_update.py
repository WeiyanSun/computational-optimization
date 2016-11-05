import pandas
import networkx
import geoplotter
import scipy
import pylab
import matplotlib.pyplot as pyplt
import pyomo
import pyomo.opt
import pyomo.environ as pe
import pdb



class austin_street():
    def __init__(self,df):
        self.df=pandas.read_csv(df)
        self.gd=networkx.DiGraph()
        self.time = self.df.SECONDS
 
    def putNode(self):
        self.df['start']=self.df.kmlgeometry.str.extract('.*\(([0-9-.]* [0-9-.]*),')
        self.df['end']=self.df.kmlgeometry.str.extract('.*,([0-9-.]* [0-9-.]*)\)')
        #self.edge_df=pandas.DataFrame(columns=["start_lon","start_lat","end_lon","end_lat","time"])
        #print len(self.df)
        for i,row in self.df.iterrows():
            #start_point=tuple([scipy.float64(j) for j in row['start'].split(" ")])
            #end_point=tuple([scipy.float64(j) for j in row['end'].split(" ")])
            #self.edge_df.loc[i]=[start_point[0],start_point[1],end_point[0],end_point[1],row['SECONDS']]
            
            if row["ONE_WAY"]=="FT":
                self.gd.add_edge(row['start'],row['end'],time=row["SECONDS"])
            if row["ONE_WAY"]=="TF":
                self.gd.add_edge(row['end'],row['start'],time=row["SECONDS"])
            else:
                self.gd.add_edge(row['start'],row['end'],time=row["SECONDS"])
                self.gd.add_edge(row['end'],row['start'],time=row["SECONDS"])   
            
    def putAddress(self,add_df):
        self.add_df=pandas.read_csv(add_df)
        try:
            self.g
        except AttributeError:
            self.g = geoplotter.GeoPlotter()

        for i,row in self.add_df.iterrows():
            if i==len(self.add_df)-1:
                self.g.drawPoints(row['Lon'],row['Lat'],color="g")
            else:
                self.g.drawPoints(row['Lon'],row['Lat'],color="r")
        
    
    def drawMap(self):
        self.g = geoplotter.GeoPlotter()
        self.g.clear()
        self.g.drawWorld()
        edge_list=[]
        #edge_list=self.edge_df[["start_lon","start_lat","end_lon","end_lat"]].values.tolist()
        #pdb.set_trace()
        # draw the network
        for edge in self.gd.edges():
            start=tuple([scipy.float64(j) for j in edge[0].split(" ")])
            end=tuple([scipy.float64(j) for j in edge[1].split(" ")]) 
            edge_list.append([start,end])   
        self.g.drawLines(edge_list, color= 'cornflowerblue')
        
    def findClosestNode(self,lon,lat):
        min_dist=scipy.inf
        min_point=[]
        for i_point in self.gd.nodes():
            start=tuple([scipy.float64(j) for j in i_point.split(" ")])
            dist=(start[0]-lon)**2+(start[1]-lat)**2
            if dist<min_dist:
                min_dist=dist
                min_point=i_point
        return min_point
    # def findClosestNode(self,lon,lat):
    #     # n*2
    #     scipy.set_printoptions(precision=16)
    #     self.node=scipy.array(self.gd.nodes())
    #     point=scipy.array([lon,lat])
    #     # axis =1 means the 1 axis will vanish due to sum
    #     dist=scipy.sum((self.node-point)**2,axis=1)
    #     index=scipy.argmin(dist)
    #     return self.node[index]



    def getSPNetworkx(self, startnode, destnode,find=True):
        if find:
            startnode=self.findClosestNode(*startnode)
            destnode=self.findClosestNode(*destnode)

        path=networkx.shortest_path(self.gd,startnode,destnode,'time')
        path=[tuple([scipy.float64(j) for j in x.split(" ")]) for x in path]
        return zip(path, path[1:])


    def getSPLP(self, startnode, destnode,find=True):
        if find:
            startnode=self.findClosestNode(*startnode)
            destnode=self.findClosestNode(*destnode)

        self.m=pe.ConcreteModel()

        # create sets
        # str_node=[str(i) for i in self.gd.nodes()]
        # str_edge=[str(i[0:-1]) for i in self.gd.edges(data=True)]
        # edge_dict={}
        # for item in self.gd.edges(data=True):
        #     edge_dict[str(i[0:-1])]=i[-1]['time']

        self.m.node_set=pe.Set(initialize=self.gd.nodes())
        self.m.arc_set=pe.Set(initialize=self.gd.edges(),dimen=2)

        #Create variable
        self.m.Y=pe.Var(self.gd.edges(),domain=pe.NonNegativeReals)

        #Create objective
        def obj_rule(m):
            return sum(m.Y[(s,e)]*t["time"] for s,e,t in self.gd.edges_iter(data=True))
        self.m.OBJ=pe.Objective(rule=obj_rule,sense=pe.minimize)

        def flow_bal_rule(m,n):
            if n==startnode:
                imbalance=-1
            elif n==destnode:
                imbalance=1
            else:
                imbalance=0
            succs=self.gd.successors(n)
            preds=self.gd.predecessors(n)
            return sum(m.Y[(p,n)] for p in preds) - sum(m.Y[(n,s)] for s in succs) == imbalance

        self.m.FlowBal = pe.Constraint(self.m.node_set, rule=flow_bal_rule)

        solver = pyomo.opt.SolverFactory('cplex')
        results = solver.solve(self.m, tee=True, keepfiles=False, options_string="mip_tolerances_integrality=1e-9 mip_tolerances_mipgap=0")

        if (results.solver.status != pyomo.opt.SolverStatus.ok):
            logging.warning('Check solver not ok?')
        if (results.solver.termination_condition != pyomo.opt.TerminationCondition.optimal):  
            logging.warning('Check solver optimality?')
        
        # # method 1, iterate over all edges and get the edges with value 1
        # path=[]
        # for item in self.gd.edges():
        #     if self.m.Y[item].value==1:
        #         path.append(item)
        
        # new_path=[]
        # for item in path:
        #     start=item[0]
        #     end=item[1]
        #     start_point=tuple([scipy.float64(j) for j in start.split(" ")])
        #     end_point=tuple([scipy.float64(j) for j in end.split(" ")])
        #     new_path.append([start_point,end_point])
        # return new_path

        # method 2, from start point and go to next node until current node is destnode
        path=[startnode]
        curnode=startnode
        while curnode!=destnode:
            succs=self.gd.successors(curnode)
            for node in succs:
                if self.m.Y[(curnode,node)]==1.0:
                    path.append(node)
                    curnode=node
                    break
        path=[tuple([scipy.float64(j) for j in x.split(" ")]) for x in path]
        return zip(path, path[1:])




network = austin_street('austin.csv')
address_df = pandas.read_csv('addresses.csv')

network.putNode()
network.drawMap()
network.putAddress('addresses.csv')

network.g.setZoom(-97.8526, 30.2147, -97.6264, 30.4323)
# # use networkx alg to get shortest path
# ToHulatHut_path = network.getSPNetworkx( (address_df.Lon[15], address_df.Lat[15]), (address_df.Lon[13], address_df.Lat[13]))
# network.g.drawLines(ToHulatHut_path, color= 'orange')


ToRudys_path = network.getSPLP( (address_df.Lon[15], address_df.Lat[15]), (address_df.Lon[3], address_df.Lat[3]))
network.g.drawLines(ToRudys_path, color= 'orange')



pyplt.show()
 