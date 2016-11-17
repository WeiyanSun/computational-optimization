import scrapy
import pdb
import re
import json
import urllib2
import cPickle as pickle

def get_facebook_likes(entity_type, entity_id):
	# the 'entity_id' could be imdb movie id, or imdb people id
	if entity_type == "person":
		url = "https://www.facebook.com/widgets/like.php?width=280&show_faces=1&layout=standard&href=http%3A%2F%2Fwww.imdb.com%2Fname%2F{}%2F&colorscheme=light".format(entity_id)
	elif entity_type == "movie":
		url = "https://www.facebook.com/widgets/like.php?width=280&show_faces=1&layout=standard&href=http%3A%2F%2Fwww.imdb.com%2Ftitle%2F{}%2F&colorscheme=light".format(entity_id)
	else:
		url = None
	return url

def extract_id(movie_url,Type):
	if Type=='movie':
		return re.search('(tt[0-9]{7})',movie_url).group(1)
	elif Type=='person':
		return re.search('(nm[0-9]{7})',movie_url).group(1)


def extract_movie_link(json_file='Imdb_info_new.json'):
	with open(json_file, "r") as f:
		movies = json.load(f)
	
	id_dict={}
	for movie in movies:
		# extract movie id
		url=movie['movie_imdb_link']
		movie_id=extract_id(url,'movie')
		fb_url=get_facebook_likes('movie',movie_id)
		id_dict[fb_url]=movie['movie_title']
		# key as fb_url, value as name

		# extract director id
		if (movie['director_info'][0]!=None)&(movie['director_info'][0] not in id_dict.values()):
			director_url=movie['director_info'][1]
			director_id=extract_id(director_url,'person')
			fb_dir_url=get_facebook_likes('person',director_id)
			id_dict[fb_dir_url]=movie['director_info'][0]

		#extract actor id
		actor_list=movie['cast_info']
		for actor_info in actor_list:
			if actor_info[0] not in id_dict.values():
				actor_url=actor_info[1]
				actor_id=extract_id(actor_url,'person')
				fb_act_url=get_facebook_likes('person',actor_id)
				id_dict[fb_act_url]=actor_info[0]

	with open('fb_url_dict_new.p', 'wb') as fp:
		pickle.dump(id_dict, fp)


extract_movie_link()


			







