import glob
import xml.etree.cElementTree as ET
import re

import scrapy


class ADAMSpider(scrapy.Spider):
    name = "ADAM"
    my_path = "/home/andres/repositories/MedQuAD/10_MPlus_ADAM_QA_trash/"
    # my_path = "/home/andres/repositories/MedQuAD/10_MPlus_ADAM_QA/"
    extension = "*.xml"
    tree = None

    def start_requests(self):
        for xml_file in glob.glob(self.my_path + self.extension):
            self.tree = ET.ElementTree(file=xml_file)
            url = self.tree.getroot().attrib['url']
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        div_main = response.css('div.main-single')
        first_ans = div_main.css('div#ency_summary ::text').getall()

        ids = div_main.css('div.section-body::attr(id)').getall()
        texts = div_main.css('div.section-body')
        answers = []

        for index, answer in zip(ids, texts):
            if re.search(r"section-\d+", index):
                answers.append(" ".join(answer.css('::text').getall()))

        second_title = div_main.css('div.section-title ::text').get()
        yield {
            'answers': answers,
            second_title: second_title
        }



        root = self.tree.getroot()
        for qapair in root.iter('QAPair'):
            question = qapair.find('Question').text
            answer = qapair.find('Answer')
            answer.text = 'Algo asi'
        tree = ET.ElementTree(root)
        tree.write('newdata.xml')

