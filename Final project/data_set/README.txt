This data set contains the original data from https://www.kaggle.com/deepmatrix/imdb-5000-movie-dataset
named movie_metadata.csv

However, the facebook likes number in this data set is wrong. So I scrape some information that is incorrect in this original data and generate a csv called movie_data_new.csv

The way to generate this movie_data_new.csv is to use organize_to_csv.py, which takes some json files from Scrapy.

Finally, use the merge.py to merge two csv into our final data set: movie_metadata_new.csv, where some variables like actor1_name, actor1_fb_like are fixed.
