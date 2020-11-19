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
        page = response.url.split("/")[-2]
        filename = f'ADAM-{page}.html'
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log(f'Saved file {filename}')