import scrapy
import pdb
import re
import json
import urllib2
#pdb.set_trace()

def prepare_imdb_title_search_urls():
    with open("movie_budget.json", "r") as f:
        movies = json.load(f)

    urls = []
    for m in movies:
        title = m['Title']
        title_for_url = urllib2.quote(title.encode('utf-8'))
        imdb_search_link = "http://www.imdb.com/find?ref_=nv_sr_fn&q={}&s=tt".format(title_for_url)
        urls.append(imdb_search_link)

    return urls


class ImdbUrlSpider(scrapy.Spider):
    name = 'Imdb_Url'

    def start_requests(self):
        urls = prepare_imdb_title_search_urls()
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)


    # Figure out how to do these queries using Selector Gadget, xpath
    # and scrapy shell 'http://mat.tepper.cmu.edu/blog/'
    def parse(self, response):
        movie_link=response.css('.result_text>a::attr(href)').extract()[0]
        full_movie_link=response.urljoin(movie_link)
        movie_name=response.css('.result_text>a::text').extract()[0]
        yield {'Movie link': full_movie_link, 'Movie name':movie_name}
        