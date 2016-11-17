This scrapy project contains four spiders. 


STEP1. Use NumberSpider.py to extract a list of movie name from http://www.the-numbers.com/movie/budgets/all
OUTPUT: movie_budget.json

STEP2. Use Imdb_UrlSpider.py to extract the pair of movie name and url on imdb OUTPUT movie_url.json

STEP3. Use ImdbSpider.py to extract the data from homepage of each movie on imdb. OUTPUT info_imdb.json

STEP4. Use get_fb_url.py to get the fb_like_url for each actor and movie. OUTPUT fb_url_dict.p

STEP5. Use fb_spider.py to extract the data for fb likes number. OUTPUT fb_like.json

STEP6. Use organize_to_csv.py to organize the info_imdb.json and fb_like.json. OUTPUT movie_data.csv 
(This part is in another folder called data_set)
