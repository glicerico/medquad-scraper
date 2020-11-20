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
        QAs = {'information': " ".join(first_ans)}

        ids = div_main.css('div.section-body::attr(id)').getall()
        all_keywords = div_main.css('div.section-title ::text').getall()
        texts = div_main.css('div.section-body')

        for index, answer, keyword in zip(ids, texts, all_keywords):
            if re.search(r"section-\d+", index):
                # Remove "(Prognosis)", eliminated in MedQuAD crawl
                if "Outlook" in keyword:
                    keyword = "Outlook"
                keyword = keyword.lower()  # Lowercaps to simplify lookup
                QAs[keyword] = " ".join(answer.css('::text').getall())

        yield QAs

        root = self.tree.getroot()
        for qapair in root.iter('QAPair'):
            qtype = qapair.find('Question').get('qtype')
            answer = qapair.find('Answer')
            answer.text = QAs[qtype]
        tree = ET.ElementTree(root)
        tree.write('newdata.xml')

