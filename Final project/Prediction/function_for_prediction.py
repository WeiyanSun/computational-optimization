import numpy as np
import pandas as pd
from sklearn.cross_validation import train_test_split
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import r2_score
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import cross_val_score

def fill_non_num_mode(df,obj_col):
    for col in obj_col:
        mode=df[col].value_counts().index[0]
        df[col]=df[col].fillna(mode)
    return df

# return only n-1 col
def get_dummy_and_append(numeric_df,non_numeric_df):
    for col in non_numeric_df.columns:
        dummy_df=pd.get_dummies(non_numeric_df[col]).ix[:,0:-1]
        numeric_df=pd.concat([numeric_df, dummy_df], axis=1)
    return numeric_df

def split_data(x_data,y_data,size=0.1):
    return train_test_split(x_data,y_data,test_size=size)

# score_type accpet R^2, abs error,mse

# by training and testing data
def train_eval_model(model,x_train,y_train,x_test,y_test,score_type="R^2"):
    model.fit(X=x_train,y=y_train)
    predicted_y_train = model.predict(x_train)
    predicted_y_test = model.predict(x_test)
    if score_type=="R^2":
        return [r2_score(y_train,predicted_y_train),r2_score(y_test,predicted_y_test)]
    elif score_type=='abs_error':
        return [mean_absolute_error(y_train,predicted_y_train),mean_absolute_error(y_test,predicted_y_test)]
    elif score_type=='mse':
        return [mean_squared_error(y_train,predicted_y_train),mean_squared_error(y_test,predicted_y_test)]

# by cross validation with 10 fold.
def cross_val_model(model,X,y,score_type="R^2"):    
    if score_type=="R^2":
        return cross_val_score(model,X,y,scoring='r2',cv=10).mean()
    elif score_type=='abs_error': 
        return -cross_val_score(model,X,y,scoring='neg_mean_absolute_error',cv=10).mean()
    elif score_type=='mse':
        return -cross_val_score(model,X,y,scoring='neg_mean_squared_error',cv=10).mean()


def cov_analysis(final_data,target):
    low_covariance_1 = []
    low_covariance_2 = []
    low_covariance_15 = []
    low_covariance_2g = []
    for x in final_data.columns:
        z = (np.corrcoef(final_data[x],y=target))
        if(np.fabs(z[0,1]) < 0.1):
            low_covariance_1.append(x)
        elif(np.fabs(z[0,1]) < 0.15):
            low_covariance_15.append(x)
        elif(np.fabs(z[0,1])<0.2):
            low_covariance_2.append(x)
        else:
            low_covariance_2g.append(x)
    return [low_covariance_1,low_covariance_15,low_covariance_2,low_covariance_2g]