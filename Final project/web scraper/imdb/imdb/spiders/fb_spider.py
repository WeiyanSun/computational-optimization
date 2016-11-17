import scrapy
import pdb
import re
import json
import urllib2
import cPickle as pickle
#pdb.set_trace()

# to lead output into a certain file, use: 
#scrapy crawl posts -o pdates.csv

# To help write the parse method, use the following for test
# scrapy shell 'http://mat.tepper.cmu.edu/blog/'

def prepare_fb_dict():
    with open('/Users/weiyansun/Documents/STUDY/second_year/computational_optimization/lecture notebook/scrapy/imdb/fb_url_dict_new.p', 'rb') as fp:
        data = pickle.load(fp)
    return data

class FbSpider(scrapy.Spider):
    name = 'Fb_like'


    def start_requests(self):
        self.id_dict=prepare_fb_dict()
        # # test
        # urls=[self.id_dict.keys()[self.id_dict.values().index('Vincent Stone')],self.id_dict.keys()[self.id_dict.values().index('Home Run')]]
        
        urls = self.id_dict.keys()
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    # Figure out how to do these queries using Selector Gadget, xpath
    # and scrapy shell 'http://mat.tepper.cmu.edu/blog/'
    def parse(self, response):

        # two ways to extract the info that we want
        # 1. regular expr
        # use the tag name ::text or ::attr(title)
        like_sentence = response.css('._51mw td span[class="hidden_elem"]::text').extract_first()
 
        try:
        	like_word=re.search('and (.*) others',like_sentence).group(1)
        except AttributeError:
        	like_word='1'
        except TypeError:
            like_word='0'
        name=self.id_dict[response.url]

        yield {name:like_word}
        
