Steps:

1. Web scrapy 
2. Perform face detection
https://blog.nycdatascience.com/student-works/machine-learning/movie-rating-prediction/
3. Feature elimination (May use RFE in scikit learn)
http://scikit-learn.org/stable/modules/generated/sklearn.feature_selection.RFE.html

Variable to get: 28 variables
name,source
"movie_title”,homepage
"color”,homepage,Details,Technical Specs
"num_critic_for_reviews”,homepage
"movie_facebook_likes”,homepage
"duration”,homepage
"director_name”,homepage
"director_facebook_likes”,

"actor_3_name”, homepage
"actor_3_facebook_likes”, 
"actor_2_name”, homepage
"actor_2_facebook_likes" 
"actor_1_name”, homepage
"actor_1_facebook_likes"
"gross”,homepage (We may use data from the-number)
"genres”, homepage,storyline
"num_voted_users”, homepage
"cast_total_facebook_likes"
"facenumber_in_poster"
"plot_keywords”, homepage,storyline
"movie_imdb_link”,exists
"num_user_for_reviews”, homepage
 "language”, homepage,details
 "country”, homepage,details
 "content_rating”, 
"budget”,homepage,Box Office (or use current data)
 "title_year”,homepage
 "imdb_score”,homepage 
"aspect_ratio”,homepage,Technical Specs


EDA: 
1. How the quality of movies varies among countries?
2. How the total amount of movie production changes among years?
3. How total number of facebook likes affects gross?  


http://blog.dlib.net/2014/04/dlib-187-released-make-your-own-object.html

 