import scrapy


class ADAMSpider(scrapy.Spider):
    name = "ADAM"

    def start_requests(self):
        urls = [
            'https://github.com/abachaa/MedQuAD/tree/master/10_MPlus_ADAM_QA'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        for row in response.css('div.flex-auto.min-width-0.col-md-2.mr-3 a.js-navigation-open.link-gray-dark'):
            print(row.attrib['href'] + '\n\n\n\n')
            yield row.attrib['href']
