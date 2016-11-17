import scrapy
import pdb
import re
#pdb.set_trace()

# to start scrapy, first go to the main directory of the project
# scrapy crawl your_spider_name -o pdates.csv

# to lead output into a certain file, use: 
#scrapy crawl posts -o pdates.csv

# To help write the parse method, use the following for test
# scrapy shell 'http://mat.tepper.cmu.edu/blog/'


class NumberSpider(scrapy.Spider):
    name = 'Number'

    def start_requests(self):
        urls = ['http://www.the-numbers.com/movie/budgets/all']
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    # Figure out how to do these queries using Selector Gadget, xpath
    # and scrapy shell 'http://mat.tepper.cmu.edu/blog/'
    def parse(self, response):

        all_money = response.css('td a , .data').re('class="data">(.*)<')
        # filter index
        all_money=[x for x in all_money if '$' in x]
        Production_Budget=all_money[0::3]
        Domestic_Gross=all_money[1::3]
        Worldwide_Gross=all_money[2::3]
        
        date_title=response.css('td a , .data::attr(href)').extract()
        date=date_title[0::2]
        title=date_title[1::2]
        date=[re.search('>(.*)<',x).group(1) for x in date]
        title=[re.search('>(.*)<',x).group(1) for x in title]

        # Yielding a dictionary produces an "item"
        for i in range(5248):
            yield {'Title': title[i], 'Date': date[i],'Production Budget':Production_Budget[i],'Domestic Gross':Domestic_Gross[i],'Worldwide Gross':Worldwide_Gross[i]}
        