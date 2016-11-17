
import pdb
import re
import json
import cPickle as pickle
import pandas as pd


raw=pd.read_csv('movie_metadata.csv')
new=pd.read_csv('movie_data_new.csv')

raw.movie_title=raw.movie_title.apply(lambda x: x.strip())
raw_set=set(raw.movie_title.values)
new_set=set(new.movie_title.values)

# get the movie that is in original but not in new.
exclude=raw_set-new_set
print len(exclude)

replace_col=['director_name','director_facebook_likes',
'actor_1_name','actor_1_facebook_likes','actor_2_name','actor_2_facebook_likes','actor_3_name','actor_3_facebook_likes',
'cast_total_facebook_likes','movie_facebook_likes']

for i, row in raw.iterrows():
	if row.movie_title in exclude:
		continue
	replace_row=new[new.movie_title==row.movie_title]
	#pdb.set_trace()
	for item in replace_col:
		raw.ix[i,item]=replace_row[item].values[0]


raw.to_csv('movie_metadata_new.csv',index=False)




    

