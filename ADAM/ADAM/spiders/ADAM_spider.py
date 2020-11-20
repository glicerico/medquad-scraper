import glob
import xml.etree.cElementTree as ET

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
        title_text = response.css('title::text').get()
        yield {'test': title_text}
        root = self.tree.getroot()
        for qapair in root.iter('QAPair'):
            question = qapair.find('Question').text
            answer = qapair.find('Answer')
            answer.text = 'Algo asi'
        tree = ET.ElementTree(root)
        tree.write('newdata.xml')

