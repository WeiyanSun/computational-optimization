from function_for_prediction import *
import numpy as np
import pandas as pd
from sklearn.preprocessing import Imputer,StandardScaler
from scipy.stats.stats import pearsonr
from sklearn.feature_selection import SelectKBest,SelectPercentile,RFE,RFECV,SelectFromModel
from sklearn.svm import SVR,SVC
from sklearn.linear_model import Lasso
from sklearn.svm import LinearSVR
from sklearn.cross_validation import train_test_split
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import r2_score
import seaborn as sns
import re
import matplotlib.pyplot as plt
import matplotlib
from sklearn.ensemble import AdaBoostRegressor
from sklearn.linear_model import LinearRegression,Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor


class predict_model():
	def __init__(self,csv="movie_metadata_new.csv"):
		self.data=pd.read_csv(csv)

	def preprocess(self):
		## model for score

		# data preprocessing, select some str variable and fill na with mode
		obj_col=['language','country','content_rating']
		self.data=fill_non_num_mode(self.data,obj_col)

		# select only numeric variable

		numeric_data=self.data.select_dtypes(exclude=['object'])

		# make our goal: imdb score a single vector
		self.score=numeric_data['imdb_score']
		numeric_data=numeric_data.drop(['imdb_score'],axis=1)


		# fillna with mean and normalize the feature.after this combine with dummy variable.
		imp = Imputer(missing_values="NaN",strategy="mean",axis=0)      #default values
		numeric_data[numeric_data.columns]=imp.fit_transform(numeric_data)
		scaler = StandardScaler()
		numeric_data[numeric_data.columns] = scaler.fit_transform(numeric_data[numeric_data.columns])

		# add dummies to numeric_data and get our final data
		final_data=get_dummy_and_append(numeric_data,self.data[obj_col])
		# select final col by cov_analysis
		final_col=['num_critic_for_reviews', 'duration', 'director_facebook_likes', 'num_voted_users', 'num_user_for_reviews', 'title_year', 'movie_facebook_likes','gross','actor_1_facebook_likes', 'English', 'UK', 'USA', 'PG-13', 'TV-MA', 'cast_total_facebook_likes', 'budget', 'actor_2_facebook_likes']
		self.final_data=final_data[final_col]

	def create_model(self):
		# svr with diff kernel
		self.svr_linear_model = LinearSVR()
		self.svr_model = SVR(kernel='rbf') # guassian kernal
		self.svr_poly_model = SVR(kernel="poly") #default degree is 3

		# knn with diff n, uniform
		self.default_knn = KNeighborsRegressor(n_neighbors=5)#,weights='distance')
		self.knn_10 = KNeighborsRegressor(n_neighbors=10,weights='distance')
		self.knn_20 = KNeighborsRegressor(n_neighbors=20)#,weights='distance')
		# knn with diff n, distance
		#distance

		self.lr=LinearRegression()
		self.rf=RandomForestRegressor()
		self.rg=Ridge()
		self.adaboost=AdaBoostRegressor()

	# choose which models needed to train
	def train_model_and_compare(self,model_list):
		self.training_x,self.test_x,self.training_Y,self.test_y = split_data(self.final_data,self.score)
		#model_list=[svr_linear_model,svr_model,svr_poly_model,knn_10,lr,rf,rg,adaboost]
		for model in model_list:
			temp=train_eval_model(model,self.training_x,self.training_Y,self.test_x,self.test_y,score_type="mse")
			model_name=re.search('(.*)\(',str(model)).group(1)
			#print(str(model_name)," training error", str(temp[0]))
			print(str(model_name)," testing error", str(temp[1]))
	def cross_validation_compare(self,model_list):
		
		#model_list=[svr_linear_model,svr_model,svr_poly_model,knn_10,lr,rf,rg,adaboost]
		for model in model_list:
			temp=cross_val_model(model,self.final_data,self.score,score_type="mse")
			model_name=re.search('(.*)\(',str(model)).group(1)
			#print(str(model_name)," training error", str(temp[0]))
			print(str(model_name)," testing error", str(temp))

	def TunParaByPlotError(self):
		train_error_list=[]
		test_error_list=[]
		train_error_list2=[]
		test_error_list2=[]

		for i in range(2,100,1):
			model = KNeighborsRegressor(n_neighbors=i)#,weights='distance')
			temp=train_eval_model(model,self.training_x,self.training_Y,self.test_x,self.test_y,score_type="mse")
			train_error_list.append(temp[0])
			test_error_list.append(temp[1])

			model = KNeighborsRegressor(n_neighbors=i,weights='distance')
			temp=train_eval_model(model,self.training_x,self.training_Y,self.test_x,self.test_y,score_type="mse")
			train_error_list2.append(temp[0])
			test_error_list2.append(temp[1])

		# do plotting only for uniform distance
		sns.set_style("whitegrid")
		line1,=plt.plot(np.linspace(2,99,98),train_error_list,'r',label='uniform(training error)')
		line2,=plt.plot(np.linspace(2,99,98),test_error_list,'g',label='uniform(testing error)')

		plt.legend(handles=[line1,line2],loc=4)
		plt.xlabel('# of nearest neighbor')
		plt.ylabel('mean squared error')
		plt.show()

		# do plotting for both distance function
		sns.set_style("whitegrid")
		line1,=plt.plot(np.linspace(2,99,98),train_error_list,'r',label='uniform(training error)')
		line2,=plt.plot(np.linspace(2,99,98),test_error_list,'g',label='uniform(testing error)')
		line3,=plt.plot(np.linspace(2,99,98),train_error_list2,'b',label='distance(training error)')
		line4,=plt.plot(np.linspace(2,99,98),test_error_list2,'y',label='distance(testing error)')
		         
		plt.legend(handles=[line1,line2,line3,line4],loc=4)
		plt.xlabel('# of nearest neighbor')
		plt.ylabel('mean squared error')
		plt.show()

	def TunParaByPlotErrorRF(self):
		test_error_auto=[]
		test_error_sqrt=[]
		test_error_log2=[]

		for i in range(5,505,5):
			model1 = RandomForestRegressor(n_estimators=i,max_features="auto")
			model2 = RandomForestRegressor(n_estimators=i,max_features="sqrt")
			model3 = RandomForestRegressor(n_estimators=i,max_features="log2")

			test_error_auto.append(train_eval_model(model1,self.training_x,self.training_Y,self.test_x,self.test_y,score_type="mse")[1])
			test_error_sqrt.append(train_eval_model(model2,self.training_x,self.training_Y,self.test_x,self.test_y,score_type="mse")[1])
			test_error_log2.append(train_eval_model(model3,self.training_x,self.training_Y,self.test_x,self.test_y,score_type="mse")[1])
			

		# do plotting only for uniform distance
		sns.set_style("whitegrid")
		line1,=plt.plot(np.linspace(5,500,100),test_error_auto,'r',label='test error(all_feature)')
		line2,=plt.plot(np.linspace(5,500,100),test_error_sqrt,'g',label='test error(sqrt)')
		line3,=plt.plot(np.linspace(5,500,100),test_error_sqrt,'b',label='test error(sqrt)')
		plt.legend(handles=[line1,line2,line3],loc=4)
		plt.xlabel('# of tree')
		plt.ylabel('mean squared error')
		plt.show()


	def HistModelPlot(self,model="knn_10",name="knn"):
		model=getattr(self,model)
		sns.distplot(model.predict(self.test_x),hist=True,color="red")
		sns.distplot(self.test_y,hist=True,color="green")
		sns.plt.title('Hist of prediction by '+name+' and true value')
		sns.plt.legend([name+' prediction','true value'])
		plt.show()

	def HistPredPlot(self,prediction):
		sns.distplot(prediction,hist=True,color="red")
		sns.distplot(self.test_y,hist=True,color="green")
		sns.plt.title('Hist of prediction by final model and true value')
		sns.plt.legend(['Final Model Prediction','true value'])
		plt.show()


	def LinearBlend(self):
		# "rg":self.rg.predict(self.training_x),
		# "rg":self.rg.predict(self.test_x),
		second_train=pd.DataFrame({'rf':self.rf.predict(self.training_x),'knn':self.knn_10.predict(self.training_x),'svr':self.svr_model.predict(self.training_x)})
		second_test=pd.DataFrame({'rf':self.rf.predict(self.test_x),'knn':self.knn_10.predict(self.test_x),'svr':self.svr_model.predict(self.test_x)})

		# simple blending
		predicted_y_test_knn=self.knn_10.predict(self.test_x)
		predicted_y_test_rf=self.rf.predict(self.test_x)
		predicted_y_test_svr=self.svr_model.predict(self.test_x)
		#blending by uniform combination
		predicted_y_test=predicted_y_test_rf*0.5+predicted_y_test_knn*0.5
		print 'blending uniforom combination'
		print sum((predicted_y_test-self.test_y)**2)/len(predicted_y_test)
		print '-----------------------------------------------------'
		# blending by linear combination
		predicted_y_test=predicted_y_test_rf*0.6+predicted_y_test_svr*0.3+predicted_y_test_knn*0.1
		print 'blending linear combination'
		print sum((predicted_y_test-self.test_y)**2)/len(predicted_y_test)
		print '-----------------------------------------------------'
		# several ways of blending by training another alg.
		final_lr=LinearRegression()
		final_rf=RandomForestRegressor()
		final_boost=AdaBoostRegressor()

		# linear regression
		print 'linear regression blending'
		print train_eval_model(final_lr,self.training_x,self.training_Y,self.test_x,self.test_y,score_type="mse")[1]
		print '-----------------------------------------------------'
		# random forest
		print 'random forest blending'
		print train_eval_model(final_rf,self.training_x,self.training_Y,self.test_x,self.test_y,score_type="mse")[1]
		print '-----------------------------------------------------'
		# adaboost 
		print 'Ada boosting blending'
		print train_eval_model(final_boost,self.training_x,self.training_Y,self.test_x,self.test_y,score_type="mse")[1]
		print '-----------------------------------------------------'

	def prediction(self):
		index=list(self.test_x.index)
		predict_df=self.data.loc[index,["movie_title","imdb_score"]]
		# final model is the linear blending of rf,knn,svr
		predicted_y_test_knn=self.knn_10.predict(self.test_x)
		predicted_y_test_rf=self.rf.predict(self.test_x)
		predicted_y_test_svr=self.svr_model.predict(self.test_x)
		#blending by uniform combination
		self.predicted_y_test=predicted_y_test_rf*0.6+predicted_y_test_svr*0.3+predicted_y_test_knn*0.1

		predict_df['predict']=self.predicted_y_test
		#predict_df.sort("imdb_score",ascending=False).to_csv('prediction_result.csv',index=False)



if __name__ == '__main__':
	score_ml = predict_model() 
	score_ml.preprocess()
	score_ml.create_model()
	score_ml.train_model_and_compare([score_ml.svr_linear_model,score_ml.svr_model,score_ml.svr_poly_model,score_ml.knn_10,score_ml.lr,score_ml.rf,score_ml.rg,score_ml.adaboost])
	#score_ml.cross_validation_compare([score_ml.svr_linear_model,score_ml.svr_model,score_ml.svr_poly_model,score_ml.knn_10,score_ml.lr,score_ml.rf,score_ml.rg,score_ml.adaboost])
	#score_ml.TunParaByPlotErrorRF()
	
	#score_ml.TunParaByPlotError()
	# score_ml.HistPlot()
	score_ml.LinearBlend()
	score_ml.prediction()
	score_ml.HistPredPlot(score_ml.predicted_y_test)