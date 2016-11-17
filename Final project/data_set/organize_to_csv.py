
import pdb
import re
import json
import cPickle as pickle
import pandas



def remove_non_ascii(s):
    # eg: u'Avatar\xa0' ---> u'Avatar'
    return re.sub(r'[^\x00-\x7F]+','', s)

def parse_price(price):
    # eg: u'$237,000,000' --> 237000000
    if not price:
        return 0
    if '$' in price:
        price=price[1::]
    price=''.join(price.split(','))
    return int(price)

def parse_fb_like(num_likes_string):
    # eg: "8.5K" --> "85000"
    if not num_likes_string:
        return 0
    size = len(num_likes_string)
    if num_likes_string[-1] == 'K':
        return int(float(num_likes_string[ : size - 1]) * 1000)
    elif num_likes_string.isdigit():
        return int(num_likes_string)
    else: 
        return 0
    
def get_total_cast_like(cast_list,fb_dict):
    # iterate through every cast and add their likes
    total_like=0
    for cast in cast_list:
        total_like+=fb_dict[cast[0]]
    return total_like



with open("Imdb_info_new.json", "r") as f:
    data= json.load(f)


with open("fb_like_new.json", "r") as f:
    fb= json.load(f)

# our fb is a list of dict, with each dict containing one key: name, one value: like
# so we can combine them into one dict
fb_dict={}
for item in fb:
    fb_dict[item.keys()[0]]=parse_fb_like(item.values()[0])


data_df=pandas.DataFrame(columns=['movie_title','movie_imdb_link','movie_facebook_likes','director_name','director_facebook_likes','actor_1_name','actor_1_facebook_likes','actor_2_name','actor_2_facebook_likes','actor_3_name','actor_3_facebook_likes','cast_total_facebook_likes']) #,'worldwide_gross','domestic_gross','budget'])
count=0
for movie in data:
    row=[]
    row.append(remove_non_ascii(movie['movie_title']))
    row.append(movie['movie_imdb_link'])
    row.append(fb_dict[movie['movie_title']])
    try:
        row.append(remove_non_ascii(movie['director_info'][0]))
        row.append(fb_dict[movie['director_info'][0]])
    except:
        row.append(None)
        row.append(None)
    try:
        row.append(remove_non_ascii(movie['cast_info'][0][0]))
        row.append(fb_dict[movie['cast_info'][0][0]])
    except IndexError:
        row.append(None)
        row.append(None)
    try:
        row.append(remove_non_ascii(movie['cast_info'][1][0]))
        row.append(fb_dict[movie['cast_info'][1][0]])
    except IndexError:
        row.append(None)
        row.append(None)
    try:
        row.append(remove_non_ascii(movie['cast_info'][2][0]))
        row.append(fb_dict[movie['cast_info'][2][0]])
    except IndexError:
        row.append(None)
        row.append(None)
    row.append(get_total_cast_like(movie['cast_info'],fb_dict))    
    
    # row.append(parse_price(movie['worldwide_gross']))
    # row.append(parse_price(movie['domestic_gross']))
    # row.append(parse_price(movie['budget']))

    data_df.loc[count]=row
    count+=1

data_df.to_csv('movie_data_new.csv',index=False)
    

