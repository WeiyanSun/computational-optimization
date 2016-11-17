import scrapy
import pdb
import re
import json
import urllib2
#pdb.set_trace()

def prepare_movie_urls():
    with open("movie_url.json", "r") as f:
        movies = json.load(f)

    urls = []
    for m in movies:
        #title = m['Title']
        #title_for_url = urllib2.quote(title.encode('utf-8'))
        imdb_link = m['Movie link']
        urls.append(imdb_link)

    return urls,movies

def movie_budget_data():
    with open("movie_budget.json", "r") as f:
        movies = json.load(f)
    return movies

def from_url_to_title(url,movies):
    for movie in movies:
        if movie["Movie link"]==url:
            return movie['Movie name']
def from_title_to_budget(title,budget_info):
    for budget in budget_info:
        if budget["Title"]==title:
            return budget



class ImdbSpider(scrapy.Spider):
    name = 'Imdb'

    def start_requests(self):
        #self.count=-1
        self.budget_info=movie_budget_data()
        urls,movies = prepare_movie_urls()
        self.movies=movies
        self.count=0
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)


    # Figure out how to do these queries using Selector Gadget, xpath
    # and scrapy shell 'http://mat.tepper.cmu.edu/blog/'
    def parse(self, response):
        self.count+=1
        print self.count
        item={}

        # add in elements from json step2 title and url
        item['movie_imdb_link']=response.url
        item['movie_title']=from_url_to_title(response.url,self.movies)
        
        # # add in elements from json step1 budget and gross
        # budget=from_title_to_budget(item['movie_title'],self.budget_info)
        # item['title_year']=budget['Date'].split('/')[-1]
        # item['budget']=budget['Production Budget']
        # item['worldwide_gross']=budget['Worldwide Gross']
        # item['domestic_gross']=budget['Domestic Gross']

        try:
            score=response.css('strong span::text').extract()[0]
        except:
            score=None

        item['imdb_score']=score
        

        try:
            content_rating=response.css('.subtext meta[itemprop="contentRating"] ::attr(content)').extract()[0]
        except:
            content_rating=None
        item['content_rating']=content_rating
        try:
            duration=response.css('.subtext time::attr(datetime)').extract()[0]
        except:
            duration=None
        item['duration']=duration

        try:
            num_vote=response.css('.imdbRating span[itemprop="ratingCount"]::text').extract_first()
        except:
            num_vote=None
        item['num_voted_users']=num_vote

        try:
            num_review=response.css('.imdbRating span[itemprop="reviewCount"]::text').extract_first()
        except:
            num_review=None
        item['num_user_for_reviews']=num_review
        
        try:
            num_review=response.css('.imdbRating span[itemprop="reviewCount"]::text').extract()
            num_review_user=num_review[0]
            num_review_critic=num_review[1]
        except:
            num_review_user=None
            num_review_critic=None
        item['num_user_for_reviews']=num_review_user
        item['num_critic_for_reviews']=num_review_critic

        try:
            kw=response.css('#titleStoryLine .itemprop::text').extract()
            kw='|'.join(kw)
        except:
            kw=None
        item['plot_keywords']=kw

        try:
            genres=response.css('.txt-block~ .canwrap a::text').extract()
            genres='|'.join(genres)
        except:
            genres=None
        item['genres']=genres

        try:
            country= response.css('.txt-block:nth-child(4) a::text').extract_first()
        except:
            country=None
        item['country']=country

        try:
            color=response.css('.txt-block:nth-child(23) a::text').extract_first()
        except:
            color=None
        item['color']=color

        try:
            aspect_ratio=response.css('.txt-block:nth-child(24)::text').extract()[1]
        except:
            aspect_ratio=None
        item['aspect_ratio']=aspect_ratio

        try:
            poster=response.css('#title-overview-widget img::attr(src)').extract_first()
        except:
            poster=None
        item['poster_url']=poster

        # cast list
        try:
            cast_url=response.css('#titleCast .itemprop a::attr(href)').extract()
            # get full url
            cast_url=[response.urljoin(x) for x in cast_url]

            cast_name=response.css('#titleCast .itemprop::text').extract()
            cast_name=cast_name[1::3]

            cast_list=zip(cast_name,cast_url)
        except:
            cast_list=None
        item['cast_info']=cast_list

        try:
            director_name=response.css('.summary_text+ .credit_summary_item span[itemprop="name"]::text').extract_first()
            director_url=response.css('.summary_text+ .credit_summary_item a::attr(href)').extract_first()
            director_url=response.urljoin(director_url)
            director_info=[director_name,director_url]
        except:
            director_info=None
        item['director_info']=director_info




        yield item
        