import scrapy


class ADAMSpider(scrapy.Spider):
    name = "ADAM"

    def start_requests(self):
        urls = [
            'https://medlineplus.gov/ency/article/000321.htm'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        yield {'test' : response.css('title::text').get()}
